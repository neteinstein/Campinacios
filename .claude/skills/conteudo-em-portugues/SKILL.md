---
name: conteudo-em-portugues
description: Manter em português europeu (ortografia anterior a 1990), nunca em inglês nem em português do Brasil, tudo o que se escreve no Wikinácios — o texto das páginas em docs/, os formulários de issue do GitHub, o README.md e o mkdocs.yml — e também tudo o resto que um agente escreve neste projecto: mensagens de commit, títulos e descrições de pull requests, comentários no GitHub e texto novo em skills, scripts ou outras ferramentas. Usar como última verificação antes de qualquer `git commit`/`git push` neste repositório, antes de abrir ou editar um pull request, sempre que perguntarem "está em português?", "isto pode ficar em inglês?" ou semelhante, e ao processar uma submissão (issue ou modelo colado) que chegou em parte em inglês ou noutro português.
---

# Writing and committing in Portuguese

The Wikinácios is a Portuguese-language archive: every page, category,
issue form and help text a visitor reads is written in European Portuguese,
in the pre-1990 spelling the original wiki used — Direcção, Director,
actualizar, contacto, equipa, Agosto with a capital — as
`docs/Wikinácios/Conteúdos.md` already asks of anyone editing. This
skill is about catching the exceptions before they get
committed: a paragraph pasted from an English source, a submission answered
in English by mistake, a machine translation that lands in Brazilian
spelling, or a stray English sentence in a new page or issue form.

This is about the **site's own content**: `docs/`, `.github/ISSUE_TEMPLATE/`,
`README.md` and `mkdocs.yml`'s visible strings (nav titles, theme labels).
A mesma regra aplica-se a tudo o resto que um agente escreve neste
projecto (a "Regra da língua" do `AGENTS.md`): mensagens de commit,
títulos e descrições de pull requests, comentários e respostas no GitHub,
e texto novo em `.claude/skills/`, `AGENTS.md`,
`.github/copilot-instructions.md` ou `scripts/` são sempre em português
europeu, nunca em inglês. Só fica como está o que não se traduz: nomes
próprios, letras e títulos de músicas em inglês, nomes de ficheiros,
comandos e identificadores de código. As ferramentas que ainda estão em
inglês passam para português quando forem editadas.

## Before writing

- Write new prose directly in Portuguese; don't draft in English and plan
  to translate later — a step that's easy to forget.
- Keep the orthography of the page you're editing or copying (regra 2 of
  `docs/Wikinácios/Conteúdos.md`): Director, Direcção, actualizar,
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
