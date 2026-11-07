(function () {
  "use strict";
  document.querySelectorAll("form[data-subscribe]").forEach(function (form) {
    var status = form.querySelector("[data-subscribe-status]");
    var lang = form.dataset.lang || "es";
    var messages = lang === "en"
      ? { ok: "Check your inbox and confirm the subscription.", bad: "Enter a valid email.", error: "Could not send the confirmation. Try again later." }
      : { ok: "Revisa tu correo y confirma la suscripción.", bad: "Escribe un email válido.", error: "No se pudo enviar la confirmación. Inténtalo más tarde." };
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (status) status.textContent = "";
      var email = form.querySelector('input[name="email"]');
      if (!email || !email.value || email.value.indexOf("@") === -1) {
        if (status) status.textContent = messages.bad;
        return;
      }
      var button = form.querySelector("button[type=submit]");
      if (button) button.disabled = true;
      fetch("/api/atlas/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.value,
          page: form.querySelector('input[name="page"]') ? form.querySelector('input[name="page"]').value : window.location.pathname,
          utm_source: new URLSearchParams(window.location.search).get("utm_source") || "",
          utm_medium: "web"
        })
      }).then(function (r) { return r.json().then(function (body) { return { ok: r.ok, body: body }; }); }).then(function (result) {
        if (status) status.textContent = result.ok ? messages.ok : (result.body.error === "email inválido" ? messages.bad : messages.error);
      }).catch(function () {
        if (status) status.textContent = messages.error;
      }).finally(function () {
        if (button) button.disabled = false;
      });
    });
  });
})();
