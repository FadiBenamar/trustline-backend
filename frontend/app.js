document.addEventListener("DOMContentLoaded", () => {
  const $ = (id) => document.getElementById(id);
  const screens = { intro: $("introScreen"), auth: $("authScreen"), register: $("registerScreen"), app: $("appScreen") };
  const pages = { check: $("checkPage"), results: $("resultsPage"), learn: $("learnPage"), lesson: $("lessonPage"), history: $("historyPage") };
  const contentText = $("contentText"), toast = $("toast"), toastText = $("toastText");
  let currentResult = null;

  const showScreen = (name) => Object.entries(screens).forEach(([key, node]) => node.classList.toggle("hidden", key !== name));
  const showPage = (name) => {
    Object.entries(pages).forEach(([key, node]) => node.classList.toggle("active", key === name));
    document.querySelectorAll(".nav-item").forEach((node) => node.classList.toggle("active", node.dataset.page === name));
    if (name === "history") renderHistory();
  };
  const notify = (message) => { toastText.textContent = message; toast.classList.remove("hidden"); setTimeout(() => toast.classList.add("hidden"), 2600); };
  const escapeHtml = (value) => value.replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
  const setSeverity = (element, value) => { const severity = (value || "low").toLowerCase(); element.textContent = severity.replaceAll("_", " ").toUpperCase(); element.className = severity; };

  $("startBtn").addEventListener("click", () => showScreen("auth"));
  document.querySelectorAll("[data-screen]").forEach((button) => button.addEventListener("click", () => showScreen(button.dataset.screen)));
  $("showRegister").addEventListener("click", () => showScreen("register"));
  $("showLogin").addEventListener("click", () => showScreen("auth"));
  [$("loginForm"), $("registerForm")].forEach((form) => form.addEventListener("submit", (event) => { event.preventDefault(); localStorage.setItem("trustline-onboarded", "1"); showScreen("app"); showPage("check"); }));
  if (localStorage.getItem("trustline-onboarded")) { showScreen("app"); showPage("check"); }

  $("languageBtn").addEventListener("click", () => $("languageMenu").classList.toggle("hidden"));
  $("languageMenu").addEventListener("click", (event) => { if (event.target.matches("button")) { $("languageBtn").childNodes[0].nodeValue = event.target.textContent === "English" ? "EN " : "ID "; $("languageMenu").classList.add("hidden"); } });
  contentText.addEventListener("input", () => { $("charCount").textContent = `${contentText.value.length} / 2,000`; $("urlDetectedBadge").classList.toggle("hidden", !/^https?:\/\/\S+$/i.test(contentText.value.trim())); });
  const presets = { scam: "URGENT! You have won $10,000. Click this link now and forward it to everyone you know!", vague: "They say scientists have found a shocking truth that the government is hiding.", news: "UNESCO announced a new initiative to promote media and information literacy among youth worldwide in 2026." };
  document.querySelectorAll("[data-preset]").forEach((button) => button.addEventListener("click", () => { contentText.value = presets[button.dataset.preset]; contentText.dispatchEvent(new Event("input")); }));
  $("quickCheckBtn").addEventListener("click", () => showPage("learn"));
  document.querySelectorAll(".nav-item").forEach((button) => button.addEventListener("click", () => { const page = button.dataset.page; if (page === "profile") return notify("Your profile is coming soon."); showPage(page); }));

  $("analyzeBtn").addEventListener("click", async () => {
    const content = contentText.value.trim(); if (!content) return notify("Paste a message, post, or link first.");
    const button = $("analyzeBtn"); button.disabled = true; button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Checking…';
    try { const response = await fetch("/analyze/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ content, lite_mode: false }) }); if (!response.ok) throw new Error((await response.json()).detail || "Analysis failed."); currentResult = await response.json(); renderResult(currentResult, content); saveHistory(content, currentResult); showPage("results"); }
    catch (error) { notify(error.message || "We couldn't check that right now."); }
    finally { button.disabled = false; button.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Analyze'; }
  });
  function renderResult(data, content) {
    $("resultContent").textContent = `“${(data.extracted_text || content).slice(0, 132)}${(data.extracted_text || content).length > 132 ? "…" : ""}”`;
    const states = { green: ["Trustworthy", "This looks safe to share.", "risk-green", "fa-circle-check"], yellow: ["Needs verification", "Pause and check before sharing.", "risk-yellow", "fa-circle-exclamation"], red: ["High risk", "This content may be misleading.", "risk-red", "fa-circle-xmark"] };
    const [title, subtitle, className, icon] = states[data.traffic_light] || states.yellow;
    $("trafficLightCard").className = `risk-card ${className}`; $("trafficLightIcon").innerHTML = `<i class="fa-solid ${icon}"></i>`; $("trafficLightTitle").textContent = title; $("trafficLightSub").textContent = subtitle; $("riskScore").textContent = data.overall_risk_score;
    const flags = data.flags; [["Sources", "expSources", "sevSources", flags.missing_sources_context], ["Emotion", "expEmotional", "sevEmotional", flags.emotional_manipulation], ["Synthetic", "expSynthetic", "sevSynthetic", flags.synthetic_text_signals], ["Logic", "expFallacies", "sevFallacies", flags.logical_fallacies]].forEach(([, explanationId, severityId, flag]) => { $(explanationId).textContent = flag.explanation; setSeverity($(severityId), flag.severity); });
    $("correctionSnippetText").textContent = data.correction_snippet;
  }
  $("backToCheck").addEventListener("click", () => showPage("check"));
  $("shareResultBtn").addEventListener("click", () => { contentText.value = ""; contentText.dispatchEvent(new Event("input")); showPage("check"); contentText.focus(); });
  $("copyCorrectionBtn").addEventListener("click", async () => { if (!currentResult) return; try { await navigator.clipboard.writeText(currentResult.correction_snippet); notify("Suggested response copied."); } catch { notify("Select and copy the response manually."); } });
  $("startLessonBtn").addEventListener("click", () => showPage("lesson")); $("backToLearn").addEventListener("click", () => showPage("learn"));
  $("answers").addEventListener("click", (event) => { const choice = event.target.closest("button"); if (!choice) return; document.querySelectorAll(".answers button").forEach((button) => button.classList.remove("selected")); choice.classList.add("selected"); $("continueLesson").classList.remove("hidden"); });
  $("continueLesson").addEventListener("click", () => { notify("Exactly — urgency is a clue to pause and verify."); showPage("learn"); });
  function saveHistory(content, result) { const history = JSON.parse(localStorage.getItem("trustline-history") || "[]"); history.unshift({ content: content.slice(0, 70), risk: result.traffic_light, score: result.overall_risk_score, time: new Date().toLocaleDateString() }); localStorage.setItem("trustline-history", JSON.stringify(history.slice(0, 12))); }
  function renderHistory() { const history = JSON.parse(localStorage.getItem("trustline-history") || "[]"); $("emptyHistory").classList.toggle("hidden", history.length > 0); $("historyList").innerHTML = history.map((item) => `<article class="history-item ${item.risk === "green" ? "" : item.risk}"><span class="dot"></span><div><b>${escapeHtml(item.content)}${item.content.length === 70 ? "…" : ""}</b><small>${item.time} · ${item.score}/100 risk</small></div></article>`).join(""); }
});
