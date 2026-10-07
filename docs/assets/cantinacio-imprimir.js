// Botão «Cantinácio Virtual» da página do Cantinácio (docs/Movimento/Cantinácio.md).
// Abre uma pequena janela de configuração (que secções de músicas entram e se
// vão as versões originais, as simplificadas do Cantinácio de 2019 ou ambas) e
// gera um PDF para descarregar com as letras e os acordes, paginado em A4 a
// duas colunas à maneira do Cantinácio de 2019 (3.ª edição) — capa, ficha
// técnica, prefácio, índice com números de página, capas das secções. As páginas são
// montadas numa moldura escondida e desenhadas no PDF com o jsPDF, com texto
// (não imagens) para o ficheiro ficar pequeno e se poder pesquisar. As
// músicas são lidas das próprias páginas do site, por isso o PDF está sempre
// actualizado.
(function () {
  "use strict";

  var SITE = "http://campinacios.pedrovicente.pt";

  // As secções de músicas que se podem escolher na configuração.
  var ESCOLHAS = ["Campinácios", "Camtil", "Cânticos", "Estrangeiras", "Gambozinos", "Portuguesas"];

  // Nas músicas com duas versões, esta legenda (em itálico) separa a original,
  // que vem antes, da simplificada do Cantinácio de 2019, que vem depois.
  var LEGENDA_SIMPLIFICADA = /^Versão simplificada Cantinácio 2019:?$/;

  // Pela ordem do Cantinácio de 2019, excepto as Portuguesas e as Estrangeiras, que vão depois dos Cânticos, e os Aplausos, que ficam no fim; o título é o da secção nessa edição.
  var SECCOES = [
    { pagina: "Prefácio", titulo: "Prefácio", texto: true, preambulo: true },  // preambulo: vai antes do índice, como em 2019, e não entra nele
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

  // Ilustrações (número do ficheiro, largura × altura em px), com o registo da
  // origem de cada uma:
  // - ORIGINAIS: as do Pica (Francisco Rodrigues), tiradas do Cantinácio de
  //   2019;
  // - GERADAS: desenhadas por IA (Claude, por código, em
  //   scripts/desenhar_ilustracoes.py) para o Wikinácios, ao estilo do Pica:
  //   lanterna, Petromax, Cerelac, latrina, roda, guitarra, djambé, sol, tenda,
  //   pão, marmelada, manteiga, leite, Coca-Cola, fogueira, caminhada, comboio,
  //   árvores, cruz, abraço, ajoelhar, mosquito, cegonha, arco-íris, pêra,
  //   galinha, sopa, aranha, semente, gota, triciclo, trotinete, bicicleta,
  //   lambreta, tractor, calhambeque, garrafa, boi, mira («tens mira?»), Super
  //   Boi, cantil, rio, banho de rio, banana, melancia, casaco camuflado da
  //   tropa, bandeira num mastro, lenço de campo, lama, jipe, chinelos, massa
  //   com atum, nadar, saco-cama, estendal, padre, criança, despedida com
  //   lágrimas, luar, estrelas no céu, apito, boné, calções, bolhas nos pés,
  //   vegetação, flores, sabão azul, moscas, botija de gás, amizade, pó, mamã,
  //   tia, director, director adjunto, capelão, animador livre, animador de
  //   equipa, maçã, palmas com uma cruz por cima e raposa (pela ordem dos
  //   ficheiros 15 a 95).
  // Cada imagem posta no Cantinácio leva a origem em data-origem e, num canto,
  // a marca «Pica» ou «IA».
  var ORIGINAIS = [
    [1, 700, 679], [2, 230, 700], [3, 443, 700], [4, 405, 700], [5, 700, 665],
    [6, 700, 464], [7, 630, 700], [8, 700, 603], [9, 649, 700], [10, 419, 700],
    [11, 700, 521], [12, 635, 700], [13, 594, 700], [14, 437, 700]
  ];
  var GERADAS = [
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
    [70, 597, 700], [71, 573, 700], [72, 700, 647], [73, 700, 682], [74, 700, 676],
    [75, 700, 496], [76, 700, 476], [77, 700, 608], [78, 602, 700], [79, 700, 400],
    [80, 700, 635], [81, 700, 631], [82, 700, 668], [83, 538, 700], [84, 493, 700],
    [85, 700, 568], [86, 499, 700], [87, 495, 700], [88, 583, 700], [89, 439, 700],
    [90, 369, 700], [91, 444, 700], [92, 700, 683], [93, 644, 700], [94, 700, 664],
    [95, 601, 700]
  ];
  function ilustracao(origem, marca) {
    return function (i) {
      return {
        ficheiro: "ilustracao-" + (i[0] < 10 ? "0" : "") + i[0] + ".jpg",
        altura: i[2] / i[1],
        origem: origem,
        marca: marca
      };
    };
  }
  var ILUSTRACOES = ORIGINAIS.map(ilustracao("Pica, Cantinácio de 2019", "Pica"))
    .concat(GERADAS.map(ilustracao("gerada por IA, ao estilo do Pica", "IA")));
  var RECENTES = 12;  // ao repetir, não se repete nenhuma das últimas 12

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

  // Numa música com duas versões, fica só a original, só a simplificada ou as
  // duas (com a legenda entre elas), conforme a configuração.
  function versoes(m, opcoes) {
    if (!m.simplificada) return m;
    var ambas = opcoes.originais && opcoes.simplificadas;
    m.partes = m.partes.filter(function (p) {
      if (p.legenda) return ambas;
      return p.simplificada ? opcoes.simplificadas : opcoes.originais;
    });
    return m;
  }

  function ler(seccao, base, opcoes) {
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
        // No preâmbulo, o subtítulo é o cabeçalho da página: não se repete.
        if (seccao.preambulo && inicio >= 0) inicio++;
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
        // As gravações (<audio>) só se ouvem no site: não se imprimem.
        if (el.tagName === "AUDIO" || el.querySelector("audio")) return;
        var soItalico = el.tagName === "P" && el.children.length === 1 &&
          el.children[0].tagName === "EM" && el.textContent.trim() === el.children[0].textContent.trim();
        var simplificada = !!actual.simplificada;
        if (soItalico && LEGENDA_SIMPLIFICADA.test(el.textContent.trim())) {
          actual.simplificada = true;
          el.classList.add("legenda-versao");
          actual.partes.push({ el: limpar(el, url), legenda: true });
        } else if (soItalico && !actual.partes.length && !actual.autor) {
          actual.autor = el.textContent.trim();
        } else if (el.tagName === "PRE") {
          var linhas = el.textContent.replace(/\s+$/, "").split("\n");
          actual.partes.push({ linhas: linhas, simplificada: simplificada });
        } else {
          actual.partes.push({ el: limpar(el, url), simplificada: simplificada });
        }
      });
      seccao.musicas = musicas.map(function (m) { return versoes(m, opcoes); });
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
      "<dt>Ilustrações adicionais</dt><dd>Geradas por IA, ao estilo do Pica</dd>" +
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
            q.dataset.url = m.video;  // no PDF, o código é também uma ligação para o vídeo
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
          var p = livro.pagina("textual", 1, s.capa ? null : s.titulo, s.preambulo ? marcaIndice : null);
          primeira = primeira || p;
          if (!s.preambulo) entradas.push({ seccao: s.titulo, pagina: primeira });
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
      // Primeiro todas uma vez, pela ordem; depois repetem-se ao acaso,
      // sem repetir nenhuma das últimas RECENTES.
      var porUsar = ILUSTRACOES.slice();
      var ultimas = [];
      var colunas = [];
      doc.querySelectorAll(".pagina.musicas .coluna").forEach(function (c) { colunas.push(c); });
      colunas.forEach(function (col) {
        if (!col.lastElementChild) return;
        var ultimo = col.lastElementChild;
        // A margem de baixo da última música junta-se à de cima da ilustração
        // (6 mm): conta a maior, mais 2 mm de folga e 2 mm para a marca.
        var margem = Math.max(6, parseFloat(w.getComputedStyle(ultimo).marginBottom) / PX_POR_MM) + 4;
        var livre = (col.getBoundingClientRect().bottom - ultimo.getBoundingClientRect().bottom) / PX_POR_MM - margem;
        var larguraCol = col.clientWidth / PX_POR_MM;
        function largura(il) {
          var larg = Math.min(larguraCol * 0.8, 70);
          if (larg * il.altura > livre) larg = livre / il.altura;
          return larg < 35 ? 0 : larg;
        }
        var il = null;
        for (var k = 0; k < porUsar.length; k++) {
          if (largura(porUsar[k])) { il = porUsar.splice(k, 1)[0]; break; }
        }
        if (!il && !porUsar.length) {
          var hipoteses = ILUSTRACOES.filter(function (i) {
            return ultimas.indexOf(i) < 0 && largura(i);
          });
          if (hipoteses.length) il = hipoteses[Math.floor(Math.random() * hipoteses.length)];
        }
        if (!il) return;
        var larg = largura(il);
        var caixa = livro.el("div", "ilustracao");
        caixa.dataset.origem = il.origem;
        caixa.style.width = larg.toFixed(1) + "mm";
        caixa.style.height = (larg * il.altura).toFixed(1) + "mm";
        var img = caixa.appendChild(livro.el("img"));
        img.src = ilustracoes + il.ficheiro;
        img.alt = "";
        caixa.appendChild(livro.el("span", "marca", il.marca));
        col.appendChild(caixa);
        ultimas.push(il);
        if (ultimas.length > RECENTES) ultimas.shift();
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
        numeros.push({ el: n, linha: linha, pagina: e.pagina });
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
      // No PDF, cada entrada do índice e cada «página N» da Música Viva são
      // ligações para essa página.
      numeros.forEach(function (n) {
        n.el.textContent = n.pagina.dataset.numero;
        n.linha.dataset.destino = n.pagina.dataset.numero;
      });
      referencias.forEach(function (r) {
        var numeroDaPagina = paginaDe[r.musica.numero].dataset.numero;
        r.el.textContent = "página " + numeroDaPagina;
        r.el.dataset.destino = numeroDaPagina;
      });
      return esperarImagens(doc.body).then(function () { return paginas.length; });
    });
  }

  var ESTILO = [
    "@page { size: A4; margin: 0; }",
    "html, body { margin: 0; background: #8a8f98; }",
    // No PDF, Arial passa a Helvetica (tem as mesmas medidas) e o texto de
    // largura fixa a Courier; a Oswald vai embutida.
    "body { font-family: " + FAMILIA + "; color: #000; }",
    // O PDF escreve sem kerning nem ligaduras: a paginação também, para as
    // larguras serem as mesmas.
    "* { font-kerning: none; font-variant-ligatures: none; }",
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
    ".musica .legenda-versao { margin-top: 3mm; }",
    ".ilustracao { position: relative; margin: 6mm auto 0; }",
    ".ilustracao img { display: block; width: 100%; height: 100%; }",
    ".ilustracao .marca { position: absolute; right: 0; bottom: -1mm; font: italic 6.5pt " + FAMILIA + "; color: #666; }",

    // Música Viva
    ".viva-intro { margin: 0 0 4mm; font-size: 9pt; line-height: 1.4; }",
    ".viva-cartao { display: flex; align-items: center; gap: 3mm; margin: 0 0 4mm; }",
    ".viva-cartao .qr { flex: none; width: 20mm; height: 20mm; }",
    ".viva-cartao .qr svg { display: block; width: 100%; height: 100%; }",
    ".viva-texto { font-size: 9pt; line-height: 1.3; min-width: 0; overflow-wrap: anywhere; }",
    ".viva-pag { display: block; margin-top: .5mm; font-size: 8pt; }",

    // Prefácio, Manual de Instruções e Escalas
    ".textual .coluna > * { margin-top: 0; }",
    ".textual .coluna > .grupo-texto:first-child > h2 { margin-top: 0; }",
    ".textual h2 { margin: 3mm 0 2mm; font: 600 15pt Oswald, 'Arial Narrow', sans-serif; text-transform: uppercase; }",
    ".textual p, .textual li { font-size: 10pt; line-height: 1.42; margin: 0 0 2.2mm; }",
    ".textual ol, .textual ul { margin: 0 0 2.2mm; padding-left: 6mm; }",
    ".textual pre { margin: 0 0 2.2mm; font: 9.5pt 'Courier New', Courier, monospace; white-space: pre-wrap; }",
    ".textual img { display: block; max-width: 100%; max-height: 225mm; height: auto; margin: 0 auto 2mm; }",
    ".textual table { width: 100%; margin: 0 0 3mm; border-collapse: collapse; font-size: 9pt; }",
    ".textual th, .textual td { padding: 1.2mm .8mm; border: .5pt solid #777; text-align: center; }",
    ".textual .wk-epigrafe { margin: 4mm 0 9mm; text-align: center; }",
    ".textual .wk-assinatura { margin-top: 9mm; text-align: right; }"
  ].join("\n");

  // --- PDF -----------------------------------------------------------------

  var JSPDF = {
    src: "https://cdnjs.cloudflare.com/ajax/libs/jspdf/4.2.1/jspdf.umd.min.js",
    integrity: "sha512-plOdviVmws4Y3JAvbnpfKb2hVxKM1lCwsi3vmElYRj+tiDLffZ4FVUj5a8vyKJ9pIgl8JCAHEJ4D1iUKBecswg=="
  };
  // A Oswald (títulos) vai embutida no PDF; as mesmas fontes servem para
  // paginar, para as medidas baterem certo. Licença em assets/fontes/OFL.txt.
  var OSWALD = [
    { ficheiro: "Oswald-Medium.ttf", peso: 500, estilo: "normal" },
    { ficheiro: "Oswald-SemiBold.ttf", peso: 600, estilo: "bold" }
  ];

  var aCarregarJsPdf = null;
  function carregarJsPdf() {
    if (window.jspdf) return Promise.resolve(window.jspdf.jsPDF);
    if (!aCarregarJsPdf) aCarregarJsPdf = new Promise(function (ok, falha) {
      var s = document.createElement("script");
      s.src = JSPDF.src;
      s.integrity = JSPDF.integrity;
      s.crossOrigin = "anonymous";
      s.referrerPolicy = "no-referrer";
      s.onload = function () {
        if (window.jspdf) ok(window.jspdf.jsPDF); else falha(new Error("o jsPDF não arrancou"));
      };
      s.onerror = function () {
        aCarregarJsPdf = null;
        s.remove();
        falha(new Error("não foi possível carregar o jsPDF"));
      };
      document.head.appendChild(s);
    });
    return aCarregarJsPdf;
  }

  function bytes(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(decodeURIComponent(url.split("/").pop()) + ": " + r.status);
      return r.arrayBuffer();
    }).then(function (b) { return new Uint8Array(b); });
  }

  function base64(u8) {
    var s = "";
    for (var i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
    return btoa(s);
  }

  // Os caracteres que as fontes de base do PDF (Helvetica, Courier) sabem
  // escrever; o resto (cirílico, grego, árabe…) vai como imagem.
  var WINANSI = /^[ -~ -ÿ€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ]*$/;
  var TROCAS = { "‟": "“", "‐": "-", "‑": "-", " ": " ", " ": " ", "­": "" };
  function normalizar(t) {
    return t.normalize("NFC").replace(/[‟‐‑  ­]/g, function (c) { return TROCAS[c]; });
  }

  function cor(css) {
    var n = (css.match(/[\d.]+/g) || [0, 0, 0]).map(Number);
    return [n[0], n[1], n[2]];
  }

  // As imagens das páginas, lidas tal como estão (os JPEG vão para o PDF sem
  // serem recomprimidos; as que se repetem vão uma só vez).
  function lerImagens(doc) {
    var imagens = {};
    var lista = [];
    doc.querySelectorAll(".pagina img").forEach(function (img) {
      if (img.src && !(img.src in imagens)) { imagens[img.src] = null; lista.push(img); }
    });
    return Promise.all(lista.map(function (img) {
      return bytes(img.src).then(function (b) {
        var tipo = b[0] === 0xff && b[1] === 0xd8 ? "JPEG" : b[0] === 0x89 && b[1] === 0x50 ? "PNG" : null;
        if (!tipo) {
          // Outro formato: passa por um <canvas> e vai como PNG.
          var c = document.createElement("canvas");
          c.width = img.naturalWidth;
          c.height = img.naturalHeight;
          c.getContext("2d").drawImage(img, 0, 0);
          b = c.toDataURL("image/png");
          tipo = "PNG";
        }
        imagens[img.src] = { dados: b, tipo: tipo, nome: "img" + Object.keys(imagens).indexOf(img.src) };
      }).catch(function () { return null; });  // uma imagem que falte não impede o PDF
    })).then(function () { return imagens; });
  }

  // Desenha no PDF as páginas montadas na moldura: o texto palavra a palavra
  // (juntando as que o PDF põe sozinho no mesmo sítio), as linhas, as imagens
  // e os QR Codes, cada coisa onde o navegador a pôs.
  function paraPdf(JsPdf, w, oswald, imagens, estado) {
    var doc = w.document;
    var pdf = new JsPdf({ unit: "mm", format: "a4", compress: true });
    oswald.forEach(function (f) {
      pdf.addFileToVFS(f.ficheiro, f.dados);
      pdf.addFont(f.ficheiro, "Oswald", f.estilo);
    });
    pdf.setProperties({
      title: "Cantinácio Virtual — " + hoje(),
      subject: "Letras e acordes do Wikinácios",
      creator: SITE
    });
    if (pdf.setLanguage) pdf.setLanguage("pt-PT");

    var paginas = Array.prototype.slice.call(doc.querySelectorAll(".pagina"));
    var gama = doc.createRange();
    var tela = document.createElement("canvas");
    var bases = {};

    // Distância do cimo do texto à linha de base, em fracção do tamanho da
    // letra, medida no próprio navegador para cada tipo de letra.
    function linhaDeBase(cs) {
      var chave = cs.fontStyle + "|" + cs.fontWeight + "|" + cs.fontFamily;
      if (chave in bases) return bases[chave];
      var s = doc.createElement("span");
      s.style.cssText = "position:absolute;left:0;top:0;white-space:nowrap;line-height:normal;font-size:100px";
      s.style.fontFamily = cs.fontFamily;
      s.style.fontWeight = cs.fontWeight;
      s.style.fontStyle = cs.fontStyle;
      s.textContent = "Hg";
      var marca = s.appendChild(doc.createElement("span"));
      marca.style.cssText = "display:inline-block;width:0;height:0;vertical-align:baseline";
      doc.body.appendChild(s);
      var g = doc.createRange();
      g.selectNodeContents(s.firstChild);
      var r = (g.getBoundingClientRect().top);
      bases[chave] = (marca.getBoundingClientRect().bottom - r) / 100;
      s.remove();
      return bases[chave];
    }

    function fonte(cs) {
      var negrito = parseInt(cs.fontWeight, 10) >= 600;
      var italico = cs.fontStyle !== "normal";
      var f = { px: parseFloat(cs.fontSize), base: linhaDeBase(cs), cor: cor(cs.color), cs: cs };
      if (/Oswald/i.test(cs.fontFamily)) {
        f.nome = "Oswald";
        f.estilo = negrito ? "bold" : "normal";
        f.unicode = true;
      } else {
        f.nome = /Courier|mono/i.test(cs.fontFamily) ? "courier" : "helvetica";
        f.estilo = negrito && italico ? "bolditalic" : negrito ? "bold" : italico ? "italic" : "normal";
      }
      f.maiusculas = cs.textTransform === "uppercase";
      f.espacado = cs.letterSpacing !== "normal" && parseFloat(cs.letterSpacing) !== 0;
      return f;
    }

    function usar(f) {
      pdf.setFont(f.nome, f.estilo);
      pdf.setFontSize(f.px * 0.75);
      pdf.setTextColor(f.cor[0], f.cor[1], f.cor[2]);
    }

    function desenharPagina(p) {
      var o = p.getBoundingClientRect();
      function X(px) { return (px - o.left) / PX_POR_MM; }
      function Y(px) { return (px - o.top) / PX_POR_MM; }
      function mm(px) { return px / PX_POR_MM; }
      function dentro(r, recorte) {
        var cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2;
        return cx >= recorte.left && cx <= recorte.right && cy >= recorte.top && cy <= recorte.bottom;
      }

      // Um bocado de texto que o PDF vai escrever de seguida.
      var seg = null;
      function fecharSegmento() {
        if (seg) pdf.text(seg.texto, seg.x, seg.y);
        seg = null;
      }

      function palavra(t, r, f, recorte) {
        if (!r.width || !dentro(r, recorte)) return;
        if (f.maiusculas) t = t.toUpperCase();
        var x = X(r.left);
        var y = Y(r.top + f.base * f.px);
        if (!f.unicode && !WINANSI.test(t)) {
          fecharSegmento();
          comoImagem(t, r, f);
          return;
        }
        if (seg && !f.espacado && Math.abs(seg.y - y) < 0.1) {
          var espaco = pdf.getTextWidth(" ");
          var n = Math.max(1, Math.round((x - seg.fim) / espaco));
          var junto = seg.texto + new Array(n + 1).join(" ") + t;
          if (Math.abs(seg.x + pdf.getTextWidth(junto) - pdf.getTextWidth(t) - x) < 0.15) {
            seg.texto = junto;
            seg.fim = X(r.right);
            return;
          }
        }
        fecharSegmento();
        seg = { texto: t, x: x, y: y, fim: X(r.right) };
      }

      // Uma palavra que as fontes de base não sabem escrever: desenha-se num
      // <canvas> com o tipo de letra do navegador e vai como imagem.
      function comoImagem(t, r, f) {
        var escala = 4;
        tela.width = Math.ceil(r.width * escala);
        tela.height = Math.ceil(r.height * escala);
        var ctx = tela.getContext("2d");
        ctx.scale(escala, escala);
        ctx.font = f.cs.fontStyle + " " + f.cs.fontWeight + " " + f.px + "px " + f.cs.fontFamily;
        ctx.fillStyle = f.cs.color;
        ctx.textBaseline = "alphabetic";
        ctx.fillText(t, 0, f.base * f.px);
        pdf.addImage(tela.toDataURL("image/png"), "PNG", X(r.left), Y(r.top), mm(r.width), mm(r.height));
      }

      function texto(n, cs, recorte) {
        var f = fonte(cs);
        usar(f);
        var dados = n.data;
        var re = /\S+/g, m;
        while ((m = re.exec(dados))) {
          gama.setStart(n, m.index);
          gama.setEnd(n, m.index + m[0].length);
          var rs = gama.getClientRects();
          if (rs.length <= 1) {
            if (rs.length) palavra(normalizar(m[0]), rs[0], f, recorte);
            continue;
          }
          // Uma palavra partida entre duas linhas: letra a letra.
          var pedaco = "", inicio = null, topo = null, fim = null;
          for (var i = 0; i < m[0].length; i++) {
            gama.setStart(n, m.index + i);
            gama.setEnd(n, m.index + i + 1);
            var c = gama.getBoundingClientRect();
            if (topo !== null && Math.abs(c.top - topo) > 1) {
              palavra(normalizar(pedaco), { left: inicio, right: fim, top: topo, bottom: topo + 1, width: fim - inicio }, f, recorte);
              pedaco = "";
              inicio = null;
            }
            if (inicio === null) { inicio = c.left; topo = c.top; }
            pedaco += m[0].charAt(i);
            fim = c.right;
          }
          if (pedaco) palavra(normalizar(pedaco), { left: inicio, right: fim, top: topo, bottom: topo + 1, width: fim - inicio }, f, recorte);
        }
        fecharSegmento();
      }

      // Um texto cortado com «…» (as entradas do índice largas demais).
      function reticencias(el, cs, r) {
        var f = fonte(cs);
        usar(f);
        var t = normalizar(el.textContent.trim());
        if (f.maiusculas) t = t.toUpperCase();
        var largura = mm(r.width);
        while (t && pdf.getTextWidth(t + "…") > largura) t = t.slice(0, -1);
        var g = doc.createRange();
        g.selectNodeContents(el);
        var topo = g.getClientRects()[0] ? g.getClientRects()[0].top : r.top;
        if (WINANSI.test(t)) pdf.text(t.replace(/\s+$/, "") + "…", X(r.left), Y(topo + f.base * f.px));
      }

      function bordas(cs, r) {
        ["Top", "Right", "Bottom", "Left"].forEach(function (lado) {
          var largura = parseFloat(cs["border" + lado + "Width"]);
          var estilo = cs["border" + lado + "Style"];
          if (!largura || estilo === "none" || estilo === "hidden") return;
          var lw = mm(largura);
          var c = cor(cs["border" + lado + "Color"]);
          pdf.setDrawColor(c[0], c[1], c[2]);
          pdf.setLineWidth(lw);
          if (estilo === "dotted") {
            pdf.setLineCap("round");
            pdf.setLineDashPattern([0, lw * 2.5], 0);
          } else if (estilo === "dashed") {
            pdf.setLineDashPattern([lw * 3, lw * 2], 0);
          }
          var meio = largura / 2;
          if (lado === "Top") pdf.line(X(r.left), Y(r.top + meio), X(r.right), Y(r.top + meio));
          else if (lado === "Bottom") pdf.line(X(r.left), Y(r.bottom - meio), X(r.right), Y(r.bottom - meio));
          else if (lado === "Left") pdf.line(X(r.left + meio), Y(r.top), X(r.left + meio), Y(r.bottom));
          else pdf.line(X(r.right - meio), Y(r.top), X(r.right - meio), Y(r.bottom));
          if (estilo === "dotted" || estilo === "dashed") {
            pdf.setLineDashPattern([], 0);
            pdf.setLineCap("butt");
          }
        });
      }

      function imagem(el, cs, r) {
        var dados = imagens[el.src];
        if (!dados || !r.width || !r.height) return;
        var x = r.left, y = r.top, larg = r.width, alt = r.height;
        if (cs.objectFit === "contain" && el.naturalWidth) {
          var e = Math.min(larg / el.naturalWidth, alt / el.naturalHeight);
          x += (larg - el.naturalWidth * e) / 2;
          y += (alt - el.naturalHeight * e) / 2;
          larg = el.naturalWidth * e;
          alt = el.naturalHeight * e;
        }
        pdf.addImage(dados.dados, dados.tipo, X(x), Y(y), mm(larg), mm(alt), dados.nome, "FAST");
      }

      // Os QR Codes: um rectângulo por sequência de módulos escuros, como no
      // <svg> de qrcode.js.
      function qr(el, r) {
        var vb = el.viewBox && el.viewBox.baseVal;
        if (!vb || !vb.width) return;
        var e = r.width / vb.width;
        pdf.setFillColor(0, 0, 0);
        el.querySelectorAll("path").forEach(function (c) {
          var re = /M(\d+) (\d+)h(\d+)/g, m;
          var d = c.getAttribute("d") || "";
          while ((m = re.exec(d))) {
            // Um pouco mais altos, para não se verem riscas entre as linhas.
            pdf.rect(X(r.left + m[1] * e), Y(r.top + m[2] * e), mm(m[3] * e), mm(e) + 0.03, "F");
          }
        });
      }

      // O número ou a bolinha de um item de lista (o ::marker não está no
      // DOM): fica à esquerda do item, na linha de base da primeira linha.
      function marcador(el, cs) {
        var tipo = cs.listStyleType;
        if (tipo === "none" || cs.listStylePosition !== "outside") return;
        var t = "•";
        if (/decimal/.test(tipo)) {
          var lista = el.parentElement;
          var n = lista && lista.tagName === "OL" && lista.hasAttribute("start") ? lista.start : 1;
          for (var irmao = el.previousElementSibling; irmao; irmao = irmao.previousElementSibling) {
            if (irmao.tagName === "LI") n++;
          }
          t = n + ".";
        }
        var andar = doc.createTreeWalker(el, NodeFilter.SHOW_TEXT, {
          acceptNode: function (n) { return /\S/.test(n.data) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP; }
        });
        var primeiro = andar.nextNode();
        if (!primeiro) return;
        var g = doc.createRange();
        g.selectNodeContents(primeiro);
        var linha = g.getClientRects()[0];
        if (!linha) return;
        var f = fonte(w.getComputedStyle(primeiro.parentElement));
        f.estilo = f.nome === "Oswald" ? f.estilo : "normal";
        usar(f);
        var r = el.getBoundingClientRect();
        pdf.text(t, X(r.left) - pdf.getTextWidth(t + " "), Y(linha.top + f.base * f.px));
      }

      function percorrer(el, recorte) {
        var cs = w.getComputedStyle(el);
        if (cs.display === "none" || cs.visibility === "hidden") return;
        var r = el.getBoundingClientRect();
        if (el !== p && cs.overflow !== "visible") {
          recorte = {
            left: Math.max(recorte.left, r.left), right: Math.min(recorte.right, r.right),
            top: Math.max(recorte.top, r.top), bottom: Math.min(recorte.bottom, r.bottom)
          };
        }
        bordas(cs, r);
        if (cs.display === "list-item") marcador(el, cs);
        if (el.dataset && el.dataset.destino) {
          pdf.link(X(r.left), Y(r.top), mm(r.width), mm(r.height), { pageNumber: Number(el.dataset.destino) });
        }
        if (el.dataset && el.dataset.url) {
          pdf.link(X(r.left), Y(r.top), mm(r.width), mm(r.height), { url: el.dataset.url });
        }
        if (el.tagName === "IMG") { if (dentro(r, recorte)) imagem(el, cs, r); return; }
        if (el.tagName.toLowerCase() === "svg") { qr(el, r); return; }
        if (cs.textOverflow === "ellipsis" && el.scrollWidth > el.clientWidth + 1) { reticencias(el, cs, r); return; }
        for (var n = el.firstChild; n; n = n.nextSibling) {
          if (n.nodeType === 1) percorrer(n, recorte);
          else if (n.nodeType === 3 && /\S/.test(n.data)) texto(n, cs, recorte);
        }
      }

      var r0 = p.getBoundingClientRect();
      percorrer(p, { left: r0.left, right: r0.right, top: r0.top, bottom: r0.bottom });
    }

    var cadeia = Promise.resolve();
    paginas.forEach(function (p, i) {
      cadeia = cadeia.then(function () {
        if (i % 5 === 0) estado("A escrever o PDF: página " + (i + 1) + " de " + paginas.length + "…");
        if (i) pdf.addPage("a4", "portrait");
        desenharPagina(p);
        return espera();
      });
    });
    return cadeia.then(function () {
      estado("A guardar o PDF…");
      return espera();
    }).then(function () {
      return { blob: pdf.output("blob"), paginas: paginas.length };
    });
  }

  function descarregar(blob, nome) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = nome;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
  }

  // --- Geração -------------------------------------------------------------

  // Monta o Cantinácio numa moldura escondida e transforma-o num PDF que se
  // descarrega. «opcoes»: { seccoes: [páginas escolhidas], originais,
  // simplificadas, aplausos }.
  function gerar(base, opcoes, estado) {
    var fontes = new URL("../assets/fontes/", base).href;
    var moldura = document.createElement("iframe");
    moldura.setAttribute("aria-hidden", "true");
    moldura.tabIndex = -1;
    moldura.style.cssText = "position:fixed;left:-10000px;top:0;width:240mm;height:600px;border:0;visibility:hidden";
    document.body.appendChild(moldura);
    var w = moldura.contentWindow;
    var doc = w.document;
    var faces = OSWALD.map(function (f) {
      return "@font-face { font-family: Oswald; font-style: normal; font-weight: " + f.peso +
        "; src: url('" + fontes + f.ficheiro + "') format('truetype'); }";
    }).join("\n");
    doc.open();
    doc.write('<!doctype html><html lang="pt"><head><meta charset="utf-8"><title>Cantinácio Virtual</title>' +
      "<style>" + faces + "\n" + ESTILO + '</style></head><body><main id="paginas"></main></body></html>');
    doc.close();

    // As letras têm de estar carregadas antes de medir as colunas.
    var letras = comPrazo(Promise.all(["500 10pt Oswald", "600 10pt Oswald"].map(function (f) {
      return doc.fonts.load(f).catch(function () { return null; });
    })), 8000);
    var oswald = Promise.all(OSWALD.map(function (f) {
      return bytes(fontes + f.ficheiro).then(function (b) {
        return { ficheiro: f.ficheiro, estilo: f.estilo, dados: base64(b) };
      });
    }));

    var seccoes = SECCOES.filter(function (s) {
      if (s.pagina === "Aplausos") return opcoes.aplausos;
      return ESCOLHAS.indexOf(s.pagina) < 0 || opcoes.seccoes.indexOf(s.pagina) >= 0;
    });

    estado("A ler as músicas do Wikinácios…");
    return Promise.all([carregarJsPdf(), oswald, letras].concat(seccoes.map(function (s) {
      return ler(Object.assign({}, s), base, opcoes);
    }))).then(function (r) {
      var JsPdf = r[0], fontesPdf = r[1];
      return montar(w, r.slice(3), base, estado).then(function () {
        estado("A juntar as imagens…");
        return lerImagens(doc);
      }).then(function (imagens) {
        return paraPdf(JsPdf, w, fontesPdf, imagens, estado);
      });
    }).then(function (feito) {
      descarregar(feito.blob, "Cantinácio Virtual " + hoje().replace(/\//g, "-") + ".pdf");
      return feito;
    }).finally(function () {
      moldura.remove();
    });
  }

  // --- Configuração --------------------------------------------------------

  function caixa(nome, valor, rotulo) {
    return '<label class="wk-cv__opcao"><input type="checkbox" name="' + nome + '" value="' + valor +
      '" checked> ' + rotulo + "</label>";
  }

  var dialogo = null;
  var emCurso = null;  // a geração em curso: { cancelada }

  function configuracao(base) {
    if (!dialogo || !document.body.contains(dialogo)) {
      dialogo = document.createElement("dialog");
      dialogo.className = "wk-cv";
      dialogo.setAttribute("aria-labelledby", "wk-cv-titulo");
      dialogo.innerHTML =
        '<form class="wk-cv__caixa md-typeset" method="dialog">' +
        '<button type="button" class="wk-cv__fechar" aria-label="Fechar">×</button>' +
        '<h2 id="wk-cv-titulo">Configuração do Cantinácio</h2>' +
        "<fieldset><legend>Deve ter músicas de:</legend>" +
        ESCOLHAS.map(function (s) { return caixa("seccao", s, s); }).join("") +
        "</fieldset>" +
        '<fieldset><legend class="wk-cv__escondido">Versões e Aplausos</legend>' +
        caixa("originais", "1", "Mostrar versões originais") +
        caixa("simplificadas", "1", "Mostrar versões simplificadas (Cantinácio 2019)") +
        caixa("aplausos", "1", "Incluir Aplausos") +
        "</fieldset>" +
        '<button type="submit" class="md-button md-button--primary wk-cv__gerar">Gerar o meu Cantinácio Virtual!</button>' +
        '<p class="wk-cv__estado" role="status" aria-live="polite"></p>' +
        "</form>";
      document.body.appendChild(dialogo);

      var form = dialogo.querySelector("form");
      var estadoEl = dialogo.querySelector(".wk-cv__estado");
      var gerarEl = dialogo.querySelector(".wk-cv__gerar");
      dialogo.querySelector('[name="originais"]').closest("label").title =
        "Nas músicas com duas versões, a que o Wikinácios já tinha";
      dialogo.querySelector('[name="simplificadas"]').closest("label").title =
        "Nas músicas com duas versões, a do Cantinácio de 2019";

      var escolhidas = function () {
        return Array.prototype.slice.call(form.querySelectorAll('[name="seccao"]:checked'))
          .map(function (c) { return c.value; });
      };
      var validar = function () {
        if (emCurso) return;
        var falta = !escolhidas().length ? "Escolha pelo menos uma secção de músicas." :
          !form.originais.checked && !form.simplificadas.checked ? "Escolha pelo menos uma das versões." : "";
        gerarEl.disabled = !!falta;
        estadoEl.textContent = falta;
      };
      form.addEventListener("change", validar);

      var fechar = function () { dialogo.close(); };
      dialogo.querySelector(".wk-cv__fechar").addEventListener("click", fechar);
      dialogo.addEventListener("click", function (ev) { if (ev.target === dialogo) fechar(); });
      dialogo.addEventListener("close", function () {
        if (emCurso) emCurso.cancelada = true;
      });

      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        if (emCurso || gerarEl.disabled) return;
        var esta = emCurso = { cancelada: false };
        var opcoes = {
          seccoes: escolhidas(),
          originais: form.originais.checked,
          simplificadas: form.simplificadas.checked,
          aplausos: form.aplausos.checked
        };
        var campos = form.querySelectorAll("input, .wk-cv__gerar");
        campos.forEach(function (c) { c.disabled = true; });
        dialogo.classList.add("wk-cv--a-gerar");
        var estado = function (t) {
          if (esta.cancelada) throw new Error("cancelado");
          estadoEl.textContent = t;
        };
        gerar(dialogo.dataset.base, opcoes, estado).then(function (feito) {
          if (!esta.cancelada) estadoEl.textContent = "Pronto! O PDF, com " + feito.paginas + " páginas, foi descarregado.";
        }).catch(function (e) {
          if (!esta.cancelada) estadoEl.textContent = "Não foi possível gerar o Cantinácio (" + e.message + ").";
        }).finally(function () {
          emCurso = null;
          dialogo.classList.remove("wk-cv--a-gerar");
          campos.forEach(function (c) { c.disabled = false; });
          if (esta.cancelada) validar();
        });
      });
      dialogo.validar = validar;
    }
    dialogo.dataset.base = base;
    if (!emCurso) dialogo.validar();
    if (!dialogo.open) dialogo.showModal();
  }

  function iniciar() {
    document.querySelectorAll(".wk-cantinacio-imprimir").forEach(function (b) {
      if (b.dataset.pronto) return;
      b.dataset.pronto = "1";
      b.addEventListener("click", function (ev) {
        ev.preventDefault();
        configuracao(window.location.href);
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
