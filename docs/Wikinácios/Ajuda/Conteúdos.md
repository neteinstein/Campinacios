---
title: "Conteúdos"
wiki_id: 155
last_edited: "2009-02-09T02:03:48Z"
last_editor: "Neteinstein"
---

# Conteúdos

**Bem-vindo à Wiki dos [Campinácios](../../Movimento/Campin%C3%A1cios.md)!**

*Este sitio faz parte da [Revolução Campinácios v2.0](../../Movimento/Revolu%C3%A7%C3%A3o%20Campin%C3%A1cios%20v2.0.md)!*

Funciona da mesma maneira que a famosa Wikipédia, com o mesmo "motor", e com uma filosofia semelhante...reunir o conhecimento e história dos Campinácios num sítio, aberto ao público.

Qualquer um de vocês, desde que se registe, pode adicionar/editar informações sobre acampamentos, encontros...

A ideia é guardar a máxima informação sobre cada acampamento/encontro, como o nome, data, equipa de animação, hino, imaginarium... a imaginação é o limite.

**As brincadeiras serão punidas imediatamente com a expulsão da Wikinácios!**

## Regras

Antes de mais é necessário ter a noção que para escrever um artigo aqui devemos seguir algumas regras. E porque?
Primeiro que tudo porque quando andamos a navegar por uma categoria, por exemplo [Animadores](../../Categorias/Animadores.md) estamos à espera que cada um dos animadores tenha a mesma organização para ser mais fácil de ler... isto aplica-se a tudo o resto.

### As 5 Regras

**1. Categorias**<br>
As categorias tem o nome no plural.

**2. Artigos**<br>
Os artigos sobre animadores, acampamentos, tema do ano, CIFAs, ou qualquer outro tema devem seguir o esquema dos artigos anteriores, ou seja, para escreverem algo abram outro artigo do mesmo tema, vão a editar, copiem, colem e alterem OS DADOS e não o esquema.

Os artigos pretendem descrever um tema, ou assunto singular, que não contém vários eventos. Por exemplo [OrienTu](../../Acampamentos/2008/OrienTu.md) é um acampamento único, faz sentido que seja posto num artigo e não seja uma categoria.

Acampamentos, fizemos já centenas... dai faz sentido que seja uma categoria onde apareça a explicar o que é um acampamento e os vários que já fizemos.

**3.Alterações**<br>
Não se toleram alterações persistentes de 2 utilizadores no mesmo artigo, imaginem um adiciona um acampamento o outro remove, e entram num ciclo persistente assim...

**4. Quem manda aqui somos nós**<br>
Estamos numa ditadura, as imposições feitas pelos administradores deste sítio são lei.

**5. Quem manda?**<br>
Ver [Staff](../../Movimento/Staff.md)

## Como adicionar conteúdo?

A Wikinácios já não corre em MediaWiki: é um site feito a partir dos
ficheiros do repositório
[neteinstein/Campinacios](https://github.com/neteinstein/Campinacios) no
GitHub. Cada artigo é um ficheiro de texto `.md`
([Markdown](https://docs.github.com/pt/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax))
dentro da pasta `docs/`, e o site actualiza-se sozinho um ou dois minutos
depois de cada alteração entrar no ramo `main`.

Para editar é preciso uma conta no GitHub, que é gratuita. Quem tem
permissão de escrita no repositório (o [Staff](../../Movimento/Staff.md))
grava as alterações directamente. Os outros fazem uma proposta de alteração
(*pull request*) que o Staff revê e aceita: as regras acima continuam a
valer.

### Como se edita um artigo?

1. Abra o artigo no site e carregue no lápis (*Editar esta página*) no
   canto superior direito. Abre-se o ficheiro no GitHub, já em modo de
   edição (se pedir, carregue em *Fork this repository*).
2. Faça as alterações. O separador *Preview* mostra como vai ficar.
3. Carregue em **Commit changes...**, escreva numa frase o que mudou e
   confirme. Sem permissão de escrita, o botão chama-se
   **Propose changes** e, a seguir, **Create pull request**.

### Como se adiciona um artigo?

Antes de mais é preciso saber se o artigo já existe: use a caixa
**Buscar** no topo do site ou [Todos os artigos](../../Todos%20os%20artigos.md),
que também lista as alcunhas e os nomes alternativos.

Se não existir, entre no GitHub na pasta certa dentro de `docs/`:

| Artigo | Pasta |
| --- | --- |
| Acampamento | `docs/Acampamentos/<ano>/` |
| Animador, jesuíta ou outra pessoa | `docs/Pessoas/<inicial>/` |
| Encontro | `docs/Encontros/` |
| Cargo | `docs/Cargos/` |
| Tudo o resto | `docs/Movimento/` |

Carregue em **Add file → Create new file** e dê ao ficheiro o nome do
artigo terminado em `.md`, por exemplo `Carlos Nunes.md`. Copie um artigo
do mesmo tipo (regra 2) e altere os dados, não o esquema. O ficheiro começa
por um cabeçalho com o título:

```markdown
---
title: "Carlos Nunes"
---

# Carlos Nunes

Carlos Nunes é animador dos Campinácios desde...
```

Grave como acima (**Commit changes...** ou **Propose changes**). Por fim,
ponha ligações para o artigo novo: no `index.md` da pasta, na página da
categoria em `docs/Categorias/` e nos artigos que falam dele. Estas listas
não se actualizam sozinhas, mas a pesquisa do site encontra-o logo.

### Como se escreve?

| Na wiki | Agora, em Markdown |
| --- | --- |
| `'''negrito'''` | `**negrito**` |
| `''itálico''` | `*itálico*` |
| `== Secção ==` | `## Secção` |
| `* item` | `- item` |
| `[[Pedro Vicente]]` | `[Pedro Vicente](<../../Pessoas/P/Pedro Vicente.md>)` |
| `[http://exemplo.pt texto]` | `[texto](http://exemplo.pt)` |

As ligações entre artigos levam o caminho do ficheiro a partir da pasta do
artigo onde se escreve: `../` sobe uma pasta. Com os `< >` à volta, o
caminho pode ter espaços e acentos. Se uma ligação apontar para um ficheiro
que não existe, a publicação falha (o GitHub mostra um ✗ vermelho no
*commit* e avisa por e-mail) e o site fica como estava até se corrigir.

Para uma imagem, carregue o ficheiro com **Add file → Upload files** para
`docs/assets/imagens/` e escreva
`![legenda](<../../assets/imagens/foto.jpg>)`, com o caminho a partir do
artigo.

### Como se cria uma categoria?

Uma categoria é uma página em `docs/Categorias/` com a lista dos seus
artigos, como [Animadores](../../Categorias/Animadores.md). Crie o ficheiro
com essa lista e, no fim de cada artigo da categoria, acrescente-a à linha
**Categorias:**.

### Como se cria uma subcategoria de uma categoria?

Na página da categoria-mãe, acrescente a subcategoria à secção
*Subcategorias*.

### E as páginas restritas?

Estão cifradas e não se editam no GitHub. Ver
[Sobre este arquivo](../Sobre%20este%20arquivo.md#páginas-restritas).
