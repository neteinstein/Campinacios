---
name: nova-pessoa
description: Add a person (animador, participante, jesuíta, director…) to the Wikinácios in this repo without duplicating or mixing people up. Before creating a person page or linking a name anywhere, search the existing people, their other names, the disambiguation pages and every camp and encontro for the same or a similar name, ask the user whether it is the same person, then either link to the existing page or create a separate page that can't be confused with the other one. Use this whenever a person is added or named — "cria a página da Ana Martins", "add these participants to the 2012 camp", "o João Silva também animou o Farol em 2003", renaming a person, or as part of adding a camp — even if the user never mentions duplicates.
---

# Adding a person to the Wikinácios

Names repeat a lot here: there are two Gonçalo Carvalho, three Miguel
Martins, a "Luís Onofre" who is also "Luís Onofre Pinto". Both mistakes are
silent: a second page for someone who already has one splits their history
in two, and linking a name to the wrong page merges two people. So search
first, let the user decide, and leave the pages so the next reader can't
mix them up either.

## "SJ" is not part of a name

"SJ" (Sociedade de Jesus) after a name is a title, not part of it. Never
include it in a page title, a link label, an `Outros nomes` entry, or any
other place a name is being treated as a name (search terms, disambiguation
notes, etc.). It may only appear as plain, unlinked text written right
after the person's name in running prose (e.g. "o Padre André Fontes, SJ,
animou..."), never as, or inside, a link.

## 1. Search

For every person being added or named:

```sh
python3 .claude/skills/nova-pessoa/scripts/pessoas.py procurar "Nome Apelido"
```

It compares without accents or case and reports, with where each is used:

- person pages with the same name, the same first and last name, one name
  inside the other, or a likely typo — with their other names (nicknames)
  and the camps that link them;
- disambiguation pages (`docs/Movimento/Desambiguação/`) for the name;
- links in camps and encontros under that name that go to someone else;
- the name written as plain text (no page) in camps and encontros.

Exit 0 means the name is new: go to 4 if a page is wanted, otherwise just
write the name. Also search any nickname the user gives.

## 2. Ask — never guess

If anything matched, ask the user before linking or creating, even for an
identical name (both Gonçalo Carvalho are real). Give enough to decide:
each candidate's page, its first line (college, years) and the camps it is
linked in, and the plain-text mentions. For example:

> "Ana Martins" já existe: animadora do CSJB desde 2005 (Nómada 2006,
> Entre ASPAS 2008, Caminho 2009…). É a mesma pessoa?

Offer one option per candidate plus "outra pessoa" (use a multiple-choice
prompt if your tool supports one). For plain-text mentions, ask which of
them are this person when the name is common.

## 3a. Same person: link

- Link the name to the existing page (the label may keep the user's
  spelling).
- A different spelling or nickname becomes another name: add it to the
  page's `**Outros nomes:** a · b` line (right after the footer's `---`;
  create it if missing), and to `docs/Todos os artigos.md` as
  `- *Alcunha* → [Nome](Pessoas/L/Nome.md)` under its letter, adding 1 to
  the "nomes alternativos" count.
- Plain-text mentions the user confirmed become links.
- On the person's page, add the camp to the list (`    - <ano> [Camp](…)`
  under **Participante**, or `… - [Cargo](…)` under **Animador/Animadora**).
  Depois corra `pessoas.py secoes` (ver "Listas geradas", no fim): as
  listas dos cargos e dos campos escrevem-se sozinhas.
  Na página do **campo**, um Animador Livre ou de Equipa novo junta-se à
  linha única do seu cargo ("Animadores Livres - A, B e C"), passando o
  cargo para o plural se antes era só um; nunca se abre uma linha por
  pessoa (ver `novo-acampamento`). A camp under
  **Participante** for someone who already has a page as Animador(a) is
  fine to add even outside Calhambeques/Formação de Animadores — the page
  itself proves they're an adult, which is what that privacy restriction
  (`processar-contributo` skill, step 2) exists to protect; it does not
  apply to them.
- If the match was only plain text (no page yet) and a page is wanted,
  create it (4) and link those mentions.

## 3b. Another person: keep them apart

- **Name the page so it differs.** Never reuse an existing page's name. Ask
  for the fuller name (a second first name or surname, as the wiki did:
  "Gonçalo Luís Carvalho" / "Gonçalo Fonseca Carvalho"); only without one
  add a qualifier: "Ana Martins (CC)".
