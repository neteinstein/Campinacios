# Sobre este arquivo

A Wikinácios foi a wiki dos Campinácios, criada em 2009 durante a
Revolução Campinácios v2.0 e mantida em MediaWiki. Este site foi gerado a
partir da cópia de segurança da base de dados MySQL da wiki pelo script
`scripts/mediawiki_to_markdown.py`.

## O que foi convertido

- A versão mais recente de cada página, em Markdown (as restritas cifradas,
  ver abaixo).
- Os redireccionamentos foram resolvidos: as ligações apontam directamente
  para a página de destino, e os nomes alternativos ficam em *Outros nomes*,
  no fim de cada página.
- As categorias têm uma página própria com a lista dos seus membros, e cada
  página mostra, no fim, as páginas que ligam para ela e uma tabela com as
  suas categorias.
- As páginas estão organizadas por pastas: acampamentos por ano, pessoas
  por inicial, encontros, cargos, movimento, categorias e as páginas sobre
  a própria wiki. [Todos os artigos](../Todos%20os%20artigos.md) lista-as
  todas, com os nomes alternativos.
- A página principal mantém a disposição que tinha na wiki.

## Páginas restritas

As páginas que na wiki eram de acesso restrito (categoria *Restrita*) e as
fichas dos [locais de acampamento](../Restrito/index.md), reservadas à
Direcção Nacional e aos directores, estão no site mas cifradas (AES-256):
o texto só aparece depois de se introduzir a palavra-passe, e nem o
repositório nem o site guardam o texto em claro. A palavra-passe fica
guardada no navegador até se fechar o separador, ou no dispositivo se se
escolher "Lembrar neste dispositivo".

Para mudar a palavra-passe, ou para editar uma página restrita:

```sh
pip install cryptography mkdocs-material
python3 scripts/restrito.py mudar-palavra-passe
python3 scripts/restrito.py abrir    # decifra para restrito-aberto/
python3 scripts/restrito.py fechar   # volta a cifrar e apaga restrito-aberto/
```

A segurança depende só da palavra-passe: quem tiver uma cópia do site pode
tentar adivinhá-la sem limite, por isso deve ser longa e aleatória.

## O que ficou de fora

- Contas de utilizador, palavras-passe, registos, páginas apagadas e o
  histórico de revisões, incluindo o autor e a data da última edição de
  cada página.
- A página "Main Page", que era a página de instalação do MediaWiki.
- As imagens: o backup só tem a base de dados, por isso as páginas das
  imagens mostram apenas a descrição e os dados do ficheiro original.

## Como editar e publicar

Os ficheiros Markdown em `docs/` são agora a fonte do site e podem ser
editados directamente no GitHub: ver
[Como adicionar conteúdo?](Ajuda/Conte%C3%BAdos.md#como-adicionar-conteúdo).
O site é construído com
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/) e publicado
no GitHub Pages pela GitHub Action em `.github/workflows/pages.yml` a cada
alteração no ramo `main`.

Em *Settings → Pages → Build and deployment*, a *Source* tem de ser
**GitHub Actions**. Com *Deploy from a branch*, o GitHub publica também uma
versão Jekyll do repositório que substitui este site, com outra página
principal e ligações partidas.

Para ver o site localmente:

```sh
pip install mkdocs-material
mkdocs serve
```

A pasta `docs/` também pode ser aberta como cofre no
[Obsidian](https://obsidian.md/), que mostra o grafo de ligações entre as
páginas.
