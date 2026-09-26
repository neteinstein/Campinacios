#!/usr/bin/env python3
"""Convert the Wikinácios MediaWiki MySQL dump into the Markdown site in docs/.

Every wiki page becomes a Markdown file, filed into a folder by what it is
(camps by year, people by initial, ...), with relative links between pages so
the result can be browsed on GitHub, built with MkDocs (see mkdocs.yml) or
opened as an Obsidian vault. The old home page becomes docs/index.md, with
the layout it had on the wiki, and a plain version of it the README.md.

Usage:
    pip install ftfy cryptography mkdocs-material
    WIKINACIOS_PALAVRA_PASSE=... python3 scripts/mediawiki_to_markdown.py <dump>

Only the latest revision of each page is exported. Pages that were
restricted on the wiki (see PRIVATE_CATEGORIES) are encrypted with the
password (see scripts/restrito.py); without one they are left out. User
accounts, password hashes, logs, deleted pages and old revisions are always
left out.
"""
import datetime
import getpass
import json
import os
import posixpath
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

import ftfy

import restrito

# --------------------------------------------------------------------------
# mysqldump parsing
# --------------------------------------------------------------------------

_ESCAPES = {ord('0'): b'\0', ord('n'): b'\n', ord('r'): b'\r', ord('t'): b'\t',
            ord('Z'): b'\x1a', ord('b'): b'\b'}
_BARE_VALUE = re.compile(rb"[^,)]*")


def _parse_values(buf, i):
    """Parse `(...),(...);` tuples starting at buf[i]. Strings stay bytes."""
    rows, n = [], len(buf)
    while i < n:
        c = buf[i]
        if c == ord('('):
            i += 1
            row = []
            while True:
                if buf[i] == ord("'"):
                    i += 1
                    out = bytearray()
                    while True:
                        c = buf[i]
                        if c == ord('\\'):
                            out += _ESCAPES.get(buf[i + 1], bytes([buf[i + 1]]))
                            i += 2
                        elif c == ord("'"):
                            if i + 1 < n and buf[i + 1] == ord("'"):
                                out += b"'"
                                i += 2
                            else:
                                i += 1
                                break
                        else:
                            out.append(c)
                            i += 1
                    row.append(bytes(out))
                else:
                    m = _BARE_VALUE.match(buf, i)
                    tok = m.group().strip()
                    i = m.end()
                    row.append(None if tok == b'NULL' else tok.decode())
                if buf[i] == ord(','):
                    i += 1
                    continue
                i += 1  # ')'
                break
            rows.append(row)
        elif c == ord(';'):
            return rows
        else:
            i += 1
    return rows


def load_tables(path, tables):
    data = {t: [] for t in tables}
    buf = Path(path).read_bytes()
    for m in re.finditer(rb"INSERT INTO `(\w+)` VALUES ", buf):
        name = m.group(1).decode()
        if name in data:
            data[name] += _parse_values(buf, m.end())
    return data


# --------------------------------------------------------------------------
# Text encoding repair
# --------------------------------------------------------------------------
# The wiki stored UTF-8 in latin1 columns, and several pages were saved after
# being mis-decoded once or twice (mojibake such as "DirecÃ§Ã£o"). ftfy undoes
# that. Bytes that cp1252 cannot represent were lost as U+FFFD; the common
# cases are restored from context.

_FTFY = ftfy.TextFixerConfig(uncurl_quotes=False)
_LOST_BYTES = [
    ('CAMPIN�CIOS', 'CAMPINÁCIOS'), ('CAP�TULO', 'CAPÍTULO'),
    ('�NDICE', 'ÍNDICE'), ('�gua', 'Água'), ('�dolo', 'Ídolo'),
    ('�reas', 'Áreas'), ('�lvares', 'Álvares'),
    ('�', '”'),  # the remaining ones all close a “quotation
]


def decode(raw):
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        text = raw.decode('cp1252', errors='replace')
    text = ftfy.fix_text(text, _FTFY)
    for bad, good in _LOST_BYTES:
        text = text.replace(bad, good)
    return text


# --------------------------------------------------------------------------
# Titles and namespaces
# --------------------------------------------------------------------------

NS_ALIASES = {
    'discussão': 1, 'talk': 1,
    'utilizador': 2, 'usuário': 2, 'usuario': 2, 'user': 2,
    'utilizador discussão': 3, 'usuário discussão': 3, 'user talk': 3,
    'wikinacios': 4, 'wikinácios': 4, 'project': 4, 'wiki @ campinácios': 4,
    'imagem': 6, 'image': 6, 'ficheiro': 6, 'arquivo': 6, 'file': 6,
    'media': 6,
    'predefinição': 10, 'template': 10, 'ajuda': 12, 'help': 12,
    'categoria': 14, 'category': 14,
    'especial': -1, 'special': -1,
}
CATEGORY_NS, IMAGE_NS, TEMPLATE_NS = 14, 6, 10

# Pages in these categories were access-restricted on the wiki (the camp-site
# pages hold directions and private phone numbers of land owners); they are
# published encrypted.
PRIVATE_CATEGORIES = {'Restrita', 'Locais de Acampamento'}
# MediaWiki's own "successfully installed" page, never part of the wiki.
SKIP_PAGES = {(0, 'Main Page')}
# [[Especial:...]] pages that have a counterpart on the site.
SPECIAL_PAGES = {'allpages': 'todos', 'newpages': 'todos',
                 'whatlinkshere': 'backlinks'}
BACKLINKS = 'Páginas que ligam para aqui'
LOCK = ' 🔒'

CAMP_CATEGORIES = {'Acampamentos', 'Triciclos', 'Trotinetas', 'Bicicletas',
                   'Lambretas', 'Calhambeques', 'Formação de Animadores',
                   'Pré-Acampamentos'}
MODALITIES = ['Triciclos', 'Trotinetas', 'Bicicletas', 'Lambretas',
              'Calhambeques', 'Formação de Animadores', 'Pré-Acampamentos']
PEOPLE_CATEGORIES = {'Animadores', 'Animadores do CAIC', 'Animadores do CC',
                     'Animadores do CSJB', 'Jesuítas', 'Assistentes Nacionais',
                     'Coordenadores Nacionais', 'Secretários da DN',
                     'Coordenador Local do CAIC', 'Coordenador Local do CSJB',
                     'Direcção Nacional', 'Direcção Local do CAIC',
                     'Direcção Local do CC', 'Direcção Local do CSJB'}
ORGAN_TITLE = re.compile(r'^(Direc|Coordenador|Secretári|Assistente|DL-|CAIC$'
                         r'|CC$|CSJB$)')
ENCONTRO_CATEGORIES = {'Encontros Nacionais',
                       'Encontros Nacionais de Animadores'}

