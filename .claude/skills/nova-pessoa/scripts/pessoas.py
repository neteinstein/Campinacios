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
                      "### Cargos"); e "Páginas que ligam para aqui" de cada
                      um tem de listar o outro. Quem foi participante ou
                      esteve em formação não tem de aparecer no campo: os
                      campos só listam a equipa.

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
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / 'docs'
PEOPLE = DOCS / 'Pessoas'
DISAMBIG = DOCS / 'Movimento' / 'Desambiguação'
ALL_PAGES = DOCS / 'Todos os artigos.md'
EVENTS = [DOCS / 'Acampamentos', DOCS / 'Encontros']
LEGACY = ROOT / '.claude' / 'skills' / 'nova-pessoa' / 'legado.txt'

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
    """The page without its backlinks list and footer (other pages' names)."""
    text = path.read_text(encoding='utf-8')
    text = re.split(r'^## Páginas que ligam para aqui$', text, flags=re.M)[0]
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


def backlinks(page):
    """As páginas listadas em "## Páginas que ligam para aqui", ou None."""
    m = re.search(r'^## Páginas que ligam para aqui\s*$(.*?)(?=^---|^## |\Z)',
                  page.read_text(encoding='utf-8'), re.M | re.S)
    if not m:
        return None
    return {target(h, page) for _, h in LINK.findall(m.group(1))}


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

    def problems(self, pages=None):
        """Linhas de erro das ligações que só existem de um lado. Só a
        equipa (animadores) tem de estar nos dois: quem foi participante
        ou esteve em formação não aparece na página do campo."""
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
        pairs = [(a, b) for a in self.links for b in self.links[a]]
        for a, b in pairs:
            listed = backlinks(b)
            if wanted(a, b) and listed is not None and a not in listed:
                out.append(f'{rel(b)}: falta {rel(a)} em "Páginas que ligam '
                           'para aqui"')
        camp_set = set(self.camps)
        for b in [*site.people, *self.camps]:
            for a in sorted(backlinks(b) or (), key=str):
                person_camp = (a in site.people and b in camp_set) or \
                    (a in camp_set and b in site.people)
                if person_camp and b not in self.links[a] and wanted(a, b):
                    out.append(f'{rel(b)}: "Páginas que ligam para aqui" tem '
                               f'{rel(a)}, que não liga para aqui')
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
    if len(sys.argv) < 3 or sys.argv[1] not in ('procurar', 'verificar',
                                                'reciprocas'):
        sys.exit(__doc__)
    if sys.argv[1] == 'procurar':
        sys.exit(procurar(' '.join(sys.argv[2:])))
    if sys.argv[1] == 'reciprocas':
        sys.exit(reciprocas(sys.argv[2:]))
    sys.exit(verificar(sys.argv[2:]))
