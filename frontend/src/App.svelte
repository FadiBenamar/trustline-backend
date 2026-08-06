<script>
  const asset = {
    logo: '/figma-assets/logo.svg', globe: '/figma-assets/globe.svg',
    scan: '/figma-assets/scan.svg', history: '/figma-assets/history.svg', learn: '/figma-assets/learn.svg', profile: '/figma-assets/profile.svg',
    bolt: '/figma-assets/bolt.svg', clip: '/figma-assets/clip.svg', paste: '/figma-assets/paste.svg', lock: '/figma-assets/lock.svg', search: '/figma-assets/search.svg', clue: '/figma-assets/clue.svg', arrow: '/figma-assets/arrow.svg',
    trusted: '/figma-assets/trusted.svg', careful: '/figma-assets/careful.svg', danger: '/figma-assets/danger.svg',
    back: '/figma-assets/back.svg', right: '/figma-assets/right.svg', close: '/figma-assets/close.svg', check: '/figma-assets/check.svg', book: '/figma-assets/book.svg', heart: '/figma-assets/heart.svg', context: '/figma-assets/context.svg', image: '/figma-assets/image.svg', robot: '/figma-assets/robot.svg', bulb: '/figma-assets/bulb.svg'
  };
  let page = localStorage.getItem('trustline-onboarded') ? 'scan' : 'onboarding', content = '', liteMode = true, result = null, checking = false, selected = [], pickedRisk = '';
  let toast = '', showFullText = false, showPasteOptions = false;
  const navItems = [['scan', asset.scan, 'Scan'], ['history', asset.history, 'History'], ['learn', asset.learn, 'Learn'], ['profile', asset.profile, 'Profile']];
  const practiceMessage = 'WARNING!!! Put your phone on airplane mode tonight or hackers can steal all your private information through 5G signals. Share this before it gets deleted!';
  const showToast = (message) => { toast = message; setTimeout(() => toast = '', 2600); };
  const authenticate = () => { localStorage.setItem('trustline-onboarded', '1'); page = 'scan'; };
  const risk = (value) => value === 'green' ? ['Trustworthy', 'Low', 'trusted'] : value === 'red' ? ['High Risk', 'High', 'danger'] : ['Careful', 'Moderate', 'careful'];
  const score = (data) => Number.isFinite(Number(data?.overall_risk_score)) ? Math.min(100, Math.max(0, Math.round(Number(data.overall_risk_score)))) : 0;
  const flags = (data) => [['Sources', data.flags.missing_sources_context, asset.book], ['Emotional Language', data.flags.emotional_manipulation, asset.heart], ['Context', data.flags.logical_fallacies, asset.context], ['Images', data.flags.synthetic_text_signals, asset.image], ['AI Content', data.flags.synthetic_text_signals, asset.robot]];
  async function paste() { try { content = await navigator.clipboard.readText(); showPasteOptions = false; } catch { showToast('Clipboard access was not available.'); } }
  async function analyze() { if (!content.trim()) return showToast('Paste a message, post or link first.'); checking = true; page = 'loading'; try { const res = await fetch('/analyze/', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({content, lite_mode: liteMode}) }); const data = await res.json(); if (!res.ok) throw new Error(data.detail || 'Analysis failed.'); result = data; const history = JSON.parse(localStorage.getItem('trustline-history') || '[]'); history.unshift({ content: content.slice(0, 80), risk: data.traffic_light, time: 'Just now' }); localStorage.setItem('trustline-history', JSON.stringify(history.slice(0, 12))); page = 'result'; } catch (error) { showToast(error.message || 'Unable to check this content.'); page = 'scan'; } finally { checking = false; } }
  async function copyCorrection() { try { await navigator.clipboard.writeText(result.correction_snippet); page = 'correction'; } catch { showToast('Select the correction and copy it.'); } }
  async function shareCorrection() { try { if (navigator.share) await navigator.share({ title: 'TrustLine correction', text: result?.correction_snippet }); page = 'share-done'; } catch { page = 'share'; } }
  const historyItems = () => JSON.parse(localStorage.getItem('trustline-history') || '[]');
  const toggle = (item) => selected = selected.includes(item) ? selected.filter((entry) => entry !== item) : [...selected, item];