- **A note at the top of both pages**, right under the `# Title`, in the
  old wiki's words:
  `*Nota: Este artigo é sobre Ana Sofia Martins, animadora do CC. Se procura Ana Martins, animadora do CSJB desde 2005, consulte [Ana Martins](../A/Ana%20Martins.md).*`
- **Three or more people** with the name, or none of them holding the bare
  name: a disambiguation page `docs/Movimento/Desambiguação/<Nome>.md`,
  shaped like `Gonçalo Carvalho.md` there (notice line, "**X** pode ser:",
  one line per person with college and years). The notes then say
  `*Nota: Há outras pessoas chamadas X: ver [X](…/Desambigua%C3%A7%C3%A3o/X.md).*`
  List the page in `docs/Movimento/Desambiguação/index.md`,
  `docs/Categorias/Desambiguação.md` and `docs/Todos os artigos.md`.
- **Check every camp mention** the search listed for the shared name:
  each link must go to the right person — re-point the wrong ones, and
  link plain mentions only once the user said whose they are.

## 4. A new page

`docs/Pessoas/<inicial>/<Nome>.md` (initial without accent: Á → A), shaped
like `docs/Pessoas/J/João Eiró.md`: `# Nome`, the note if any, an intro if
given, `### Acampamentos` with **Participante** / **Formação** /
**Animador(a)** lists, then the footer `---` and `| Categorias |` table (Animadores,
Animadores do <colégio> if known, Jesuítas…). As relações de parentesco ou de casamento (irmãos, pais, filhos, cônjuges…)
escrevem-se sempre numa secção `### Família`, nunca soltas no fim da página
nem noutra secção.
Then list it: the letter's
`index.md` (sorted), its count in `docs/Pessoas/index.md`, each category's
`## Páginas nesta categoria (N)` (sorted, N+1), `docs/Todos os artigos.md`
("N artigos" +1) and the home page count in `docs/index.md`; o grafo
(`docs/assets/graph.json`) não se edita à mão: corra
`python3 scripts/actualizar_grafo.py`.

## 5. Validate

```sh
python3 .claude/skills/nova-pessoa/scripts/pessoas.py verificar "Nome" "Nome parecido"
python3 .claude/skills/nova-pessoa/scripts/pessoas.py procurar "Nome"
python3 .claude/skills/nova-pessoa/scripts/pessoas.py reciprocas "docs/Pessoas/<L>/<Nome>.md" "docs/Acampamentos/<ano>/<Campo>.md"
mkdocs build --strict
```

`reciprocas` verifica as páginas que mexeu (ou todas, com `--todos`):
quem a página de uma pessoa diz ter sido animador num campo tem de estar
na equipa desse campo, quem está na equipa de um campo tem de o ter em
`### Acampamentos`. Uma ligação para uma página de desambiguação na equipa de
um campo também falha: aponte-a para a pessoa. Quem foi **Participante**
ou esteve em **Formação** não tem de aparecer no campo, porque os campos
só listam a equipa.

`verificar` fails if two person pages share a name or if a similar-named
pair lacks the note that tells them apart; fix every `ERRO`. Run `procurar`
again to see that the camps now link the right page. If camps changed, also
run the `novo-acampamento` validator. `verificar --todos` checks everyone;
pairs the original wiki already had are in `legado.txt` and don't fail —
never add a new pair there.

## Listas geradas

Já não há "Páginas que ligam para aqui" em nenhuma página. Só duas listas
se escrevem a partir das páginas das pessoas, antes do rodapé:

- **"Pessoas com este cargo"**, em cada página de `docs/Cargos/`: só
  pessoas (nunca campos), todas as que ligam para o cargo em qualquer sítio
  da sua página;
- **"Participantes que se tornaram animadores"**, nos campos: as pessoas
  com a categoria Animadores que têm o campo em **Participante** ou
  **Formação** (quem foi animador do campo está na equipa, não aqui). Um
  campo sem ninguém assim não tem a secção.

Não se escrevem à mão: depois de mexer numa pessoa, num cargo ou num campo,
corra

```sh
python3 .claude/skills/nova-pessoa/scripts/pessoas.py secoes
```

(muda só as páginas que mudam, e tira a antiga "Páginas que ligam para
aqui" dessas páginas). `reciprocas` falha se uma destas listas estiver
desactualizada ou se ainda existir a secção antiga.

Finally tell the user who was linked to whom, which pages were created or
got a note, and which names stayed plain text.

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
geradas não aparecem nunca em Recentes; e só entram as 50 mais recentes.