FOLDER_INTROS = {
    'Acampamentos': 'Acampamentos dos Campinácios, organizados por ano.',
    'Pessoas': 'Animadores, jesuítas e outras pessoas do movimento, por '
               'ordem alfabética.',
    'Encontros': 'Encontros Nacionais e Encontros Nacionais de Animadores.',
    'Cargos': 'Os cargos das equipas de animação.',
    'Movimento': 'História, organização, colégios, manuais e outros artigos '
                 'sobre o movimento.',
    'Categorias': 'As categorias da Wikinácios.',
    'Wikinácios': 'Páginas sobre a própria wiki: ajuda, políticas, '
                  'predefinições, imagens e discussões. Ver também '
                  '[Sobre este arquivo](Sobre%20este%20arquivo.md).',
    'Restrito': 'Páginas que na wiki eram de acesso restrito (Direcção '
                'Nacional e Directores). O conteúdo das páginas marcadas com '
                '🔒 está cifrado e só pode ser lido com a palavra-passe.',
}


SITE_URL = 'https://neteinstein.github.io/Campinacios/'
ABOUT_PAGE = 'docs/Wikinácios/Sobre este arquivo.md'
ALL_PAGES = 'docs/Todos os artigos.md'
ABOUT_TEXT = '''# Sobre este arquivo

A Wikinácios foi a wiki dos Campinácios, criada em 2009 durante a
Revolução Campinácios v2.0 e mantida em MediaWiki. Este site foi gerado a
partir da cópia de segurança da base de dados MySQL da wiki pelo script
`scripts/mediawiki_to_markdown.py`.

## O que foi convertido

- A versão mais recente de cada página, em Markdown (as restritas cifradas,
  ver abaixo).
- Os redireccionamentos foram resolvidos: as ligações apontam directamente
  para a página de destino, e os nomes alternativos ficam em *Outros nomes*,
  no fim de cada página.
- As categorias têm uma página própria com a lista dos seus membros, e cada
  página mostra, no fim, as páginas que ligam para ela e uma tabela com as
  suas categorias.
- As páginas estão organizadas por pastas: acampamentos por ano, pessoas
  por inicial, encontros, cargos, movimento, categorias e as páginas sobre
  a própria wiki. [Todos os artigos](../Todos%20os%20artigos.md) lista-as
  todas, com os nomes alternativos.
- A página principal mantém a disposição que tinha na wiki.

## Páginas restritas

As páginas que na wiki eram de acesso restrito (categoria *Restrita*) e as
fichas dos [locais de acampamento](../Restrito/index.md), reservadas à
Direcção Nacional e aos directores, estão no site mas cifradas (AES-256):
o texto só aparece depois de se introduzir a palavra-passe, e nem o
repositório nem o site guardam o texto em claro. A palavra-passe fica
guardada no navegador até se fechar o separador, ou no dispositivo se se
escolher "Lembrar neste dispositivo".

Para mudar a palavra-passe, ou para editar uma página restrita:

```sh
pip install cryptography mkdocs-material
python3 scripts/restrito.py mudar-palavra-passe
python3 scripts/restrito.py abrir    # decifra para restrito-aberto/
python3 scripts/restrito.py fechar   # volta a cifrar e apaga restrito-aberto/
```

A segurança depende só da palavra-passe: quem tiver uma cópia do site pode
tentar adivinhá-la sem limite, por isso deve ser longa e aleatória.

## O que ficou de fora

- Contas de utilizador, palavras-passe, registos, páginas apagadas e o
  histórico de revisões, incluindo o autor e a data da última edição de
  cada página.
- A página "Main Page", que era a página de instalação do MediaWiki.
- As imagens: o backup só tem a base de dados, por isso as páginas das
  imagens mostram apenas a descrição e os dados do ficheiro original.

## Como editar e publicar

Os ficheiros Markdown em `docs/` são agora a fonte do site e podem ser
editados directamente no GitHub: ver
[Como adicionar conteúdo?](Ajuda/Conte%C3%BAdos.md#como-adicionar-conteúdo).
O site é construído com
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/) e publicado
no GitHub Pages pela GitHub Action em `.github/workflows/pages.yml` a cada
alteração no ramo `main`.

Em *Settings → Pages → Build and deployment*, a *Source* tem de ser
**GitHub Actions**. Com *Deploy from a branch*, o GitHub publica também uma
versão Jekyll do repositório que substitui este site, com outra página
principal e ligações partidas.

Para ver o site localmente:

```sh
pip install mkdocs-material
mkdocs serve
```

A pasta `docs/` também pode ser aberta como cofre no
[Obsidian](https://obsidian.md/), que mostra o grafo de ligações entre as
páginas.
'''
# Replaces the MediaWiki instructions of Ajuda:Conteúdos (from this heading on)
HELP_PAGE = (12, 'Conteúdos')
HELP_SECTION = '## Como adicionar conteúdo?'
HELP_TEXT = '''## Como adicionar conteúdo?

A Wikinácios já não corre em MediaWiki: é um site feito a partir dos
ficheiros do repositório
[neteinstein/Campinacios](https://github.com/neteinstein/Campinacios) no
GitHub. Cada artigo é um ficheiro de texto `.md`
([Markdown](https://docs.github.com/pt/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax))
dentro da pasta `docs/`, e o site actualiza-se sozinho um ou dois minutos
depois de cada alteração entrar no ramo `main`.

Para editar é preciso uma conta no GitHub, que é gratuita. Quem tem
permissão de escrita no repositório (o [Staff](../../Movimento/Staff.md))
grava as alterações directamente. Os outros fazem uma proposta de alteração
(*pull request*) que o Staff revê e aceita: as regras acima continuam a
valer.

### Como se edita um artigo?

1. Abra o artigo no site e carregue no lápis (*Editar esta página*) no
   canto superior direito. Abre-se o ficheiro no GitHub, já em modo de
   edição (se pedir, carregue em *Fork this repository*).
2. Faça as alterações. O separador *Preview* mostra como vai ficar.
3. Carregue em **Commit changes...**, escreva numa frase o que mudou e
   confirme. Sem permissão de escrita, o botão chama-se
   **Propose changes** e, a seguir, **Create pull request**.

### Como se adiciona um artigo?

Antes de mais é preciso saber se o artigo já existe: use a caixa
**Buscar** no topo do site ou [Todos os artigos](../../Todos%20os%20artigos.md),
que também lista as alcunhas e os nomes alternativos.

Se não existir, entre no GitHub na pasta certa dentro de `docs/`:

| Artigo | Pasta |
| --- | --- |
| Acampamento | `docs/Acampamentos/<ano>/` |
| Animador, jesuíta ou outra pessoa | `docs/Pessoas/<inicial>/` |
| Encontro | `docs/Encontros/` |
| Cargo | `docs/Cargos/` |
| Tudo o resto | `docs/Movimento/` |

Carregue em **Add file → Create new file** e dê ao ficheiro o nome do
artigo terminado em `.md`, por exemplo `Carlos Nunes.md`. Copie um artigo
do mesmo tipo (regra 2) e altere os dados, não o esquema. O ficheiro começa
por um cabeçalho com o título:

```markdown
---
title: "Carlos Nunes"
---

# Carlos Nunes

Carlos Nunes é animador dos Campinácios desde...
```

Grave como acima (**Commit changes...** ou **Propose changes**). Por fim,
ponha ligações para o artigo novo: no `index.md` da pasta, na página da
categoria em `docs/Categorias/` e nos artigos que falam dele. Estas listas
não se actualizam sozinhas, mas a pesquisa do site encontra-o logo.

### Como se escreve?

| Na wiki | Agora, em Markdown |
| --- | --- |
| `\'\'\'negrito\'\'\'` | `**negrito**` |
| `''itálico''` | `*itálico*` |
| `== Secção ==` | `## Secção` |
| `* item` | `- item` |
| `[[Pedro Vicente]]` | `[Pedro Vicente](<../../Pessoas/P/Pedro Vicente.md>)` |
| `[http://exemplo.pt texto]` | `[texto](http://exemplo.pt)` |

As ligações entre artigos levam o caminho do ficheiro a partir da pasta do
artigo onde se escreve: `../` sobe uma pasta. Com os `< >` à volta, o
caminho pode ter espaços e acentos. Se uma ligação apontar para um ficheiro
que não existe, a publicação falha (o GitHub mostra um ✗ vermelho no
*commit* e avisa por e-mail) e o site fica como estava até se corrigir.

Para uma imagem, carregue o ficheiro com **Add file → Upload files** para
`docs/assets/imagens/` e escreva
`![legenda](<../../assets/imagens/foto.jpg>)`, com o caminho a partir do
artigo.

### Como se cria uma categoria?

Uma categoria é uma página em `docs/Categorias/` com a lista dos seus
artigos, como [Animadores](../../Categorias/Animadores.md). Crie o ficheiro
com essa lista e, no fim de cada artigo da categoria, acrescente-a à linha
**Categorias:**.

### Como se cria uma subcategoria de uma categoria?

Na página da categoria-mãe, acrescente a subcategoria à secção
*Subcategorias*.

### E as páginas restritas?

Estão cifradas e não se editam no GitHub. Ver
[Sobre este arquivo](../Sobre%20este%20arquivo.md#páginas-restritas).
'''
GRAPH_TEXT = '''# Grafo de ligações

Cada ponto é um artigo e cada linha uma ligação entre dois artigos. Passe
o cursor por cima de um ponto para ver o nome, clique para abrir o artigo,
arraste para mover e use a roda do rato para aproximar.

<div class="wiki-graph" data-src="assets/graph.json"></div>
'''


