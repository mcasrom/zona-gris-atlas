(function () {
  "use strict";
  var list = document.getElementById("primary-list");
  var meta = document.getElementById("primary-meta");
  if (!list) return;
  fetch("assets/data/primary.json").then(function (r) { return r.json(); }).then(function (data) {
    var docs = data.documents || [];
    var sources = (data.sources || []).map(function (s) { return s.name; }).join(" · ");
    if (meta) meta.textContent = docs.length + " documentos · " + (sources || "fuentes primarias") + " · condiciones por fuente";
    list.replaceChildren();
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
      p.textContent = (doc.published_at || "sin fecha") + " · " + doc.source + (doc.source_country ? " · " + doc.source_country : "") + (doc.tlp ? " · TLP:" + doc.tlp : "");
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
