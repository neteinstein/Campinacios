#!/usr/bin/env python3
"""Verifica que as páginas dos campos estão em todas as listas onde um campo
tem de aparecer.

O MkDocs não constrói estas listas: são Markdown simples, escritas uma vez
por scripts/mediawiki_to_markdown.py e mantidas à mão desde então. Uma
página de campo que falte nelas continua a ser publicada (o mkdocs --strict
só apanha ligações partidas), mas ninguém a encontra.

Para cada página de campo docs/Acampamentos/<ano>/<nome>.md verifica:

  1. docs/Categorias/Acampamentos.md
       a. a linha de <ano> na tabela dos acampamentos por ano liga a ela
       b. a lista "Páginas nesta categoria (N)" liga a ela
  2. docs/Acampamentos/<ano>/index.md liga a ela
  3. o mkdocs.yml tem <ano> na navegação

e, para o site todo, que a contagem "(N)" bate certo com a lista e que
docs/Acampamentos/index.md, que mostra o mesmo que a categoria, é igual a
ela: os mesmos campos em cada linha da tabela, a mesma lista de páginas e a
mesma contagem.

Uso:
    python3 .claude/skills/novo-acampamento/scripts/validar.py <campo.md> ...
    python3 .claude/skills/novo-acampamento/scripts/validar.py --todos

Sai com 1 se um campo verificado ou uma contagem estiver errado. Com
--todos, as falhas que a wiki antiga já tinha (ver LEGACY) aparecem à parte
e não fazem falhar.
"""
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / 'docs'
CAMPS = DOCS / 'Acampamentos'
CATEGORY = DOCS / 'Categorias' / 'Acampamentos.md'
MIRROR = CAMPS / 'index.md'  # a mesma tabela e lista de páginas que CATEGORY
UNDATED = 'Sem data'  # campos sem ano: não têm linha na tabela

LINK = re.compile(r'\]\((<[^>]+>|[^)\s]+)\)')


def targets(text, source):
    """Os ficheiros que as ligações Markdown de `text` (escritas em `source`)
    abrem; tanto na forma [a](Nome%20x.md) como [a](<Nome x.md>)."""
    out = set()
    for href in LINK.findall(text):
        href = href.strip('<>').split('#')[0]
        if href and not re.match(r'[a-z]+:', href):
            out.add(Path(os.path.normpath(source.parent / unquote(href))))
    return out


def section_list(text, heading):
    """As linhas '- ...' debaixo de um '## título (N)', e esse N."""
    m = re.search(rf'^## {re.escape(heading)} \((\d+)\)\n\n((?:- .*\n?)*)',
                  text, re.M)
    if not m:
        return None, []
    return int(m.group(1)), m.group(2).rstrip('\n').splitlines()


def year_of(camp):
    return camp.parent.name


def table_rows(text):
    """A tabela dos acampamentos por ano: {ano: o texto dessa linha}."""
    return {m.group(1): m.group(0) for m in
            re.finditer(r'^\| \[?(\d{4})\]?(?:\([^)]*\))? \|.*$', text, re.M)}


def camp_pages():
    return sorted(p for p in CAMPS.glob('*/*.md') if p.name != 'index.md')


EQUIPA = re.compile(r'- \[(Animador(?:es)? (?:Livres?|de Equipa))\]'
                    r'\(\.\./\.\./Cargos/[^)]*\) - (.*)')


def equipa_problems(camp):
    """Animadores Livres e de Equipa: uma só linha por cargo, com todos."""
    linhas = {}
    for line in camp.read_text(encoding='utf-8').splitlines():
        m = EQUIPA.match(line)
        if m:
            cargo = 'Animador Livre' if 'Livre' in m.group(1) else \
                'Animador de Equipa'
            linhas.setdefault(cargo, []).append(m.groups())
    found = []
    for cargo, itens in linhas.items():
        plural = {'Animador Livre': 'Animadores Livres',
                  'Animador de Equipa': 'Animadores de Equipa'}[cargo]
        if len(itens) > 1:
            found.append(f'{len(itens)} linhas de "{cargo}": ponha todos '
                         f'numa só linha "{plural} - A, B e C"')
        else:
            nomes = re.sub(r'\[[^\]]*\]\([^)]*\)|\([^)]*\)', 'X', itens[0][1])
            vários = re.search(r',| e ', nomes)
            if itens[0][0] == cargo and vários:
                found.append(f'"{cargo}" tem vários nomes: use "{plural}"')
            elif itens[0][0] == plural and not vários \
                    and re.search(r'[^\W\d_]', nomes):
                found.append(f'"{plural}" só tem um nome: use "{cargo}"')
    return found