def normalize_title(title):
    title = re.sub(r'[\s_]+', ' ', title).strip()
    return title[:1].upper() + title[1:]


def parse_target(target):
    """'Category:Foo_bar#x' -> (14, 'Foo bar', 'x')."""
    target = target.strip()
    anchor = ''
    if '#' in target:
        target, anchor = target.split('#', 1)
    ns = 0
    if ':' in target:
        prefix, rest = target.split(':', 1)
        key = re.sub(r'[\s_]+', ' ', prefix).strip().lower()
        if key in NS_ALIASES:
            ns, target = NS_ALIASES[key], rest
    return ns, normalize_title(target), anchor.strip()


_UNSAFE = str.maketrans({'/': '-', '\\': '-', ':': ' -', '*': '', '?': '',
                         '"': '', '<': '', '>': '', '|': '-', '#': '',
                         '^': '', '[': '(', ']': ')'})


def safe_name(title):
    return re.sub(r'\s+', ' ', title.translate(_UNSAFE)).strip()


def initial(title):
    ch = unicodedata.normalize('NFKD', title)[:1].upper()
    return ch if 'A' <= ch <= 'Z' else 'Outros'


def slugify(text):
    """Heading anchor, as GitHub and pymdownx.slugs (case=lower) make it."""
    text = re.sub(r'<[^>]+>|[*`]', '', text).strip().lower()
    text = re.sub(r'[^\w\- ]', '', text)
    return text.replace(' ', '-')


# --------------------------------------------------------------------------
# Wikitext -> Markdown
# --------------------------------------------------------------------------
# Links are emitted as placeholders, since where a page lands (and therefore
# the relative path to it) is only known once every page has been converted.

# Private-use characters, so str.split()/strip() never touch them.
LINK = re.compile('\ue000(-?\\d+)\ue001([^\ue001]*)\ue001([^\ue001]*)'
                  '\ue001([^\ue002]*)\ue002')


def link_token(ns, title, anchor, label):
    return f'\ue000{ns}\ue001{title}\ue001{anchor}\ue001{label}\ue002'


# List tags inside table cells, kept out of convert_html_lists' way until
# the end of the conversion.
CELL_TAGS = {'ul': ('\ue010', '\ue011'), 'ol': ('\ue012', '\ue013'),
             'li': ('\ue014', '\ue015')}


