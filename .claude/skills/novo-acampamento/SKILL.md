---
name: novo-acampamento
description: Add a camp (acampamento) to the Wikinácios site in this repo and validate it is listed everywhere a camp must appear — above all in the camps-by-year table and page list of docs/Categorias/Acampamentos.md and in its copy, docs/Acampamentos/index.md. Use this whenever a camp page under docs/Acampamentos/ is created, renamed, moved to another year or deleted, e.g. "add a new camp in 2012 called X", "novo acampamento", "cria o campo Y de Bicicletas", "this camp was actually in 2008", even if the user only gives a name, a year and a team and never mentions the lists.
---

# Adding a camp to the Wikinácios

The site is plain Markdown built by MkDocs. Nothing generates the lists of
camps: the old wiki's converter wrote them once and they are kept by hand
since (never re-run `scripts/mediawiki_to_markdown.py`; it would regenerate
`docs/` from the 2010 backup and erase every later edit). A camp page that
is missing from a list still builds — `mkdocs build --strict` only catches
broken links — it just can't be found. So every camp edit ends with the
validator below.

## 1. Gather what the user gave

Name, year, escalão (Triciclos, Trotinetas, Bicicletas, Lambretas,
Calhambeques, Formação de Animadores), team with roles, participants, and
any dates, place or theme. Don't invent what isn't given; a one-line intro
("O X foi um acampamento de [Bicicletas](...) realizado em 2012.") is fine.

Look up each person with the `nova-pessoa` skill
(`.claude/skills/nova-pessoa/scripts/pessoas.py procurar "Nome"`), which
finds the same or similar names in pages, nicknames and other camps, and
ask the user before linking whenever it finds any (e.g. "Luís Onofre Pinto"
is the page "Luís Onofre"; the two Gonçalo Carvalho are different people).
Leave new names as plain text unless the user asks for pages.

## 2. Write the camp page

`docs/Acampamentos/<ano>/<Nome>.md`. Copy the shape of a recent camp,
e.g. `docs/Acampamentos/2011/Esperança.md`: intro, `### Animadores`
(`- [Director](../../Cargos/Director.md) - [Pessoa](...)`),
`### Participantes` if given, `## Páginas que ligam para aqui` (the pages
you are about to make link here, sorted by title), then the footer:

```markdown
---

| Categorias |
| --- |
| [Acampamentos](../../Categorias/Acampamentos.md) |
| [Acampamentos de <ano>](../../Categorias/Acampamentos%20de%20<ano>.md) |
| [<Escalão>](../../Categorias/<Escalão>.md) |
```

## 3. List it everywhere

The two lists the validator checks first, because they are what readers
browse:

- **`docs/Categorias/Acampamentos.md`**
  - the camps-by-year table: add the camp to the `| <ano> |` row under its
    escalão, as `<li>**<Escalão>**<ul><li>[Nome](../Acampamentos/<ano>/Nome.md)</li></ul></li>`;
    a new year gets a new row after the previous year
    (`| <ano> | <ul>…</ul> | *tema* | <ul><li>local</li></ul> |`, empty cells
    if unknown);
  - `## Páginas nesta categoria (N)`: insert the link in title order and
    add 1 to N.
- **`docs/Acampamentos/index.md`**: shows the same content as
  `docs/Categorias/Acampamentos.md` (the same table, subcategories and page
  list, links written the same way), so make the same two edits there.

And the rest of the year and cross-references:

- `docs/Acampamentos/<ano>/index.md`: `- [Nome](Nome.md) — <Escalão>`,
  sorted; create it (`# <ano>` heading) for a new year.
- `mkdocs.yml` nav, for a new year: `    - "<ano>": Acampamentos/<ano>/index.md`.
- `docs/Categorias/Acampamentos de <ano>.md` (create it for a new year, and
  add it to `docs/Categorias/index.md` and to the `## Subcategorias` of
  `docs/Categorias/Acampamentos.md`), and the escalão's category page
  (`## Páginas nesta categoria (N)`).
- Each linked person: add `    - <ano> [Nome](…) - [Cargo](…)` under
  **Animador/Animadora** (team) or `    - <ano> [Nome](…)` under
  **Participante**, and the camp to their `## Páginas que ligam para aqui`.
  Same for the role pages in `docs/Cargos/` (Director, Mamã, …).
- `docs/Todos os artigos.md`: the camp under its letter, and 1 more in the
  "N artigos" count; the home page `docs/index.md` count (`**[N artigos]**`)
  too.
- Optionally `docs/assets/graph.json`: a node for the camp and its links.

For a rename, move or deletion, update the same places the other way round.

## 4. Validate

```sh
python3 .claude/skills/novo-acampamento/scripts/validar.py "docs/Acampamentos/<ano>/<Nome>.md"
mkdocs build --strict
```

The validator checks the table row, the category list and its count, that
`docs/Acampamentos/index.md` has the same table rows, page list and count
as the category, the year's index and the nav. Fix every `ERRO` and run it again until it prints `OK`; then the
strict build catches any broken link. `validar.py --todos` checks every
camp; gaps the original wiki already had are listed in `legado.txt` and
don't fail — never add a new camp there.

Then tell the user what was added and where, what was left as plain text,
and anything you had to assume.
