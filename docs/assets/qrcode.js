// Gerador de QR Codes (modo de bytes, correcção de erros M ou L, versões 1 a
// 10) sem dependências, para os endereços dos vídeos do Cantinácio impresso
// (docs/assets/cantinacio-imprimir.js). Segue a norma ISO/IEC 18004.
//
// Uso: WkQR.svg("https://…") devolve o texto de um <svg> com o código.
(function () {
  "use strict";

  var MAX_VERSAO = 10;

  // Por versão (1 a 10): palavras de correcção por bloco e número de blocos.
  var CORRECCAO = {
    M: { bits: 0, porBloco: [10, 16, 26, 18, 24, 16, 18, 22, 22, 26], blocos: [1, 1, 1, 2, 2, 4, 4, 4, 5, 5] },
    L: { bits: 1, porBloco: [7, 10, 15, 20, 26, 18, 20, 24, 30, 18], blocos: [1, 1, 1, 1, 1, 2, 2, 2, 2, 4] }
  };

  function bit(n, i) { return (n >>> i) & 1; }

  function modulosDeDados(versao) {
    var r = (16 * versao + 128) * versao + 64;
    if (versao >= 2) {
      var n = Math.floor(versao / 7) + 2;
      r -= (25 * n - 10) * n - 55;
      if (versao >= 7) r -= 36;
    }
    return r;
  }

  function posicoesDeAlinhamento(versao) {
    if (versao === 1) return [];
    var n = Math.floor(versao / 7) + 2;
    var passo = Math.floor((versao * 8 + n * 3 + 5) / (n * 4 - 4)) * 2;
    var tam = versao * 4 + 17;
    var r = [6];
    for (var pos = tam - 7; r.length < n; pos -= passo) r.splice(1, 0, pos);
    return r;
  }

  // --- Reed-Solomon sobre GF(256) -------------------------------------------

  function multiplicar(x, y) {
    var z = 0;
    for (var i = 7; i >= 0; i--) {
      z = (z << 1) ^ ((z >>> 7) * 0x11D);
      z ^= ((y >>> i) & 1) * x;
    }
    return z;
  }

  function divisor(grau) {
    var r = [];
    for (var i = 0; i < grau - 1; i++) r.push(0);
    r.push(1);
    var raiz = 1;
    for (i = 0; i < grau; i++) {
      for (var j = 0; j < r.length; j++) {
        r[j] = multiplicar(r[j], raiz);
        if (j + 1 < r.length) r[j] ^= r[j + 1];
      }
      raiz = multiplicar(raiz, 2);
    }
    return r;
  }

  function resto(dados, div) {
    var r = div.map(function () { return 0; });
    dados.forEach(function (b) {
      var f = b ^ r.shift();
      r.push(0);
      div.forEach(function (c, i) { r[i] ^= multiplicar(c, f); });
    });
    return r;
  }

  // --- Dados ----------------------------------------------------------------

  function codificar(bytes, versao, nivel) {
    var c = CORRECCAO[nivel];
    var capacidade = Math.floor(modulosDeDados(versao) / 8) - c.porBloco[versao - 1] * c.blocos[versao - 1];
    var bits = [];
    function juntar(valor, n) { for (var i = n - 1; i >= 0; i--) bits.push(bit(valor, i)); }
    juntar(4, 4);                              // modo: bytes
    juntar(bytes.length, versao < 10 ? 8 : 16);
    bytes.forEach(function (b) { juntar(b, 8); });
    juntar(0, Math.min(4, capacidade * 8 - bits.length));
    while (bits.length % 8) bits.push(0);
    var palavras = [];
    for (var i = 0; i < bits.length; i += 8) {
      var p = 0;
      for (var j = 0; j < 8; j++) p = (p << 1) | bits[i + j];
      palavras.push(p);
    }
    for (var pad = 0xEC; palavras.length < capacidade; pad ^= 0xEC ^ 0x11) palavras.push(pad);
    return palavras;
  }

  function comCorreccao(dados, versao, nivel) {
    var c = CORRECCAO[nivel];
    var nBlocos = c.blocos[versao - 1];
    var ecc = c.porBloco[versao - 1];
    var total = Math.floor(modulosDeDados(versao) / 8);
    var curtos = nBlocos - total % nBlocos;
    var tamCurto = Math.floor(total / nBlocos);
    var div = divisor(ecc);
    var blocos = [];
    for (var i = 0, k = 0; i < nBlocos; i++) {
      var d = dados.slice(k, k + tamCurto - ecc + (i < curtos ? 0 : 1));
      k += d.length;
      var e = resto(d, div);
      if (i < curtos) d.push(0);
      blocos.push(d.concat(e));
    }
    var r = [];
    for (i = 0; i < blocos[0].length; i++) {
      blocos.forEach(function (b, j) {
        if (i !== tamCurto - ecc || j >= curtos) r.push(b[i]);
      });
    }
    return r;
  }

  // --- Matriz ---------------------------------------------------------------

  function novaMatriz(versao, nivel) {
    var mat = { versao: versao, nivel: nivel, tam: versao * 4 + 17, m: [], fixo: [] };
    for (var y = 0; y < mat.tam; y++) {
      mat.m.push([]);
      mat.fixo.push([]);
      for (var x = 0; x < mat.tam; x++) { mat.m[y].push(false); mat.fixo[y].push(false); }
    }
    return mat;
  }

  function pôr(mat, x, y, escuro) {
    mat.m[y][x] = escuro;
    mat.fixo[y][x] = true;
  }

  function desenharFuncoes(mat) {
    var tam = mat.tam, i;
    for (i = 0; i < tam; i++) {
      pôr(mat, 6, i, i % 2 === 0);
      pôr(mat, i, 6, i % 2 === 0);
    }
    function localizador(cx, cy) {
      for (var dy = -4; dy <= 4; dy++) {
        for (var dx = -4; dx <= 4; dx++) {
          var d = Math.max(Math.abs(dx), Math.abs(dy));
          var x = cx + dx, y = cy + dy;
          if (x >= 0 && x < tam && y >= 0 && y < tam) pôr(mat, x, y, d !== 2 && d !== 4);
        }
      }
    }
    localizador(3, 3);
    localizador(tam - 4, 3);
    localizador(3, tam - 4);
    var pos = posicoesDeAlinhamento(mat.versao);
    var ultimo = pos.length - 1;
    pos.forEach(function (cy, a) {
      pos.forEach(function (cx, b) {
        if ((a === 0 && b === 0) || (a === 0 && b === ultimo) || (a === ultimo && b === 0)) return;
        for (var dy = -2; dy <= 2; dy++) {
          for (var dx = -2; dx <= 2; dx++) pôr(mat, cx + dx, cy + dy, Math.max(Math.abs(dx), Math.abs(dy)) !== 1);
        }
      });
    });
    desenharFormato(mat, 0);
    if (mat.versao >= 7) {
      var r = mat.versao;
      for (i = 0; i < 12; i++) r = (r << 1) ^ ((r >>> 11) * 0x1F25);
      var bits = (mat.versao << 12) | r;
      for (i = 0; i < 18; i++) {
        var a = tam - 11 + i % 3, b = Math.floor(i / 3);
        pôr(mat, a, b, bit(bits, i) === 1);
        pôr(mat, b, a, bit(bits, i) === 1);
      }
    }
  }

  function desenharFormato(mat, mascara) {
    var tam = mat.tam, i;
    var dados = (CORRECCAO[mat.nivel].bits << 3) | mascara;
    var r = dados;
    for (i = 0; i < 10; i++) r = (r << 1) ^ ((r >>> 9) * 0x537);
    var bits = ((dados << 10) | r) ^ 0x5412;
    for (i = 0; i <= 5; i++) pôr(mat, 8, i, bit(bits, i) === 1);
    pôr(mat, 8, 7, bit(bits, 6) === 1);
    pôr(mat, 8, 8, bit(bits, 7) === 1);
    pôr(mat, 7, 8, bit(bits, 8) === 1);
    for (i = 9; i < 15; i++) pôr(mat, 14 - i, 8, bit(bits, i) === 1);
    for (i = 0; i < 8; i++) pôr(mat, tam - 1 - i, 8, bit(bits, i) === 1);
    for (i = 8; i < 15; i++) pôr(mat, 8, tam - 15 + i, bit(bits, i) === 1);
    pôr(mat, 8, tam - 8, true);
  }

  function desenharPalavras(mat, palavras) {
    var tam = mat.tam, i = 0;
    for (var direita = tam - 1; direita >= 1; direita -= 2) {
      if (direita === 6) direita = 5;
      for (var vert = 0; vert < tam; vert++) {
        for (var j = 0; j < 2; j++) {
          var x = direita - j;
          var y = ((direita + 1) & 2) === 0 ? tam - 1 - vert : vert;
          if (!mat.fixo[y][x] && i < palavras.length * 8) {
            mat.m[y][x] = bit(palavras[i >>> 3], 7 - (i & 7)) === 1;
            i++;
          }
        }
      }
    }
  }

  var MASCARAS = [
    function (x, y) { return (x + y) % 2 === 0; },
    function (x, y) { return y % 2 === 0; },
    function (x, y) { return x % 3 === 0; },
    function (x, y) { return (x + y) % 3 === 0; },
    function (x, y) { return (Math.floor(x / 3) + Math.floor(y / 2)) % 2 === 0; },
    function (x, y) { return x * y % 2 + x * y % 3 === 0; },
    function (x, y) { return (x * y % 2 + x * y % 3) % 2 === 0; },
    function (x, y) { return ((x + y) % 2 + x * y % 3) % 2 === 0; }
  ];

  function mascarar(mat, mascara) {
    for (var y = 0; y < mat.tam; y++) {
      for (var x = 0; x < mat.tam; x++) {
        if (!mat.fixo[y][x] && MASCARAS[mascara](x, y)) mat.m[y][x] = !mat.m[y][x];
      }
    }
  }

  function penalidade(mat) {
    var tam = mat.tam, m = mat.m, total = 0, escuros = 0, x, y, i;
    function linha(get) {
      var s = 0, cor = false, corrida = 0, historia = [];
      for (var k = 0; k < tam; k++) {
        var v = get(k);
        if (v === cor) {
          corrida++;
          if (corrida === 5) s += 3; else if (corrida > 5) s++;
        } else { cor = v; corrida = 1; }
        historia.push(v ? 1 : 0);
      }
      // Padrão 1:1:3:1:1 com quatro módulos claros de um dos lados.
      var txt = historia.join("");
      var re = /(?=(00001011101|10111010000))/g, f;
      while ((f = re.exec(txt))) { s += 40; re.lastIndex = f.index + 1; }
      return s;
    }
    for (y = 0; y < tam; y++) total += linha(function (k) { return m[y][k]; });
    for (x = 0; x < tam; x++) total += linha(function (k) { return m[k][x]; });
    for (y = 0; y < tam - 1; y++) {
      for (x = 0; x < tam - 1; x++) {
        if (m[y][x] === m[y][x + 1] && m[y][x] === m[y + 1][x] && m[y][x] === m[y + 1][x + 1]) total += 3;
      }
    }
    for (y = 0; y < tam; y++) for (x = 0; x < tam; x++) if (m[y][x]) escuros++;
    var n = tam * tam;
    for (i = Math.ceil(Math.abs(escuros * 20 - n * 10) / n) - 1; i > 0; i--) total += 10;
    return total;
  }

  // --- Interface --------------------------------------------------------------

  function utf8(texto) {
    return Array.prototype.slice.call(new TextEncoder().encode(texto));
  }

  // Devolve a matriz de módulos (true = escuro) do código para o texto.
  function gerar(texto) {
    var bytes = utf8(texto), nivel, versao;
    var niveis = ["M", "L"];
    escolher:
    for (var n = 0; n < niveis.length; n++) {
      for (var v = 1; v <= MAX_VERSAO; v++) {
        var c = CORRECCAO[niveis[n]];
        var capacidade = Math.floor(modulosDeDados(v) / 8) - c.porBloco[v - 1] * c.blocos[v - 1];
        if (4 + (v < 10 ? 8 : 16) + bytes.length * 8 <= capacidade * 8) {
          nivel = niveis[n];
          versao = v;
          break escolher;
        }
      }
    }
    if (!nivel) throw new Error("Endereço demasiado comprido para o QR Code");

    var palavras = comCorreccao(codificar(bytes, versao, nivel), versao, nivel);
    var melhor = null, melhorNota = Infinity;
    for (var mascara = 0; mascara < 8; mascara++) {
      var mat = novaMatriz(versao, nivel);
      desenharFuncoes(mat);
      desenharPalavras(mat, palavras);
      mascarar(mat, mascara);
      desenharFormato(mat, mascara);
      var nota = penalidade(mat);
      if (nota < melhorNota) { melhor = mat; melhorNota = nota; }
    }
    return melhor.m;
  }

  // O código como <svg> (um rectângulo por sequência de módulos escuros), com
  // uma margem de «margem» módulos.
  function svg(texto, margem) {
    var m = gerar(texto);
    margem = margem == null ? 2 : margem;
    var tam = m.length + margem * 2;
    var caminho = "";
    m.forEach(function (linha, y) {
      for (var x = 0; x < linha.length; x++) {
        if (!linha[x]) continue;
        var ini = x;
        while (x + 1 < linha.length && linha[x + 1]) x++;
        caminho += "M" + (ini + margem) + " " + (y + margem) + "h" + (x - ini + 1) + "v1h-" + (x - ini + 1) + "z";
      }
    });
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + tam + " " + tam +
      '" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="#fff"/>' +
      '<path d="' + caminho + '" fill="#000"/></svg>';
  }

  window.WkQR = { gerar: gerar, svg: svg };
})();
