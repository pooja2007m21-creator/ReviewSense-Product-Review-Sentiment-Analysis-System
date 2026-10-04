let current = null;
async function load() {
  $('details').hidden = true;
  const rows = await api('/history').catch(() => null); if (!rows) return;
  $('clearAll').hidden = !rows.length;
  $('list').innerHTML = rows.length ? rows.map(r => `<article class="card"><div class="item"><div>
    <p class="prev">${esc(r.text.slice(0,140))}${r.text.length>140?'…':''}</p>
    <div class="meta">${EMO[r.label]||''} ${NAMES[r.label]||esc(r.label)} · score ${sgn(r.score)} · ${r.word_count} words · ${esc(r.created_at)} UTC</div></div>
    <div class="row"><button class="btn" data-v="${r.id}">View</button><button class="btn danger" data-d="${r.id}">Delete</button></div></div></article>`).join('')
    : '<p class="card">No analysis history available.</p>';
}
async function del(id) { if (!confirm('Delete this analysis?')) return; await api('/history/' + id, {method:'DELETE'}); toast('Analysis deleted'); load(); }
$('list').onclick = async e => {
  const v = e.target.dataset.v, d = e.target.dataset.d;
  if (d) return del(d); if (!v) return;
  current = await api('/history/' + v);
  $('dMsg').textContent = current.text;
  renderResult(current.result, $('dRes')); $('details').hidden = false; $('details').scrollIntoView({behavior:'smooth'});
};
$('dDel').onclick = () => del(current.id);
$('clearAll').onclick = async () => { if (!confirm('Delete all saved analyses? This cannot be undone.')) return; await api('/history', {method:'DELETE'}); toast('History cleared'); load(); };
window.addEventListener('historychanged', load);
load();
