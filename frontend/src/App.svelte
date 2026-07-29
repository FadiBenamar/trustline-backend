<script>
  const presets = {
    scam: 'URGENT! You have won $10,000. Click this link now and forward it to everyone you know!',
    vague: 'They say scientists have found a shocking truth that the government is hiding.',
    news: 'UNESCO announced a new initiative to promote media and information literacy among youth worldwide in 2026.'
  };
  let screen = localStorage.getItem('trustline-onboarded') ? 'app' : 'intro';
  let page = 'check';
  let content = '';
  let result = null;
  let isChecking = false;
  let toast = '';
  let selectedAnswer = '';

  const showToast = (message) => { toast = message; setTimeout(() => toast = '', 2600); };
  const authenticate = () => { localStorage.setItem('trustline-onboarded', '1'); screen = 'app'; page = 'check'; };
  const setPreset = (kind) => content = presets[kind];
  const riskClass = (risk) => risk === 'green' ? 'green' : risk === 'red' ? 'red' : 'yellow';
  const riskText = (risk) => risk === 'green' ? ['Trustworthy', 'This looks safe to share.'] : risk === 'red' ? ['High risk', 'This content may be misleading.'] : ['Needs verification', 'Pause and check before sharing.'];

  async function analyze() {
    if (!content.trim()) return showToast('Paste a message, post, or link first.');
    isChecking = true;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/analyze/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content, lite_mode: false }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Analysis failed.');
      result = data;
      const history = JSON.parse(localStorage.getItem('trustline-history') || '[]');
      history.unshift({ content: content.slice(0, 70), risk: data.traffic_light, score: data.overall_risk_score, time: new Date().toLocaleDateString() });
      localStorage.setItem('trustline-history', JSON.stringify(history.slice(0, 12)));
      page = 'results';
    } catch (error) { showToast(error.message || 'We could not check that right now.'); }
    finally { isChecking = false; }
  }
  async function copySuggestion() {
    try { await navigator.clipboard.writeText(result.correction_snippet); showToast('Suggested response copied.'); }
    catch { showToast('Select and copy the response manually.'); }
  }
  function history() { return JSON.parse(localStorage.getItem('trustline-history') || '[]'); }
</script>

<svelte:head>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,700;0,800;1,700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" />
</svelte:head>

