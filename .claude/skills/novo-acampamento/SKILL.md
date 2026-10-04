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
any dates, place or theme. Os participantes não vão na página do campo, que
só tem a equipa de animação: entram só na página de cada participante que já
a tem (`nova-pessoa`). Don't invent what isn't given; a one-line intro
("O X foi um acampamento de [Bicicletas](...) realizado em 2012.") is fine.

As letras de músicas (hino, genérico da novela…) nunca ficam na página do
campo: vão para `docs/Movimento/Cantinácio/Campinácios.md` e o campo liga
para lá (ver a skill `processar-contributo`, "Músicas").

Look up each person with the `nova-pessoa` skill
(`.claude/skills/nova-pessoa/scripts/pessoas.py procurar "Nome"`), which
finds the same or similar names in pages, nicknames and other camps, and
ask the user before linking whenever it finds any (e.g. "Luís Onofre Pinto"
is the page "Luís Onofre"; the two Gonçalo Carvalho are different people).
Leave new names as plain text unless the user asks for pages.

## 2. Write the camp page

`docs/Acampamentos/<ano>/<Nome>.md`. Copy the shape of a recent camp,
e.g. `docs/Acampamentos/2011/Esperança.md`: intro, `### Animadores`
(`- [Director](../../Cargos/Director.md) - [Pessoa](...)`), nunca
`### Participantes`, then the footer:

```markdown
---

| Categorias |
| --- |
| [Acampamentos](../../Categorias/Acampamentos.md) |
| [Acampamentos de <ano>](../../Categorias/Acampamentos%20de%20<ano>.md) |
| [<Escalão>](../../Categorias/<Escalão>.md) |
```

**Animadores Livres e Animadores de Equipa** ficam cada um numa **só linha**,
com todos os nomes da equipa, nunca uma linha por pessoa: o cargo no plural
("Animadores Livres", "Animadores de Equipa") se forem vários, no singular
se for só um, e os nomes separados por vírgulas com "e" antes do último
(`- [Animadores Livres](../../Cargos/Animador%20Livre.md) - A, B e C`). O
mesmo vale ao acrescentar uma equipa a um campo que já a tem: junta-se à
linha existente em vez de abrir outra. O validador falha se houver duas
linhas do mesmo cargo ou o cargo no singular com vários nomes.
Director, Mamã, Capelão, Tio/Tia e os restantes cargos mantêm uma linha por
pessoa.

## 3. List it everywhere

The two lists the validator checks first, because they are what readers
browse:

- **`docs/Categorias/Acampamentos.md`**
  - the camps-by-year table: add the camp to the `| <ano> |` row under its
    escalão, as `<li>**<Escalão>**<ul><li>[Nome](../Acampamentos/<ano>/Nome.md)</li></ul></li>`;
    um ano novo ganha uma linha nova a seguir à do ano anterior
    (`| <ano> | <ul>…</ul> | *tema* | <ul><li>local</li></ul> |`, com as
    células vazias se não se souber);
  - `## Páginas nesta categoria (N)`: insert the link in title order and
    add 1 to N.
- **`docs/Acampamentos/index.md`**: shows the same content as
  `docs/Categorias/Acampamentos.md` (the same table, subcategories and page
  list, links written the same way), so make the same two edits there.
- **Local de campo** (regra): sempre que o campo tiver local de campo —
  dado pelo utilizador, pelo formulário ("Local de campo") ou escrito na
  página do campo —, esse local entra na última coluna da tabela
  ([Locais de Acampamento](https://campinacios.pedrovicente.pt/Acampamentos/index.html)),
  na linha `| <ano> |` do ano do campo, em `docs/Acampamentos/index.md` **e**
  em `docs/Categorias/Acampamentos.md`, como mais um
  `<li>…</li>` dentro do `<ul>` dessa célula. Se o local já lá estiver
  nesse ano (outro campo no mesmo sítio), não se repete. Se tiver ficha em
  `docs/Restrito/Locais de Acampamento/`, liga-se a ela com o título exacto
  da ficha (`[Quinta da Adaúfa (Silgueiros,Viseu)](../Restrito/Locais%20de%20Acampamento/Quinta%20da%20Ada%C3%BAfa%20%28Silgueiros%2CViseu%29.md)`),
  e o campo entra em `## Acampamentos` da ficha (com `scripts/restrito.py`,
  ver `processar-contributo`); se não tiver, fica em texto simples. Só o
  nome do local: nunca indicações, coordenadas nem contactos.

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
  **Participante**. Um participante com página não entra na equipa do campo;
  se é animador, o campo ganha-o em `## Participantes que se tornaram
  animadores`, e as páginas de `docs/Cargos/` ganham as pessoas em
  `## Pessoas com este cargo`. Ambas se escrevem com
  `python3 .claude/skills/nova-pessoa/scripts/pessoas.py secoes` (ver
  `nova-pessoa`), não à mão.
  Same for the role pages in `docs/Cargos/` (Director, Mamã, …).
- `docs/Todos os artigos.md`: the camp under its letter, and 1 more in the
  "N artigos" count; the home page `docs/index.md` count (`**[N artigos]**`)
  too.
- `docs/assets/graph.json` (o grafo): não se edita à mão; depois de mexer em
  páginas ou ligações, corra `python3 scripts/actualizar_grafo.py`.

For a rename, move or deletion, update the same places the other way round.

## 4. Validate

```sh
python3 .claude/skills/novo-acampamento/scripts/validar.py "docs/Acampamentos/<ano>/<Nome>.md"
python3 .claude/skills/nova-pessoa/scripts/pessoas.py reciprocas "docs/Acampamentos/<ano>/<Nome>.md"
mkdocs build --strict
```

`reciprocas` confirma que cada pessoa da equipa tem o campo na sua página,
e o contrário, e que as listas geradas dos campos e dos cargos estão
certas. Os participantes não entram na equipa do campo.

The validator checks the table row, the category list and its count, que
`docs/Acampamentos/index.md` has the same table rows, page list and count
as the category, the year's index and the nav. Fix every `ERRO` and run it again until it prints `OK`; then the
strict build catches any broken link. `validar.py --todos` checks every
camp; gaps the original wiki already had are listed in `legado.txt` and
don't fail — never add a new camp there.

Then tell the user what was added and where, what was left as plain text,
and anything you had to assume.

## Recentes

Toda a alteração a uma página tem de ficar reflectida na página
[Recentes](../../../docs/Recentes.md). Essa página não se edita à mão: lê o
histórico do git e reescreve-se a cada publicação. Por isso, a alteração tem
de estar num commit (ficheiros em `docs/`) e, antes de dar o trabalho por
terminado, confirma-se:

```sh
python3 scripts/actualizar_recentes.py   # depois do commit
grep "<nome da página>" docs/Recentes.md # as páginas mexidas têm de aparecer
git restore docs/Recentes.md             # a publicação volta a gerá-la
```

As páginas restritas, os índices, as categorias, `Wikinácios/` e as páginas
geradas não aparecem nunca em Recentes; e só entram as 100 mais recentes.
