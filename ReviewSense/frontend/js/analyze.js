$('save').checked = get('save', false);
$('mode').onchange = () => { const b = $('mode').value === 'bulk'; $('saveRow').hidden = b; $('text').placeholder = b ? 'One review per line (up to 100)…' : 'Paste a product review…'; $('result').hidden = true; };
$('go').onclick = async () => {
  const text = $('text').value.trim(), bulk = $('mode').value === 'bulk';
  if (text.length < 3) return toast('Enter a review to analyze.', 'err');
  $('go').disabled = true;
  try {
    if (bulk) renderBatch(await api('/analyze-batch', {method:'POST', body:JSON.stringify({text})}), $('result'));
    else { const r = await api('/analyze', {method:'POST', body:JSON.stringify({text, save:$('save').checked})}); renderResult(r, $('result')); if (r.id) toast('Analysis saved to history'); }
    $('result').scrollIntoView({behavior:'smooth'});
  } catch {} finally { $('go').disabled = false; }
};
$('clear').onclick = () => { if ($('text').value && !confirm('Clear the text and result?')) return; $('text').value = ''; $('result').hidden = true; };
