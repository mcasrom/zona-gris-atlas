(function () {
  "use strict";
  var D2R = Math.PI / 180;
  var projection = null;
  var incidents = [];

  function naturalEarth1(lon, lat) {
    var lambda = lon * D2R;
    var phi = lat * D2R;
    var phi2 = phi * phi;
    var phi4 = phi2 * phi2;
    var x = lambda * (0.8707 - 0.131979 * phi2 + phi4 * (-0.013791 + phi4 * (0.003971 * phi2 - 0.001529 * phi4)));
    var y = phi * (1.007226 + phi2 * (0.015085 + phi4 * (-0.044475 + 0.028874 * phi2 - 0.005916 * phi4)));
    return [projection.scale * x + projection.translate[0], projection.translate[1] - projection.scale * y];
  }

  function pct(xy) {
    return { left: (xy[0] / projection.width) * 100, top: (xy[1] / projection.height) * 100 };
  }

  function attribution(incident) {
    var first = (incident.attributions || [])[0];
    return first ? first.status : "none";
  }

  function markerSize(severity) {
    if (severity === "alta") return 14;
    if (severity === "media") return 10;
    return 7;
  }

  function marker(incident, full) {
    var xy = naturalEarth1(incident.lon, incident.lat);
    var pos = pct(xy);
    var button = document.createElement("button");
    button.type = "button";
    button.className = "marker";
    button.dataset.id = incident.id;
    button.dataset.attribution = attribution(incident);
    button.style.left = pos.left + "%";
    button.style.top = pos.top + "%";
    button.style.setProperty("--size", markerSize(incident.severity) + "px");
    button.setAttribute(
      "aria-label",
      incident.title + ". Dominio " + incident.domain + ". Atribución: " + attribution(incident)
    );
    button.title = incident.title;
    button.addEventListener("click", function () {
      if (full) {
        select(incident);
      } else {
        window.location.href = "mapa.html#" + encodeURIComponent(incident.id);
      }
    });
    return button;
  }

  function render(frame, list, full) {
    var holder = frame.querySelector(".map-markers");
    if (!holder) return;
    holder.replaceChildren();
    list.forEach(function (incident) {
      if (incident.lat === null || incident.lon === null) return;
      holder.appendChild(marker(incident, full));
    });
  }

  function selectedFromHash() {
    var id = decodeURIComponent(window.location.hash.slice(1));
    return incidents.find(function (item) { return item.id === id; });
  }

  function select(incident) {
    if (!incident) return;
    var detail = document.getElementById("detail");
    if (detail) {
      detail.classList.remove("detail-empty");
      detail.innerHTML = "";
      var badge = document.createElement("p");
      badge.className = "data-badge";
      badge.textContent = incident.demo ? "Ejemplo ilustrativo" : "Incidente publicado";
      var title = document.createElement("h3");
      title.textContent = incident.title;
      var summary = document.createElement("p");
      summary.textContent = incident.summary;
      var meta = document.createElement("dl");
      meta.className = "incident-meta";
      [
        ["Dominio", incident.domain],
        ["Lugar", incident.place || "—"],
        ["Gravedad", incident.severity],
        ["Atribución", attribution(incident)],
        ["Atribuido por", (incident.attributions[0] || {}).attributed_by || "—"],
        ["Incidente real", incident.reality],
        ["Fecha", incident.event_date],
        ["Revisión humana", incident.reviewed_by_human ? "sí" : "pendiente"]
      ].forEach(function (pair) {
        var box = document.createElement("div");
        var dt = document.createElement("dt");
        dt.textContent = pair[0];
        var dd = document.createElement("dd");
        dd.textContent = pair[1];
        box.appendChild(dt);
        box.appendChild(dd);
        meta.appendChild(box);
      });
      detail.appendChild(badge);
      detail.appendChild(title);
      detail.appendChild(summary);
      detail.appendChild(meta);
    }
    var open = document.getElementById("detail-open");
    if (open) {
      open.href = "mapa.html#" + encodeURIComponent(incident.id);
      open.setAttribute("aria-disabled", "false");
    }
    var report = document.getElementById("report-error");
    if (report) {
      var repo = document.body.dataset.repo || "";
      report.href = repo + "/issues/new?template=corregir-ficha.yml&ficha=" + encodeURIComponent(incident.id);
    }
    if (window.location.hash !== "#" + incident.id) {
      history.replaceState(null, "", "#" + incident.id);
    }
  }

  function filterList() {
    var domains = new Set(Array.from(document.querySelectorAll('input[name="domain"]:checked')).map(function (x) { return x.value; }));
    var severity = new Set(Array.from(document.querySelectorAll('input[name="severity"]:checked')).map(function (x) { return x.value; }));
    var attributionValue = (document.querySelector('input[name="attribution"]:checked') || {}).value || "all";
    var period = document.querySelector("[data-period][aria-pressed='true']");
    var days = period ? Number(period.dataset.period) : 0;
    var maxDate = Math.max.apply(null, incidents.map(function (incident) { return new Date(incident.event_date).getTime(); }));
    return incidents.filter(function (incident) {
      if (!domains.has(incident.domain) || !severity.has(incident.severity)) return false;
      if (attributionValue !== "all" && attribution(incident) !== attributionValue) return false;
      if (days && (maxDate - new Date(incident.event_date).getTime()) / 86400000 > days) return false;
      return true;
    });
  }

  function update() {
    var frame = document.querySelector('[data-map="full"]');
    if (!frame) return;
    var list = filterList();
    render(frame, list, true);
    var count = document.getElementById("map-count");
    if (count) count.textContent = String(list.length);
    var selected = selectedFromHash();
    if (selected) select(selected);
  }

  function bindFilters() {
    document.querySelectorAll('.filters input').forEach(function (input) {
      input.addEventListener("change", update);
    });
    document.querySelectorAll("[data-period]").forEach(function (button) {
      button.addEventListener("click", function () {
        document.querySelectorAll("[data-period]").forEach(function (other) {
          other.setAttribute("aria-pressed", other === button ? "true" : "false");
        });
        update();
      });
    });
    var copy = document.getElementById("copy-link");
    if (copy) {
      copy.addEventListener("click", function () {
        var url = window.location.href;
        if (navigator.clipboard) {
          navigator.clipboard.writeText(url).then(function () {
            copy.textContent = "Enlace copiado";
            setTimeout(function () { copy.textContent = "Copiar enlace"; }, 1600);
          });
        }
      });
    }
    window.addEventListener("hashchange", function () {
      var selected = selectedFromHash();
      if (selected) select(selected);
    });
  }

  function boot() {
    var frames = document.querySelectorAll("[data-map]");
    if (!frames.length) return;
    Promise.all([
      fetch("assets/data/projection.json").then(function (response) { return response.json(); }),
      fetch("assets/data/incidents.json").then(function (response) { return response.json(); })
    ]).then(function (values) {
      projection = values[0];
      incidents = values[1].incidents || [];
      frames.forEach(function (frame) {
        render(frame, frame.dataset.map === "preview" ? incidents.slice(0, 10) : incidents, frame.dataset.map === "full");
      });
      bindFilters();
      update();
    }).catch(function () {
      var frame = document.querySelector('[data-map="full"]');
      if (frame) {
        var fallback = document.createElement("p");
        fallback.className = "muted small";
        fallback.textContent = "No se pudo cargar el mapa. Revisa los datos locales.";
        frame.appendChild(fallback);
      }
    });
  }

  boot();
  window.ZonaGrisProjection = naturalEarth1;
})();