class Converter:
    def __init__(self, templates, article_count):
        self.templates = templates      # title -> wikitext
        self.article_count = article_count

    # ---- links -----------------------------------------------------------

    def image_link(self, name, caption):
        name = normalize_title(name)
        return link_token(IMAGE_NS, name, '', '🖼️ ' + (caption or name))

    def convert_link(self, m, categories):
        inner, trail = m.group(1), m.group(2) or ''
        parts = self.split_pipes(inner)
        raw_target = parts[0].strip()
        leading_colon = raw_target.startswith(':')
        ns, title, anchor = parse_target(raw_target.lstrip(':'))
        label = parts[-1].strip() if len(parts) > 1 else None
        if label:
            label = self.plain(label)

        if ns == CATEGORY_NS and not leading_colon:
            categories.append(title)
            return ''
        if ns == IMAGE_NS and not leading_colon:
            caption = next((p.strip() for p in reversed(parts[1:])
                            if not re.fullmatch(
                                r'\s*(thumb|thumbnail|frame|frameless|border|'
                                r'left|right|center|none|upright|'
                                r'\d*x?\d+px)\s*', p)), '')
            return self.image_link(title, self.plain(caption))
        if ns == -1:  # Special pages do not exist outside MediaWiki
            special = SPECIAL_PAGES.get(title.split('/')[0].lower())
            if special:
                return link_token(-1, special, '', (label or title) + trail)
            return (label or title) + trail
        if not title and anchor:  # [[#Section]]
            return (label or anchor) + trail
        if label is None:
            label = title if ns else raw_target.lstrip(':').replace('_', ' ')
        return link_token(ns, title, anchor, label + trail)

    @staticmethod
    def plain(text):
        """Links nested in a link label or caption: keep only their text."""
        text = re.sub(r'\[(?:https?|ftp)://\S+\s+([^\]]+)\]', r'\1', text)
        return re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', text)

    @staticmethod
    def split_pipes(text):
        """Split on | that are not inside [[...]] or {{...}}."""
        parts, depth, cur, i = [], 0, '', 0
        while i < len(text):
            two = text[i:i + 2]
            if two in ('[[', '{{'):
                depth += 1
                cur += two
                i += 2
            elif two in (']]', '}}'):
                depth -= 1
                cur += two
                i += 2
            elif text[i] == '|' and depth == 0:
                parts.append(cur)
                cur = ''
                i += 1
            else:
                cur += text[i]
                i += 1
        parts.append(cur)
        return parts

    # ---- templates ---------------------------------------------------------

    MAGIC = {'CURRENTTIME', 'CURRENTDAYNAME', 'CURRENTDAY', 'CURRENTMONTHNAME',
             'CURRENTYEAR', 'NAMESPACE'}

    def expand_templates(self, text, page_title, depth=0):
        pattern = re.compile(r'\{\{(?!\{)((?:[^{}]|\{(?!\{)|\}(?!\}))*?)\}\}')

        def repl(m):
            parts = self.split_pipes(m.group(1))
            name = parts[0].strip()
            if name == 'PAGENAME':
                return page_title
            if name == 'NUMBEROFARTICLES':
                return str(self.article_count)
            if name in self.MAGIC:
                return ''
            ns, tname, _ = parse_target(name)
            if ns not in (0, TEMPLATE_NS):
                return ''
            body = self.templates.get(tname)
            if body is None or depth > 5:
                return ''
            args, pos = {}, 1
            for p in parts[1:]:
                key, eq, val = p.partition('=')
                if eq and re.fullmatch(r'[^\[\]{}]+', key):
                    args[key.strip()] = val.strip()
                else:
                    args[str(pos)] = p.strip()
                    pos += 1
            body = re.sub(r'<noinclude>.*?</noinclude>', '', body, flags=re.S)
            body = re.sub(r'</?includeonly>', '', body)

            def param(pm):
                key, _, default = pm.group(1).partition('|')
                return args.get(key.strip(), default)
            body = re.sub(r'\{\{\{([^{}]*)\}\}\}', param, body)
            return self.expand_templates(body, page_title, depth + 1)

        for _ in range(10):
            new = pattern.sub(repl, text)
            if new == text:
                break
            text = new
        return text

    # ---- block structures --------------------------------------------------

    def convert_tables(self, text):
        def table(m):
            rows, cur = [], None
            for line in m.group(1).split('\n'):
                s = line.strip()
                if s.startswith('|+'):
                    continue
                if s.startswith('|-'):
                    cur = None
                    continue
                if s[:1] in ('|', '!'):
                    if cur is None:
                        cur = []
                        rows.append(cur)
                    sep = '!!' if s[0] == '!' else '||'
                    for cell in s[1:].split(sep):
                        cur.append([cell.split('|')[-1].strip()])
                elif cur and s:
                    cur[-1].append(s)
            rows = [[self.cell_html(c) for c in r] for r in rows]
            rows = [r for r in rows if any(c for c in r)]
            if not rows:
                return ''
            width = max(len(r) for r in rows)

            def fmt(r):
                r += [''] * (width - len(r))
                return '| ' + ' | '.join(c.replace('|', '\\|') for c in r) + ' |'
            out = [fmt(rows[0]), '|' + ' --- |' * width]
            out += [fmt(r) for r in rows[1:]]
            return '\n\n' + '\n'.join(out) + '\n\n'
        return re.sub(r'^\s*\{\|[^\n]*\n(.*?)^\s*\|\}', table, text,
                      flags=re.S | re.M)

    @staticmethod
    def cell_html(lines):
        """A table cell's lines as the single line a Markdown table cell
        allows, with its wiki and HTML lists as (placeholder) HTML lists."""
        def tag(name, closing=False):
            return CELL_TAGS[name][closing]
        out, stack, text_last = [], [], False

        def close_to(depth):
            while len(stack) > depth:
                out.append(tag('li', True) + tag(stack.pop(), True))
        for line in lines:
            line = re.sub(r'<(/?)(ul|ol|li)\b[^>]*>',
                          lambda m: tag(m.group(2).lower(), bool(m.group(1))),
                          line, flags=re.I).strip()
            m = re.match(r'([*#]+)([;:]?)\s*(.*)', line)
            if not m:
                close_to(0)
                if line:
                    out.append(('<br>' if text_last else '') + line)
                    text_last = True
                continue
            marks, term, item = m.groups()
            if term == ';':  # *;term is a bold item
                item = f"'''{item}'''"
            if len(marks) > len(stack):
                while len(stack) < len(marks):
                    kind = 'ol' if marks[len(stack)] == '#' else 'ul'
                    out.append(tag(kind) + tag('li'))
                    stack.append(kind)
            else:
                close_to(len(marks))
                out.append(tag('li', True) + tag('li'))
            out.append(item)
            text_last = False
        close_to(0)
        return ''.join(out)

    def convert_gallery(self, text):
        def gallery(m):
            items = []
            for line in m.group(1).strip().split('\n'):
                if not line.strip():
                    continue
                name, _, caption = line.partition('|')
                _, title, _ = parse_target(name)
                items.append('<li>' + self.image_link(title, caption.strip()))
            return '\n<ul>' + ''.join(items) + '</ul>\n'
        return re.sub(r'<gallery[^>]*>(.*?)</gallery>', gallery, text,
                      flags=re.S | re.I)

    @staticmethod
    def convert_html_lists(text):
        """<ul>/<ol>/<li> markup into Markdown list lines."""
        tokens = re.split(r'(</?(?:ul|ol|li)\b[^>]*>)', text, flags=re.I)
        out, stack, item = [], [], None

        def flush():
            nonlocal item
            if item is not None:
                content = ' '.join(item.split())
                if content:
                    indent = '    ' * (len(stack) - 1)
                    bullet = '1.' if stack and stack[-1] == 'ol' else '-'
                    out.append(f'\n{indent}{bullet} {content}\n')
                item = None

        for tok in tokens:
            tag = re.match(r'<(/?)(ul|ol|li)\b', tok, flags=re.I)
            if not tag:
                if item is not None:
                    item += tok
                elif stack:
                    if tok.strip():  # stray text directly inside <ul>
                        item = tok
                else:
                    out.append(tok)
                continue
            closing, name = tag.group(1), tag.group(2).lower()
            if name in ('ul', 'ol'):
                flush()
                if closing:
                    if stack:
                        stack.pop()
                    if not stack:
                        out.append('\n\n')
                else:
                    if not stack:
                        out.append('\n\n')
                    stack.append(name)
            elif not closing:
                flush()
                item = ''
                if not stack:
                    stack.append('ul')
            else:
                flush()
        flush()
        text = ''.join(out)
        # list items produced above are separated by single newlines
        return re.sub(r'(^ *(?:-|1\.) .*)\n\n+(?= *(?:-|1\.) )', r'\1\n',
                      text, flags=re.M)

    @staticmethod
    def convert_wiki_line(line):
        m = re.match(r'^([*#:;]+)\s*(.*)$', line)
        if not m:
            return line
        marks, content = m.groups()
        if set(marks) == {':'}:
            return '> ' * len(marks) + content
        indent = '    ' * (len(marks) - 1)
        last = marks[-1]
        if last == '#':
            return f'{indent}1. {content}'
        if last == ';':
            term, _, desc = content.partition(':')
            return f'{indent}**{term.strip()}**' + (
                f': {desc.strip()}' if desc else '')
        if last == ':':
            return f'{indent}{content}'
        return f'{indent}- {content}'

    # ---- inline ------------------------------------------------------------

    @staticmethod
    def convert_emphasis(line):
        # Markdown ignores "** bold **", so spaces move outside the markers
        def wrap(marker):
            def repl(m):
                inner = m.group(1)
                if not inner.strip():
                    return inner
                lead = inner[:len(inner) - len(inner.lstrip())]
                trail = inner[len(inner.rstrip()):]
                return f'{lead}{marker}{inner.strip()}{marker}{trail}'
            return repl
        line = re.sub(r"'''''(.+?)'''''", wrap('***'), line)
        line = re.sub(r"'''(.+?)'''", wrap('**'), line)
        line = re.sub(r"''(.+?)''", wrap('*'), line)
        return line

    def convert(self, text, page_title):
        categories = []
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'<!--.*?(-->|$)', '', text, flags=re.S)
        text = re.sub(r'__[A-Z]+__', '', text)
        text = re.sub(r'</?(?:noinclude|includeonly|onlyinclude)>', '', text)
        text = self.expand_templates(text, page_title)
        text = self.convert_gallery(text)

        # Links
        text = re.sub(r'\[\[((?:[^\[\]]|\[\[?[^\[\]]*\]\]?)+)\]\]([^\W\d_]+)?',
                      lambda m: self.convert_link(m, categories), text)
        text = re.sub(r'(?<!\[)\[((?:https?|ftp|mailto):[^\s\]]+)\s+([^\]]+)\]',
                      r'[\2](\1)', text)
        text = re.sub(r'(?<!\[)\[((?:https?|ftp):[^\s\]]+)\]', r'<\1>', text)

        text = self.convert_tables(text)

        # Inline HTML
        text = re.sub(r'<br\s*/?>', '<br>', text, flags=re.I)
        text = re.sub(r'<(b|strong)>(.*?)</\1>', r'**\2**', text,
                      flags=re.S | re.I)
        text = re.sub(r'<(i|em)>(.*?)</\1>', r'*\2*', text, flags=re.S | re.I)
        text = re.sub(r'</?(?:div|span|font|big|small|center|p|table|tr|td|th'
                      r'|tbody)\b[^>]*>', '\n', text, flags=re.I)
        text = self.convert_html_lists(text)

        lines = []
        for line in text.split('\n'):
            if not re.match(r'^ *(?:-|1\.) ', line):
                line = self.convert_wiki_line(line.strip())
            h = re.match(r'^(={1,6})\s*(.*?)\s*\1$', line)
            if h:
                title = re.sub(r"^'''(.*)'''$", r'\1', h.group(2))
                line = '\n' + '#' * len(h.group(1)) + ' ' + title + '\n'
            elif re.fullmatch(r'-{4,}', line):
                line = '\n---\n'
            lines.append(self.convert_emphasis(line))

        # Python-Markdown needs a blank line before a list or a table
        out = []
        for line in '\n'.join(lines).split('\n'):
            starts_block = re.match(r'^(?:(?:-|1\.) |\| |> )', line)
            if (starts_block and out and out[-1].strip()
                    and not re.match(r'^ *(?:(?:-|1\.) |\| |> )|^    ',
                                     out[-1])
                    and line[:2] != out[-1][:2]):
                out.append('')
            out.append(line.rstrip())
        text = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip()
        for name, (opening, closing) in CELL_TAGS.items():
            text = text.replace(opening, f'<{name}>').replace(
                closing, f'</{name}>')
        seen = set()
        categories = [c for c in categories if not (c in seen or seen.add(c))]
        return text, categories


