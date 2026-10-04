const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const get = (k,d) => { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } };
const put = (k,v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };
const NAMES = {positive:'Positive', negative:'Negative', neutral:'Neutral'};
const EMO = {positive:'😊', negative:'😞', neutral:'😐'};
const sgn = v => (v > 0 ? '+' : '') + v.toFixed(2);
const stars = n => '★'.repeat(n) + '☆'.repeat(5 - n);
function toast(msg, type='ok') { const t = document.createElement('div'); t.className = 'toast ' + type; t.textContent = msg; $('toasts').appendChild(t); setTimeout(() => t.remove(), 4000); }
async function api(path, opt={}) {
  try {
    const r = await fetch('/api' + path, {headers:{'Content-Type':'application/json'}, ...opt});
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.error || 'Request failed.');
    return d;
  } catch (e) { toast(e.message === 'Failed to fetch' ? 'Cannot reach the server. Is Flask running?' : e.message, 'err'); throw e; }
}
function applyTheme() { document.documentElement.dataset.theme = get('dark', false) ? 'dark' : 'light'; if ($('themeBtn')) $('themeBtn').textContent = get('dark', false) ? '☀️ Light' : '🌙 Dark'; }
const bars = p => Object.entries(p).sort((a,b) => b[1]-a[1]).map(([k,v]) => `<div class="pr"><span>${EMO[k]||''} ${NAMES[k]||esc(k)}</span><div class="meter"><div class="fill ${esc(k)}" style="width:${v}%"></div></div><b>${v}%</b></div>`).join('');
const aspTable = a => a.length ? `<div class="tbl-wrap"><table class="tbl"><tr><th>Topic</th><th>Mentions</th><th>Sentiment</th><th>Score</th></tr>${a.map(x => `<tr><td>${esc(x.aspect)}</td><td>${x.mentions}</td><td>${EMO[x.label]} ${NAMES[x.label]}</td><td>${sgn(x.score)}</td></tr>`).join('')}</table></div>` : '<p class="note">No specific product topics (battery, price, delivery, etc.) were mentioned.</p>';
function renderResult(r, el) {
  const kp = r.keywords.positive.map(w => `<span class="tag pos">${esc(w)}</span>`).join(''), kn = r.keywords.negative.map(w => `<span class="tag neg">${esc(w)}</span>`).join('');
  const cl = r.clauses.length ? r.clauses.map(x => `<div class="sent"><small class="tag">${EMO[x.label]} ${sgn(x.score)}</small><span>${esc(x.text)}</span></div>`).join('') : '';
  const s = r.stats;
  el.innerHTML = `<div class="verdict ${esc(r.label)}"><h2>${EMO[r.label]||''} ${NAMES[r.label]||esc(r.label)}</h2><p style="margin:.3rem 0 0">Sentiment score <strong>${sgn(r.score)}</strong> (-1 very negative, +1 very positive) · model confidence <strong>${r.confidence}%</strong>${r.low_confidence ? ' (low)' : ''} · estimated rating <span title="Estimated from the score, not given by the reviewer">${stars(r.estimated_stars)}</span></p></div>
  <div class="card"><h2>Review insight</h2><p>${esc(r.insight)}</p></div>
  <div class="card"><h2>Sentiment probabilities</h2>${bars(r.probabilities)}</div>
  <div class="card"><h2>Keywords</h2><p><strong>Positive:</strong> ${kp || '<span class="note">none</span>'}</p><p><strong>Negative:</strong> ${kn || '<span class="note">none</span>'}</p></div>
  <div class="card"><h2>Product topics</h2>${aspTable(r.aspects)}<p class="note">Topics are found with a keyword list; their sentiment comes from the model.</p></div>
  ${cl ? `<div class="card"><h2>Clause by clause</h2>${cl}</div>` : ''}
  <div class="card"><h2>Text statistics</h2><div class="kv"><div><small>Words</small><b>${s.words}</b></div><div><small>Characters</small><b>${s.characters}</b></div><div><small>Sentences</small><b>${s.sentences}</b></div><div><small>Avg words / sentence</small><b>${s.avg_words_per_sentence}</b></div><div><small>Exclamation marks</small><b>${s.exclamation_marks}</b></div><div><small>Question marks</small><b>${s.question_marks}</b></div></div></div>
  <p class="note">A statistical estimate. Sarcasm, mixed opinions and unusual wording can be misread.</p>`;
  el.hidden = false;
}
function renderBatch(b, el) {
  const pct = Object.fromEntries(Object.entries(b.counts).map(([k,v]) => [k, Math.round(1000*v/b.total)/10]));
  const overall = b.avg_score >= 0.2 ? 'positive' : b.avg_score <= -0.2 ? 'negative' : 'neutral';
  el.innerHTML = `<div class="verdict ${overall}"><h2>${EMO[overall]} ${b.total} reviews analyzed</h2><p style="margin:.3rem 0 0">Average sentiment score <strong>${sgn(b.avg_score)}</strong></p></div>
  <div class="card"><h2>Insight</h2><p>${esc(b.insight) || 'No clear praised or criticised topics.'}</p></div>
  <div class="card"><h2>Distribution</h2>${bars(pct)}</div>
  <div class="card"><h2>Topics across all reviews</h2>${aspTable(b.aspects)}</div>
  <div class="card"><h2>Reviews</h2>${b.reviews.map(x => `<div class="sent"><small class="tag">${EMO[x.label]} ${sgn(x.score)}</small><span>${esc(x.text)}</span></div>`).join('')}</div><p class="note">Bulk analyses are not saved to history.</p>`;
  el.hidden = false;
}
const page = location.pathname.split('/').pop() || 'index.html';
const nl = (h, t) => `<a href="${h}"${page === h ? ' class="cur" aria-current="page"' : ''}>${t}</a>`;
$('hdr').innerHTML = `<header class="top"><a class="logo" href="index.html">⭐ ReviewSense</a>
<button id="menuBtn" class="icon" aria-label="Toggle menu" aria-expanded="false">☰</button>
<nav id="nav" aria-label="Main">${nl('index.html','Analyze')}${nl('dashboard.html','Dashboard')}${nl('history.html','History')}${nl('about.html','About')}
<button id="setBtn" class="link">Settings</button><button id="themeBtn" class="icon" aria-label="Switch between light and dark mode"></button></nav></header>
<dialog id="dlg" aria-labelledby="dt"><h2 id="dt">Settings</h2>
<label><input type="checkbox" id="sSave"> Save analyses to history by default</label>
<label><input type="checkbox" id="sDark"> Dark mode</label>
<div class="row"><button id="sClear" class="btn danger">Clear history</button><button id="sClose" class="btn primary">Close</button></div></dialog>
<div id="toasts" aria-live="polite"></div>`;
$('sSave').checked = get('save', false); $('sDark').checked = get('dark', false); applyTheme();
$('menuBtn').onclick = () => { const o = $('nav').classList.toggle('open'); $('menuBtn').setAttribute('aria-expanded', o); };
$('themeBtn').onclick = () => { put('dark', !get('dark', false)); $('sDark').checked = get('dark', false); applyTheme(); };
$('setBtn').onclick = () => $('dlg').showModal(); $('sClose').onclick = () => $('dlg').close();
$('sSave').onchange = e => { put('save', e.target.checked); if ($('save')) $('save').checked = e.target.checked; };
$('sDark').onchange = e => { put('dark', e.target.checked); applyTheme(); };
$('sClear').onclick = async () => {
  if (!confirm('Delete all saved analyses? This cannot be undone.')) return;
  await api('/history', {method:'DELETE'}); toast('History cleared'); window.dispatchEvent(new Event('historychanged'));
};
