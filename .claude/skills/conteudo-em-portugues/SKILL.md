---
name: conteudo-em-portugues
description: Keep everything committed to the Wikinácios site itself — page text under docs/, the GitHub issue forms, README.md and mkdocs.yml — in the site's own European (pre-1990) Portuguese, never English or Brazilian Portuguese. Use it as the last check before any `git commit`/`git push` in this repo that touches those files, whenever asked "está em português?", "isto pode ficar em inglês?" or similar, and when processing a submission (issue or pasted template) that arrived partly in English or in a different Portuguese. It does not apply to skills, scripts or other project tooling, which stay in English by this project's own convention.
---

# Writing and committing in Portuguese

The Wikinácios is a Portuguese-language archive: every page, category,
issue form and help text a visitor reads is written in European Portuguese,
in the pre-1990 spelling the original wiki used — Direcção, Director,
actualizar, contacto, equipa, Agosto with a capital — as
`docs/Wikinácios/Ajuda/Conteúdos.md` already asks of anyone editing. This
skill is about catching the exceptions before they get
committed: a paragraph pasted from an English source, a submission answered
in English by mistake, a machine translation that lands in Brazilian
spelling, or a stray English sentence in a new page or issue form.

This is about the **site's own content**: `docs/`, `.github/ISSUE_TEMPLATE/`,
`README.md` and `mkdocs.yml`'s visible strings (nav titles, theme labels).
It does not apply to `.claude/skills/`, `scripts/` or any other project
tooling — those are written in English, this project's own convention for
instructions to Claude and for code, and translating them would work
against every other skill in this repo.

## Before writing

- Write new prose directly in Portuguese; don't draft in English and plan
  to translate later — a step that's easy to forget.
- Keep the orthography of the page you're editing or copying (regra 2 of
  `docs/Wikinácios/Ajuda/Conteúdos.md`): Director, Direcção, actualizar,
  contacto, equipa — not Diretor, Direção, atualizar, contato, equipe,
  which are the Brazilian spellings and don't belong here even though
  they're also Portuguese.
- Proper nouns stay as they are: a person's name, a camp's own name
  ("OrienTu", "TufarfarAway") or a place name is never translated.
- A submission (GitHub issue or pasted template, see the
  `processar-contributo` skill) that arrives in English, in Brazilian
  Portuguese, or mixed: translate the content into the site's Portuguese
  when you apply it to a page; never publish it as received. Say so to the
  sender when you answer.

## Before committing

Run the checker on whatever is staged or changed, from the repository
root:

```sh
python3 .claude/skills/conteudo-em-portugues/scripts/verificar_portugues.py
```

It looks at the lines you added or changed (via `git diff`, plus any new
untracked file) in `docs/`, `.github/ISSUE_TEMPLATE/`, `README.md` and
`mkdocs.yml`, and prints a warning for common English words and for the
Brazilian spellings this project doesn't use (`atualizar`, `contato`,
`equipe`, `diretor`, `direção`…). It is a word list, not a language
detector: it can miss an English sentence made only of short words, and it
can flag a false positive (an English proper noun quoted in an example, a
Portuguese sentence that happens to contain one of the flagged forms
another way). Read every line it prints and judge for yourself — the tool
is a net for a careless paste, not the last word. It never edits a file;
fix what it finds, run it again until it prints `OK`, and only then commit.

If the diff spans a commit you already made (rare — normally run this
before committing), pass the commit's parent: `verificar_portugues.py
HEAD~1`.

## Where this fits with the other skills

`novo-acampamento`, `nova-pessoa` and `processar-contributo` end with their
own validators (`validar.py`, `pessoas.py verificar`, `mkdocs build
--strict`); run this checker alongside them, as part of the same
pre-commit pass, whenever any of them changes a file this skill covers.
