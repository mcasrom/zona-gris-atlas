(function(){
  var box=document.getElementById('review-list');
  fetch('assets/data/events.json').then(function(r){ return r.json(); }).then(function(data){
    var pending=(data.events||[]).filter(function(e){ return e.verification_status==='PENDIENTE'; });
    box.replaceChildren();
    if(!pending.length){ box.textContent='No hay pendientes.'; return; }
    var p=document.createElement('p'); p.className='muted'; p.textContent=pending.length+' pendientes · revisión humana necesaria'; box.appendChild(p);
    pending.forEach(function(e){
      var card=document.createElement('article'); card.className='state-card'; card.style.margin='14px 0';
      var h=document.createElement('h2'); h.style.fontSize='1.1rem'; h.textContent=e.title; card.appendChild(h);
      var meta=document.createElement('p'); meta.className='muted small'; meta.textContent=(e.event_date||'—')+' · '+(e.place||'No documentado')+' · '+(e.category_label||e.category||'—'); card.appendChild(meta);
      var desc=document.createElement('p'); desc.textContent=e.description||''; card.appendChild(desc);
      var ul=document.createElement('ul'); ul.className='small'; (e.sources||[]).forEach(function(s){ var li=document.createElement('li'); var a=document.createElement('a'); a.href=s.url; a.target='_blank'; a.rel='noopener'; a.textContent=s.title||s.url; li.appendChild(a); ul.appendChild(li); }); card.appendChild(ul);
      var links=document.createElement('p'); var map=document.createElement('a'); map.href='mapa.html#'+encodeURIComponent(e.id); map.textContent='Abrir en el mapa'; links.appendChild(map); card.appendChild(links);
      box.appendChild(card);
    });
  }).catch(function(){ box.textContent='No se pudo cargar la cola de revisión.'; });
})();
