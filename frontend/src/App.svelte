<script>
  const asset = {
    logo: 'https://www.figma.com/api/mcp/asset/a3d4b584-c46e-4380-bcfd-8c3b92e3f111', globe: 'https://www.figma.com/api/mcp/asset/0fcd4548-7870-45e2-a581-1509ad1b000e',
    scan: 'https://www.figma.com/api/mcp/asset/6dbfcab0-2d23-4895-9b0a-be38a88235af', history: 'https://www.figma.com/api/mcp/asset/56afc08b-6316-46ca-bb8d-96499691eddd', learn: 'https://www.figma.com/api/mcp/asset/37bf8820-6fcb-4105-b394-37cc081387bc', profile: 'https://www.figma.com/api/mcp/asset/c838434c-1e69-472c-be43-256e9a2c78ac',
    bolt: 'https://www.figma.com/api/mcp/asset/e42244db-5475-4f4c-ade5-404e2b1d5dd5', clip: 'https://www.figma.com/api/mcp/asset/7592e2ee-ceb6-482b-9145-aecc110da52c', paste: 'https://www.figma.com/api/mcp/asset/c649f61a-1761-400e-b147-e2e06cfcff53', lock: 'https://www.figma.com/api/mcp/asset/c1c78d1a-284f-4a30-b270-9a7f69d99e8d', search: 'https://www.figma.com/api/mcp/asset/da443065-1b6e-4b62-83e7-3c5e7ea6d797', clue: 'https://www.figma.com/api/mcp/asset/e25c040e-2d7d-495c-91ea-630d80040574', arrow: 'https://www.figma.com/api/mcp/asset/d60dc294-4c65-422a-9290-c943cc30b72d',
    trusted: 'https://www.figma.com/api/mcp/asset/0280981d-bc0c-4386-9476-ff44c5fd320b', careful: 'https://www.figma.com/api/mcp/asset/4836175c-0164-4f48-9b22-ce8ff4b8e397', danger: 'https://www.figma.com/api/mcp/asset/ee901e51-be3c-49a1-a315-b587d6d392ac',
    back: 'https://www.figma.com/api/mcp/asset/83e173ef-f291-4c74-bd57-b7879d21c8fa', right: 'https://www.figma.com/api/mcp/asset/5c25b43b-d407-477e-8ba7-b689edd6ab25', close: 'https://www.figma.com/api/mcp/asset/84c8e29e-805b-4061-8012-4b0b7689b26b', check: 'https://www.figma.com/api/mcp/asset/1e71530a-a261-40b2-a74f-522ca03ea323', book: 'https://www.figma.com/api/mcp/asset/b9719803-cf9c-4d86-89cf-2bf0bc140aec', heart: 'https://www.figma.com/api/mcp/asset/088a52f0-bc36-41aa-a6c6-ceef809d92bd', context: 'https://www.figma.com/api/mcp/asset/ce3e94a0-599d-4447-bfad-a88475dfeb80', image: 'https://www.figma.com/api/mcp/asset/089ac48f-b8ec-4066-b644-dfb209d2542c', robot: 'https://www.figma.com/api/mcp/asset/2a38149c-ac6b-4d74-bf3b-d23d1e7288ab', bulb: 'https://www.figma.com/api/mcp/asset/2aa83a7f-019a-4464-9bab-da2fbb211b12'
  };
  let page = 'scan', content = '', liteMode = true, result = null, checking = false, selected = ['Emotional language', 'Clickbait'];
  let toast = '', showFullText = false;
  const navItems = [['scan', asset.scan, 'Scan'], ['history', asset.history, 'History'], ['learn', asset.learn, 'Learn'], ['profile', asset.profile, 'Profile']];
  const showToast = (message) => { toast = message; setTimeout(() => toast = '', 2600); };
  const risk = (value) => value === 'green' ? ['Trustworthy', 'Low', 'trusted'] : value === 'red' ? ['High Risk', 'High', 'danger'] : ['Careful', 'Moderate', 'careful'];
  const flags = (data) => [['Sources', data.flags.missing_sources_context, asset.book], ['Emotional Language', data.flags.emotional_manipulation, asset.heart], ['Context', data.flags.logical_fallacies, asset.context], ['Images', data.flags.synthetic_text_signals, asset.image], ['AI Content', data.flags.synthetic_text_signals, asset.robot]];
  async function paste() { try { content = await navigator.clipboard.readText(); } catch { showToast('Clipboard access was not available.'); } }
  async function analyze() { if (!content.trim()) return showToast('Paste a message, post or link first.'); checking = true; page = 'loading'; try { const res = await fetch('/analyze/', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({content, lite_mode: liteMode}) }); const data = await res.json(); if (!res.ok) throw new Error(data.detail || 'Analysis failed.'); result = data; const history = JSON.parse(localStorage.getItem('trustline-history') || '[]'); history.unshift({ content: content.slice(0, 80), risk: data.traffic_light, time: 'Just now' }); localStorage.setItem('trustline-history', JSON.stringify(history.slice(0, 3))); page = 'result'; } catch (error) { showToast(error.message || 'Unable to check this content.'); page = 'scan'; } finally { checking = false; } }
  async function copyCorrection() { try { await navigator.clipboard.writeText(result.correction_snippet); showToast('Correction copied.'); } catch { showToast('Select the correction and copy it.'); } }
  const historyItems = () => JSON.parse(localStorage.getItem('trustline-history') || '[]');
  const toggle = (item) => selected = selected.includes(item) ? selected.filter((entry) => entry !== item) : [...selected, item];
