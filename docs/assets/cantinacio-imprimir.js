// Botão «Cantinácio Virtual» da página do Cantinácio (docs/Movimento/Cantinácio.md).
// Junta as letras e os acordes de todas as secções do Cantinácio numa janela
// nova, paginada em A4 a duas colunas à maneira do Cantinácio de 2019
// (3.ª edição) — capa, ficha técnica, índice com números de página, capas das
// secções —, e abre a caixa de impressão do navegador (onde também se pode
// guardar em PDF). As músicas são lidas das próprias páginas do site, por
// isso a versão impressa está sempre actualizada.
(function () {
  "use strict";

  var SITE = "http://campinacios.pedrovicente.pt";

  // Pela ordem do Cantinácio de 2019, excepto as Portuguesas e as Estrangeiras, que vão depois dos Cânticos, e os Aplausos, que ficam no fim; o título é o da secção nessa edição.
  var SECCOES = [
    { pagina: "Campinácios", titulo: "Hits de Campo", capa: "p089.jpg" },
    { pagina: "Camtil", titulo: "Camtil" },
    { pagina: "Gambozinos", titulo: "Gambozinos" },
    { pagina: "Cânticos", titulo: "Cânticos", capa: "p127.jpg" },
    { pagina: "Portuguesas", titulo: "Radar Tuga", capa: "p011.jpg" },
    { pagina: "Estrangeiras", titulo: "Da França, Espanha, tudo", capa: "p041.jpg" },
    { titulo: "Música Viva", viva: true },  // QR Codes dos vídeos das músicas; vai antes do manual
    { pagina: "Manual de Instruções", titulo: "Manual de Instruções", capa: "p175.jpg", texto: true },
    { pagina: "Escalas", titulo: "Escalas", texto: true },
    { pagina: "Aplausos", titulo: "Não há palmas nos Campinácios", capa: "p111.jpg", fluir: true }  // fluir: as músicas seguem-se sem começar página nova
  ];

  // Como no Cantinácio de 2019: Arial, letras e acordes a 11 pt, títulos a 18 pt.
  var FAMILIA = "Arial, Helvetica, 'Liberation Sans', sans-serif";
  var TAM_LETRA = 11;  // pt, o tamanho normal das letras e acordes
  var TAM_MINIMO = 7;  // pt, o mais pequeno a que se encolhe uma música larga

  // Ilustrações (largura × altura em px): as 14 primeiras são do Pica, tiradas
  // do Cantinácio de 2019; as seguintes foram desenhadas para o Wikinácios ao
  // mesmo estilo, com temas de campo (lanterna, Petromax, Cerelac, latrina,
  // roda, guitarra, djambé, sol, tenda, pão, marmelada, manteiga, leite,
  // Coca-Cola, fogueira, caminhada, comboio, árvores, cruz, abraço, ajoelhar)
  // e da Camtilena (mosquito, cegonha, arco-íris, pêra, galinha, sopa, aranha,
  // semente, gota), e ainda triciclo, trotinete, bicicleta, lambreta, tractor,
  // calhambeque, garrafa, boi, mira («tens mira?»), Super Boi, cantil, rio,
  // banho de rio, banana, melancia, casaco camuflado da tropa, bandeira num
  // mastro, lenço de campo, lama, jipe, chinelos, massa com atum, nadar,
  // saco-cama, estendal, padre, criança, despedida com lágrimas, luar e
  // estrelas no céu.
  var ILUSTRACOES = [
    [1, 700, 679], [2, 230, 700], [3, 443, 700], [4, 405, 700], [5, 700, 665],
    [6, 700, 464], [7, 630, 700], [8, 700, 603], [9, 649, 700], [10, 419, 700],
    [11, 700, 521], [12, 635, 700], [13, 594, 700], [14, 437, 700],
    [15, 700, 482], [16, 433, 700], [17, 644, 700], [18, 700, 635], [19, 690, 700],
    [20, 573, 700], [21, 601, 700], [22, 700, 699], [23, 700, 559], [24, 700, 528],
    [25, 700, 685], [26, 700, 593], [27, 553, 700], [28, 441, 700], [29, 651, 700],
    [30, 700, 680], [31, 700, 636], [32, 700, 632], [33, 656, 700], [34, 480, 700],
    [35, 476, 700], [36, 700, 668], [37, 700, 639], [38, 700, 433], [39, 582, 700],
    [40, 700, 601], [41, 650, 700], [42, 700, 693], [43, 683, 700], [44, 614, 700],
    [45, 700, 487], [46, 700, 585], [47, 700, 476], [48, 700, 513], [49, 700, 663],
    [50, 700, 430], [51, 541, 700], [52, 700, 571], [53, 612, 700], [54, 700, 667],
    [55, 358, 700], [56, 655, 700], [57, 700, 523], [58, 700, 667], [59, 700, 615],
    [60, 700, 614], [61, 658, 700], [62, 700, 630], [63, 674, 700], [64, 700, 412],
    [65, 587, 700], [66, 700, 695], [67, 700, 475], [68, 700, 592], [69, 697, 700],
    [70, 597, 700], [71, 573, 700], [72, 700, 647], [73, 700, 682], [74, 700, 676]
  ].map(function (i) {
    return { ficheiro: "ilustracao-" + (i[0] < 10 ? "0" : "") + i[0] + ".jpg", altura: i[2] / i[1] };
  });
  var PX_POR_MM = 96 / 25.4;

  var NOTA = "(?:Dó|Do|Ré|Re|Mi|Fá|Fa|Sol|Lá|La|Si|[A-G])(?:#|b|♯|♭)?";
  var ACORDE = new RegExp("^\\(?" + NOTA +
    "(?:m|M|maj|min|dim|aug|sus|add|º|°|\\+)?\\d*(?:sus\\d*|add\\d*|maj\\d*|M\\d*|\\+|º|°)*\\*?" +
    "(?:/" + NOTA + ")?\\)?[,.]?$");
  var NEUTRO = /^(\|+|-|–|—|\/|x\d+|\(x\d+\)|\d+x|\(\d+x\)|\.\.\.|…|%|\(|\))$/i;

  function linhaDeAcordes(linha) {
    var palavras = linha.trim().split(/\s+/);
    var acordes = 0;
    for (var i = 0; i < palavras.length; i++) {
      if (!palavras[i] || NEUTRO.test(palavras[i])) continue;
      if (!ACORDE.test(palavras[i])) return false;
      acordes++;
    }
    return acordes > 0;
  }

  // No site os títulos das músicas estão em maiúsculas; no Cantinácio de 2019
  // só a primeira letra é maiúscula («Amar alguém», «Árvore da montanha»).
  // Ficam em maiúsculas as siglas (palavras sem vogais, como BDS ou CSJB) e as
  // poucas que se sabem de cor.
  var SIGLAS = /^(AEIOU|ABC|DVD|OK|ONU|TV|UE|EUA|USA|JMJ|SJ|CC|CAIC|CSJB)$/;
  function titulo(t) {
    if (t !== t.toUpperCase()) return t;  // já tem minúsculas: foi escrito à mão
    var primeira = true;
    return t.replace(/[A-Za-zÀ-ÿ0-9]+(?:['’][A-Za-zÀ-ÿ]+)?/g, function (p) {
      var f = p.toLowerCase();
      if (SIGLAS.test(p) || (!/[AEIOUÀ-ÿ0-9]/.test(p) && p.length > 1)) f = p;
      else if (/^i(['’](m|ll|ve|d))?$/.test(f)) f = "I" + f.slice(1);
      else if (primeira) f = f.charAt(0).toUpperCase() + f.slice(1);
      primeira = false;
      return f;
    });
  }

  function hoje() {
    var d = new Date();
    function dois(n) { return (n < 10 ? "0" : "") + n; }
    return dois(d.getDate()) + "/" + dois(d.getMonth() + 1) + "/" + d.getFullYear();
  }

  function espera() {
    return new Promise(function (ok) { setTimeout(ok, 0); });
  }

  function comPrazo(promessa, ms) {
    return Promise.race([promessa, new Promise(function (ok) { setTimeout(ok, ms); })]);
  }

  // --- Leitura das páginas do site -----------------------------------------

  function texto(el) {
    var c = el.cloneNode(true);
    c.querySelectorAll(".headerlink").forEach(function (a) { a.remove(); });
    return c.textContent.trim();
  }

  // Tira as ligações (fica o texto; nas que saem do site, como os vídeos no
  // YouTube, fica também o endereço entre parênteses) e põe os endereços das
  // imagens absolutos.
  function limpar(el, url) {
    el.querySelectorAll(".headerlink").forEach(function (a) { a.remove(); });
    el.querySelectorAll("img").forEach(function (img) {
      img.setAttribute("src", new URL(img.getAttribute("src"), url).href);
      img.removeAttribute("width");
      img.removeAttribute("height");
    });
    el.querySelectorAll("a").forEach(function (a) {
      var href = a.getAttribute("href") || "";
      if (/^https?:/.test(href)) a.appendChild(a.ownerDocument.createTextNode(" (" + href + ")"));
      while (a.firstChild) a.parentNode.insertBefore(a.firstChild, a);
      a.remove();
    });
    return el;
  }

  // O endereço do vídeo de uma música: a primeira ligação para fora do site
  // cujo texto fala em «vídeo» (por exemplo «Há um [vídeo do hino](…)»).
  function videoDe(el) {
    var ligacoes = el.tagName === "A" ? [el] : Array.prototype.slice.call(el.querySelectorAll("a"));
    for (var i = 0; i < ligacoes.length; i++) {
      var href = ligacoes[i].getAttribute("href") || "";
      if (/^https?:/.test(href) && /v[ií]deo/i.test(ligacoes[i].textContent)) return href;
    }
    return "";
  }

  function ler(seccao, base) {
    if (seccao.viva) return Promise.resolve(seccao);
    var url = new URL("Cantin%C3%A1cio/" + encodeURIComponent(seccao.pagina) + ".html", base).href;
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(seccao.pagina + ": " + r.status);
      return r.text();
    }).then(function (html) {
      var doc = new DOMParser().parseFromString(html, "text/html");
      var artigo = doc.querySelector("article.md-content__inner") || doc.body;
      var filhos = Array.prototype.slice.call(artigo.children);
      seccao.url = url;

      if (seccao.texto) {
        // Tudo a partir do primeiro subtítulo: fica de fora a capa da secção
        // e o «Voltar ao Cantinácio».
        var inicio = filhos.findIndex(function (el) { return el.tagName === "H2"; });
        seccao.elementos = [];
        for (var i = Math.max(inicio, 0); i < filhos.length; i++) {
          if (filhos[i].tagName === "HR") break;
          seccao.elementos.push(limpar(filhos[i], url));
        }
        return seccao;
      }

      var musicas = [];
      var actual = null;
      var dentro = false;
      filhos.forEach(function (el) {
        if (el.tagName === "H2") {
          var t = texto(el);
          dentro = /^Músicas$|^Aplausos$/.test(t);
          actual = null;
          return;
        }
        if (!dentro || el.tagName === "HR") { if (el.tagName === "HR") dentro = false; return; }
        if (el.tagName === "H3") {
          actual = { titulo: titulo(texto(el)), autor: "", partes: [], video: "" };
          musicas.push(actual);
          return;
        }
        if (!actual) return;
        if (!actual.video) actual.video = videoDe(el);
        // «Há um vídeo … no YouTube» (ou no Google Drive…) não se imprime: o vídeo fica na «Música Viva», com o QR Code.
        if (el.tagName === "P" && videoDe(el)) return;
        var soItalico = el.tagName === "P" && el.children.length === 1 &&
          el.children[0].tagName === "EM" && el.textContent.trim() === el.children[0].textContent.trim();
        if (soItalico && !actual.partes.length && !actual.autor) {
          actual.autor = el.textContent.trim();
        } else if (el.tagName === "PRE") {
          var linhas = el.textContent.replace(/\s+$/, "").split("\n");
          actual.partes.push({ linhas: linhas });
        } else {
          actual.partes.push({ el: limpar(el, url) });
        }
      });
      seccao.musicas = musicas;
      return seccao;
    });
  }

  // --- Paginação -----------------------------------------------------------

  function Livro(doc) {
    this.doc = doc;
    this.raiz = doc.getElementById("paginas");
    this.colunas = [];
    this.coluna = 0;
    this.molde = null;
  }

  Livro.prototype.el = function (tag, classe, conteudo) {
    var e = this.doc.createElement(tag);
    if (classe) e.className = classe;
    if (conteudo != null) e.textContent = conteudo;
    return e;
  };

  // Uma página A4; «colunas» é 0 (página livre), 1 ou 2.
  Livro.prototype.pagina = function (classe, colunas, cabecalho, antesDe) {
    var p = this.el("section", "pagina " + (classe || ""));
    if (cabecalho) p.appendChild(this.el("h1", "cabecalho", cabecalho));
    var cols = [];
    if (colunas) {
      var caixa = this.el("div", "colunas");
      for (var i = 0; i < colunas; i++) cols.push(caixa.appendChild(this.el("div", "coluna")));
      p.appendChild(caixa);
    }
    this.raiz.insertBefore(p, antesDe || null);
    this.colunas = cols;
    this.coluna = 0;
    this.molde = { classe: classe, colunas: colunas, antesDe: antesDe };
    return p;
  };

  Livro.prototype.proximaColuna = function () {
    if (this.coluna + 1 < this.colunas.length) this.coluna++;
    else this.pagina(this.molde.classe, this.molde.colunas, null, this.molde.antesDe);
    return this.colunas[this.coluna];
  };

  function fundo(el) { return el.getBoundingClientRect().bottom; }

  // Põe um bloco na coluna actual. Se não couber, passa para a coluna seguinte
  // ou — se se puder partir — corta-o entre linhas e continua na seguinte.
  // Os elementos com data-junto (título, autor, linha de acordes) nunca ficam
  // separados do que vem a seguir.
  Livro.prototype.colocar = function (bloco, partir) {
    var col = this.colunas[this.coluna];
    col.appendChild(bloco);
    for (;;) {
      var limite = fundo(col) + 0.5;
      if (fundo(bloco) <= limite) return;
      var primeiro = bloco === col.firstChild;
      if (!partir) {
        if (primeiro) return;  // maior do que uma coluna inteira: fica assim
        col = this.proximaColuna();
        col.appendChild(bloco);
        continue;
      }
      var atomos = Array.prototype.slice.call(bloco.children);
      var cabem = 0;
      while (cabem < atomos.length && fundo(atomos[cabem]) <= limite) cabem++;
      var k = cabem;
      while (k > 0 && atomos[k - 1].hasAttribute("data-junto")) k--;
      var cabecalhos = atomos.filter(function (a, i) {
        return i < k && (a.classList.contains("titulo") || a.classList.contains("autor"));
      }).length;
      if (cabecalhos && k - cabecalhos < 3) k = 0;  // título sozinho no fundo
      if (k === 0) {
        if (!primeiro) {
          col = this.proximaColuna();
          col.appendChild(bloco);
          continue;
        }
        k = Math.max(cabem, 1);
        if (k >= atomos.length) return;
      }
      var resto = bloco.cloneNode(false);
      resto.classList.add("continua");
      atomos.slice(k).forEach(function (a) { resto.appendChild(a); });
      while (resto.firstChild && resto.firstChild.classList.contains("vazia")) resto.firstChild.remove();
      if (!resto.firstChild) return;
      col = this.proximaColuna();
      col.appendChild(resto);
      bloco = resto;
    }
  };

  // Põe uma música na página actual se ela couber toda nas colunas que sobram
  // (pode passar da primeira para a segunda coluna, mas não para outra
  // página); se não couber, desfaz e começa uma página nova. Devolve o
  // primeiro bloco da música.
  Livro.prototype.colocarNaPagina = function (criar) {
    var pagina = this.colunas[0].closest(".pagina");
    var coluna = this.coluna;
    var colunas = this.colunas;
    var molde = this.molde;
    var contagens = colunas.map(function (c) { return c.childNodes.length; });
    var b = criar();
    this.colocar(b, true);
    var vazia = contagens.every(function (n) { return n === 0; });
    if (this.colunas[0].closest(".pagina") === pagina || vazia) return b;

    // Passou para outra página: desfaz tudo o que a música acrescentou.
    var seguinte;
    while ((seguinte = pagina.nextElementSibling)) {
      if (seguinte.classList.contains("pagina")) seguinte.remove();
      else break;
    }
    colunas.forEach(function (c, i) {
      while (c.childNodes.length > contagens[i]) c.lastChild.remove();
    });
    this.colunas = colunas;
    this.coluna = coluna;
    this.molde = molde;
    this.pagina(molde.classe, molde.colunas, null, molde.antesDe);
    b = criar();
    this.colocar(b, true);
    return b;
  };

  // Largura (em «em») de um texto em Arial, medida num <canvas>; serve para
  // pôr cada acorde por cima da letra certa, como no Cantinácio de 2019.
  Livro.prototype.largura = function (texto, italico) {
    if (!this.tela) this.tela = this.doc.createElement("canvas").getContext("2d");
    this.tela.font = (italico ? "italic " : "") + "100px " + FAMILIA;
    return this.tela.measureText(texto).width / 100;
  };

  // Uma música: as linhas de acordes vêm por cima da letra, na posição do
  // carácter correspondente, e o tamanho da letra é sempre o mesmo (TAM_LETRA),
  // só encolhendo se uma linha com acordes não couber na coluna.
  Livro.prototype.blocoMusica = function (m, numero, largura) {
    var livro = this;
    var b = this.el("article", "musica");
    var t = b.appendChild(this.el("h3", "titulo", numero + ". " + m.titulo));
    t.setAttribute("data-junto", "");
    if (m.autor) b.appendChild(this.el("p", "autor", m.autor)).setAttribute("data-junto", "");

    // 1.º passo: as linhas de cada bloco, sem o recuo comum, e o tamanho.
    var emPorPt = 96 / 72;
    var maisLarga = 0;  // em «em», entre as linhas que não podem partir-se
    var itens = [];
    m.partes.forEach(function (p) {
      if (!p.linhas) { itens.push({ el: p.el }); return; }
      var recuo = Infinity;
      p.linhas.forEach(function (l) {
        if (l.trim()) recuo = Math.min(recuo, l.match(/^ */)[0].length);
      });
      var linhas = p.linhas.map(function (l) { return l.replace(/\s+$/, "").slice(isFinite(recuo) ? recuo : 0); });
      for (var i = 0; i < linhas.length; i++) {
        var l = linhas[i];
        if (!l) { itens.push({ vazia: true }); continue; }
        if (linhaDeAcordes(l)) {
          var letra = linhas[i + 1];
          if (letra && !linhaDeAcordes(letra)) {
            itens.push({ acordes: l, letra: letra });
            maisLarga = Math.max(maisLarga, livro.largura(letra), livro.largura(l.trim(), true) * 0.8);
            i++;
          } else {
            itens.push({ acordes: l, letra: "" });
            maisLarga = Math.max(maisLarga, livro.largura(l.trim().split(/\s+/).join("   "), true));
          }
        } else {
          itens.push({ solta: l });
        }
      }
    });
    var tam = TAM_LETRA;
    if (maisLarga * tam * emPorPt > largura) tam = Math.max(largura / (maisLarga * emPorPt), TAM_MINIMO);
    b.style.setProperty("--tam", tam.toFixed(2) + "pt");
    var larguraEm = largura / (tam * emPorPt);
    var espaco = livro.largura(" ");

    // 2.º passo: os elementos.
    itens.forEach(function (it) {
      if (it.el) {
        var e = livro.doc.importNode(it.el, true);
        e.classList.add("texto");
        b.appendChild(e);
      } else if (it.vazia) {
        b.appendChild(livro.el("div", "linha vazia"));
      } else if (it.solta != null) {
        b.appendChild(livro.el("div", "linha solta", it.solta));
      } else if (!it.letra) {
        // Só acordes (introdução, ponte…): ficam lado a lado.
        b.appendChild(livro.el("div", "linha acorde", it.acordes.trim().split(/\s+/).join(" ")));
      } else {
        var par = b.appendChild(livro.el("div", "par"));
        var linhaAc = par.appendChild(livro.el("div", "acordes"));
        // Acordes escritos para outro tipo de letra podem ser bem mais
        // compridos do que a letra: aproximam-se na mesma proporção.
        var fator = it.acordes.length > it.letra.length * 1.2 ? it.letra.length / it.acordes.length : 1;
        var fim = 0;
        var re = /\S+/g, m2;
        while ((m2 = re.exec(it.acordes))) {
          var idx = m2.index * fator;
          var k = Math.floor(idx);
          var x = k <= it.letra.length
            ? livro.largura(it.letra.slice(0, k)) + (idx - k) * espaco
            : livro.largura(it.letra) + (idx - it.letra.length) * espaco;
          var w = livro.largura(m2[0], true);
          x = Math.max(x, fim ? fim + 0.35 : 0);
          if (x + w > larguraEm) x = Math.max(larguraEm - w, fim ? fim + 0.1 : 0);
          var s = linhaAc.appendChild(livro.el("span", "ac", m2[0]));
          s.style.left = x.toFixed(3) + "em";
          fim = x + w;
        }
        par.appendChild(livro.el("div", "linha", it.letra));
      }
    });
    return b;
  };

  function esperarImagens(el) {
    var imgs = el.tagName === "IMG" ? [el] : Array.prototype.slice.call(el.querySelectorAll("img"));
    return Promise.all(imgs.map(function (img) {
      if (img.complete) return null;
      return comPrazo(new Promise(function (ok) { img.onload = img.onerror = ok; }), 15000);
    }));
  }

  // --- Montagem ------------------------------------------------------------

  function montar(w, seccoes, base, estado) {
    var doc = w.document;
    var livro = new Livro(doc);
    var imagens = new URL("../assets/imagens/", base).href;
    var ilustracoes = imagens + "Cantin%C3%A1cio%202019/";

    // Capa (a de 2019) e ficha técnica.
    var capa = livro.pagina("capa ilustrada", 0);
    capa.appendChild(livro.el("img")).src = ilustracoes + "p001.jpg";

    var ficha = livro.pagina("ficha", 0);
    ficha.innerHTML =
      '<h1 class="grande">Cantinácio</h1>' +
      '<img class="logotipo" alt="">' +
      '<p class="movimento">Campos de Férias dos Colégios da Companhia de Jesus</p>' +
      '<p class="colegios">Colégio da Imaculada Conceição<br>Colégio de S. João de Brito<br>Colégio das Caldinhas</p>' +
      '<h2 class="edicao">Cantinácio Virtual</h2>' +
      '<p class="versao"></p>' +
      '<dl class="creditos">' +
      "<dt>Pesquisa e edição</dt><dd>Sara Moinhos</dd>" +
      "<dt>Ilustrações</dt><dd>Francisco Rodrigues (Pica)</dd>" +
      "<dt>Ilustrações adicionais</dt><dd>Wikinácios, ao estilo do Pica</dd>" +
      "<dt>Coordenação e assistência</dt><dd>Francisca Pimentel</dd>" +
      "</dl>" +
      '<p class="agradecimento">Um agradecimento muito especial a todos os que colaboraram neste projecto.<br>' +
      "Conseguimos o que parecia impossível. UMA SALVA DE PALMAS! Clap.</p>" +
      '<p class="origem">Gerado a partir de: <span></span></p>';
    ficha.querySelector(".logotipo").src = imagens + "Campin%C3%A1cios_2025.png";
    ficha.querySelector(".versao").textContent = "Versão " + hoje();
    ficha.querySelector(".origem span").textContent = SITE;

    var marcaIndice = livro.el("div", "marca");
    livro.raiz.appendChild(marcaIndice);

    var entradas = [];  // para o índice: { seccao, titulo, numero, pagina }
    var numero = 0;

    // Os números das músicas são seguidos de secção para secção, por isso
    // sabem-se já, e a «Música Viva» pode ir antes de algumas das músicas.
    var comVideo = [];
    var contador = 0;
    seccoes.forEach(function (s) {
      (s.musicas || []).forEach(function (m) {
        m.numero = ++contador;
        if (m.video) comVideo.push(m);
      });
    });
    var paginaDe = {};  // número da música -> página
    var cadeia = Promise.resolve();

    var referencias = [];  // números de página a preencher: { el, musica }

    seccoes.forEach(function (s) {
      if (s.viva && !comVideo.length) return;
      cadeia = cadeia.then(function () {
        estado("A paginar «" + s.titulo + "»…");
        if (s.viva) {
          var pv = livro.pagina("musica-viva", 2, s.titulo);
          entradas.push({ seccao: s.titulo, pagina: pv });
          var intro = livro.el("p", "viva-intro",
            "Aponte a câmara do telemóvel para o código para ver o vídeo da música.");
          livro.colunas[0].appendChild(intro);
          comVideo.forEach(function (m) {
            var c = livro.el("div", "viva-cartao");
            var q = c.appendChild(livro.el("div", "qr"));
            q.innerHTML = window.WkQR.svg(m.video);
            var t = c.appendChild(livro.el("div", "viva-texto"));
            t.appendChild(livro.el("strong", "", m.numero + ". " + m.titulo));
            var pg = t.appendChild(livro.el("span", "viva-pag", "página 000"));
            referencias.push({ el: pg, musica: m });
            livro.colocar(c, false);
          });
          return espera();
        }
        var primeira;
        if (s.capa) {
          primeira = livro.pagina("capa", 0);
          primeira.appendChild(livro.el("img")).src = ilustracoes + s.capa;
        }
        if (s.texto) {
          var p = livro.pagina("textual", 1, s.capa ? null : s.titulo);
          primeira = primeira || p;
          entradas.push({ seccao: s.titulo, pagina: primeira });
          // Cada subtítulo vai junto com o que vem a seguir.
          var elementos = [];
          s.elementos.forEach(function (el, i) {
            var anterior = s.elementos[i - 1];
            if (anterior && anterior.tagName === "H2") {
              var g = elementos[elementos.length - 1];
              g.appendChild(el);
            } else if (el.tagName === "H2") {
              var grupo = el.ownerDocument.createElement("div");
              grupo.className = "grupo-texto";
              grupo.appendChild(el);
              elementos.push(grupo);
            } else {
              elementos.push(el);
            }
          });
          var feito = Promise.resolve();
          elementos.forEach(function (el) {
            feito = feito.then(function () {
              var e = doc.importNode(el, true);
              livro.colunas[livro.coluna].appendChild(e);
              return esperarImagens(e).then(function () {
                e.remove();
                livro.colocar(e, false);
              });
            });
          });
          return feito;
        }
        var p2 = livro.pagina("musicas", 2, s.capa ? null : s.titulo);
        primeira = primeira || p2;
        entradas.push({ seccao: s.titulo, pagina: primeira });
        var largura = livro.colunas[0].clientWidth;
        s.musicas.forEach(function (m) {
          numero++;
          // Cada página começa com uma música: só se junta outra a uma página
          // se couber inteira nela (as músicas maiores do que uma página, e as
          // dos Aplausos, seguem-se sem esta regra).
          var b = s.fluir ? livro.blocoMusica(m, numero, largura) : livro.colocarNaPagina(function () {
            return livro.blocoMusica(m, numero, largura);
          });
          if (s.fluir) livro.colocar(b, true);
          paginaDe[m.numero] = b.closest(".pagina");
          entradas.push({ titulo: m.titulo, numero: numero, pagina: b.closest(".pagina") });
        });
        return espera();
      });
    });

    // Onde sobra espaço no fim de uma coluna de músicas, pôr uma das
    // ilustrações de 2019 (cada uma só uma vez, pela ordem).
    cadeia = cadeia.then(function () {
      estado("A pôr as ilustrações…");
      var porUsar = ILUSTRACOES.slice();
      var colunas = [];
      doc.querySelectorAll(".pagina.musicas .coluna").forEach(function (c) { colunas.push(c); });
      colunas.forEach(function (col) {
        if (!porUsar.length || !col.lastElementChild) return;
        var livre = (col.getBoundingClientRect().bottom - col.lastElementChild.getBoundingClientRect().bottom) / PX_POR_MM;
        var larguraCol = col.clientWidth / PX_POR_MM;
        for (var k = 0; k < porUsar.length; k++) {
          var il = porUsar[k];
          var larg = Math.min(larguraCol * 0.8, 70);
          if (larg * il.altura > livre - 8) larg = (livre - 8) / il.altura;
          if (larg < 35) continue;
          var img = livro.el("img", "ilustracao");
          img.src = ilustracoes + il.ficheiro;
          img.alt = "";
          img.style.width = larg.toFixed(1) + "mm";
          img.style.height = (larg * il.altura).toFixed(1) + "mm";
          col.appendChild(img);
          porUsar.splice(k, 1);
          break;
        }
      });
    });

    return cadeia.then(function () {
      estado("A fazer o índice…");
      livro.pagina("indice", 2, "Índice", marcaIndice);
      var numeros = [];
      var cabecalho = null;
      entradas.forEach(function (e) {
        var linha = livro.el("div", e.titulo ? "entrada" : "entrada seccao");
        linha.appendChild(livro.el("span", "nome", e.titulo ? e.numero + ". " + e.titulo : e.seccao));
        linha.appendChild(livro.el("span", "pontos"));
        var n = linha.appendChild(livro.el("span", "pag", "000"));
        numeros.push({ el: n, pagina: e.pagina });
        if (!e.titulo) {
          // O nome da secção fica sempre junto da primeira música.
          if (cabecalho) livro.colocar(cabecalho, false);
          cabecalho = livro.el("div", "grupo");
          cabecalho.appendChild(linha);
          return;
        }
        if (cabecalho) {
          cabecalho.appendChild(linha);
          livro.colocar(cabecalho, false);
          cabecalho = null;
        } else {
          livro.colocar(linha, false);
        }
      });
      if (cabecalho) livro.colocar(cabecalho, false);
      marcaIndice.remove();

      // Números de página (a capa e as capas das secções não os mostram).
      var paginas = Array.prototype.slice.call(doc.querySelectorAll(".pagina"));
      paginas.forEach(function (p, i) {
        p.dataset.numero = i + 1;
        if (p.classList.contains("capa") || p.classList.contains("ficha")) return;
        p.appendChild(livro.el("div", "numero " + (i % 2 ? "esquerda" : "direita"), String(i + 1)));
      });
      numeros.forEach(function (n) { n.el.textContent = n.pagina.dataset.numero; });
      referencias.forEach(function (r) {
        r.el.textContent = "página " + paginaDe[r.musica.numero].dataset.numero;
      });
      return esperarImagens(doc.body).then(function () { return paginas.length; });
    });
  }

  var ESTILO = [
    "@page { size: A4; margin: 0; }",
    "html, body { margin: 0; background: #8a8f98; }",
    "body { font-family: Roboto, Arial, Helvetica, sans-serif; color: #000; }",
    "#barra { position: sticky; top: 0; z-index: 1; display: flex; gap: 12px; align-items: center;",
    "  padding: 10px 16px; background: #1f2a44; color: #fff; font-size: 14px; }",
    "#barra button { font: inherit; padding: 6px 14px; border: 0; border-radius: 4px; background: #fff; color: #1f2a44; cursor: pointer; }",
    "#barra button:disabled { opacity: .5; cursor: default; }",
    ".pagina { position: relative; box-sizing: border-box; width: 210mm; height: 297mm; margin: 8mm auto;",
    "  padding: 14mm 12mm 17mm; overflow: hidden; background: #fff; display: flex; flex-direction: column;",
    "  box-shadow: 0 1px 6px rgba(0,0,0,.35); }",
    ".colunas { flex: 1; min-height: 0; display: flex; gap: 7mm; }",
    ".coluna { flex: 1; min-width: 0; overflow: hidden; }",
    ".numero { position: absolute; bottom: 8mm; font: 700 16pt " + FAMILIA + "; }",
    ".numero.direita { right: 12mm; } .numero.esquerda { left: 12mm; }",
    ".cabecalho { margin: 0 0 5mm; padding-bottom: 1.5mm; border-bottom: 1.5pt solid #000;",
    "  font: 600 22pt Oswald, 'Arial Narrow', sans-serif; text-transform: uppercase; letter-spacing: .02em; }",

    // Capas
    ".capa { padding: 0; align-items: center; justify-content: center; }",
    ".capa img { width: 100%; height: 100%; object-fit: contain; }",

    // Ficha técnica
    ".ficha { padding: 22mm 24mm 18mm; align-items: center; text-align: center; }",
    ".ficha .grande { margin: 4mm 0 10mm; font: 600 44pt Oswald, 'Arial Narrow', sans-serif; text-transform: uppercase; }",
    ".ficha .logotipo { width: 42mm; height: 42mm; object-fit: contain; }",
    ".ficha .movimento { margin: 5mm 0 2mm; font-size: 12pt; font-weight: 700; }",
    ".ficha .colegios { margin: 0; font-size: 10pt; line-height: 1.45; }",
    ".ficha .edicao { align-self: flex-start; margin: 22mm 0 0; font: 600 20pt Oswald, 'Arial Narrow', sans-serif; text-transform: uppercase; }",
    ".ficha .versao { align-self: flex-start; margin: 1mm 0 6mm; font: 500 13pt Oswald, 'Arial Narrow', sans-serif; }",
    ".ficha .creditos { align-self: flex-start; margin: 0; text-align: left; font-size: 10pt; }",
    ".ficha dt { font-weight: 700; margin-top: 3.5mm; } .ficha dd { margin: .5mm 0 0; }",
    ".ficha .agradecimento { margin: auto 0 6mm; font-size: 9.5pt; line-height: 1.45; }",
    ".ficha .origem { margin: 0; font-size: 9.5pt; }",

    // Índice
    ".entrada { display: flex; align-items: baseline; font-size: 7.6pt; line-height: 1.32; }",
    ".entrada .nome { flex: 0 1 auto; min-width: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }",
    ".entrada .pontos { flex: 1 0 3mm; margin: 0 .8mm; border-bottom: .8pt dotted #000; }",
    ".entrada .pag { flex: none; }",
    ".entrada.seccao { margin: 3mm 0 1mm; font: 600 12pt Oswald, 'Arial Narrow', sans-serif; }",
    ".entrada.seccao .pontos { border: 0; }",
    ".coluna > .grupo:first-child .entrada.seccao { margin-top: 0; }",

    // Músicas
    ".musica { margin: 0 0 11mm; }",
    ".musica.continua { margin-top: 0; }",
    ".musica { font-family: " + FAMILIA + "; font-size: var(--tam, 11pt); line-height: 1.25; }",
    ".titulo { margin: 0 0 3.5mm; padding-bottom: .8mm; border-bottom: 1pt solid #000; font-size: 18pt; font-weight: 700; line-height: 1.15; }",
    ".titulo:has(+ .autor) { margin-bottom: 0; }",
    ".autor { margin: .6mm 0 3mm; text-align: right; font-size: 12pt; line-height: 1.2; }",
    ".linha { min-height: 1.25em; white-space: pre-wrap; overflow-wrap: anywhere; }",
    ".linha.acorde { font-style: italic; }",
    ".linha.solta { padding-left: 1.5em; text-indent: -1.5em; }",
    ".par .acordes { position: relative; height: 1.25em; }",
    ".par .ac { position: absolute; top: 0; font-style: italic; white-space: pre; }",
    ".musica .texto { margin: 0 0 1.6mm; font-size: 1em; line-height: 1.3; overflow-wrap: anywhere; }",
    ".musica ul.texto, .musica ol.texto { padding-left: 5mm; }",
    ".ilustracao { display: block; margin: 6mm auto 0; }",

    // Música Viva
    ".viva-intro { margin: 0 0 4mm; font-size: 9pt; line-height: 1.4; }",
    ".viva-cartao { display: flex; align-items: center; gap: 3mm; margin: 0 0 4mm; }",
    ".viva-cartao .qr { flex: none; width: 20mm; height: 20mm; }",
    ".viva-cartao .qr svg { display: block; width: 100%; height: 100%; }",
    ".viva-texto { font-size: 9pt; line-height: 1.3; min-width: 0; overflow-wrap: anywhere; }",
    ".viva-pag { display: block; margin-top: .5mm; font-size: 8pt; }",

    // Manual de Instruções e Escalas
    ".textual .coluna > * { margin-top: 0; }",
    ".textual .coluna > .grupo-texto:first-child > h2 { margin-top: 0; }",
    ".textual h2 { margin: 3mm 0 2mm; font: 600 15pt Oswald, 'Arial Narrow', sans-serif; text-transform: uppercase; }",
    ".textual p, .textual li { font-size: 10pt; line-height: 1.42; margin: 0 0 2.2mm; }",
    ".textual ol, .textual ul { margin: 0 0 2.2mm; padding-left: 6mm; }",
    ".textual pre { margin: 0 0 2.2mm; font: 9.5pt 'Roboto Mono', monospace; white-space: pre-wrap; }",
    ".textual img { display: block; max-width: 100%; max-height: 225mm; height: auto; margin: 0 auto 2mm; }",
    ".textual table { width: 100%; margin: 0 0 3mm; border-collapse: collapse; font-size: 9pt; }",
    ".textual th, .textual td { padding: 1.2mm .8mm; border: .5pt solid #777; text-align: center; }",

    "@media print {",
    "  html, body { background: none; }",
    "  #barra { display: none; }",
    "  .pagina { margin: 0; box-shadow: none; break-after: page; }",
    "  .pagina:last-child { break-after: auto; }",
    "}"
  ].join("\n");

  var FONTES = "https://fonts.googleapis.com/css2?family=Oswald:wght@500;600" +
    "&family=Roboto:ital,wght@0,400;0,700;1,400&display=swap";

  function abrir(base) {
    var w = window.open("", "_blank");
    if (!w) {
      window.alert("O navegador bloqueou a janela nova. Autorize as janelas deste site e carregue outra vez em «Cantinácio Virtual».");
      return;
    }
    var doc = w.document;
    doc.open();
    doc.write('<!doctype html><html lang="pt"><head><meta charset="utf-8">' +
      "<title>Cantinácio Virtual — " + hoje() + "</title>" +
      '<link rel="stylesheet" href="' + FONTES + '"><style>' + ESTILO + "</style></head>" +
      '<body><div id="barra"><span id="estado">A preparar o Cantinácio…</span>' +
      '<button type="button" id="imprimir" disabled>Imprimir</button></div>' +
      '<main id="paginas"></main></body></html>');
    doc.close();

    var estado = function (t) { doc.getElementById("estado").textContent = t; };
    var botao = doc.getElementById("imprimir");
    botao.addEventListener("click", function () { w.print(); });

    // As letras têm de estar carregadas antes de medir as colunas.
    var folha = doc.querySelector("link[rel=stylesheet]");
    var fontes = comPrazo(new Promise(function (ok) {
      if (folha.sheet) ok(); else { folha.onload = folha.onerror = ok; }
    }), 5000).then(function () {
      return comPrazo(Promise.all(["10pt Roboto", "bold 10pt Roboto", "600 10pt Oswald"].map(function (f) {
        return doc.fonts.load(f).catch(function () { return null; });
      })), 5000);
    });

    estado("A ler as músicas do Wikinácios…");
    Promise.all([fontes].concat(SECCOES.map(function (s) {
      return ler(Object.assign({}, s), base);
    }))).then(function (r) {
      return montar(w, r.slice(1), base, estado);
    }).then(function (paginas) {
      estado("Cantinácio Virtual pronto: " + paginas + " páginas.");
      botao.disabled = false;
      w.focus();
      w.print();
    }).catch(function (e) {
      estado("Não foi possível gerar o Cantinácio (" + e.message + ").");
    });
  }

  function iniciar() {
    document.querySelectorAll(".wk-cantinacio-imprimir").forEach(function (b) {
      if (b.dataset.pronto) return;
      b.dataset.pronto = "1";
      b.addEventListener("click", function (ev) {
        ev.preventDefault();
        abrir(window.location.href);
      });
    });
  }
  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(iniciar);  // navegação instantânea do Material
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