# --------------------------------------------------------------------------
# Where each page goes
# --------------------------------------------------------------------------

def year_of(title, categories):
    for c in categories:
        m = re.fullmatch(r'Acampamentos de (\d{4})', c)
        if m:
            return m.group(1)
    m = re.search(r'\b(19[89]\d|20[01]\d|[89]\d|0\d|1[0-2])\b', title)
    if m:
        y = m.group(1)
        return y if len(y) == 4 else ('19' + y if y >= '80' else '20' + y)
    return None


def folder_for(ns, title, categories, private=False):
    cats = set(categories)
    if ns == CATEGORY_NS:
        return 'Categorias'
    if private or title == 'Áreas Restrictas':
        return ('Restrito/Locais de Acampamento'
                if 'Locais de Acampamento' in cats else 'Restrito')
    if ns == 4:
        return 'Wikinácios'
    if ns == 12:
        return 'Wikinácios/Ajuda'
    if ns == 2:
        return 'Wikinácios/Utilizadores'
    if ns in (1, 3):
        return 'Wikinácios/Discussão'
    if ns == IMAGE_NS:
        return 'Wikinácios/Imagens'
    if ns == TEMPLATE_NS:
        return 'Wikinácios/Predefinições'
    if cats & ENCONTRO_CATEGORIES or title.startswith('Encontro'):
        return 'Encontros'
    if cats & CAMP_CATEGORIES or any(c.startswith('Acampamentos de ')
                                     for c in cats):
        return 'Acampamentos/' + (year_of(title, categories) or 'Sem data')
    if 'Cargos' in cats:
        return 'Cargos'
    if 'Desambiguação' in cats:
        return 'Movimento/Desambiguação'
    if cats & {'Livros', 'Piadas'}:
        return 'Movimento'
    if cats & PEOPLE_CATEGORIES and not ORGAN_TITLE.match(title):
        return 'Pessoas/' + initial(safe_name(title))
    return 'Movimento'


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

