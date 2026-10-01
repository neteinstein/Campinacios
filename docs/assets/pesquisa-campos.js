// Caixa de pesquisa da tabela de acampamentos (docs/Acampamentos/index.md).
// Filtra os campos por nome, ano, escalão, tema ou local e mostra no título
// quantos campos se vêem. Cada palavra escrita tem de aparecer no campo ou na
// linha do seu ano (pesquisa sem acentos nem maiúsculas).
(function () {
  "use strict";

  function norm(s) {
    return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "")
      .toLowerCase().replace(/\s+/g, " ").trim();
  }

  function init(box) {
    if (box.dataset.ready) return;
    box.dataset.ready = "1";
    var content = box.closest(".md-content") || document;
    var table = content.querySelector("table");
    var title = content.querySelector("h1");
    if (!table || !title) return;

    // O texto do título, sem o símbolo de ligação que o tema acrescenta.
    var titleText = Array.prototype.find.call(title.childNodes, function (n) {
      return n.nodeType === Node.TEXT_NODE && n.nodeValue.trim();
    });
    var baseTitle = titleText ? titleText.nodeValue.trim() : "Acampamentos";

    var rows = Array.prototype.map.call(table.tBodies[0].rows, function (tr) {
      var c = tr.cells;
      var rowText = norm([c[0], c[2], c[3]].map(function (td) {
        return td ? td.textContent : "";
      }).join(" "));
      var groups = Array.prototype.map.call(
        c[1].querySelectorAll(":scope > ul > li"), function (g) {
          var label = g.querySelector(":scope > strong");
          var labelText = label ? label.textContent : "";
          // Na tabela o escalão aparece como «Formação»; a categoria chama-se
          // «Formação de Animadores».
          if (norm(labelText) === "formacao") labelText += " Formação de Animadores";
          var camps = Array.prototype.map.call(
            g.querySelectorAll(":scope > ul > li"), function (li) {
              return { el: li, text: norm(li.textContent + " " + labelText) };
            });
          return { el: g, camps: camps };
        });
      return { el: tr, text: rowText, groups: groups };
    });
    var total = rows.reduce(function (n, r) {
      return n + r.groups.reduce(function (m, g) { return m + g.camps.length; }, 0);
    }, 0);

    var input = document.createElement("input");
    input.type = "search";
    input.placeholder = "Procurar por nome, ano, escalão, tema ou local…";
    input.setAttribute("aria-label", "Procurar acampamentos");
    box.appendChild(input);

    function setTitle(n) {
      var text = baseTitle + " (" + n + ")";
      if (titleText) titleText.nodeValue = text;
      else title.insertBefore(document.createTextNode(text), title.firstChild);
    }

    function filter() {
      var terms = norm(input.value).split(" ").filter(Boolean);
      var shown = 0;
      rows.forEach(function (r) {
        var rowShown = 0;
        r.groups.forEach(function (g) {
          var groupShown = 0;
          g.camps.forEach(function (c) {
            var hay = c.text + " " + r.text;
            var ok = terms.every(function (t) { return hay.indexOf(t) !== -1; });
            c.el.hidden = !ok;
            if (ok) groupShown++;
          });
          g.el.hidden = !groupShown;
          rowShown += groupShown;
        });
        r.el.hidden = !rowShown;
        shown += rowShown;
      });
      setTitle(terms.length ? shown : total);
      var url = new URL(window.location.href);
      if (terms.length) url.searchParams.set("q", input.value);
      else url.searchParams.delete("q");
      window.history.replaceState(window.history.state, "", url);
    }

    input.value = new URL(window.location.href).searchParams.get("q") || "";
    input.addEventListener("input", filter);
    filter();
  }

  function start() {
    document.querySelectorAll(".wk-pesquisa-campos").forEach(init);
  }
  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(start);  // navegação instantânea do Material
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
