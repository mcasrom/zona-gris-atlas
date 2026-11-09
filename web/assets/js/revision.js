(function(){
  var box=document.getElementById('review-list');
  var tokenInput=document.getElementById('review-token');
  var msg=document.getElementById('review-msg');
  var token=sessionStorage.getItem('atlas_review_token')||'';
  if(tokenInput) tokenInput.value=token ? '••••••••' : '';
  document.getElementById('review-token-save').addEventListener('click',function(){
    token=tokenInput.value.trim();
    if(token==='••••••••') token=sessionStorage.getItem('atlas_review_token')||'';
    sessionStorage.setItem('atlas_review_token',token);
    msg.textContent=token?'Token guardado en esta pestaña.':'Token vacío.';
    render();
  });
  function esc(value){var n=document.createElement('span');n.textContent=value||'';return n.innerHTML;}
  function review(id,status){
    if(!token){msg.textContent='Introduce el token de revisión.';return;}
    fetch('/api/atlas/review',{method:'POST',headers:{'Content-Type':'application/json','X-Atlas-Review-Token':token},body:JSON.stringify({id:id,status:status})}).then(function(r){return r.json().then(function(d){return {ok:r.ok,d:d};});}).then(function(res){
      if(!res.ok){msg.textContent=res.d.message||'No se pudo guardar.';return;}
      msg.textContent='Guardado. Se aplicará en el próximo ciclo.';
      render();
    }).catch(function(){msg.textContent='Error de conexión.';});
  }
  function render(){
    fetch('assets/data/events.json').then(function(r){return r.json();}).then(function(data){
      var pending=(data.events||[]).filter(function(e){return e.verification_status==='PENDIENTE';});
      box.replaceChildren();
      if(!pending.length){box.textContent='No hay pendientes.';return;}
      var p=document.createElement('p');p.className='muted';p.textContent=pending.length+' pendientes · revisión humana necesaria';box.appendChild(p);
      pending.forEach(function(e){
        var card=document.createElement('article');card.className='state-card';card.style.margin='14px 0';
        var h=document.createElement('h2');h.style.fontSize='1.1rem';h.style.color='#151b22';h.textContent=e.title;card.appendChild(h);
        var meta=document.createElement('p');meta.className='muted small';meta.textContent=(e.event_date||'—')+' · '+(e.place||'No documentado')+' · '+(e.category_label||e.category||'—');card.appendChild(meta);
        var desc=document.createElement('p');desc.textContent=e.description||'';card.appendChild(desc);
        var ul=document.createElement('ul');ul.className='small';(e.sources||[]).forEach(function(s){var li=document.createElement('li');var a=document.createElement('a');a.href=s.url;a.target='_blank';a.rel='noopener';a.textContent=s.title||s.url;li.appendChild(a);ul.appendChild(li);});card.appendChild(ul);
        var actions=document.createElement('p');var map=document.createElement('a');map.href='mapa.html#'+encodeURIComponent(e.id);map.textContent='Abrir en el mapa';actions.appendChild(map);actions.appendChild(document.createTextNode(' · '));
        var ok=document.createElement('button');ok.type='button';ok.className='btn';ok.textContent='Documentar';ok.addEventListener('click',function(){review(e.id,'DOCUMENTADO');});actions.appendChild(ok);actions.appendChild(document.createTextNode(' '));
        var no=document.createElement('button');no.type='button';no.className='btn';no.textContent='Rechazar';no.addEventListener('click',function(){review(e.id,'RECHAZADO');});actions.appendChild(no);
        card.appendChild(actions);box.appendChild(card);
      });
    }).catch(function(){box.textContent='No se pudo cargar la cola de revisión.';});
  }
  render();
})();
