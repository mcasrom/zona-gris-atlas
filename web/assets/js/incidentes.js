(function () {
  "use strict";
  var API = "/api/atlas/incidentes";
  var PAGE_SIZE = 50;
  var state = { cursor: null, stack: [], total: 0, next: null, facets: false };

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
  function zone(item) {
    return [item.place, item.country].filter(Boolean).join(" · ") || "No documentada";
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
    var cells = [item.id, item.event_date || "—", null, item.category_label || item.category || "—", zone(item), null, attributionLabel(item), null];
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
  function params(cursor) {
    var p = new URLSearchParams();
    p.set("limit", String(PAGE_SIZE));
    var domain = document.getElementById("incident-domain").value;
    var status = document.getElementById("incident-status").value;
    var attribution = document.getElementById("incident-attribution").value;
    var days = document.getElementById("incident-date").value;
    var q = document.getElementById("incident-search").value.trim();
    if (domain !== "all") p.set("domain", domain);
    if (status !== "all") p.set("status", status);
    if (attribution !== "all") p.set("attribution", attribution);
    if (days !== "all") p.set("days", days);
    if (q) p.set("q", q);
    if (cursor) p.set("cursor", cursor);
    return p;
  }
  function downloadUrl() {
    var p = params(null);
    p.delete("limit");
    p.delete("cursor");
    return "/api/atlas/incidentes.csv?" + p.toString();
  }
  function fillDomains(domains) {
    if (state.facets || !domains) return;
    var node = document.getElementById("incident-domain");
    domains.forEach(function (pair) {
      var option = document.createElement("option");
      option.value = pair.id;
      option.textContent = pair.label;
      node.appendChild(option);
    });
    state.facets = true;
  }
  function render(data) {
    var items = data.items || [];
    var body = document.getElementById("incident-rows");
    body.replaceChildren();
    if (!items.length) {
      var tr = document.createElement("tr");
      var td = document.createElement("td");
      td.colSpan = 8; td.className = "muted"; td.textContent = "No hay incidentes con estos filtros.";
      tr.appendChild(td); body.appendChild(tr);
    } else {
      items.forEach(function (item) { body.appendChild(row(item)); });
    }
    state.total = data.total || 0;
    state.next = data.next_cursor || null;
    var counts = data.counts || {};
    document.getElementById("incident-count").textContent = items.length;
    document.getElementById("incident-total").textContent = state.total;
    document.getElementById("incident-summary").textContent =
      items.length + " en esta página · " + state.total + " con los filtros · " +
      (counts.documented || 0) + " documentados · " + (counts.pending || 0) +
      " pendientes · " + (counts.confirmed || 0) + " confirmados · " +
      (counts.attributed || 0) + " con atribución";
    document.getElementById("incident-page").textContent = String(state.stack.length + 1);
    document.getElementById("incident-prev").disabled = state.stack.length === 0;
    document.getElementById("incident-next").disabled = !state.next;
    document.getElementById("incident-download").href = downloadUrl();
    document.getElementById("incident-meta").textContent = state.total + " hechos revisados · 50 por página · filtros en servidor";
  }
  function load() {
    var p = params(state.cursor);
    fetch(API + "?" + p.toString()).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }).then(function (data) {
      fillDomains(data.domains);
      render(data);
    }).catch(function () {
      document.getElementById("incident-rows").innerHTML = "<tr><td colspan=\"8\" class=\"muted\">No se pudo cargar la matriz.</td></tr>";
      document.getElementById("incident-summary").textContent = "Error de carga";
    });
  }
  function reset() {
    state.cursor = null;
    state.stack = [];
    load();
  }
  function boot() {
    ["incident-domain", "incident-status", "incident-attribution", "incident-date"].forEach(function (id) {
      document.getElementById(id).addEventListener("change", reset);
    });
    var timer = null;
    document.getElementById("incident-search").addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(reset, 300);
    });
    document.getElementById("incident-reset").addEventListener("click", function () {
      ["incident-domain", "incident-status", "incident-attribution", "incident-date"].forEach(function (id) { document.getElementById(id).value = "all"; });
      document.getElementById("incident-search").value = "";
      reset();
    });
    document.getElementById("incident-prev").addEventListener("click", function () {
      if (!state.stack.length) return;
      state.cursor = state.stack.pop();
      load();
    });
    document.getElementById("incident-next").addEventListener("click", function () {
      if (!state.next) return;
      state.stack.push(state.cursor);
      state.cursor = state.next;
      load();
    });
    load();
  }
  boot();
})();
