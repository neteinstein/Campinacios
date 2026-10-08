#!/usr/bin/env python3
"""Find a person in the Wikinácios before adding them, and check that people
with the same or similar names are kept apart.

  procurar "Nome"     every person page, other name (alias) and
                      disambiguation page with the same or a similar name,
                      and every camp or encontro that mentions it, linked
                      (and to whom) or as plain text. Exit 2 if anything
                      matched, 0 if the name is new.
  verificar "Nome"... for each person page named: pages with a similar name
                      must be told apart (a "Nota:" at the top linking the
                      other page, or a disambiguation page listing both),
                      and no two person pages may have the same name.
  verificar --todos   the same for every person page; pairs the original
                      wiki already had are listed in legado.txt and don't
                      fail.
  reciprocas <página.md>... | --todos
                      pessoas e acampamentos ligados nos dois sentidos: quem
                      a página de uma pessoa diz ter sido animador num campo
                      tem de estar na equipa desse campo, e quem está na
                      equipa de um campo tem de o ter em "### Acampamentos"
                      (a coordenação de um curso basta estar ligada, em
                      "### Cargos"). Confere também as duas secções que se
                      geram a partir das páginas das pessoas ("Pessoas com
                      este cargo" nos cargos e "Participantes que se
                      tornaram animadores" nos campos) e que já não há
                      "Páginas que ligam para aqui" em lado nenhum. Quem
                      foi participante ou esteve em formação não tem de
                      aparecer na equipa do campo.
  secoes              escreve essas duas secções em todos os cargos e campos
                      (só mexe nas páginas que mudam). Corra-o sempre que
                      uma pessoa ganhar ou perder um cargo ou um campo.
  campo <pessoa.md> <Participante|Formação|Animador> "<linha>" [rótulo]
                      acrescenta a linha ("    - <ano> [Campo](…)…") ao
                      grupo de "### Acampamentos", por ordem de ano; cria a
                      secção e o grupo se faltarem (rótulo por omissão:
                      "Animador(a)") e tira os "- Nenhum" desse grupo.
  inserir <ficheiro> "<cabeçalho>" "<linha>"
                      insere a linha, por ordem alfabética, na lista a
                      seguir ao cabeçalho (ex.: "## Páginas nesta
                      categoria") e soma 1 ao "(N)" do cabeçalho.

Names are compared without accents or case. "Similar" means: the same
first and last name ("Ana Martins" / "Ana Rita Martins"), one name inside
the other ("Luís Onofre" / "Luís Onofre Pinto"), or a likely typo.
"""
import difflib
import os
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / 'docs'
PEOPLE = DOCS / 'Pessoas'
DISAMBIG = DOCS / 'Movimento' / 'Desambiguação'
ALL_PAGES = DOCS / 'Todos os artigos.md'
EVENTS = [DOCS / 'Acampamentos', DOCS / 'Encontros']
LEGACY = ROOT / '.claude' / 'skills' / 'nova-pessoa' / 'legado.txt'

# Secções geradas a partir das páginas das pessoas (ver `secoes`).
SEC_CARGO = 'Pessoas com este cargo'
SEC_CAMPO = 'Participantes que se tornaram animadores'
DERIVED = re.compile(rf'^## (?:{SEC_CARGO}|{SEC_CAMPO})$', re.M)
FOOTER = re.compile(r'^---$\n\n(?:\*\*Outros nomes|\| Categorias)', re.M)
CARGOS = DOCS / 'Cargos'
# papéis, na página de uma pessoa, que põem o campo na secção do campo
JOINED = ('Participante', 'Formação')

LINK = re.compile(r'\[([^\]]*)\]\((<[^>]+>|[^)\s]+)\)')
PARTICLES = {'de', 'da', 'do', 'dos', 'das', 'e', 'sj'}


def fold(text):
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', text).strip().lower()


def tokens(name):
    return [t for t in re.findall(r'[a-z0-9]+', fold(name))
            if t not in PARTICLES]


def similar(a, b):
    """Why names a and b could be the same person, or None."""
    fa, fb = fold(a), fold(b)
    if not fa or not fb:
        return None
    if fa == fb:
        return 'mesmo nome'
    ta, tb = tokens(a), tokens(b)
    if len(ta) >= 2 and len(tb) >= 2:
        if ta[0] == tb[0] and ta[-1] == tb[-1]:
            return 'mesmo primeiro e último nome'
        if set(ta) <= set(tb) or set(tb) <= set(ta):
            return 'um nome contém o outro'
    # a typo: same number of names, each one nearly the same
    # ("Pedro Vicentee", but not "Ana"/"Joana Martins")
    if len(ta) == len(tb) and min(len(fa), len(fb)) >= 6 and all(
            difflib.SequenceMatcher(None, x, y).ratio() >= 0.8
            for x, y in zip(ta, tb)):
        return 'nome parecido (erro de escrita?)'
    return None


