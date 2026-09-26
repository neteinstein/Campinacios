// Unlocks the restricted pages. Each one holds only AES-256-GCM ciphertext
// (written by scripts/restrito.py); the key is derived here from the
// password with PBKDF2-SHA256 and kept in sessionStorage, or localStorage if
// "Lembrar neste dispositivo" is ticked, so every other restricted page
// opens without asking again.
(function () {
  "use strict";

  var STORE = "wikinacios-restrito:";

  function bytes(b64) {
    return Uint8Array.from(atob(b64), function (c) { return c.charCodeAt(0); });
  }

  function b64(buf) {
    return btoa(String.fromCharCode.apply(null, new Uint8Array(buf)));
  }

  function storage(name) {
    try { return window[name]; } catch (e) { return null; }
  }

  function saved(salt) {
    var names = ["sessionStorage", "localStorage"];
    for (var i = 0; i < names.length; i++) {
      var s = storage(names[i]);
      try {
        var v = s && s.getItem(STORE + salt);
        if (v) return v;
      } catch (e) { /* storage blocked */ }
    }
    return null;
  }

  function save(salt, raw, remember) {
    var s = storage(remember ? "localStorage" : "sessionStorage");
    try { if (s) s.setItem(STORE + salt, raw); } catch (e) { /* ignore */ }
  }

  function forget() {
    ["sessionStorage", "localStorage"].forEach(function (name) {
      var s = storage(name);
      try {
        if (!s) return;
        for (var i = s.length - 1; i >= 0; i--) {
          var k = s.key(i);
          if (k && k.indexOf(STORE) === 0) s.removeItem(k);
        }
      } catch (e) { /* ignore */ }
    });
  }

  function deriveKey(el, password) {
    var enc = new TextEncoder();
    return crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2",
                                   false, ["deriveKey"])
      .then(function (base) {
        return crypto.subtle.deriveKey(
          { name: "PBKDF2", salt: bytes(el.dataset.salt),
            iterations: parseInt(el.dataset.iter, 10), hash: "SHA-256" },
          base, { name: "AES-GCM", length: 256 }, true, ["decrypt"]);
      });
  }

  function importKey(raw) {
    return crypto.subtle.importKey("raw", bytes(raw), "AES-GCM", true,
                                   ["decrypt"]);
  }

  function decrypt(el, key) {
    return crypto.subtle.decrypt(
      { name: "AES-GCM", iv: bytes(el.dataset.iv) }, key, bytes(el.dataset.ct))
      .then(function (plain) {
        return JSON.parse(new TextDecoder().decode(plain)).html;
      });
  }

  function show(el, html) {
    el.innerHTML = html;
    el.classList.add("aberto");
    var bar = document.createElement("p");
    bar.className = "wiki-restrito-barra";
    var link = document.createElement("a");
    link.href = "#";
    link.textContent = "Esquecer a palavra-passe neste navegador";
    link.addEventListener("click", function (e) {
      e.preventDefault();
      forget();
      window.location.reload();
    });
    bar.appendChild(document.createTextNode("🔓 Página restrita · "));
    bar.appendChild(link);
    el.insertBefore(bar, el.firstChild);
    if (window.location.hash) {
      var target = document.getElementById(
        decodeURIComponent(window.location.hash.slice(1)));
      if (target) target.scrollIntoView();
    }
  }

  function form(el) {
    var notice = el.querySelector("p");
    var f = document.createElement("form");
    f.className = "wiki-restrito-form";
    f.innerHTML =
      '<label>Palavra-passe <input type="password" autocomplete="current-password" required></label>' +
      '<label class="lembrar"><input type="checkbox"> Lembrar neste dispositivo</label>' +
      '<button type="submit" class="md-button md-button--primary">Abrir</button>' +
      '<p class="erro" role="alert" hidden></p>';
    var input = f.querySelector('input[type="password"]');
    var remember = f.querySelector('input[type="checkbox"]');
    var button = f.querySelector("button");
    var error = f.querySelector(".erro");
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      button.disabled = true;
      button.textContent = "A abrir…";
      error.hidden = true;
      var key;
      deriveKey(el, input.value)
        .then(function (k) { key = k; return decrypt(el, k); })
        .then(function (html) {
          return crypto.subtle.exportKey("raw", key).then(function (raw) {
            save(el.dataset.salt, b64(raw), remember.checked);
            show(el, html);
          });
        })
        .catch(function () {
          error.textContent = "Palavra-passe errada.";
          error.hidden = false;
          button.disabled = false;
          button.textContent = "Abrir";
          input.select();
        });
    });
    if (notice) notice.after(f); else el.appendChild(f);
    if (!window.location.hash) input.focus();
  }

  function unsupported(el) {
    var p = document.createElement("p");
    p.className = "erro";
    p.textContent = "Este navegador não consegue abrir páginas cifradas " +
                    "(é preciso um navegador recente e uma ligação https).";
    el.appendChild(p);
  }

  function init(el) {
    if (el.dataset.ready) return;
    el.dataset.ready = "1";
    if (!(window.crypto && crypto.subtle && window.TextDecoder)) {
      unsupported(el);
      return;
    }
    var raw = saved(el.dataset.salt);
    if (!raw) { form(el); return; }
    importKey(raw)
      .then(function (key) { return decrypt(el, key); })
      .then(function (html) { show(el, html); })
      .catch(function () { forget(); form(el); });
  }

  function run() {
    document.querySelectorAll(".wiki-restrito").forEach(init);
  }

  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(run);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