# The section index links "Direcção Local do CC" to the CAIC category.
HOME_FIXES = [('[[:Category:Direcção Local do CAIC|Direcção Local do CC]]',
               '[[:Category:Direcção Local do CC|Direcção Local do CC]]')]
TOP_LINKS = ('[[Boas-vindas]] | [[Ajuda:Conteúdos|Ajuda]] | '
             '[[FAQ|Perguntas Frequentes]] | [[Contactos]]')


class Home:
    """The old home page was a nest of layout tables around four templates.
    Their content, converted, laid out as on the wiki (docs/index.md, styled
    by assets/extra.css) or as plain sections (README.md)."""

    def __init__(self, conv, templates):
        def md(wikitext):
            return conv.convert(wikitext, 'Página principal')[0]
        featured = templates.get('Em destaque', '')
        more = re.search(r'<div align="right">(.*?)</div>', featured, re.S)
        if more:
            featured = featured.replace(more.group(0), '')
        self.featured = md(featured)
        self.more = md(more.group(1)) if more else ''
        self.trivia = md(templates.get('Sabia que', ''))
        self.events = md(templates.get('Eventos actuais', ''))
        self.top = md(TOP_LINKS)
        self.welcome = md("[[Boas-vindas|Bem-vindo(a)]] à '''Wikinacios''',")
        self.tagline = md('a enciclopédia livre sobre Campinácios que '
                          '[[Ajuda:Conteúdos|(quase) todos podem editar]].')
        directory = templates.get('Enciclopédia secções', '')
        for bad, good in HOME_FIXES:
            directory = directory.replace(bad, good)
        self.sections = []
        for row in directory.split('\n|-'):
            m = re.search(r"('''.+?''')\s*<br\s*/?>(.*)", row, re.S)
            if m:
                links = re.sub(r'\|\}\s*$', '', m.group(2))
                self.sections.append((md(m.group(1)),
                                      md(' '.join(links.split()))))

    @staticmethod
    def box(cls, template, head, body):
        head = link_token(TEMPLATE_NS, template, '', head)
        return (f'<div class="wk-box {cls}" markdown>\n'
                f'<div class="wk-head" markdown="span">{head}</div>\n\n'
                f'{body}\n\n</div>')

    def page(self, articles):
        count = link_token(-1, 'todos', '', f'{articles} artigos')
        index = '\n'.join(
            f'<div class="wk-section" markdown="span">{head}'
            + (f'<br>{links}' if links else '') + '</div>'
            for head, links in self.sections)
        more = (f'\n\n<div class="wk-more" markdown="span">{self.more}</div>'
                if self.more else '')
        return '\n\n'.join([
            # an <h1> of its own stops MkDocs adding a visible "Início" one
            '<h1 class="wk-title">Wikinácios</h1>',
            f'<div class="wk-top" markdown="span">{self.top}</div>',
            '<div class="wk-banner" markdown>\n'
            f'<div class="wk-count" markdown="span">**{count}**</div>\n'
            f'<div class="wk-welcome" markdown="span">{self.welcome}</div>\n'
            f'<div class="wk-tagline" markdown="span">{self.tagline}</div>\n'
            '</div>',
            '<div class="wk-grid" markdown>\n<div class="wk-col" markdown>',
            self.box('wk-blue', 'Em destaque', 'Como tudo começou...',
                     self.featured + more),
            self.box('wk-yellow', 'Sabia que', 'Sabia que..', self.trivia),
            '</div>\n<div class="wk-col" markdown>',
            self.box('wk-green', 'Eventos actuais', 'Eventos recentes',
                     self.events),
            f'<div class="wk-index" markdown>\n{index}\n</div>',
            '</div>\n</div>',
        ])

    def plain(self, explore):
        sections = '\n'.join(f'- {head}' + (f' — {links}' if links else '')
                             for head, links in self.sections)
        return '\n\n'.join([
            self.welcome + ' ' + self.tagline, self.top,
            explore, '## Secções', sections,
            '## Como tudo começou...', self.featured, self.more,
            '## Sabia que...', self.trivia,
            '## Eventos recentes', self.events])


def yaml_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def iso(ts):
    return datetime.datetime.strptime(ts, '%Y%m%d%H%M%S').strftime(
        '%Y-%m-%dT%H:%M:%SZ')


def page_footer(aliases, category_links):
    """The other names of a page and a table of its categories, closing it.

    Pages carry no front matter: GitHub shows it as a table at the top."""
    out = []
    if aliases:
        out.append('**Outros nomes:** ' + ' · '.join(aliases))
    if category_links:
        out.append('| Categorias |\n| --- |\n' + '\n'.join(
            f'| {link} |' for link in category_links))
    return '---\n\n' + '\n\n'.join(out) if out else ''


def md_link(label, from_path, to_path, anchor=''):
    rel = posixpath.relpath(to_path, posixpath.dirname(from_path))
    label = label.replace('[', '\\[').replace(']', '\\]')
    return f'[{label}]({quote(rel)}' + (f'#{slugify(anchor)}' if anchor
                                         else '') + ')'