def target(href, source):
    href = href.strip('<>').split('#')[0]
    if not href or re.match(r'[a-z]+:', href):
        return None
    return Path(os.path.normpath(source.parent / unquote(href)))


def title(path):
    m = re.search(r'^# (.+)$', path.read_text(encoding='utf-8'), re.M)
    return m.group(1).strip() if m else path.stem


def body(path):
    """The page without its derived lists and footer (other pages' names)."""
    text = path.read_text(encoding='utf-8')
    text = DERIVED.split(text)[0]
    return re.split(r'^---$\n\n(?:\*\*Outros nomes|\| Categorias)', text,
                    flags=re.M)[0]


def rel(path):
    return str(path.relative_to(ROOT))


class Site:
    def __init__(self):
        self.people = {}      # path -> title
        self.aliases = defaultdict(set)   # path -> other names
        for p in sorted(PEOPLE.glob('*/*.md')):
            if p.name != 'index.md':
                self.people[p] = title(p)
                m = re.search(r'^\*\*Outros nomes:\*\* (.+)$',
                              p.read_text(encoding='utf-8'), re.M)
                if m:
                    self.aliases[p] |= {a.strip() for a in m.group(1).split('·')}
        for m in re.finditer(r'^- \*(.+?)\* → \[[^\]]*\]\(([^)]+)\)',
                             ALL_PAGES.read_text(encoding='utf-8'), re.M):
            t = target(m.group(2), ALL_PAGES)
            if t in self.people:
                self.aliases[t].add(m.group(1))
        self.disambigs = {p: title(p) for p in sorted(DISAMBIG.glob('*.md'))
                          if p.name != 'index.md'}
        self.events = sorted(p for d in EVENTS for p in d.rglob('*.md')
                             if p.name != 'index.md')

    def names(self, person):
        return [self.people[person], *sorted(self.aliases[person])]

    def listed_in(self, disambig):
        return {target(h, disambig) for _, h in
                LINK.findall(disambig.read_text(encoding='utf-8'))}

    def mentions(self, name):
        """(event, 'ligado', label, person) and (event, 'texto', text)."""
        toks = tokens(name)
        plain_re = None
        if len(toks) >= 2:  # first ... last, up to 3 names in between
            plain_re = re.compile(rf'\b{toks[0]}\b(?:\s+[\w-]+){{0,3}}?\s+'
                                  rf'\b{toks[-1]}\b')
        elif toks:
            plain_re = re.compile(rf'\b{re.escape(fold(name))}\b')
        out = []
        for ev in self.events:
            text = body(ev)
            for label, href in LINK.findall(text):
                t = target(href, ev)
                who = self.people.get(t) or self.disambigs.get(t)
                if who and (similar(name, label) or similar(name, who)
                            or any(similar(name, a)
                                   for a in self.aliases.get(t, ()))):
                    out.append((ev, 'ligado', label, t))
            plain = fold(LINK.sub(' | ', text))
            for line in plain.splitlines():
                for m in plain_re.finditer(line) if plain_re else ():
                    if similar(name, m.group(0)) or \
                            fold(m.group(0)) == fold(name):
                        out.append((ev, 'texto', m.group(0), None))
        return out


