#!/usr/bin/env python3
"""Check that the wiki content about to be committed is in Portuguese.

The Wikinácios is written in European Portuguese, with the pre-1990
orthography the original wiki used (Direcção, Director, actualizar,
contacto, equipa — see docs/Wikinácios/Ajuda/Conteúdos.md). Nothing stops a
pasted paragraph, a machine translation or a slip into Brazilian spelling
from landing on the site instead, and once it is on `main` the site is
already published.

This script cannot know a language for certain, and does not try to: it
flags the added or changed lines of the site's own content — new lines in
tracked files (via `git diff`) and every line of new, untracked files —
under docs/, the GitHub issue forms and the two files at the repository
root a visitor reads, and reports common English words and the Brazilian
Portuguese spellings this project doesn't use. It is a net for a careless
paste, not a judge: read every line it prints and decide for yourself
before you commit. It never changes a file.

Skills, scripts and other project tooling are project language (English)
by convention and are never checked; see CHECKED_PREFIXES.

Usage:
    python3 .claude/skills/conteudo-em-portugues/scripts/verificar_portugues.py [<ref>]

Compares the working tree (staged and unstaged) against <ref> (default:
HEAD). Exits 1 if anything was flagged.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

# Only these paths carry text a wiki visitor reads.
CHECKED_PREFIXES = ('docs/', '.github/ISSUE_TEMPLATE/', 'README.md',
                     'mkdocs.yml')

# Common English words very unlikely to appear inside Portuguese prose.
# Short or ambiguous words (people's initials, "a", "e", brand names...) are
# left out on purpose to keep this a net, not noise.
ENGLISH_WORDS = {
    'the', 'and', 'you', 'your', 'yours', 'please', 'click', 'should',
    'must', 'with', 'from', 'this', 'that', 'have', 'has', 'will', 'add',
    'added', 'create', 'created', 'update', 'updated', 'team', 'camp',
    'camps', 'location', 'participant', 'participants', 'person', 'people',
    'leader', 'leaders', 'welcome', 'thanks', 'thank', 'was', 'were',
    'not', 'name', 'names', 'when', 'where', 'what', 'who', 'how', 'why',
    'page', 'pages', 'file', 'files', 'edit', 'edited', 'about', 'because',
    'before', 'after', 'between', 'year', 'years', 'role', 'roles',
    'chaplain', 'counselor', 'counselors', 'father', 'mother', 'uncle',
    'aunt',
    # Excluded on purpose, even though they're common English words: "for"
    # is an ordinary Portuguese verb form (ir/ser, subjunctive: "se for
    # preciso"), and "director"/"directora" are identical, valid words in
    # the site's own (pre-1990) Portuguese orthography.
}

# Brazilian Portuguese spellings this project never uses (an exact-word
# list, not a stemmer, so it only catches the forms listed here — a net,
# not a proof; see the module docstring).
BRAZILIAN_WORDS = {
    'atualizar', 'atualizo', 'atualiza', 'atualizamos', 'atualizam',
    'atualizando', 'atualizado', 'atualizada', 'atualizados',
    'atualizadas', 'atualização', 'atualizações',
    'contato', 'contatos', 'equipe', 'equipes',
    'usuário', 'usuária', 'usuários', 'usuárias',
    'diretor', 'diretora', 'diretores', 'diretoras',
    'direção', 'direções', 'seção', 'seções',
    'ônibus', 'trem', 'celular', 'fone',
    # "legal" is excluded: a valid word in both dialects ("comprovativo
    # legal"), not just Brazilian slang for "cool".
}

WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+")


YAML_KEY = re.compile(r'^(\s*-?\s*)[a-z_]+:(\s|$)')


def strip_code(text):
    """Drop inline code, link targets, bare URLs and a leading YAML field
    name (e.g. "name:", "id:"): Markdown examples, file paths and the
    issue-form schema's own keywords are not the page's prose."""
    text = YAML_KEY.sub(r'\1', text, count=1)
    text = re.sub(r'`[^`]*`', ' ', text)
    text = re.sub(r'\]\([^)]*\)', ']', text)
    text = re.sub(r'https?://\S+', ' ', text)
    return text


def checked(path):
    return path.startswith(CHECKED_PREFIXES)


# -c core.quotepath=false: otherwise git wraps any path with an accented
# character in quotes and octal-escapes it (e.g. "docs/Wikin\303\241cios/..."),
# which would silently break the "+++ b/<path>" match below.
GIT = ['git', '-c', 'core.quotepath=false']


def diff_added_lines(ref):
    """(path, line number, text) for every line `git diff` against `ref`
    adds, restricted to tracked files this checker covers."""
    diff = subprocess.run(
        GIT + ['diff', '--unified=0', ref, '--'] + list(CHECKED_PREFIXES),
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    path = lineno = None
    for line in diff.splitlines():
        if line.startswith('+++ b/'):
            # git appends a trailing tab when the path itself contains a
            # space, to keep the unified-diff header unambiguous.
            path = line[len('+++ b/'):].rstrip('\t')
        elif line.startswith('@@'):
            m = re.search(r'\+(\d+)', line)
            lineno = int(m.group(1)) if m else None
        elif line.startswith('+') and path is not None and lineno is not None:
            yield path, lineno, line[1:]
            lineno += 1


def untracked_files():
    """Paths `git status` reports as untracked (new files not yet added)."""
    status = subprocess.run(
        GIT + ['status', '--porcelain', '--untracked-files=all'],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    for line in status.splitlines():
        if line.startswith('?? '):
            path = line[3:].strip().strip('"')
            if checked(path):
                yield path


def untracked_lines():
    for path in untracked_files():
        full = ROOT / path
        if full.is_file():
            for lineno, text in enumerate(
                    full.read_text(encoding='utf-8').splitlines(), 1):
                yield path, lineno, text


def flag(text):
    clean = strip_code(text)
    words = [w.lower() for w in WORD.findall(clean)]
    hits = sorted(set(w for w in words if w in ENGLISH_WORDS))
    hits += sorted(set(f'{w} (ortografia brasileira)' for w in words
                       if w in BRAZILIAN_WORDS))
    return hits


def check(ref):
    problems = []
    in_fence = {}
    for path, lineno, text in list(diff_added_lines(ref)) + list(
            untracked_lines()):
        if text.strip().startswith('```'):
            in_fence[path] = not in_fence.get(path, False)
            continue
        if in_fence.get(path):
            continue
        hits = flag(text)
        if hits:
            problems.append((path, lineno, hits, text.strip()))
    return problems


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
    problems = check(ref)
    if not problems:
        print('OK: nada de suspeito nas linhas novas ou alteradas.')
        return
    for path, lineno, hits, text in problems:
        print(f'AVISO {path}:{lineno}: {", ".join(hits)}')
        print(f'    {text}')
    print(f'\n{len(problems)} linha(s) para rever à mão antes de gravar.')
    sys.exit(1)


if __name__ == '__main__':
    main()
