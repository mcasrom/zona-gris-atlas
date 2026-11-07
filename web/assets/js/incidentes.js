(function () {
  "use strict";
  var events = [];
  var reference = new Date();

  function text(value) { return value == null || value === "" ? "—" : String(value); }
  function statusLabel(value) {
    if (value === "CONFIRMADO") return "Confirmado";
    if (value === "DOCUMENTADO") return "Documentado";
    return "Pendiente";
  }
  function statusClass(value) { return value === "PENDIENTE" ? "pending" : "documented"; }
  function attributionLabel(item) {
    var status = item.attribution && item.attribution.status;
    if (status === "official") return "Oficial";
    if (status === "claimed") return "Reivindicada";
    return "Por definir";
  }
  function attributionKey(item) {
    return (item.attribution && item.attribution.status) || "none";
  }
  function zone(item) {
    return [item.place, item.country].filter(Boolean).join(" · ") || "No documentada";
  }
  function dateValue(item) {
    var value = Date.parse((item.event_date || item.published_at || "") + "T00:00:00Z");
    return Number.isNaN(value) ? 0 : value;
  }
  function sourceCell(item) {
    var sources = item.sources || [];
    if (!sources.length) return "—";
    var a = document.createElement("a");
    a.href = sources[0].url;
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = sources.length === 1 ? "1 fuente" : sources.length + " fuentes";
    return a;
  }
  function row(item) {
    var tr = document.createElement("tr");
    tr.dataset.id = item.id;
    var cells = [
      item.id,
      item.event_date || item.published_at || "—",
      null,
      item.category_label || item.category || "—",
      zone(item),
      null,
      attributionLabel(item),
      null,
    ];
    cells.forEach(function (value, index) {
      var td = document.createElement("td");
      if (index === 2) {
        var strong = document.createElement("strong");
        strong.textContent = item.title || "—";
        td.appendChild(strong);
        if (item.description) {
          var p = document.createElement("p");
          p.className = "muted small";
          p.textContent = item.description;
          td.appendChild(p);
        }
      } else if (index === 5) {
        var span = document.createElement("span");
        span.className = "status-pill " + statusClass(item.verification_status);
        span.textContent = statusLabel(item.verification_status);
        td.appendChild(span);
      } else if (index === 7) {
        td.appendChild(sourceCell(item));
      } else {
        td.textContent = text(value);
      }
      tr.appendChild(td);
    });
    return tr;
  }
  function filtered() {
    var domain = document.getElementById("incident-domain").value;
    var status = document.getElementById("incident-status").value;
    var attribution = document.getElementById("incident-attribution").value;
    var date = document.getElementById("incident-date").value;
    var q = document.getElementById("incident-search").value.trim().toLowerCase();
    var limit = date === "all" ? Infinity : Number(date) * 86400000;
    var base = reference.getTime();
    return events.filter(function (item) {
      if (domain !== "all" && item.category !== domain) return false;
      if (status !== "all" && item.verification_status !== status) return false;
      if (attribution !== "all" && attributionKey(item) !== attribution) return false;
      if (limit !== Infinity && base - dateValue(item) > limit) return false;
      if (q && [item.id, item.title, item.description, item.place, item.country, item.category_label].join(" ").toLowerCase().indexOf(q) === -1) return false;
      return true;
    }).sort(function (a, b) { return dateValue(b) - dateValue(a); });
  }
  function summary(list) {
    var total = events.length;
    var docs = events.filter(function (i) { return i.verification_status === "DOCUMENTADO"; }).length;
    var pending = events.filter(function (i) { return i.verification_status === "PENDIENTE"; }).length;
    var confirmed = events.filter(function (i) { return i.verification_status === "CONFIRMADO"; }).length;
    var attributed = events.filter(function (i) { return attributionKey(i) !== "none"; }).length;
    return list.length + " de " + total + " · " + docs + " documentados · " + pending + " pendientes · " + confirmed + " confirmados · " + attributed + " con atribución";
  }
  function update() {
    var list = filtered();
    var body = document.getElementById("incident-rows");
    body.replaceChildren();
    if (!list.length) {
      var tr = document.createElement("tr");
      var td = document.createElement("td");
      td.colSpan = 8; td.className = "muted"; td.textContent = "No hay incidentes con estos filtros.";
      tr.appendChild(td); body.appendChild(tr);
    } else {
      list.forEach(function (item) { body.appendChild(row(item)); });
    }
    document.getElementById("incident-count").textContent = list.length;
    document.getElementById("incident-total").textContent = events.length;
    document.getElementById("incident-summary").textContent = summary(list);
  }
  function fill(id, values) {
    var node = document.getElementById(id);
    values.forEach(function (pair) {
      var option = document.createElement("option");
      option.value = pair[0]; option.textContent = pair[1]; node.appendChild(option);
    });
  }
  function boot() {
    fetch("assets/data/events.json").then(function (r) { return r.json(); }).then(function (data) {
      events = data.events || [];
      reference = new Date(data.generated_at || Date.now());
      var domains = {};
      events.forEach(function (item) { domains[item.category] = item.category_label || item.category; });
      fill("incident-domain", Object.keys(domains).sort().map(function (k) { return [k, domains[k]]; }));
      document.getElementById("incident-meta").textContent = events.length + " acontecimientos · actualizado " + (data.generated_at || "sin fecha") + " · sin gravedad ni índice ZG inventados";
      ["incident-domain", "incident-status", "incident-attribution", "incident-date"].forEach(function (id) {
        document.getElementById(id).addEventListener("change", update);
      });
      document.getElementById("incident-search").addEventListener("input", update);
      document.getElementById("incident-reset").addEventListener("click", function () {
        ["incident-domain", "incident-status", "incident-attribution", "incident-date"].forEach(function (id) { document.getElementById(id).value = "all"; });
        document.getElementById("incident-search").value = "";
        update();
      });
      update();
    }).catch(function () {
      document.getElementById("incident-rows").innerHTML = "<tr><td colspan=\"8\" class=\"muted\">No se pudo cargar la matriz.</td></tr>";
    });
  }
  boot();
})();