def procurar(name):
    site = Site()
    pages = []
    for p, t in site.people.items():
        for n in site.names(p):
            why = similar(name, n)
            if why:
                pages.append((p, n, why))
                break
    dis = [(p, t, similar(name, t)) for p, t in site.disambigs.items()
           if similar(name, t)]
    found = site.mentions(name)
    linked = defaultdict(list)
    plain = defaultdict(list)
    for ev, kind, label, who in found:
        (linked[who] if kind == 'ligado' else plain[label]).append(
            (ev, label))

    print(f'# Procura de "{name}"\n')
    if pages:
        print('## Páginas de pessoas com nome igual ou parecido\n')
        for p, n, why in pages:
            via = f' (como "{n}")' if n != site.people[p] else ''
            print(f'- {site.people[p]} — {rel(p)} — {why}{via}')
            evs = sorted({rel(e) for e, _ in linked.get(p, [])})
            if evs:
                print(f'    - ligada em: {", ".join(evs)}')
            others = sorted(site.aliases[p])
            if others:
                print(f'    - outros nomes: {", ".join(others)}')
        print()
    if dis:
        print('## Páginas de desambiguação\n')
        for p, t, why in dis:
            names = [site.people.get(x, '?') for x in site.listed_in(p)
                     if x in site.people]
            print(f'- {t} — {rel(p)} — {why}; lista: {", ".join(names)}')
        print()
    other_links = {w: v for w, v in linked.items()
                   if w not in {p for p, _, _ in pages}}
    if other_links:
        print('## Ligações com esse nome para outras páginas\n')
        for who, evs in other_links.items():
            labels = sorted({lbl for _, lbl in evs})
            print(f'- "{", ".join(labels)}" → {rel(who)} em '
                  f'{", ".join(sorted({rel(e) for e, _ in evs}))}')
        print()
    if plain:
        print('## Nos acampamentos e encontros, sem ligação (texto)\n')
        for text, evs in sorted(plain.items()):
            print(f'- "{text}" em {", ".join(sorted({rel(e) for e, _ in evs}))}')
        print()
    if pages or dis or other_links or plain:
        print('Há nomes iguais ou parecidos: pergunte se é a mesma pessoa '
              'antes de criar ou ligar.')
        return 2
    print('Nenhum nome igual ou parecido: é um nome novo.')
    return 0


CAMPS = DOCS / 'Acampamentos'
TEAM = re.compile(r'animador|coordena|direc')  # secções da equipa num campo


def role_of(line):
    """'Animador', 'Participante', 'Formação' ou 'Locais' se a linha é um
    dos cabeçalhos da lista de acampamentos de uma pessoa, senão None."""
    if '[' in line:
        return None
    r = fold(re.sub(r'[-*:"()]', ' ', line))
    for start, role in (('animador', 'Animador'), ('particip', 'Participante'),
                        ('forma', 'Formação'), ('loca', 'Locais')):
        if r.startswith(start):
            return role
    return None


def listed(page, name):
    """As páginas listadas em "## name", ou None se a secção não existe."""
    m = re.search(rf'^## {re.escape(name)}\s*$(.*?)(?=^---$|^## |\Z)',
                  page.read_text(encoding='utf-8'), re.M | re.S)
    if not m:
        return None
    return {target(h, page) for _, h in LINK.findall(m.group(1))}


def is_animador(person):
    """Tem a categoria "Animadores" no rodapé."""
    text = person.read_text(encoding='utf-8')
    return bool(re.search(r'^\| \[Animadores\]\([^)]*Categorias/', text,
                          re.M))


def set_section(page, name, targets):
    """Reescreve a secção "## name" de `page` (ou tira-a, se `targets` é
    vazio), antes do rodapé. Tira também a antiga "Páginas que ligam para
    aqui". Devolve True se a página mudou."""
    old = page.read_text(encoding='utf-8')
    text = re.sub(rf'^## (?:Páginas que ligam para aqui|{name})\s*$'
                  r'.*?(?=^---$|^## |\Z)', '', old, flags=re.M | re.S)
    if targets:
        items = sorted(((title(t), t) for t in targets),
                       key=lambda x: (fold(x[0]), x[0]))
        block = f'## {name}\n\n' + ''.join(
            '- [{}]({})\n'.format(
                label, quote(Path(os.path.relpath(t, page.parent)).as_posix()))
            for label, t in items) + '\n'
        m = FOOTER.search(text)
        if m:
            text = text[:m.start()] + block + text[m.start():]
        else:
            text = text.rstrip('\n') + '\n\n' + block.rstrip('\n') + '\n'
    if text == old:
        return False
    page.write_text(text, encoding='utf-8')
    return True