</script>

<svelte:head><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous"><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:ital,wght@1,500&display=swap" rel="stylesheet"></svelte:head>

<main class="figma-app">
  <div class="screen-content">
    {#if page === 'onboarding'}
      <header class="brand-row"><div class="brand"><img src={asset.logo} alt=""/> <strong>Trust</strong>Line</div></header>
      <section class="onboarding-screen"><img class="onboarding-hero" src="/figma-assets/onboarding-hero.png" alt="People checking information together"/><div class="onboarding-copy"><h1>Think First.<br/>Share Better.</h1><p>Verify information, understand the truth behind it, and learn the skills to recognize misinformation—before you share.</p><button class="main-button" onclick={() => page = 'signin'}>Get started</button></div><div class="onboarding-nav" aria-label="Primary navigation">{#each navItems as item}<button onclick={() => page = item[0]} class:active={item[0] === 'scan'}><img src={item[1]} alt=""/><span>{item[2]}</span></button>{/each}</div></section>
    {:else if page === 'signin' || page === 'signup'}
      <header class="brand-row"><div class="brand"><img src={asset.logo} alt=""/> <strong>Trust</strong>Line</div></header>
      <section class="auth-screen"><h1>{page === 'signin' ? 'Log in to TrustLine' : 'Let’s get you started'}</h1><p>{page === 'signin' ? 'Welcome back. Check before you share.' : 'Create an account to keep learning.'}</p><label>Email<input type="email" placeholder="name@email.com"/></label><label>Password<input type="password" placeholder="••••••••"/></label><button class="main-button" onclick={authenticate}>{page === 'signin' ? 'Log in' : 'Create an account'}</button><div class="divider"><span></span>or<span></span></div><button class="auth-provider">Continue with Google</button><button class="auth-provider">Continue with Facebook</button><p class="auth-switch">{page === 'signin' ? 'Don’t have an account?' : 'Already have an account?'} <button onclick={() => page = page === 'signin' ? 'signup' : 'signin'}>{page === 'signin' ? 'Sign up' : 'Log in'}</button></p></section>
    {:else if page === 'scan'}
      <header class="brand-row"><div class="brand"><img src={asset.logo} alt=""/> <strong>Trust</strong>Line</div><button class="language"><img src={asset.globe} alt=""/> EN <span>⌄</span></button></header>
      <section class="lite"><div><img src={asset.bolt} alt=""/><p><b>Lite mode</b><small>Designed for slow internet</small></p></div><button class:enabled={liteMode} class="switch" onclick={() => liteMode = !liteMode} aria-label="Toggle lite mode"><i></i></button></section>
      <section class="scan-form"><div class="paste-box"><textarea bind:value={content} placeholder="Paste the message, post or link here..."></textarea><div><img src={asset.clip} alt=""/><button onclick={() => showPasteOptions = !showPasteOptions}><img src={asset.paste} alt=""/>Paste</button></div></div>{#if showPasteOptions}<div class="paste-options"><button onclick={paste}>Paste from clipboard</button><button onclick={() => showToast('Upload is ready to connect to the backend.')}>Upload file</button></div>{/if}<p class="privacy"><img src={asset.lock} alt=""/>We only use this to check the message. It's not saved or shared.</p><button class="main-button" onclick={analyze} disabled={checking}><img src={asset.search} alt=""/>{checking ? 'Analyzing…' : 'Analyze'}</button></section>
      <button class="clue-card" onclick={() => page = 'learn'}><img src={asset.clue} alt=""/><span><b>Spot the Clues</b><small>Practice spotting misinformation before revealing the answer. Encourage your critical thinking!</small></span><i><img src={asset.arrow} alt=""/></i></button>
      <div class="divider"><span></span>or<span></span></div><section class="indications"><p>Indications</p><div><span><img src={asset.trusted} alt=""/>TRUSTWORTHY</span><span><img src={asset.careful} alt=""/>CAREFUL</span><span><img src={asset.danger} alt=""/>HIGH RISK</span></div></section>
    {:else if page === 'result' && result}
      {@const label = risk(result.traffic_light)}
      <header class="title-row"><button onclick={() => page = 'scan'}><img src={asset.back} alt="Back"/></button><b>Results</b><i></i></header>
      <article class="message-card"><em>"{(result.extracted_text || content).slice(0, 135)}{(result.extracted_text || content).length > 135 ? '…' : ''}"</em><button onclick={() => showFullText = true}>View full text <img src={asset.right} alt=""/></button></article>
      <section class="verdict {label[2]}"><div class="verdict-icon"><img src={asset.check} alt=""/></div><b>{label[0]}</b><strong class="risk-score">{score(result)}%</strong><small>Risk level: {label[1]}</small></section>
      <section class="breakdown"><h2>Trust Breakdown</h2>{#each flags(result) as [name, item, icon]}<article><i></i><span><img src={icon} alt=""/></span><div><b>{name}</b><p>{item.explanation}</p></div></article>{/each}</section>
      <section class="correction"><b>⌕ &nbsp;SUGGESTED CORRECTION</b><p>{result.correction_snippet}</p><button onclick={copyCorrection}>Create correction</button></section><button class="main-button" onclick={() => { content=''; page='scan'; }}>Verify another content</button><aside class="tip"><span><img src={asset.bulb} alt=""/></span><p><b>Tip:</b> Even trustworthy posts are worth a second look before you share.</p></aside>
    {:else if page === 'correction'}
      <header class="title-row"><button onclick={() => page='result'}><img src={asset.back} alt="Back"/></button><b>Correction</b><i></i></header><section class="completion-screen"><div class="completion-icon">✓</div><h1>Your correction is ready.</h1><p>Share a calm, evidence-based response that helps people check the claim.</p><article>{result?.correction_snippet}</article><div class="button-pair"><button onclick={() => showToast('Correction copied.')}>Copy</button><button onclick={shareCorrection}>Share</button></div></section>
    {:else if page === 'share' || page === 'share-done'}
      <header class="title-row"><button onclick={() => page='correction'}><img src={asset.back} alt="Back"/></button><b>Share</b><i></i></header><section class="completion-screen"><div class="completion-icon">↗</div><h1>{page === 'share-done' ? 'Thanks for sharing thoughtfully.' : 'Share your correction'}</h1><p>{page === 'share-done' ? 'You helped make a clearer, kinder conversation possible.' : 'Choose where you want to share this suggested correction.'}</p>{#if page === 'share'}<div class="share-grid"><button onclick={() => page='share-done'}>WhatsApp</button><button onclick={() => page='share-done'}>Messages</button><button onclick={() => page='share-done'}>Email</button><button onclick={() => showToast('Correction copied.')}>Copy</button></div>{:else}<button class="main-button" onclick={() => page='scan'}>Done</button>{/if}</section>
    {:else if page === 'learn'}
      <header class="title-row"><button onclick={() => page = 'scan'}><img src={asset.back} alt="Back"/></button><b>Spot the Clues</b><i></i></header><section class="learning-intro"><img src={asset.clue} alt=""/><h1>Learn to spot misinformation</h1><p>Read the message, trust your instincts, then reveal the clues TrustLine found.</p><button class="main-button" onclick={() => page = 'learn-risk'}>Start practice</button></section>
    {:else if page === 'learn-risk'}
      <header class="title-row"><button onclick={() => page = 'learn'}><img src={asset.back} alt="Back"/></button><b>Spot the Clues</b><i></i></header><article class="message-card lesson-message"><em>"WARNING!!! Put your phone on airplane mode tonight or hackers can steal all your private information through 5G signals. Share this before it gets deleted!"</em></article><section class="question"><h1>How would you rate this?</h1><div class="risk-choices">{#each [['Low risk','green'],['Need verification','yellow'],['High risk','red']] as choice}<button class:selected={pickedRisk === choice[1]} onclick={() => pickedRisk = choice[1]}>{choice[0]}</button>{/each}</div></section><button class="main-button" onclick={() => page = 'learn-clues'} disabled={!pickedRisk}>Continue</button>
    {:else if page === 'learn-clues'}
      <header class="title-row"><button onclick={() => page = 'scan'}><img src={asset.back} alt="Back"/></button><b>Spot the Clues</b><i></i></header><article class="message-card lesson-message"><em>"WARNING!!! Put your phone on airplane mode tonight or hackers can steal all your private information through 5G signals. Share this before it gets deleted!"</em></article><section class="question"><h1>What caught your attention?</h1><div class="choices">{#each [['No source', asset.book], ['Emotional language', asset.heart], ['Clickbait', asset.clue], ['Missing context', asset.context], ['Edited image', asset.image], ['AI-generated', asset.robot]] as item}<button class:selected={selected.includes(item[0])} onclick={() => toggle(item[0])}><img src={item[1]} alt=""/>{item[0]}</button>{/each}</div></section><button class="main-button" onclick={() => page = 'lesson-result'}>Reveal TrustLine Analysis</button>
    {:else if page === 'lesson-result'}
      <header class="title-row"><button onclick={() => page = 'learn-clues'}><img src={asset.back} alt="Back"/></button><b>Results</b><i></i></header><article class="message-card lesson-message"><em>"WARNING!!! Put your phone on airplane mode tonight or hackers can steal all your private information through 5G signals. Share this before it gets deleted!"</em></article><section class="practice-result"><h1>🎉 Great thinking!</h1><div><p>You chose</p><span>{pickedRisk === 'red' ? 'High risk' : pickedRisk === 'yellow' ? 'Need verification' : 'Low risk'}</span></div><div><p>You noticed</p>{#each selected as choice}<span>{choice}</span>{/each}</div><div><p>TrustLine also found</p><span>Emotional language</span><span>Clickbait</span><span>Missing source</span></div></section><div class="button-pair"><button onclick={() => { selected=[]; pickedRisk=''; page = 'learn'; }}>Try Another</button><button onclick={() => { content = practiceMessage; analyze(); }}>Full Analysis</button></div><aside class="tip"><span><img src={asset.bulb} alt=""/></span><p><b>Tip:</b> Emotional words and missing sources are two of the biggest red flags — trust your gut when something feels rushed or urgent.</p></aside>
    {:else if page === 'loading'}
      <header class="title-row"><button onclick={() => { checking = false; page = 'scan'; }}><img src={asset.back} alt="Back"/></button><b>Checking content</b><i></i></header>
      <section class="loading-card">
        <div class="loading-spinner" aria-hidden="true"></div>
        <h1>Reviewing the message</h1>
        <p>TrustLine is checking for manipulation cues, missing context, and AI-generated signals.</p>
      </section>
      <aside class="tip"><span><img src={asset.bulb} alt=""/></span><p><b>Tip:</b> Larger posts can take a few seconds, and a calm second look often catches more than a rushed one.</p></aside>
    {:else if page === 'history'}
      {@const historyList = historyItems()}
      <header class="history-title"><b>History</b></header>
      <section class="history-list">
        {#if historyList.length}
          {#each historyList as item}
            <article>
              <div><span class={risk(item.risk)[2]}>{risk(item.risk)[0]}</span><small>{item.time}</small></div>
              <b>{item.content}</b>
            </article>
          {/each}
        {:else}
          <article class="empty-history">
            <strong>No checks yet</strong>
            <p>Analyze a post or link to start building your review history here.</p>
          </article>
        {/if}
      </section>
    {:else if page === 'profile'}
      <header class="history-title"><b>Profile</b></header><section class="completion-screen profile-screen"><div class="completion-icon">T</div><h1>TrustLine learner</h1><p>Keep checking, keep learning.</p><button class="auth-provider" onclick={() => { localStorage.removeItem('trustline-onboarded'); page='onboarding'; }}>Log out</button></section>
    {/if}
  </div>
  {#if !['onboarding', 'signin', 'signup', 'loading', 'correction', 'share', 'share-done'].includes(page)}<nav>{#each navItems as item}<button class:active={page === item[0] || (item[0] === 'learn' && page.startsWith('learn')) || (item[0] === 'learn' && page === 'lesson-result')} onclick={() => item[0] === 'profile' ? page = 'profile' : page = item[0]}><img src={item[1]} alt=""/><span>{item[2]}</span></button>{/each}</nav>{/if}
</main>
{#if showFullText}
  <div class="full-text-overlay">
    <button class="full-text-backdrop" aria-label="Close full text" onclick={() => showFullText = false}></button>
    <div class="full-text-sheet" role="dialog" aria-modal="true" aria-label="Full text" tabindex="-1">
      <header><b>Full Text</b><button aria-label="Close full text" onclick={() => showFullText = false}><img src={asset.close} alt=""/></button></header>
      <div class="full-text-quote"><span>"</span><p>{result.extracted_text || content}</p><span>"</span></div>
    </div>
  </div>
{/if}
{#if toast}<div class="toast">{toast}</div>{/if}

<style>
  @media (min-width: 768px) {
    :global(body) { background: #dfe6df; }
    .figma-app {
      width: 100%;
      min-height: 100vh;
      margin: 0;
      padding: 48px 8vw 76px 148px;
      background: radial-gradient(circle at 70% 82%, #b9e6ae 0, transparent 24%), #eef0e4;
    }
    .screen-content { max-width: 760px; margin: 0 auto; }
    .brand-row, .title-row { height: 48px; }
    .brand { font-size: 25px; }
    .brand img { height: 27px; width: 24px; }
    .lite { margin-top: 32px; }
    .paste-box { height: 178px; }
    .paste-box textarea { height: 92px; font-size: 16px; }
    .clue-card { min-height: 126px; }
    .verdict { min-height: 180px; }
    .message-card { min-height: 136px; }
    .message-card em { font-size: 23px; }
    .breakdown article { min-height: 68px; }
    .tip { margin-bottom: 0; }
    .figma-app nav {
      position: fixed;
      z-index: 2;
      left: 24px;
      right: auto;
      top: 50%;
      bottom: auto;
      transform: translateY(-50%);
      width: 92px;
      height: auto;
      min-height: 286px;
      flex-direction: column;
      border-radius: 24px;
      padding: 8px;
    }
    .figma-app nav button { min-height: 62px; flex: 1; }
    .figma-app nav img { width: 28px; height: 28px; }
  }

  @media (min-width: 1200px) {
    .screen-content { max-width: 920px; }
    .figma-app { padding-right: 14vw; }
    .indications > div { justify-content: flex-start; }
  }

  .full-text-overlay { position: fixed; inset: 0; z-index: 10; display: flex; align-items: flex-end; justify-content: center; }
  .full-text-backdrop { position: absolute; inset: 0; border: 0; background: #0000008c; }
  .full-text-sheet { z-index: 1; width: min(100%, 393px); height: min(811px, 95vh); position: relative; overflow: hidden; border-radius: 24px 24px 0 0; padding: 26px 16px; background: radial-gradient(circle at 78% 96%, #b9e6ae 0, transparent 21%), #eef0e4; }
  .full-text-sheet header { display: flex; align-items: center; justify-content: center; font-size: 16px; }
  .full-text-sheet header button { position: absolute; top: 26px; right: 16px; display: grid; place-items: center; width: 34px; height: 34px; padding: 8px; border: 0; border-radius: 8px; background: #fff; box-shadow: 2px 3px 4.3px #00000017; }
  .full-text-sheet header img { width: 18px; height: 18px; }
  .full-text-quote { height: 288px; margin-top: 138px; display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center; font-family: "IBM Plex Serif", serif; font-style: italic; }
  .full-text-quote span { height: 69px; font: 96px/.7 "IBM Plex Serif", serif; font-style: italic; }
  .full-text-quote p { width: min(309px, 100%); margin: 0; font-size: 20px; line-height: 1.14; color: #000000c7; }

  @media (min-width: 768px) {
    .full-text-overlay { align-items: center; padding: 32px; }
    .full-text-sheet { width: min(760px, calc(100vw - 64px)); height: min(720px, calc(100vh - 64px)); border-radius: 24px; padding: 32px 48px; box-shadow: 0 24px 80px #0000003d; }
    .full-text-sheet header { font-size: 18px; }
    .full-text-sheet header button { top: 24px; right: 24px; }
    .full-text-quote { width: min(590px, 100%); height: auto; min-height: 360px; margin: 92px auto 0; justify-content: center; }
    .full-text-quote p { width: min(560px, 100%); font-size: clamp(22px, 2vw, 30px); line-height: 1.22; }
  }

  .onboarding-art { height: 220px; display: grid; place-items: center; border-radius: 28px; background: radial-gradient(circle, #fff 0 20%, transparent 21%); }
  .onboarding-art img { width: 116px; height: 116px; }
  .onboarding-screen h1 { margin: 44px 0 20px; font-size: 46px; line-height: 1.12; font-style: italic; }
  .onboarding-screen p { margin: 0 0 24px; font-size: 16px; line-height: 1.42; }
  .auth-screen { margin-top: 24px; padding: 24px; border-radius: 16px; background: #fff; box-shadow: 0 10px 28px #163b2b12; }
  .auth-screen h1 { margin: 0; font-size: 25px; }
  .auth-screen > p { margin: 7px 0 18px; color: #475569; font-size: 14px; }
  .auth-screen label { display: grid; gap: 7px; margin: 14px 0; font-size: 13px; font-weight: 600; }
  .auth-screen input { height: 43px; padding: 0 12px; border: 1px solid #00000024; border-radius: 8px; font: 400 14px inherit; }
  .auth-provider { width: 100%; height: 43px; margin: 5px 0; border: 1px solid #0000002b; border-radius: 99px; background: #fff; font: 600 14px inherit; }
  .auth-switch { text-align: center; }
  .auth-switch button { padding: 0; border: 0; background: transparent; color: #2563eb; font: 600 13px inherit; }
  .paste-options { display: grid; gap: 2px; margin-top: 5px; padding: 7px; border-radius: 10px; background: #fff; box-shadow: 0 8px 18px #0002; }
  .paste-options button { border: 0; padding: 8px; background: transparent; text-align: left; font: 500 13px inherit; }
  .learning-intro, .completion-screen { margin-top: 56px; padding: 28px 20px; border-radius: 16px; background: #fff; text-align: center; box-shadow: 0 8px 20px #163b2b0d; }
  .learning-intro > img { width: 76px; height: 76px; margin-bottom: 16px; }
  .learning-intro h1, .completion-screen h1 { margin: 0 0 10px; font-size: 23px; }
  .learning-intro p, .completion-screen p { margin: 0 0 20px; color: #475569; font-size: 14px; line-height: 1.42; }
  .risk-choices { display: flex; flex-wrap: wrap; gap: 8px; }
  .risk-choices button { min-height: 40px; padding: 8px 12px; border: 1px solid #00000020; border-radius: 99px; background: #fff; font: 600 14px inherit; }
  .risk-choices button.selected { border: 2px solid #269e7d; background: #269e7d18; }
  .completion-icon { width: 64px; height: 64px; display: grid; place-items: center; margin: 0 auto 18px; border-radius: 50%; background: #c7f0d8; color: #1a7058; font-size: 34px; font-weight: 700; }
  .completion-screen article { padding: 15px; border-radius: 12px; background: #eef0e4; text-align: left; font-size: 14px; line-height: 1.45; }
  .share-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .share-grid button { height: 68px; border: 0; border-radius: 12px; background: #eef0e4; font: 600 14px inherit; }
  .profile-screen { margin-top: 80px; }
  .risk-score { margin-top: -3px; font-size: 30px; line-height: 1; color: #0f6e56; }
  .verdict.careful .risk-score { color: #9a5e0b; }
  .verdict.danger .risk-score { color: #b42318; }
  .onboarding-screen { position: relative; min-height: 768px; }
  .onboarding-hero { width: 100%; }
  .onboarding-copy h1 { margin: 0 0 20px; font-size: 48px; line-height: 1.14; font-style: italic; }
  .onboarding-copy p { margin: 0 0 24px; font-size: 16px; line-height: 1.4; }
  .onboarding-nav { position: absolute; right: 0; bottom: 0; left: 0; display: flex; padding: 4px; border-radius: 999px; background: rgba(248, 249, 251, .2); }
  .onboarding-nav button { flex: 1; min-height: 58px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; border: 0; border-radius: 999px; background: transparent; font: 500 10px inherit; }
  .onboarding-nav button.active { color: #1a7058; background: rgba(217, 218, 218, .58); }
  .onboarding-nav img { width: 26px; height: 26px; }

  @media (min-width: 768px) {
    .onboarding-screen { min-height: 680px; max-width: 620px; margin: 0 auto; }
    .onboarding-nav { display: none; }
  }
</style>
