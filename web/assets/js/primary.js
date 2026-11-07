(function () {
  "use strict";
  var list = document.getElementById("primary-list");
  var meta = document.getElementById("primary-meta");
  if (!list) return;
  fetch("assets/data/primary.json").then(function (r) { return r.json(); }).then(function (data) {
    var docs = data.documents || [];
    if (meta) meta.textContent = docs.length + " documentos · " + (data.source || "fuente primaria") + " · " + (data.license || "licencia no indicada");
    if (!docs.length) {
      list.innerHTML = "<li class=\"muted\">No hay documentos primarios cargados.</li>";
      return;
    }
    docs.forEach(function (doc) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = doc.url; a.target = "_blank"; a.rel = "noopener";
      a.textContent = doc.title;
      li.appendChild(a);
      var p = document.createElement("p");
      p.className = "muted small";
      p.textContent = (doc.published_at || "sin fecha") + " · " + doc.source + (doc.tlp ? " · TLP:" + doc.tlp : "");
      li.appendChild(p);
      if (doc.summary) {
        var s = document.createElement("p");
        s.textContent = doc.summary;
        li.appendChild(s);
      }
      list.appendChild(li);
    });
  }).catch(function () {
    list.innerHTML = "<li class=\"muted\">No se pudo cargar la capa primaria.</li>";
  });
})();