class Ties:
    """Ligações entre pessoas e acampamentos."""

    def __init__(self, site):
        self.site = site
        self.camps = sorted(p for p in CAMPS.rglob('*.md')
                            if p.name != 'index.md')
        camp_set = set(self.camps)
        self.roles = defaultdict(dict)     # pessoa -> {campo: papel}
        self.links = defaultdict(set)      # página -> pessoas/campos que liga
        for person in site.people:
            text = body(person)
            for _, h in LINK.findall(text):
                t = target(h, person)
                if t in camp_set:
                    self.links[person].add(t)
            m = re.search(r'^### Acampamentos\s*$(.*?)(?=^##? |\Z)', text,
                          re.M | re.S)
            role = '?'
            for line in (m.group(1).splitlines() if m else ()):
                role = role_of(line) or role
                hrefs = [target(h, person) for _, h in LINK.findall(line)]
                # sem cabeçalho, um cargo na linha diz que foi animador
                here = role if role != '?' or not any(
                    t and t.parent.name == 'Cargos' for t in hrefs) \
                    else 'Animador'
                for t in hrefs:
                    if t in camp_set:
                        self.roles[person].setdefault(t, here)
        self.team = defaultdict(dict)      # campo -> {pessoa: secção}
        self.team_disambig = defaultdict(list)  # campo -> [(desamb., rótulo)]
        for camp in self.camps:
            section = ''
            for line in body(camp).splitlines():
                if line.startswith('#'):
                    section = fold(line.lstrip('#'))
                    continue
                for label, h in LINK.findall(line):
                    t = target(h, camp)
                    if t in site.people:
                        self.links[camp].add(t)
                        if TEAM.search(section):
                            self.team[camp].setdefault(t, section)
                    elif t in site.disambigs and TEAM.search(section):
                        self.team_disambig[camp].append((t, label))

    def derived(self):
        """{página: (secção, páginas que lá têm de estar)}: as pessoas com
        cada cargo (as que ligam para a página do cargo, em qualquer sítio)
        e, em cada campo, os animadores que lá foram participantes (ou
        estiveram em formação)."""
        cargos = {p for p in CARGOS.glob('*.md') if p.name != 'index.md'}
        out = {c: (SEC_CARGO, set()) for c in cargos}
        out.update({c: (SEC_CAMPO, set()) for c in self.camps})
        for person in self.site.people:
            for _, h in LINK.findall(body(person)):
                if target(h, person) in cargos:
                    out[target(h, person)][1].add(person)
            if is_animador(person):
                for camp, role in self.roles[person].items():
                    if role in JOINED:
                        out[camp][1].add(person)
        return out

    def problems(self, pages=None):
        """Linhas de erro das ligações que só existem de um lado (só a
        equipa tem de estar nos dois: quem foi participante ou esteve em
        formação não aparece na equipa do campo) e das secções geradas."""
        site, out = self.site, []

        def wanted(*ps):
            return pages is None or any(p in pages for p in ps)

        for person, camps in self.roles.items():
            for camp, role in camps.items():
                if role != 'Animador' or not wanted(person, camp) \
                        or person in self.links[camp]:
                    continue
                via = [d for d, _ in self.team_disambig[camp]
                       if person in site.listed_in(d)]
                extra = (f' (liga a {rel(via[0])}; aponte-a para a pessoa)'
                         if via else '')
                out.append(f'{rel(person)} diz que foi animador em '
                           f'{rel(camp)}, mas o campo não liga à pessoa'
                           f'{extra}')
        for camp, team in self.team.items():
            for person, section in team.items():
                if not wanted(person, camp):
                    continue
                role = self.roles[person].get(camp)
                if 'animador' not in section:
                    # coordenação de um curso ou encontro: vai para os
                    # "### Cargos" da pessoa, basta ligar ao campo
                    if camp not in self.links[person]:
                        out.append(f'{rel(camp)} tem {rel(person)} na '
                                   'coordenação, mas a página da pessoa não '
                                   'liga ao campo (em "### Cargos")')
                    continue
                if role is None:
                    out.append(f'{rel(camp)} tem {rel(person)} na equipa, mas '
                               'a página da pessoa não tem o campo em '
                               '"### Acampamentos"')
                elif role not in ('Animador', '?'):
                    out.append(f'{rel(camp)} tem {rel(person)} na equipa, mas '
                               f'a página da pessoa tem-no como {role}')
        for page, (name, want) in self.derived().items():
            have = listed(page, name)
            if not wanted(page, *want, *(have or ())):
                continue
            fix = '; corra pessoas.py secoes'
            if want and have is None:
                out.append(f'{rel(page)}: falta a secção "## {name}"{fix}')
            elif have is not None and not want:
                out.append(f'{rel(page)}: a secção "## {name}" devia ser '
                           f'tirada, não há ninguém para listar{fix}')
            elif have is not None and have != want:
                lines = [f'falta {rel(x)}' for x in sorted(want - have, key=str)]
                lines += [f'{rel(x)} não devia estar'
                          for x in sorted(have - want, key=str)]
                out.append(f'{rel(page)}: "## {name}" desactualizada '
                           f'({"; ".join(lines)}){fix}')
        for page in sorted(DOCS.rglob('*.md')):
            if wanted(page) and re.search(r'^## Páginas que ligam para aqui',
                                          page.read_text(encoding='utf-8'),
                                          re.M):
                out.append(f'{rel(page)}: "Páginas que ligam para aqui" já '
                           'não se usa; tire a secção')
        return out


