// Índice das Pessoas: cada letra passa a ser uma lista que se abre e fecha,
// e uma caixa de procura no topo filtra os nomes de todas as letras. A lista
// de cada letra lê-se da página dessa letra (Pessoas/A/, Pessoas/B/, …), que
// continua a ser a fonte; sem JavaScript fica a lista de ligações de sempre.
(function () {
  "use strict";

  // Sem acentos e em minúsculas, para "Joao" encontrar "João".
  function normal(texto) {
    return texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }

  function carregar(letra) {
    if (!letra.pedido) {
      letra.pedido = fetch(letra.url)
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          return r.text();
        })
        .then(function (html) {
          var doc = new DOMParser().parseFromString(html, "text/html");
          var ligacoes = doc.querySelectorAll(".md-content__inner ul a");
          var vistos = {};
          letra.pessoas = [];
          ligacoes.forEach(function (a) {
            var url = new URL(a.getAttribute("href"), letra.url).href;
            if (vistos[url]) return;
            vistos[url] = true;
            var nome = a.textContent.trim();
            letra.pessoas.push({ nome: nome, url: url, chave: normal(nome) });
          });
          return letra.pessoas;
        })
        .catch(function (e) {
          letra.pedido = null;
          throw e;
        });
    }
    return letra.pedido;
  }

  function lista(pessoas) {
    var ul = document.createElement("ul");
    pessoas.forEach(function (p) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = p.url;
      a.textContent = p.nome;
      li.appendChild(a);
      ul.appendChild(li);
    });
    return ul;
  }

  function iniciar() {
    var caixa = document.querySelector(".pessoas-indice");
    if (!caixa || caixa.dataset.pronto) return;
    var ul = caixa.querySelector("ul");
    if (!ul) return;
    caixa.dataset.pronto = "1";

    var letras = [];
    var blocos = document.createElement("div");
    blocos.className = "pessoas-letras";

    ul.querySelectorAll(":scope > li").forEach(function (li) {
      var a = li.querySelector("a");
      if (!a) return;
      var letra = { url: a.href, pedido: null, pessoas: null };
      letras.push(letra);

      var det = document.createElement("details");
      det.className = "pessoas-letra";
      var sum = document.createElement("summary");
      sum.textContent = li.textContent.trim();
      det.appendChild(sum);
      var corpo = document.createElement("div");
      corpo.className = "pessoas-letra__corpo";
      corpo.textContent = "A carregar…";
      det.appendChild(corpo);

      det.addEventListener("toggle", function () {
        if (!det.open || corpo.dataset.cheio) return;
        carregar(letra).then(function (pessoas) {
          corpo.dataset.cheio = "1";
          corpo.textContent = "";
          corpo.appendChild(lista(pessoas));
        }, function () {
          corpo.textContent = "";
          var erro = document.createElement("a");
          erro.href = letra.url;
          erro.textContent = "Não foi possível carregar a lista; abrir a página da letra.";
          corpo.appendChild(erro);
        });
      });
      blocos.appendChild(det);
    });

    var procura = document.createElement("div");
    procura.className = "pessoas-procura";
    var campo = document.createElement("input");
    campo.type = "search";
    campo.placeholder = "Procurar um animador pelo nome…";
    campo.setAttribute("aria-label", "Procurar uma pessoa pelo nome");
    campo.autocomplete = "off";
    var resultados = document.createElement("div");
    resultados.className = "pessoas-procura__resultados";
    resultados.setAttribute("aria-live", "polite");
    procura.appendChild(campo);
    procura.appendChild(resultados);

    function filtrar() {
      var termo = normal(campo.value.trim());
      if (!termo) {
        resultados.textContent = "";
        blocos.hidden = false;
        return;
      }
      blocos.hidden = true;
      resultados.textContent = "A procurar…";
      var partes = termo.split(/\s+/);
      Promise.all(letras.map(function (l) {
        return carregar(l).catch(function () { return []; });
      })).then(function (porLetra) {
        if (normal(campo.value.trim()) !== termo) return; // já mudou
        var achados = [];
        porLetra.forEach(function (pessoas) {
          pessoas.forEach(function (p) {
            if (partes.every(function (t) { return p.chave.indexOf(t) !== -1; })) {
              achados.push(p);
            }
          });
        });
        resultados.textContent = "";
        var conta = document.createElement("p");
        conta.textContent = achados.length === 1
          ? "1 pessoa encontrada."
          : achados.length + " pessoas encontradas.";
        resultados.appendChild(conta);
        if (achados.length) resultados.appendChild(lista(achados));
      });
    }

    campo.addEventListener("input", filtrar);
    campo.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        var primeiro = resultados.querySelector("a");
        if (primeiro) window.location.href = primeiro.href;
      }
    });

    caixa.replaceChild(blocos, ul);
    caixa.insertBefore(procura, blocos);
  }

  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(iniciar);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
