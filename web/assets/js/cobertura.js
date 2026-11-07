(function () {
  "use strict";
  var target = document.getElementById("coverage-regions");
  if (!target) return;
  fetch("assets/data/coverage.json").then(function (r) { return r.json(); }).then(function (data) {
    var regions = data.regions || [];
    target.replaceChildren();
    regions.forEach(function (region) {
      var card = document.createElement("section");
      card.className = "coverage-card";
      var h = document.createElement("h3");
      h.textContent = region.label;
      card.appendChild(h);
      var p = document.createElement("p");
      p.className = "muted small";
      p.textContent = (region.queries_count || 0) + " consultas · " + (region.scope_events || 0) + " candidatos en el ámbito · " + (region.located_events || 0) + " con ubicación documentada";
      card.appendChild(p);
      var ul = document.createElement("ul");
      (region.queries || []).forEach(function (q) {
        var li = document.createElement("li");
        li.textContent = q.query + " · " + q.category;
        ul.appendChild(li);
      });
      card.appendChild(ul);
      target.appendChild(card);
    });
    var total = regions.reduce(function (n, r) { return n + (r.queries_count || 0); }, 0);
    document.getElementById("coverage-meta").textContent = regions.length + " regiones · " + total + " consultas · los ceros son huecos, no pruebas de ausencia";
  }).catch(function () { target.innerHTML = "<p class=\"muted\">No se pudo cargar la matriz.</p>"; });
})();