def reciprocas(args):
    site = Site()
    ties = Ties(site)
    everything = args == ['--todos']
    pages = None if everything else {
        Path(os.path.normpath(Path.cwd() / a)) for a in args}
    problems = [f'{p} não existe' for p in pages or () if not p.exists()]
    problems += ties.problems(pages)
    for line in problems:
        print(f'ERRO  {line}')
    if not problems:
        n = 'todas as' if everything else f'{len(pages)}'
        print(f'OK  {n} página(s): pessoas e acampamentos ligados nos dois '
              'sentidos.')
    return 1 if problems else 0


def secoes():
    """Escreve "Pessoas com este cargo" e "Participantes que se tornaram
    animadores" em todos os cargos e campos."""
    changed = [page for page, (name, want) in Ties(Site()).derived().items()
               if set_section(page, name, want)]
    for page in changed:
        print(f'escrita  {rel(page)}')
    print(f'{len(changed)} página(s) mudaram.')
    return 0


# Grupos de "### Acampamentos" na página de uma pessoa, pela ordem em que
# aparecem. "Animador" apanha também Animadora e Animador(a).
GROUPS = ('Participante', 'Formação', 'Animador')


def group_rx(name):
    return re.compile(rf'^- (?:\*\*)?{re.escape(name)}')


def campo(path, group, line, label=None):
    """Acrescenta `line` ("    - <ano> [Campo](…)…") ao grupo `group` de
    "### Acampamentos" da pessoa, por ordem de ano. Cria a secção e o grupo
    se faltarem (com o rótulo `label`; por omissão o neutro "Animador(a)")
    e tira os "- Nenhum" desse grupo. Devolve False se a linha já lá está."""
    if group not in GROUPS:
        sys.exit(f'grupo desconhecido: {group} (use {", ".join(GROUPS)})')
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
    if any(l.rstrip('\n') == line for l in lines):
        return False
    label = label or ('Animador(a)' if group == 'Animador' else group)
    s = next((i for i, l in enumerate(lines)
              if l.startswith('### Acampamentos')), None)
    if s is None:
        s = next(i for i, l in enumerate(lines)
                 if l.startswith(('### Encontros', '## ')) or l.rstrip() == '---')
        lines[s:s] = ['### Acampamentos\n', '\n', '\n']
    e = s + 1
    while e < len(lines) and not (lines[e].startswith('#')
                                  or lines[e].rstrip() == '---'):
        e += 1
    g = next((i for i in range(s + 1, e) if group_rx(group).match(lines[i])),
             None)
    if g is None:
        later = GROUPS[GROUPS.index(group) + 1:]
        g = next((i for i in range(s + 1, e)
                  if any(group_rx(n).match(lines[i]) for n in later)), None)
        if g is None:
            g = e
            while g > s + 1 and lines[g - 1].strip() == '':
                g -= 1
        lines.insert(g, f'- **{label}:**\n')
        if g == s + 1:
            lines.insert(g, '\n')
            g += 1
    i = g + 1
    while i < len(lines) and lines[i].startswith('    - '):
        if lines[i].strip().lower() in ('- nenhum', '- nenhuma'):
            del lines[i]
        else:
            i += 1
    year = line.strip()[2:6]
    pos = next((j for j in range(g + 1, i) if lines[j].strip()[2:6] > year), i)
    lines.insert(pos, line + '\n')
    text = ''.join(lines)
    text = re.sub(r'### Acampamentos\n\n\n+', '### Acampamentos\n\n', text)
    text = re.sub(r'\n{3,}(### |## |---)', r'\n\n\1', text)
    path.write_text(text, encoding='utf-8')
    return True


def sort_key(line):
    m = re.match(r'- \*?\[?([^\]*]+)', line)
    return fold(m.group(1) if m else line)


