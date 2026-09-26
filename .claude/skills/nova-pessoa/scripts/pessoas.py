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
    if len(sys.argv) < 3 or sys.argv[1] not in ('procurar', 'verificar'):
        sys.exit(__doc__)
    if sys.argv[1] == 'procurar':
        sys.exit(procurar(' '.join(sys.argv[2:])))
    sys.exit(verificar(sys.argv[2:]))
