(function(){
  var frame=document.getElementById('graph-frame');
  fetch('assets/data/graph.json').then(function(r){ if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); }).then(function(data){
    var nodes=data.nodes||[], edges=data.edges||[], W=1200, H=760, cx=W/2, cy=H/2;
    var colors={event:'#ffb020',source:'#8794a3',place:'#8ec5ff',category:'#3ddc97',pending:'#5b6877'};
    var rings={category:90,event:205,place:295,source:345};
    var byType={}; nodes.forEach(function(n){ (byType[n.type]=byType[n.type]||[]).push(n); });
    var pos={};
    Object.keys(byType).forEach(function(t){ byType[t].forEach(function(n,i){ var a=-Math.PI/2+2*Math.PI*i/Math.max(byType[t].length,1), r=rings[t]||250; pos[n.id]={x:cx+r*Math.cos(a),y:cy+r*Math.sin(a)}; }); });
    function active(n){ if(n.type==='event') return true; var cb=document.querySelector('[data-type="'+n.type+'"]'); return !cb || cb.checked; }
    function render(){
      var svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
      svg.setAttribute('viewBox','0 0 '+W+' '+H); svg.setAttribute('role','img'); svg.setAttribute('aria-label','Grafo de acontecimientos, fuentes, lugares y categorías');
      var drawn=0;
      edges.forEach(function(e){
        var a=pos[e.source], b=pos[e.target]; if(!a||!b) return;
        var target=nodes.find(function(n){return n.id===e.target;}); if(target && !active(target)) return;
        var l=document.createElementNS('http://www.w3.org/2000/svg','line'); l.setAttribute('x1',a.x); l.setAttribute('y1',a.y); l.setAttribute('x2',b.x); l.setAttribute('y2',b.y); l.setAttribute('class','graph-edge'); svg.appendChild(l); drawn++;
      });
      nodes.forEach(function(n){
        if(!active(n)||!pos[n.id]) return;
        var g=document.createElementNS('http://www.w3.org/2000/svg','g'); g.setAttribute('class','graph-node '+n.type);
        var c=document.createElementNS('http://www.w3.org/2000/svg','circle'); var r=n.type==='event'?8:n.type==='category'?7:5; c.setAttribute('cx',pos[n.id].x); c.setAttribute('cy',pos[n.id].y); c.setAttribute('r',r); c.setAttribute('fill',n.type==='event'&&n.status==='PENDIENTE'?colors.pending:colors[n.type]); g.appendChild(c);
        var title=document.createElementNS('http://www.w3.org/2000/svg','title'); title.textContent=n.label||n.id; g.appendChild(title);
        if(n.type!=='source'){ var t=document.createElementNS('http://www.w3.org/2000/svg','text'); t.setAttribute('x',pos[n.id].x+10); t.setAttribute('y',pos[n.id].y+3); t.textContent=n.label||n.id; g.appendChild(t); }
        if(n.type==='event'){ g.addEventListener('click',function(){ window.location.href='mapa.html#'+encodeURIComponent(n.id); }); }
        svg.appendChild(g);
      });
      frame.replaceChildren(svg);
      document.getElementById('graph-count').textContent=String((data.counts||{}).events||(byType.event||[]).length||0);
      document.getElementById('graph-edges').textContent=String(drawn);
    }
    document.querySelectorAll('[data-type]').forEach(function(cb){ cb.addEventListener('change',render); });
    render();
  }).catch(function(){ frame.innerHTML='<div class="graph-empty">No se pudo cargar el grafo. Revisa los datos publicados.</div>'; });
})();
