---
title: "Sobre este arquivo"
---

# Sobre este arquivo

A Wikinácios foi a wiki dos Campinácios, criada em 2009 durante a
Revolução Campinácios v2.0 e mantida em MediaWiki. Este site foi gerado a
partir da cópia de segurança da base de dados MySQL da wiki pelo script
`scripts/mediawiki_to_markdown.py`.

## O que foi convertido

- A versão mais recente de cada página pública, em Markdown.
- Os redireccionamentos foram resolvidos: as ligações apontam directamente
  para a página de destino, e os nomes alternativos ficam em `aliases` no
  cabeçalho de cada ficheiro.
- As categorias têm uma página própria com a lista dos seus membros, e cada
  página mostra as páginas que ligam para ela.
- As páginas estão organizadas por pastas: acampamentos por ano, pessoas
  por inicial, encontros, cargos, movimento, categorias e as páginas sobre
  a própria wiki.

## O que ficou de fora

- As páginas que eram de acesso restrito na wiki (categoria *Restrita*) e
  as fichas dos locais de acampamento, que eram reservadas aos directores e
  contêm contactos privados.
- Contas de utilizador, palavras-passe, registos, páginas apagadas e o
  histórico de revisões.
- As imagens: o backup só tem a base de dados, por isso as páginas das
  imagens mostram apenas a descrição e os dados do ficheiro original.

## Como editar e publicar

Os ficheiros Markdown em `docs/` são agora a fonte do site e podem ser
editados directamente no GitHub. O site é construído com
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/) e publicado
no GitHub Pages pela GitHub Action em `.github/workflows/pages.yml` a cada
alteração no ramo `main` (em *Settings → Pages*, a fonte deve ser
*GitHub Actions*).

Para ver o site localmente:

```sh
pip install mkdocs-material
mkdocs serve
```

A pasta `docs/` também pode ser aberta como cofre no
[Obsidian](https://obsidian.md/), que mostra o grafo de ligações entre as
páginas.