def main(dump, root='.', password=None):
    root = Path(root)
    docs = root / 'docs'
    data = load_tables(dump, ['mw_page', 'mw_revision', 'mw_text', 'mw_image'])
    texts = {int(r[0]): r[1] for r in data['mw_text']}
    revisions = {int(r[0]): r for r in data['mw_revision']}

    pages = {}
    for r in data['mw_page']:
        rev = revisions[int(r[9])]
        ns, title = int(r[1]), normalize_title(decode(r[2]))
        pages[(ns, title)] = dict(redirect=r[5] == '1',
                                  text=decode(texts[int(rev[2])]))

    images = {}
    for r in data['mw_image']:
        images[normalize_title(decode(r[0]))] = dict(
            size=int(r[1]), width=int(r[2]), height=int(r[3]),
            mime=f'{decode(r[7])}/{decode(r[8])}', uploader=decode(r[11]),
            timestamp=decode(r[12]))

    redirects = {}
    for key, p in pages.items():
        m = re.match(r'\s*#REDIRECT\s*\[\[([^\]|]+)', p['text'], flags=re.I)
        if p['redirect'] and m:
            redirects[key] = parse_target(m.group(1).lstrip(':'))

    def resolve(ns, title, anchor=''):
        seen = set()
        while (ns, title) in redirects and (ns, title) not in seen:
            seen.add((ns, title))
            ns, title, a = redirects[(ns, title)]
            anchor = anchor or a
        return ns, title, anchor

    templates = {t: p['text'] for (ns, t), p in pages.items()
                 if ns == TEMPLATE_NS}
    home = (0, 'Página principal')
    pages[home]['text'] = ''  # laid out by Home
    article_count = sum(1 for (ns, _), p in pages.items()
                        if ns == 0 and not p['redirect'])
    conv = Converter(templates, article_count)

    # 1. Convert every page
    notes = {}
    for key, p in sorted(pages.items()):
        if key in redirects or key in SKIP_PAGES:
            continue
        ns, title = key
        if ns == TEMPLATE_NS:  # templates are kept as their source
            body, cats = f'```text\n{p["text"].strip()}\n```', []
        else:
            body, cats = conv.convert(p['text'], title)
        if key == HELP_PAGE:  # how to edit is now a GitHub matter
            body = body.split(HELP_SECTION)[0] + HELP_TEXT.strip()
        notes[key] = dict(body=body, categories=cats)

    members = defaultdict(list)
    for key, note in notes.items():
        for c in note['categories']:
            members[c].append(key)
    for c in members:  # categories used without a page of their own
        notes.setdefault((CATEGORY_NS, c), dict(body='', categories=[]))

    # 2. What was restricted on the wiki is encrypted; without a password it
    # is left out.
    private = {k for k, n in notes.items()
               if set(n['categories']) & PRIVATE_CATEGORIES
               or (k[0] == CATEGORY_NS and k[1] in PRIVATE_CATEGORIES)}
    left_out = []
    if not password:
        left_out = sorted(private)
        for k in private:
            del notes[k]
        private = set()
    members = {c: [k for k in ks if k in notes] for c, ks in members.items()}

    # 3. Decide where every page goes
    paths, taken = {}, Counter()
    for key in sorted(notes):
        ns, title = key
        if key == home:
            paths[key] = 'docs/index.md'
            continue
        folder = folder_for(ns, title, notes[key]['categories'],
                            key in private)
        name = safe_name(title) or 'Sem título'
        if ns == 3:
            name = 'Utilizador ' + name
        base = f'docs/{folder}/{name}'
        taken[base.lower()] += 1
        n = taken[base.lower()]
        paths[key] = base + (f' ({n})' if n > 1 else '') + '.md'

    aliases = defaultdict(list)
    for key in redirects:
        target = resolve(*key)[:2]
        if target in notes and key[0] == target[0]:
            aliases[target].append(key[1])

    # 4. Resolve links. MediaWiki titles are case-sensitive after the first
    # letter; a link that only differs in case from one page goes to it.
    by_lower = defaultdict(set)
    for k in list(notes) + list(redirects):
        by_lower[(k[0], k[1].lower())].add(k)

    def find(ns, title, anchor=''):
        ns, title, anchor = resolve(ns, title, anchor)
        if (ns, title) in notes:
            return (ns, title), anchor
        found = {resolve(*k)[:2] for k in by_lower[(ns, title.lower())]}
        found &= set(notes)
        return (found.pop(), anchor) if len(found) == 1 else (None, anchor)

    edges = defaultdict(set)
    for src, note in notes.items():
        for m in LINK.finditer(note['body']):
            if m.group(1) != '-1':
                dst = find(int(m.group(1)), m.group(2))[0]
                if dst and dst != src:
                    edges[src].add(dst)
    backlinks = defaultdict(set)
    for src, dsts in edges.items():
        for dst in dsts:
            backlinks[dst].add(src)

    def title_of(key):
        return 'Wikinácios' if key == home else key[1]

    def refs_of(key):
        """Pages linking here; a restricted page's links stay hidden."""
        return sorted((k for k in backlinks.get(key, ())
                       if k[0] != CATEGORY_NS
                       and (k not in private or key in private)),
                      key=title_of)

    def link_to(key, from_path, label=None):
        return md_link(label or title_of(key), from_path, paths[key]) + (
            LOCK if key in private else '')

    def render_links(text, src_key, src_path):
        def repl(m):
            ns, title, anchor, label = (int(m.group(1)), m.group(2),
                                        m.group(3), m.group(4))
            if ns == -1:
                if title == 'todos':
                    return md_link(label, src_path, ALL_PAGES)
                if title == 'backlinks' and src_key and refs_of(src_key):
                    return md_link(label, src_path, src_path, BACKLINKS)
                return label
            dst, anchor = find(ns, title, anchor)
            if dst is None:
                return label  # the page never existed
            return md_link(label, src_path, paths[dst], anchor)
        return LINK.sub(repl, text)

    # 5. Write the pages
    cipher = restrito.Key(password) if private else None
    layout = Home(conv, templates)
    articles = sum(1 for k in notes if k[0] == 0)
    if docs.exists():
        for child in docs.iterdir():
            if child.name != 'assets':
                shutil.rmtree(child) if child.is_dir() else child.unlink()
    for key, note in sorted(notes.items()):
        ns, title = key
        path = paths[key]
        if key == home:
            parts = [render_links(layout.page(articles), None, path)]
        else:
            parts = [f'# {title}']
        rest = []  # everything under the title
        body = render_links(note['body'], key, path)
        if body and key != home:
            rest.append(body)
        img = images.get(title) if ns == IMAGE_NS else None
        if img:
            rest.append(
                '> **Ficheiro original não incluído no backup.** '
                f"{img['mime']}, {img['width']}×{img['height']} px, "
                f"{img['size']:,} bytes — carregado por {img['uploader']} "
                f"em {iso(img['timestamp'])[:10]}.")
        if ns == CATEGORY_NS:
            inside = sorted(members.get(title, []), key=lambda k: k[1])
            subcats = [k for k in inside if k[0] == CATEGORY_NS]
            pages_in = [k for k in inside if k[0] != CATEGORY_NS]
            if subcats:
                rest.append('## Subcategorias\n\n' + '\n'.join(
                    '- ' + link_to(k, path) for k in subcats))
            if pages_in:
                rest.append(f'## Páginas nesta categoria ({len(pages_in)})'
                            '\n\n' + '\n'.join(
                                '- ' + link_to(k, path) for k in pages_in))
        refs = refs_of(key)
        if refs and key != home:
            rest.append(f'## {BACKLINKS}\n\n' + '\n'.join(
                '- ' + link_to(k, path) for k in refs))
        cats = [c for c in note['categories'] if (CATEGORY_NS, c) in notes]
        footer = page_footer(sorted(aliases.get(key, [])), [
            link_to((CATEGORY_NS, c), path, c) for c in cats])
        if footer:
            rest.append(footer)
        if key in private:
            parts.append(restrito.seal_page(cipher, '\n\n'.join(rest)))
        else:
            parts += rest
        out = root / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text('\n\n'.join(parts) + '\n', encoding='utf-8')

    for path, text in [(ABOUT_PAGE, ABOUT_TEXT), ('docs/Grafo.md', GRAPH_TEXT)]:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding='utf-8')

    # Every article and every alternative name, as Especial:Allpages did
    entries = [(title_of(k), k, None) for k in notes
               if k[0] == 0 and k != home]
    entries += [(a, k, a) for k, names in aliases.items() if k[0] == 0
                for a in names]
    entries.sort(key=lambda e: (unicodedata.normalize('NFKD', e[0]).lower(),
                                e[0]))
    groups = defaultdict(list)
    for name, k, alias in entries:
        groups[initial(safe_name(name))].append(
            f'- *{alias}* → {link_to(k, ALL_PAGES)}' if alias
            else f'- {link_to(k, ALL_PAGES)}')
    (root / ALL_PAGES).write_text('\n\n'.join(
        ['# Todos os artigos',
         f'{articles - 1} artigos e, em itálico, os '
         f'{len(entries) - articles + 1} nomes alternativos que apontam para '
         'eles, como na página especial "Todas as páginas" da wiki.'
         + (f' As páginas marcadas com{LOCK} são restritas.' if private
            else '')]
        + [f'## {g}\n\n' + '\n'.join(groups[g]) for g in sorted(
            groups, key=lambda g: (g == 'Outros', g))]) + '\n',
        encoding='utf-8')

    # 6. An index page for every folder
    by_folder = defaultdict(list)
    for key, path in paths.items():
        if key != home:
            by_folder[posixpath.dirname(path)].append(key)
    folders = set()
    for f in by_folder:
        while f != 'docs':
            folders.add(f)
            f = posixpath.dirname(f)
    for folder in sorted(folders):
        index = f'{folder}/index.md'
        name = posixpath.basename(folder)
        parts = [f'# {name}']
        if name in FOLDER_INTROS:
            parts.append(FOLDER_INTROS[name])
        subs = sorted(f for f in folders if posixpath.dirname(f) == folder)
        if subs:
            def count(f):
                return sum(len(v) for k, v in by_folder.items()
                           if k == f or k.startswith(f + '/'))
            parts.append('\n'.join(
                f'- {md_link(posixpath.basename(s), index, s + "/index.md")}'
                f' ({count(s)})' for s in subs))
        entries = sorted(by_folder.get(folder, []),
                         key=lambda k: title_of(k).lower())
        if entries:
            lines = []
            for k in entries:
                extra = [c for c in MODALITIES if c in notes[k]['categories']]
                lines.append('- ' + link_to(k, index) + (
                    f' — {", ".join(extra)}' if extra else ''))
            parts.append('\n'.join(lines))
        (root / index).write_text('\n\n'.join(parts) + '\n', encoding='utf-8')

    # Only section pages go in the sidebar: a nav with every article would be
    # copied into each of the ~700 HTML pages.
    def nav_entries(folder, depth):
        out = []
        for sub in sorted(f for f in folders if posixpath.dirname(f) == folder):
            name, rel = posixpath.basename(sub), sub[len('docs/'):]
            if any(posixpath.dirname(f) == sub for f in folders):
                out.append(f'{"  " * depth}- {yaml_str(name)}:')
                out.append(f'{"  " * (depth + 1)}- {rel}/index.md')
                out += nav_entries(sub, depth + 1)
            else:
                out.append(f'{"  " * depth}- {yaml_str(name)}: {rel}/index.md')
        return out
    nav = ['nav:', '  - "Início": index.md'] + nav_entries('docs', 1) + [
        f'  - "Todos os artigos": {ALL_PAGES[5:]}', '  - "Grafo": Grafo.md']
    config = root / 'mkdocs.yml'
    if config.exists():
        text = config.read_text(encoding='utf-8')
        marker = '# --- nav ---\n'
        if marker in text:
            config.write_text(text.split(marker)[0] + marker + '\n'.join(nav)
                              + '\n', encoding='utf-8')

    # 7. A plain version of the home page is the repository README
    explore = ['## Explorar', '']
    for folder, label in [
            ('Acampamentos', 'Acampamentos, por ano'),
            ('Pessoas', 'Pessoas, de A a Z'),
            ('Encontros', 'Encontros'), ('Cargos', 'Cargos'),
            ('Movimento', 'Movimento'), ('Categorias', 'Categorias'),
            ('Wikinácios', 'Sobre a wiki')]:
        explore.append('- ' + md_link(label, 'README.md',
                                      f'docs/{folder}/index.md'))
    explore.append('- ' + md_link('Todos os artigos', 'README.md',
                                  ALL_PAGES))
    explore.append('- ' + md_link('Grafo de ligações', 'README.md',
                                  'docs/Grafo.md'))
    intro = ('> Arquivo da **Wikinácios**, a wiki dos Campinácios '
             '(2009–2010), convertida para Markdown e publicada como site '
             f'em <{SITE_URL}>. Como foi feito, como o publicar e como '
             'ler as páginas restritas: ' +
             md_link('Sobre este arquivo', 'README.md', ABOUT_PAGE) + '.')
    readme = render_links(layout.plain('\n'.join(explore)), None, 'README.md')
    (root / 'README.md').write_text(
        f'# Wikinácios\n\n{intro}\n\n{readme}\n', encoding='utf-8')

    # 8. Link graph for docs/Grafo.md (without the restricted pages' links)
    content = [k for k in notes if k[0] == 0]
    public_edges = {s: d for s, d in edges.items() if s not in private}
    linked = {k for k in content if public_edges.get(k)
              or any(s not in private for s in backlinks.get(k, ()))}
    nodes = [dict(id=paths[k][5:-3] + '.html', title=title_of(k),
                  group=paths[k][5:].split('/')[0] if '/' in paths[k][5:]
                  else 'Movimento')
             for k in sorted(content) if k in linked]
    ids = {k: i for i, k in enumerate(k for k in sorted(content)
                                      if k in linked)}
    links = sorted({(ids[s], ids[d]) for s in ids
                    for d in public_edges.get(s, ()) if d in ids})
    (docs / 'assets').mkdir(exist_ok=True)
    (docs / 'assets' / 'graph.json').write_text(
        json.dumps({'nodes': nodes, 'links': links}, ensure_ascii=False),
        encoding='utf-8')

    print(f'{len(notes)} pages written ({len(private)} of them encrypted), '
          f'{len(redirects)} redirects folded into aliases.')
    if left_out:
        print(f'No password given: {len(left_out)} restricted pages left out.')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    secret = os.environ.get('WIKINACIOS_PALAVRA_PASSE')
    if secret is None and sys.stdin.isatty():
        secret = getpass.getpass('Palavra-passe das páginas restritas (vazia '
                                 'para as deixar de fora): ')
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '.', secret)
