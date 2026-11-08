(function () {
  "use strict";
  var D2R = Math.PI / 180;
  var projection = null;
  var events = [];
  var referenceDate = null;

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

  function statusLabel(status) {
    if (status === "CONFIRMADO") return "Confirmado";
    if (status === "PENDIENTE") return "Pendiente";
    return "Documentado";
  }

  function statusClass(status) {
    if (status === "CONFIRMADO") return "confirmed";
    if (status === "PENDIENTE") return "pending";
    return "documented";
  }

  function eventDate(item) {
    return item.event_date || item.published_at || "";
  }

  function timeValue(item) {
    var value = Date.parse(eventDate(item) + "T00:00:00Z");
    return Number.isNaN(value) ? 0 : value;
  }

  function marker(item) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "marker";
    button.dataset.id = item.id;
    button.dataset.status = item.verification_status;
    var pos = pct(naturalEarth1(item.lon, item.lat));
    button.style.left = pos.left + "%";
    button.style.top = pos.top + "%";
    button.setAttribute("aria-label", item.title + ". " + item.place + ". Estado: " + statusLabel(item.verification_status));
    button.title = item.title;
    button.addEventListener("click", function () {
      if (!document.getElementById("detail")) window.location.href = "mapa.html#" + encodeURIComponent(item.id);
      else select(item);
    });
    return button;
  }

  function renderMap(frame, list) {
    var holder = frame.querySelector(".map-markers");
    if (!holder) return;
    holder.replaceChildren();
    list.forEach(function (item) {
      if (item.lat === null || item.lon === null) return;
      holder.appendChild(marker(item));
    });
  }

  function makeText(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    node.textContent = text;
    return node;
  }

  function renderList(list) {
    var listNode = document.getElementById("event-list");
    if (!listNode) return;
    listNode.replaceChildren();
    if (!list.length) {
      listNode.appendChild(makeText("li", "muted", "No hay acontecimientos con estos filtros."));
      return;
    }
    list.forEach(function (item) {
      var li = document.createElement("li");
      var button = document.createElement("button");
      button.type = "button";
      button.className = "event-row";
      button.addEventListener("click", function () {
      if (!document.getElementById("detail")) window.location.href = "mapa.html#" + encodeURIComponent(item.id);
      else select(item);
    });
      button.appendChild(makeText("span", "event-date", eventDate(item)));
      button.appendChild(makeText("strong", "", item.title));
      button.appendChild(makeText("span", "event-meta", item.category_label + " · " + item.place + " · " + statusLabel(item.verification_status)));
      li.appendChild(button);
      listNode.appendChild(li);
    });
  }

  function addMeta(meta, label, value) {
    if (value === null || value === undefined || value === "") return;
    var box = document.createElement("div");
    box.appendChild(makeText("dt", "", label));
    var dd = document.createElement("dd");
    if (value instanceof Node) dd.appendChild(value); else dd.textContent = value;
    box.appendChild(dd);
    meta.appendChild(box);
  }

  function sourceList(item) {
    var list = document.createElement("ul");
    list.className = "source-list";
    (item.sources || []).forEach(function (source) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = source.url;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = source.title || source.url;
      li.appendChild(a);
      li.appendChild(document.createTextNode(" · " + (source.type || "fuente")));
      list.appendChild(li);
    });
    return list;
  }

  function select(item) {
    if (!item) return;
    var detail = document.getElementById("detail");
    if (!detail) return;
    detail.classList.remove("detail-empty");
    detail.replaceChildren();
    detail.appendChild(makeText("p", "data-badge", statusLabel(item.verification_status) + " · " + item.category_label));
    detail.appendChild(makeText("h3", "", item.title));
    detail.appendChild(makeText("p", "", item.description));
    var meta = document.createElement("dl");
    meta.className = "incident-meta";
    addMeta(meta, "Fecha del acontecimiento", eventDate(item));
    addMeta(meta, "Publicación", item.published_at || "—");
    addMeta(meta, "Lugar", item.place || "No documentado");
    addMeta(meta, "País", item.country || "—");
    addMeta(meta, "Infraestructura", item.infrastructure);
    addMeta(meta, "Consecuencias", item.consequences);
    addMeta(meta, "Precisión geográfica", item.geo_precision || "sin coordenada");
    addMeta(meta, "Atribución", item.attribution && item.attribution.note ? item.attribution.note : "No se atribuye autoría");
    addMeta(meta, "Fuentes", sourceList(item));
    detail.appendChild(meta);
    if (item.observations) detail.appendChild(makeText("p", "muted small", "Limitación: " + item.observations));
    var open = document.getElementById("detail-open");
    if (open) {
      open.href = "mapa.html#" + encodeURIComponent(item.id);
      open.setAttribute("aria-disabled", "false");
    }
    var report = document.getElementById("report-error");
    if (report) {
      var repo = document.body.dataset.repo || "";
      report.href = repo + "/issues/new?template=corregir-ficha.yml&ficha=" + encodeURIComponent(item.id);
    }
    if (window.location.hash !== "#" + item.id) history.replaceState(null, "", "#" + item.id);
  }

  function filtered() {
    var dateValue = (document.getElementById("filter-date") || {}).value || "168";
    var category = (document.getElementById("filter-category") || {}).value || "all";
    var country = (document.getElementById("filter-country") || {}).value || "all";
    var status = (document.getElementById("filter-status") || {}).value || "all";
    var limit = dateValue === "all" ? Infinity : Number(dateValue) * 3600000;
    var base = referenceDate ? referenceDate.getTime() : Date.now();
    return events.filter(function (item) {
      if (category !== "all" && item.category !== category) return false;
      if (country !== "all" && item.country !== country) return false;
      if (status !== "all" && item.verification_status !== status) return false;
      if (limit !== Infinity && (base - timeValue(item)) > limit) return false;
      return true;
    }).sort(function (a, b) { return timeValue(b) - timeValue(a); });
  }

  function update() {
    var frame = document.querySelector('[data-map="full"]');
    var list = filtered();
    if (frame) renderMap(frame, list);
    renderList(list);
    var count = document.getElementById("map-count");
    if (count) count.textContent = String(list.length);
  }

  function bindFilters() {
    ["filter-date", "filter-category", "filter-country", "filter-status"].forEach(function (id) {
      var node = document.getElementById(id);
      if (node) node.addEventListener("change", update);
    });
    var reset = document.getElementById("filter-reset");
    if (reset) reset.addEventListener("click", function () {
      document.getElementById("filter-date").value = "168";
      document.getElementById("filter-category").value = "all";
      document.getElementById("filter-country").value = "all";
      document.getElementById("filter-status").value = "all";
      update();
    });
    var copy = document.getElementById("copy-link");
    if (copy) copy.addEventListener("click", function () {
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(window.location.href).then(function () {
        copy.textContent = "Enlace copiado";
        setTimeout(function () { copy.textContent = "Copiar enlace"; }, 1600);
      });
    });
    window.addEventListener("hashchange", function () {
      var id = decodeURIComponent(window.location.hash.slice(1));
      var item = events.find(function (event) { return event.id === id; });
      if (item) select(item);
    });
  }

  function fillFilter(id, values) {
    var node = document.getElementById(id);
    if (!node) return;
    values.forEach(function (pair) {
      var option = document.createElement("option");
      option.value = pair[0];
      option.textContent = pair[1];
      node.appendChild(option);
    });
  }

  function updateStats() {
    var counts = {total: events.length, confirmed: 0, documented: 0, pending: 0, coordinates: 0, unlocated: 0, sources: 0};
    var urls = new Set();
    events.forEach(function (item) {
      if (item.verification_status === "CONFIRMADO") counts.confirmed += 1;
      else if (item.verification_status === "PENDIENTE") counts.pending += 1;
      else counts.documented += 1;
      if (item.lat !== null && item.lon !== null) counts.coordinates += 1; else counts.unlocated += 1;
      (item.sources || []).forEach(function (source) { if (source.url) urls.add(source.url); });
    });
    counts.sources = urls.size;
    document.querySelectorAll("[data-stat]").forEach(function (node) {
      var key = node.getAttribute("data-stat");
      if (Object.prototype.hasOwnProperty.call(counts, key)) node.textContent = String(counts[key]);
    });
  }

  function buildFilters() {
    var categories = {};
    var countries = {};
    events.forEach(function (item) {
      categories[item.category] = item.category_label;
      if (item.country) countries[item.country] = item.country;
    });
    fillFilter("filter-category", Object.keys(categories).sort().map(function (key) { return [key, categories[key]]; }));
    fillFilter("filter-country", Object.keys(countries).sort().map(function (key) { return [key, countries[key]]; }));
  }

  function renderPreview(frame) {
    var list = events.filter(function (item) { return item.lat !== null && item.lon !== null; }).slice(0, 10);
    renderMap(frame, list);
  }

  function renderDays() {
    var holder = document.getElementById("preview-days-bars");
    if (!holder) return;
    var end = new Date(referenceDate || Date.now());
    end.setUTCHours(0, 0, 0, 0);
    var counts = {};
    events.forEach(function (item) {
      var raw = eventDate(item);
      if (!raw) return;
      var key = raw.slice(0, 10);
      counts[key] = (counts[key] || 0) + 1;
    });
    var days = [];
    var max = 1;
    for (var i = 7; i >= 0; i -= 1) {
      var date = new Date(end.getTime());
      date.setUTCDate(end.getUTCDate() - i);
      var key = date.toISOString().slice(0, 10);
      var count = counts[key] || 0;
      if (count > max) max = count;
      days.push({date: date, count: count, key: key});
    }
    var dayFmt = new Intl.DateTimeFormat("es-ES", {day: "numeric", timeZone: "UTC"});
    var monthFmt = new Intl.DateTimeFormat("es-ES", {month: "short", timeZone: "UTC"});
    holder.replaceChildren();
    days.forEach(function (day) {
      var column = document.createElement("div");
      column.className = "preview-day";
      column.title = day.key + ": " + day.count + (day.count === 1 ? " evento" : " eventos");
      var count = makeText("span", "preview-day-count", String(day.count));
      var bar = document.createElement("span");
      bar.className = "preview-day-bar";
      bar.style.height = Math.max(2, Math.round((day.count / max) * 28)) + "px";
      if (!day.count) bar.classList.add("is-zero");
      var label = makeText("span", "preview-day-label", dayFmt.format(day.date));
      column.appendChild(count);
      column.appendChild(bar);
      column.appendChild(label);
      holder.appendChild(column);
    });
    holder.setAttribute("aria-label", "Eventos documentados por día: " + days.map(function (day) {
      return dayFmt.format(day.date) + ": " + day.count;
    }).join(", "));
    var range = document.getElementById("preview-days-range");
    if (range) {
      range.textContent = dayFmt.format(days[0].date) + "–" + dayFmt.format(days[7].date) + " " + monthFmt.format(days[7].date).replace(".", "");
    }
  }

  function boot() {
    var frames = document.querySelectorAll("[data-map]");
    if (!frames.length) return;
    Promise.all([
      fetch("assets/data/projection.json").then(function (response) { return response.json(); }),
      fetch("assets/data/events.json").then(function (response) { return response.json(); })
    ]).then(function (values) {
      projection = values[0];
      events = values[1].events || [];
      referenceDate = new Date(values[1].generated_at || Date.now());
      var capture = document.getElementById("last-capture");
      if (capture && values[1].generated_at) {
        capture.textContent = new Intl.DateTimeFormat("es-ES", {
          dateStyle: "medium", timeStyle: "short", timeZone: "Europe/Madrid"
        }).format(new Date(values[1].generated_at));
        capture.dateTime = values[1].generated_at;
      }
      updateStats();
      buildFilters();
      frames.forEach(function (frame) {
        if (frame.dataset.map === "preview") renderPreview(frame); else renderMap(frame, events);
      });
      if (document.querySelector('[data-map="full"]')) {
        bindFilters();
        update();
      }
      var previewLatest = document.getElementById("preview-latest");
      if (previewLatest) {
        previewLatest.replaceChildren();
        events.slice().sort(function (a, b) { return timeValue(b) - timeValue(a); }).slice(0, 5).forEach(function (item) {
          var li = document.createElement("li");
          var a = document.createElement("a");
          a.href = "mapa.html#" + encodeURIComponent(item.id);
          a.textContent = item.title;
          li.appendChild(a);
          li.appendChild(makeText("span", "meta", (item.event_date || "—") + " · " + (item.place || "sin ubicación") + " · " + statusLabel(item.verification_status)));
          previewLatest.appendChild(li);
        });
      }
      renderDays();
      var coverage = document.getElementById("preview-coverage");
      if (coverage) {
        var located = events.filter(function (item) { return item.lat !== null && item.lon !== null; }).length;
        coverage.textContent = located + " de " + events.length + " registros tienen ubicación documentada; los demás quedan en la lista, no en el mapa.";
      }
      var latest = document.getElementById("latest-events");
      if (latest) {
        var recent = events.slice().sort(function (a, b) { return timeValue(b) - timeValue(a); }).slice(0, 5);
        recent.forEach(function (item) {
          var li = document.createElement("li");
          var a = document.createElement("a");
          a.href = "mapa.html#" + encodeURIComponent(item.id);
          a.textContent = item.title + " · " + item.place;
          li.appendChild(a);
          latest.appendChild(li);
        });
      }
      var id = decodeURIComponent(window.location.hash.slice(1));
      var selected = events.find(function (item) { return item.id === id; });
      if (selected) select(selected);
    }).catch(function () {
      var frame = document.querySelector("[data-map]");
      if (frame) frame.appendChild(makeText("p", "muted small", "No se pudo cargar el mapa. Revisa los datos locales."));
    });
  }

  boot();
  window.ZonaGrisProjection = naturalEarth1;
})();