</script>

<svelte:head><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous"><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:ital,wght@1,500&display=swap" rel="stylesheet"></svelte:head>

<main class="figma-app">
  <div class="screen-content">
    {#if page === 'scan'}
      <header class="brand-row"><div class="brand"><img src={asset.logo} alt=""/> <strong>Trust</strong>Line</div><button class="language"><img src={asset.globe} alt=""/> EN <span>⌄</span></button></header>
      <section class="lite"><div><img src={asset.bolt} alt=""/><p><b>Lite mode</b><small>Designed for slow internet</small></p></div><button class:enabled={liteMode} class="switch" onclick={() => liteMode = !liteMode} aria-label="Toggle lite mode"><i></i></button></section>
      <section class="scan-form"><div class="paste-box"><textarea bind:value={content} placeholder="Paste the message, post or link here..."></textarea><div><img src={asset.clip} alt=""/><button onclick={paste}><img src={asset.paste} alt=""/>Paste</button></div></div><p class="privacy"><img src={asset.lock} alt=""/>We only use this to check the message. It's not saved or shared.</p><button class="main-button" onclick={analyze} disabled={checking}><img src={asset.search} alt=""/>{checking ? 'Analyzing…' : 'Analyze'}</button></section>
      <button class="clue-card" onclick={() => page = 'learn'}><img src={asset.clue} alt=""/><span><b>Spot the Clues</b><small>Practice spotting misinformation before revealing the answer. Encourage your critical thinking!</small></span><i><img src={asset.arrow} alt=""/></i></button>
      <div class="divider"><span></span>or<span></span></div><section class="indications"><p>Indications</p><div><span><img src={asset.trusted} alt=""/>TRUSTWORTHY</span><span><img src={asset.careful} alt=""/>CAREFUL</span><span><img src={asset.danger} alt=""/>HIGH RISK</span></div></section>
    {:else if page === 'result' && result}
      {@const label = risk(result.traffic_light)}
      <header class="title-row"><button onclick={() => page = 'scan'}><img src={asset.back} alt="Back"/></button><b>Results</b><i></i></header>
      <article class="message-card"><em>"{(result.extracted_text || content).slice(0, 135)}{(result.extracted_text || content).length > 135 ? '…' : ''}"</em><button onclick={() => showFullText = true}>View full text <img src={asset.right} alt=""/></button></article>
      <section class="verdict {label[2]}"><div class="verdict-icon"><img src={asset.check} alt=""/></div><b>{label[0]}</b><small>Risk level: {label[1]}</small></section>
      <section class="breakdown"><h2>Trust Breakdown</h2>{#each flags(result) as [name, item, icon]}<article><i></i><span><img src={icon} alt=""/></span><div><b>{name}</b><p>{item.explanation}</p></div></article>{/each}</section>
      <section class="correction"><b>⌕ &nbsp;SUGGESTED CORRECTION</b><p>{result.correction_snippet}</p><button onclick={copyCorrection}>Create correction</button></section><button class="main-button" onclick={() => { content=''; page='scan'; }}>Verify another content</button><aside class="tip"><span><img src={asset.bulb} alt=""/></span><p><b>Tip:</b> Even trustworthy posts are worth a second look before you share.</p></aside>
    {:else if page === 'learn'}
      <header class="title-row"><button onclick={() => page = 'scan'}><img src={asset.back} alt="Back"/></button><b>Spot the Clues</b><i></i></header><article class="message-card lesson-message"><em>"WARNING!!! Put your phone on airplane mode tonight or hackers can steal all your private information through 5G signals. Share this before it gets deleted!"</em></article><section class="question"><h1>What caught your attention?</h1><div class="choices">{#each [['No source', asset.book], ['Emotional language', asset.heart], ['Clickbait', asset.clue], ['Missing context', asset.context], ['Edited image', asset.image], ['AI-generated', asset.robot]] as item}<button class:selected={selected.includes(item[0])} onclick={() => toggle(item[0])}><img src={item[1]} alt=""/>{item[0]}</button>{/each}</div></section><button class="main-button" onclick={() => page = 'lesson-result'}>Reveal TrustLine Analysis</button>
    {:else if page === 'lesson-result'}
      <header class="title-row"><button onclick={() => page = 'learn'}><img src={asset.back} alt="Back"/></button><b>Results</b><i></i></header><article class="message-card lesson-message"><em>"WARNING!!! Put your phone on airplane mode tonight or hackers can steal all your private information through 5G signals. Share this before it gets deleted!"</em></article><section class="practice-result"><h1>🎉 Great thinking!</h1><div><p>You chose</p><span>⚠ High risk</span></div><div><p>You noticed</p><span>Emotional language</span><span>Clickbait</span></div><div><p>TrustLine also found</p><span>AI-generated</span></div></section><div class="button-pair"><button onclick={() => page = 'learn'}>Try Another</button><button onclick={() => page = 'scan'}>Full Analysis</button></div><aside class="tip"><span><img src={asset.bulb} alt=""/></span><p><b>Tip:</b> Emotional words and missing sources are two of the biggest red flags — trust your gut when something feels rushed or urgent.</p></aside>
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
    {/if}
  </div>
  <nav>{#each navItems as item}<button class:active={page === item[0]} onclick={() => item[0] === 'profile' ? showToast('Profile is not included in Final Design V1.') : page = item[0]}><img src={item[1]} alt=""/><span>{item[2]}</span></button>{/each}</nav>
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
</style>