{#if screen === 'intro'}
  <main class="intro"><div class="brand">✦ TrustLine</div><div class="art">◌ <i class="fa-solid fa-magnifying-glass"></i></div><div><h1>Think First.<br />Share Better.</h1><p>Verify information, understand the truth behind it, and share it with confidence.</p></div><button class="primary" onclick={() => screen = 'auth'}>Get started <i class="fa-solid fa-arrow-right"></i></button></main>
{:else if screen === 'auth'}
  <main class="auth"><button class="back" onclick={() => screen = 'intro'}>‹</button><div class="brand">✦ TrustLine</div><section><i class="fa-solid fa-shield-halved shield"></i><h1>Log in to TrustLine</h1><p>Your guide to safer sharing.</p><form onsubmit={(event) => { event.preventDefault(); authenticate(); }}><label>Email<input type="email" value="user@example.com" required /></label><label>Password<input type="password" value="password" required /></label><button class="primary">Log in</button></form><div class="or">or</div><button class="secondary"><i class="fa-brands fa-google"></i> Continue with Google</button><p>Don't have an account? <button class="link" onclick={() => screen = 'register'}>Sign up</button></p></section></main>
{:else if screen === 'register'}
  <main class="auth"><button class="back" onclick={() => screen = 'auth'}>‹</button><div class="brand">✦ TrustLine</div><section><h1>Let's get you started</h1><p>Create an account to build safer sharing habits.</p><form onsubmit={(event) => { event.preventDefault(); authenticate(); }}><label>Name<input required placeholder="Your name" /></label><label>Email<input required type="email" placeholder="you@example.com" /></label><label>Password<input required type="password" placeholder="Create a password" /></label><button class="primary">Create an account</button></form><p>Already have an account? <button class="link" onclick={() => screen = 'auth'}>Log in</button></p></section></main>
{:else}
  <main class="app"><header><div class="brand">✦ TrustLine</div><button class="lang">EN⌄</button></header>
    {#if page === 'check'}
      <section class="page check"><div class="welcome"><h1>Hi, there! 👋</h1><p>Let’s make your next share a little smarter.</p></div><div class="checker"><label>Paste the message, post or link here.<textarea bind:value={content} rows="5" placeholder="Paste a WhatsApp forward, social post, or article link..."></textarea></label><small>{content.length} / 2,000</small><button class="primary" disabled={isChecking} onclick={analyze}>{isChecking ? 'Checking…' : '⌕ Analyze'}</button></div><button class="quick" onclick={() => page = 'learn'}><span>💡</span><div><b>Spot the Clues</b><small>Practice identifying misleading content.</small></div>›</button><div class="situations"><h2>Situations</h2>{#each Object.keys(presets) as preset}<button onclick={() => setPreset(preset)}>{preset === 'scam' ? '🚨 Viral scam' : preset === 'vague' ? '💬 Vague claim' : '📰 Verified news'}</button>{/each}</div></section>
    {:else if page === 'results' && result}
      {@const labels = riskText(result.traffic_light)}
      <section class="page results"><button class="link" onclick={() => page = 'check'}>‹ Back</button><h1>Results</h1><blockquote>“{(result.extracted_text || content).slice(0, 140)}”</blockquote><div class="risk {riskClass(result.traffic_light)}"><i class="fa-solid fa-circle-check"></i><div><b>{labels[0]}</b><small>{labels[1]}</small></div><strong>{result.overall_risk_score}<small>/100</small></strong></div><h2>Trust breakdown</h2>{#each [['Sources', result.flags.missing_sources_context], ['Emotional language', result.flags.emotional_manipulation], ['Content signals', result.flags.synthetic_text_signals], ['Logic', result.flags.logical_fallacies]] as item}<article class="flag"><i class="fa-solid fa-circle-check"></i><div><b>{item[0]}</b><p>{item[1].explanation}</p></div><span class={item[1].severity}>{item[1].severity}</span></article>{/each}<div class="suggestion"><div><b>💬 Suggested response</b><p>{result.correction_snippet}</p></div><button aria-label="Copy suggested response" onclick={copySuggestion}><i class="fa-regular fa-copy"></i></button></div><button class="primary" onclick={() => { content = ''; page = 'check'; }}>Verify another content</button></section>
    {:else if page === 'learn'}
      <section class="page learn"><div class="hero"><small>LEARN AT YOUR PACE</small><h1>Spot the Clues</h1><p>Build the skills to pause, question and share wisely.</p></div><article><small>LESSON 01</small><h2>What caught your attention?</h2><p>Learn to notice the signals that make a message feel urgent or convincing.</p><button class="primary" onclick={() => page = 'lesson'}>Start the lesson</button></article></section>
    {:else if page === 'lesson'}
      <section class="page lesson"><button class="link" onclick={() => page = 'learn'}>‹ Learning mode</button><small>SPOT THE CLUES</small><h1>What do you think?</h1><p>Which message is most likely trying to make you react before you check?</p>{#each ['The report was published today.', 'Scientists announced a new study.', 'Share this now before they delete it!'] as answer}<button class:selected={selectedAnswer === answer} class="answer" onclick={() => selectedAnswer = answer}>{answer}</button>{/each}{#if selectedAnswer}<button class="primary" onclick={() => { showToast('Exactly — urgency is a clue to pause and verify.'); page = 'learn'; }}>Continue</button>{/if}</section>
    {:else if page === 'history'}
      <section class="page history"><h1>History</h1>{#if history().length}{#each history() as item}<article class="history-item {item.risk}"><span></span><div><b>{item.content}</b><small>{item.time} · {item.score}/100 risk</small></div></article>{/each}{:else}<div class="empty">◷<p>Your checked content will appear here.</p></div>{/if}</section>
    {/if}
    <nav>{#each [['check','▣','Check'],['learn','♧','Learn'],['history','◷','History'],['profile','◯','Profile']] as item}<button class:active={page === item[0]} onclick={() => item[0] === 'profile' ? showToast('Your profile is coming soon.') : page = item[0]}><i>{item[1]}</i>{item[2]}</button>{/each}</nav>
  </main>
{/if}
{#if toast}<div class="toast">✓ {toast}</div>{/if}
