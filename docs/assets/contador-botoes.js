// Contadores dos botões da página do Cantinácio (docs/Movimento/Cantinácio.md).
// Os cliques nos botões com data-goatcounter-click="chave" são contados pelo
// próprio GoatCounter (overrides/main.html) como eventos; aqui só se lê o
// contador público de cada evento e se escreve em cada
// <span data-contador="chave"> quantas vezes esse botão já foi usado. Se o
// GoatCounter não responder (ou estiver bloqueado), mostra-se só um traço.
(function () {
  "use strict";

  var API = "https://wikinacios.goatcounter.com/counter/";

  function texto(n) {
    return "Usado " + n.toLocaleString("pt-PT") + (n === 1 ? " vez" : " vezes");
  }

  function mostrar(chave, valor) {
    document.querySelectorAll('[data-contador="' + chave + '"]').forEach(function (s) {
      s.textContent = valor == null ? "—" : texto(valor);
    });
  }

  function ler(chave) {
    fetch(API + encodeURIComponent(chave) + ".json")
      .then(function (r) {
        if (r.status === 404) return { count: "0" };  // ainda ninguém clicou
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      // O GoatCounter devolve o número como texto, por vezes com separadores.
      .then(function (d) { mostrar(chave, parseInt(String(d.count).replace(/\D/g, ""), 10) || 0); })
      .catch(function () { mostrar(chave, null); });
  }

  function iniciar() {
    var vistos = {};
    document.querySelectorAll("[data-contador]").forEach(function (s) {
      var chave = s.dataset.contador;
      if (vistos[chave]) return;
      vistos[chave] = true;
      ler(chave);
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