def inserir(path, heading, line):
    """Insere `line`, por ordem alfabética, na lista a seguir ao primeiro
    cabeçalho que começa por `heading`, e soma 1 ao "(N)" do cabeçalho se o
    tiver. Devolve False se a linha já lá está."""
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
    h = next((n for n, l in enumerate(lines) if l.startswith(heading)), None)
    if h is None:
        sys.exit(f'{rel(path)}: sem cabeçalho {heading!r}')
    first = h + 1
    while first < len(lines) and lines[first].strip() == '':
        first += 1
    end = first
    while end < len(lines) and lines[end].startswith('- '):
        end += 1
    if any(l.rstrip('\n') == line for l in lines[first:end]):
        return False
    pos = next((j for j in range(first, end)
                if sort_key(lines[j]) > sort_key(line)), end)
    lines.insert(pos, line + '\n')
    if first == end and pos + 1 < len(lines) and lines[pos + 1].strip():
        lines.insert(pos + 1, '\n')
    m = re.search(r'\((\d+)\)\s*$', lines[h])
    if m:
        lines[h] = lines[h][:m.start(1)] + str(int(m.group(1)) + 1) \
            + lines[h][m.end(1):]
    path.write_text(''.join(lines), encoding='utf-8')
    return True


def told_apart(site, a, b):
    """Is there a "Nota:" on a pointing to b, or a disambiguation page
    listing both and linked from a's note?"""
    text = a.read_text(encoding='utf-8')
    notes = re.findall(r"^\*{1,3}Nota:.*$", text, re.M)
    for note in notes:
        for _, href in LINK.findall(note):
            t = target(href, a)
            if t == b or (t in site.disambigs and b in site.listed_in(t)):
                return True
    return False


def verificar(args):
    site = Site()
    everything = args == ['--todos']
    if everything:
        chosen = list(site.people)
    else:
        chosen = []
        for name in args:
            hits = [p for p, t in site.people.items()
                    if fold(t) == fold(name)]
            if not hits:
                print(f'ERRO  não há página de pessoa "{name}" em docs/Pessoas/')
            chosen += hits
    legacy = set()
    if everything and LEGACY.exists():
        legacy = {l.strip() for l in LEGACY.read_text(encoding='utf-8')
                  .splitlines() if l.strip() and not l.startswith('#')}
    problems, old = [], 0
    seen = set()
    for a in chosen:
        for b in site.people:
            if a == b or (b, a) in seen:
                continue
            why = similar(site.people[a], site.people[b])
            if not why:
                continue
            seen.add((a, b))
            if why == 'mesmo nome':
                line = (f'{rel(a)} e {rel(b)}: duas páginas com o mesmo nome')
            else:
                missing = [x for x, y in ((a, b), (b, a))
                           if not told_apart(site, x, y)]
                if not missing:
                    continue
                line = (f'{rel(a)} e {rel(b)} ({why}): falta a "Nota:" que '
                        f'as distingue em {", ".join(rel(x) for x in missing)}')
            key = ' | '.join(sorted([rel(a), rel(b)]))
            if key in legacy:
                old += 1
            else:
                problems.append(line)
    for line in problems:
        print(f'ERRO  {line}')
    if everything and old:
        print(f'({old} pares antigos, da wiki original, listados em '
              f'{rel(LEGACY)})')
    if not problems:
        print(f'OK  {len(chosen)} pessoa(s): nomes parecidos distinguidos.')
    return 1 if problems else 0


if __name__ == '__main__':
    if sys.argv[1:2] == ['secoes']:
        sys.exit(secoes())
    if sys.argv[1:2] == ['campo'] and len(sys.argv) in (5, 6):
        ok = campo(Path(sys.argv[2]), sys.argv[3], sys.argv[4], *sys.argv[5:])
        print('acrescentado' if ok else 'já lá estava')
        sys.exit(0)
    if sys.argv[1:2] == ['inserir'] and len(sys.argv) == 5:
        ok = inserir(Path(sys.argv[2]), sys.argv[3], sys.argv[4])
        print('inserido' if ok else 'já lá estava')
        sys.exit(0)
    if len(sys.argv) < 3 or sys.argv[1] not in ('procurar', 'verificar',
                                                'reciprocas'):
        sys.exit(__doc__)
    if sys.argv[1] == 'procurar':
        sys.exit(procurar(' '.join(sys.argv[2:])))
    if sys.argv[1] == 'reciprocas':
        sys.exit(reciprocas(sys.argv[2:]))
    sys.exit(verificar(sys.argv[2:]))