def check(camps):
    """Os problemas de cada campo (lista de textos) e os do site todo."""
    cat_text = CATEGORY.read_text(encoding='utf-8')
    nav = (ROOT / 'mkdocs.yml').read_text(encoding='utf-8')
    rows = table_rows(cat_text)
    count, members = section_list(cat_text, 'Páginas nesta categoria')
    member_files = targets('\n'.join(members), CATEGORY)

    general = []
    if count is None:
        general.append(f'{CATEGORY.relative_to(ROOT)}: falta a lista '
                       '"## Páginas nesta categoria (N)"')
    elif count != len(members):
        general.append(f'{CATEGORY.relative_to(ROOT)}: diz "Páginas nesta '
                       f'categoria ({count})" mas a lista tem {len(members)}')
    general += mirror_problems(rows, count, member_files)

    problems = {}
    for camp in camps:
        year, rel = year_of(camp), camp.relative_to(ROOT)
        found = []
        if not camp.exists():
            problems[camp] = [f'{rel} não existe']
            continue
        if year != UNDATED:
            if year not in rows:
                found.append(f'a tabela de {CATEGORY.relative_to(ROOT)} não '
                             f'tem a linha de {year}')
            elif camp not in targets(rows[year], CATEGORY):
                found.append(f'a linha de {year} da tabela de '
                             f'{CATEGORY.relative_to(ROOT)} não o inclui')
            if f'- "{year}": Acampamentos/{year}/index.md' not in nav:
                found.append(f'mkdocs.yml não tem {year} na navegação')
        if camp not in member_files:
            found.append('não está em "Páginas nesta categoria" de '
                         f'{CATEGORY.relative_to(ROOT)}')
        year_index = camp.parent / 'index.md'
        if not year_index.exists():
            found.append(f'falta {year_index.relative_to(ROOT)}')
        elif camp not in targets(year_index.read_text(encoding='utf-8'),
                                 year_index):
            found.append(f'não está em {year_index.relative_to(ROOT)}')
        found += equipa_problems(camp)
        if found:
            problems[camp] = found
    return problems, general


def mirror_problems(rows, count, member_files):
    """Onde docs/Acampamentos/index.md é diferente da página da categoria."""
    rel_m, rel_c = MIRROR.relative_to(ROOT), CATEGORY.relative_to(ROOT)
    text = MIRROR.read_text(encoding='utf-8')
    out = []
    mirror_rows = table_rows(text)
    for year in sorted(set(rows) | set(mirror_rows)):
        if year not in mirror_rows:
            out.append(f'{rel_m}: falta a linha de {year} da tabela '
                       f'(está em {rel_c})')
        elif year not in rows:
            out.append(f'{rel_m}: tem a linha de {year} da tabela, que '
                       f'falta em {rel_c}')
        else:
            mine = targets(mirror_rows[year], MIRROR)
            theirs = targets(rows[year], CATEGORY)
            for f in sorted(theirs - mine):
                out.append(f'{rel_m}: a linha de {year} da tabela não tem '
                           f'{f.relative_to(ROOT)} (está em {rel_c})')
            for f in sorted(mine - theirs):
                out.append(f'{rel_m}: a linha de {year} da tabela tem '
                           f'{f.relative_to(ROOT)}, que falta em {rel_c}')
    m_count, m_members = section_list(text, 'Páginas nesta categoria')
    m_files = targets('\n'.join(m_members), MIRROR)
    if m_count is None:
        out.append(f'{rel_m}: falta a lista "## Páginas nesta categoria (N)"')
        return out
    if m_count != count:
        out.append(f'{rel_m}: diz "Páginas nesta categoria ({m_count})" e '
                   f'{rel_c} diz ({count})')
    for f in sorted(member_files - m_files):
        out.append(f'{rel_m}: "Páginas nesta categoria" não tem '
                   f'{f.relative_to(ROOT)} (está em {rel_c})')
    for f in sorted(m_files - member_files):
        out.append(f'{rel_m}: "Páginas nesta categoria" tem '
                   f'{f.relative_to(ROOT)}, que falta em {rel_c}')
    return out


# Falhas que a wiki já tinha quando foi convertida (também lá a tabela e a
# categoria eram mantidas à mão). Os campos novos não podem aumentar a lista.
LEGACY = ROOT / '.claude' / 'skills' / 'novo-acampamento' / 'legado.txt'


def legacy():
    if not LEGACY.exists():
        return set()
    return {line.strip() for line in LEGACY.read_text(encoding='utf-8')
            .splitlines() if line.strip() and not line.startswith('#')}


def main(argv):
    if not argv:
        sys.exit(__doc__)
    everything = argv == ['--todos']
    camps = camp_pages() if everything else [
        Path(os.path.normpath(Path.cwd() / a)) for a in argv]
    problems, general = check(camps)
    known = legacy() if everything else set()
    failed = bool(general)
    for line in general:
        print(f'ERRO  {line}')
    old = 0
    for camp, found in problems.items():
        rel = str(camp.relative_to(ROOT))
        for line in found:
            if f'{rel}: {line}' in known:
                old += 1
                continue
            failed = True
            print(f'ERRO  {rel}: {line}')
    if everything and old:
        print(f'({old} falhas antigas, da wiki original, listadas em '
              f'{LEGACY.relative_to(ROOT)})')
    if not failed:
        print(f'OK  {len(camps)} acampamento(s) em todas as listas.')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
