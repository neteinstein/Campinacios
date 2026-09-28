# Conteúdos

**Bem-vindo à Wiki dos [Campinácios](../Movimento/Campin%C3%A1cios.md)!**

*Este sitio faz parte da [Revolução Campinácios v2.0](../Movimento/Revolu%C3%A7%C3%A3o%20Campin%C3%A1cios%20v2.0.md)!*

Funciona da mesma maneira que a famosa Wikipédia, com o mesmo "motor", e com uma filosofia semelhante...reunir o conhecimento e história dos Campinácios num sítio, aberto ao público.

Qualquer um de vocês, desde que se registe, pode adicionar/editar informações sobre acampamentos, encontros...

A ideia é guardar a máxima informação sobre cada acampamento/encontro, como o nome, data, equipa de animação, hino, imaginarium... a imaginação é o limite.

**As brincadeiras serão punidas imediatamente com a expulsão da Wikinácios!**

## Regras

Os artigos seguem regras de organização e escrita, para ficarem todos
parecidos e fáceis de ler — ver [Regras de Conteúdo](Regras%20de%20Conte%C3%BAdo.md).
São seguidas pelos [Contribuidores](Contribuidores.md) quando escrevem ou
publicam um artigo; quem só quer [pedir uma alteração](#pedir-uma-alteracao)
não precisa de as conhecer.

## Como pedir uma alteração? {#pedir-uma-alteracao}

Sabe alguma coisa sobre um acampamento ou uma pessoa que falta na
Wikinácios, ou que está errada? Não precisa de mexer em ficheiros nem de
saber Markdown: basta abrir um pedido (uma *issue*) no GitHub a dizer o que
quer que se acrescente, corrija ou remova. Um dos
[Contribuidores](Contribuidores.md) trata depois de pôr a informação no
site.

1.  Abra a página de pedidos:
    [github.com/neteinstein/Campinacios/issues](https://github.com/neteinstein/Campinacios/issues).
    Se nunca usou o GitHub, é preciso criar uma conta (gratuita) — o próprio
    site pede para o fazer quando carregar em **Sign up**.

    ![Abrir o separador Issues do repositório](<../assets/imagens/pedido-passo1-issues.svg>)

2.  Carregue no botão verde **New issue**.

    ![Carregar em New issue](<../assets/imagens/pedido-passo2-novo-pedido.svg>)

3.  Escolha o modelo que corresponde ao que quer pedir (Acampamento, Pessoa,
    Local de Acampamento...) e carregue em **Get started**.

    ![Escolher o modelo certo](<../assets/imagens/pedido-passo3-escolher-modelo.svg>)

4.  Preencha só o que souber — os campos que não sabe ficam em branco — e
    carregue em **Submit new issue**.

    ![Preencher e enviar o pedido](<../assets/imagens/pedido-passo4-enviar.svg>)

E está feito: o pedido fica visível aos Contribuidores, que o revêem e
acrescentam a informação ao site. Não precisa de fazer mais nada.

Os modelos disponíveis:

- [🏕️ Acampamento](https://github.com/neteinstein/Campinacios/issues/new?template=acampamento.yml):
  um acampamento novo, ou informação para um que já existe.
- [🙋 Pessoa](https://github.com/neteinstein/Campinacios/issues/new?template=pessoa.yml):
  um animador, jesuíta ou outra pessoa do movimento, nova ou que já tem
  página.
- [🔗 Pessoas em Acampamentos](https://github.com/neteinstein/Campinacios/issues/new?template=pessoas-em-acampamentos.yml):
  ligar uma pessoa e um acampamento que já têm página (quem animou o quê,
  quem esteve lá).
- [🙋 Participantes de um Acampamento](https://github.com/neteinstein/Campinacios/issues/new?template=participantes.yml):
  a lista de participantes de um Calhambeques ou Formação de Animadores
  que já tem página.
- [🏞️ Local de Acampamento](https://github.com/neteinstein/Campinacios/issues/new?template=local-de-acampamento.yml):
  avisar que falta a ficha de um local, ou que local se usou num
  acampamento — **nunca com indicações, coordenadas ou contactos**, que
  ficam para depois, em privado com os Contribuidores.
- [🔒 Remoção de Informação](https://github.com/neteinstein/Campinacios/issues/new?template=remocao-de-informacao.yml):
  pedir que a sua própria informação seja removida, corrigida ou ocultada
  do site.

O que se envia por um pedido do GitHub fica público. Não escreva contactos
(telefones, e-mails, moradas), indicações para chegar aos locais de campo
nem nomes de participantes menores de idade, e só envie informação sobre
outra pessoa se ela concordar.

Prefere não usar o GitHub, ou tem coisas privadas a dizer (indicações,
coordenadas, contactos)? Escreva antes a um dos
[Contribuidores](Contribuidores.md):
[Pedro Vicente](../Pessoas/P/Pedro%20Vicente.md) ou
[Tiago Bahia](../Pessoas/T/Tiago%20Bahia.md).

## Editar directamente

Quem tem conta no GitHub e prefere editar os ficheiros do site pode fazê-lo
directamente, sem passar por um pedido.

A Wikinácios já não corre em MediaWiki: é um site feito a partir dos
ficheiros do repositório
[neteinstein/Campinacios](https://github.com/neteinstein/Campinacios) no
GitHub. Cada artigo é um ficheiro de texto `.md`
([Markdown](https://docs.github.com/pt/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax))
dentro da pasta `docs/`, e o site actualiza-se sozinho um ou dois minutos
depois de cada alteração entrar no ramo `main`.

Para editar é preciso uma conta no GitHub, que é gratuita. Quem tem
permissão de escrita no repositório (os [Contribuidores](Contribuidores.md): [Pedro Vicente](../Pessoas/P/Pedro%20Vicente.md) e [Tiago Bahia](../Pessoas/T/Tiago%20Bahia.md))
grava as alterações directamente. Os outros fazem uma proposta de alteração
(*pull request*) que os Contribuidores revêem e aceitam: as regras acima continuam a
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
**Buscar** no topo do site ou [Todos os artigos](../Todos%20os%20artigos.md),
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
do mesmo tipo (regra 2) e altere os dados, não o esquema: os
[Modelos](#modelos) abaixo têm o esquema dos artigos mais comuns. O
ficheiro começa pelo título:

```markdown
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
| `[[Pedro Vicente]]` | `[Pedro Vicente](<../Pessoas/P/Pedro Vicente.md>)` |
| `[http://exemplo.pt texto]` | `[texto](http://exemplo.pt)` |

As ligações entre artigos levam o caminho do ficheiro a partir da pasta do
artigo onde se escreve: `../` sobe uma pasta. Com os `< >` à volta, o
caminho pode ter espaços e acentos. Se uma ligação apontar para um ficheiro
que não existe, a publicação falha (o GitHub mostra um ✗ vermelho no
*commit* e avisa por e-mail) e o site fica como estava até se corrigir.

Para uma imagem, carregue o ficheiro com **Add file → Upload files** para
`docs/assets/imagens/` e escreva
`![legenda](<../assets/imagens/foto.jpg>)`, com o caminho a partir do
artigo.

### Como se cria uma categoria?

Uma categoria é uma página em `docs/Categorias/` com a lista dos seus
artigos, como [Animadores](../Categorias/Animadores.md). Crie o ficheiro
com essa lista e, no fim de cada artigo da categoria, acrescente-a à linha
**Categorias:**.

### Como se cria uma subcategoria de uma categoria?

Na página da categoria-mãe, acrescente a subcategoria à secção
*Subcategorias*.

### E as páginas restritas?

Estão cifradas e não se editam no GitHub. Ver
[Sobre este arquivo](Sobre%20este%20arquivo.md#páginas-restritas).

## Modelos

Esquemas prontos a copiar para os artigos mais comuns, com a informação que
cada um precisa e os cuidados a ter. Copie o bloco (botão no canto do
bloco), cole-o no ficheiro e substitua o que está entre `« »`. Apague as
linhas de que não sabe nada, em vez de as deixar vazias ou de inventar.

Não tem conta no GitHub ou prefere não editar ficheiros? Reúna a mesma
informação e [peça a alteração](#pedir-uma-alteracao) por um pedido.

- [Acampamento novo, com a equipa de animação](#acampamento-novo)
- [Pessoa nova](#pessoa-nova)
- [Pessoas em acampamentos](#pessoas-em-acampamentos)
- [Local de acampamento](#local-de-acampamento)
- [Participantes de um acampamento](#participantes)

### Cuidados em todos os modelos {#cuidados}

!!! warning "Antes de escrever"

    - **Procure primeiro.** Veja em [Todos os artigos](../Todos%20os%20artigos.md),
      que também lista as alcunhas, ou na caixa **Buscar**, se a pessoa, o
      acampamento ou o local já existe. Se existir, acrescente ao artigo que
      lá está em vez de criar outro.
    - **Escreva os nomes exactamente como já estão.** Uma pessoa, um
      acampamento ou um local que já tem artigo escreve-se como o título
      desse artigo, com os mesmos apelidos, acentos e maiúsculas:
      "Maria Cortês Ferreira" e não "Maria Ferreira", "OrienTu" e não
      "Orientu", "Murtinheira (Vila Nova do Ceira)" e não "Murtinheira". Um
      nome escrito de outra maneira cria uma pessoa a mais (um duplicado) ou
      uma ligação partida. O texto da ligação pode ser a alcunha, mas a
      ligação aponta sempre para o artigo que já existe:
      `[Jonifa](<../Pessoas/J/João Freire de Andrade.md>)`.
    - **Nome igual não quer dizer mesma pessoa.** Há dois Gonçalo Carvalho e
      três Miguel Martins. Se já há um artigo com o nome e é outra pessoa,
      não crie outro com o mesmo nome: use o nome completo (mais um nome ou
      apelido) e fale com os Contribuidores.
    - **Cargos sempre com o nome completo**, um destes e com a ligação para
      a página do cargo: [Director](../Cargos/Director.md) (ou
      Directora), [Director-Adjunto](../Cargos/Director-Adjunto.md) (ou
      Directora-Adjunta), [Mamã](../Cargos/Mam%C3%A3.md),
      [Tio](../Cargos/Tio.md) (ou Tia), [Capelão](../Cargos/Capel%C3%A3o.md),
      [Capelinho](../Cargos/Capelinho.md),
      [Animador de Equipa](../Cargos/Animador%20de%20Equipa.md) e
      [Animador Livre](../Cargos/Animador%20Livre.md). Nunca abreviados:
      "Director-Adjunto", com hífen, e não "Adjunto", "Director Adjunto",
      "Sub-director" ou "DA"; "Animador Livre" e não "Livre"; "Animador de
      Equipa" e não "Animador" ou "AE". Quando são vários, o cargo vai no
      plural ("Tios", "Animadores de Equipa", "Animadores Livres"), mas a
      ligação é sempre para a página do cargo no singular.
    - **Escalões com o nome exacto:** Triciclos, Trotinetas, Bicicletas,
      Lambretas, Calhambeques ou Formação de Animadores.
    - **Jesuítas** levam "sj" a seguir ao nome, fora da ligação:
      `[Luís Onofre](<../Pessoas/L/Luís Onofre.md>) sj`.
    - **Português de Portugal, com a ortografia da wiki:** Director,
      Direcção, actualizar, contacto, e os meses com maiúscula ("de 5 a 14
      de Agosto").
    - **Nada de dados privados** nas páginas públicas: telefones, e-mails,
      moradas, indicações para chegar aos locais de campo ou nomes de
      participantes menores de idade. Sobre outra pessoa, só com o acordo
      dela. O GitHub guarda o histórico de todas as alterações, por isso o
      que se grava fica lá mesmo depois de apagado.
    - **Não invente.** O que não se sabe fica de fora; os Contribuidores
      preferem um artigo curto a um artigo com dúvidas.
    - **As ligações vão nos dois sentidos.** Quando um artigo passa a ligar
      para outro, este ganha a ligação de volta em *Páginas que ligam para
      aqui*, por ordem alfabética.

### Acampamento novo, com a equipa de animação {#acampamento-novo}

Ficheiro: `docs/Acampamentos/«ano»/«Nome do acampamento».md` (sem ano
conhecido, em `docs/Acampamentos/Sem data/`). Exemplos:
[Esperança](../Acampamentos/2011/Esperan%C3%A7a.md) e
[OrienTu](../Acampamentos/2008/OrienTu.md).

| Informação | Obrigatória? | Como se escreve |
| --- | --- | --- |
| Nome do acampamento | sim | Como era conhecido, com as maiúsculas e os acentos certos: *OrienTu*, *Êxodo* |
| Ano | sim | *2008* |
| Escalão | sim | Triciclos, Trotinetas, Bicicletas, Lambretas, Calhambeques ou Formação de Animadores |
| Equipa de animação | sim | Uma linha por cargo, "Cargo - Nome": *Tios - Sara Póvoa e Elias Oliveira* |
| Datas | não | *de 5 a 14 de Agosto* |
| Local | não | O nome da ficha do local: ver [Local de acampamento](#local-de-acampamento) |
| Tema do ano, imaginário | não | Texto livre |
| Hino, história, curiosidades, blogue | não | Texto livre |
| Participantes | não | Ver [Participantes de um acampamento](#participantes) |

```markdown
# «Nome do acampamento»

O «Nome do acampamento» foi um acampamento de [«Escalão»](<../Categorias/«Escalão».md>) que decorreu de «dia» a «dia» de «Mês» de «ano» em [«Lugar»](<../Restrito/Locais de Acampamento/«Lugar» («Concelho»).md>).

### Animadores

- [Director](<../Cargos/Director.md>) - [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)
- [Mamã](<../Cargos/Mamã.md>) - [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)
- [Director-Adjunto](<../Cargos/Director-Adjunto.md>) - [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)
- [Capelão](<../Cargos/Capelão.md>) - [«Nome»](<../Pessoas/«Inicial»/«Nome».md>) sj
- [Capelinho](<../Cargos/Capelinho.md>) - [«Nome»](<../Pessoas/«Inicial»/«Nome».md>) sj
- [Tios](<../Cargos/Tio.md>) - [«Nome»](<../Pessoas/«Inicial»/«Nome».md>) e [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)
- [Animadores Livres](<../Cargos/Animador Livre.md>) - [«Nome»](<../Pessoas/«Inicial»/«Nome».md>) e [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)
- [Animadores de Equipa](<../Cargos/Animador de Equipa.md>) - [«Nome»](<../Pessoas/«Inicial»/«Nome».md>), [«Nome»](<../Pessoas/«Inicial»/«Nome».md>) e [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)

## Música

### Hino

«Letra do hino»

## Curiosidades

«De onde veio o nome, o que aconteceu, as histórias que vale a pena guardar»

## Páginas que ligam para aqui

- [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)

---

| Categorias |
| --- |
| [Acampamentos](<../Categorias/Acampamentos.md>) |
| [Acampamentos de «ano»](<../Categorias/Acampamentos de «ano».md>) |
| [«Escalão»](<../Categorias/«Escalão».md>) |
```

!!! warning "Cuidados"

    - Veja se o acampamento ainda não existe, noutro ano ou em *Sem data*.
    - O nome do ficheiro é o título mais `.md`, com os mesmos acentos e
      pontuação (`Era Uma Vez....md`), e fica na pasta do ano em que o
      acampamento se fez.
    - Cada nome da equipa escreve-se como o título do artigo da pessoa, se
      já tiver um; quem não tem artigo fica só com o nome, sem ligação (uma
      ligação para um artigo que não existe faz falhar a publicação).
    - Cada cargo aparece uma só vez: várias pessoas no mesmo cargo ficam na
      mesma linha, separadas por vírgulas e "e". Os cargos com o nome
      completo, como em [Cuidados](#cuidados).
    - Num acampamento de Formação de Animadores, a ligação do escalão é
      para `Formação de Animadores.md`.

Depois de gravar, acrescente o acampamento também em:

1. `docs/Categorias/Acampamentos.md`: na tabela, na linha do ano e debaixo
   do escalão; e na lista *Páginas nesta categoria*, por ordem alfabética,
   somando 1 ao número entre parênteses.
2. `docs/Acampamentos/«ano»/index.md` (`- [Nome](<Nome.md>) — Escalão`, por
   ordem alfabética) e o número do ano em `docs/Acampamentos/index.md`.
3. `docs/Categorias/Acampamentos de «ano».md` e a página do escalão em
   `docs/Categorias/`.
4. O artigo de cada pessoa da equipa (ver
   [Pessoas em acampamentos](#pessoas-em-acampamentos)) e as páginas dos
   cargos em `docs/Cargos/`, em *Páginas que ligam para aqui*.
5. `docs/Todos os artigos.md`, somando 1 ao número de artigos, e o mesmo
   número na página principal (`docs/index.md`).

### Pessoa nova {#pessoa-nova}

Ficheiro: `docs/Pessoas/«Inicial»/«Nome completo».md`, com a inicial sem
acento (Álvaro vai para `A`). Exemplos:
[Pedro Vicente](../Pessoas/P/Pedro%20Vicente.md) e
[João Eiró](../Pessoas/J/Jo%C3%A3o%20Eir%C3%B3.md).

| Informação | Obrigatória? | Como se escreve |
| --- | --- | --- |
| Nome completo | sim | O nome e os apelidos por que é conhecida no movimento: *Maria Cortês Ferreira* |
| Acordo da pessoa | sim | Só se escreve sobre quem concorda |
| Outros nomes e alcunhas | não | *Jonifa*, *Majo* |
| Colégio e anos | não | CAIC, CC ou CSJB; *de 1995 a 2003* |
| Animador desde | não | *2003* |
| Cargos no movimento | não | Um por linha, com os anos: *2005/2006 Coordenador Nacional*, separados em nacionais e locais |
| Acampamentos | não | Como participante, na formação e como animador, com o cargo: ver [Pessoas em acampamentos](#pessoas-em-acampamentos) |
| História, testemunho | não | Texto livre, escrito ou aprovado pela pessoa |

```markdown
# «Nome completo»

«Nome» frequentou o [«Colégio»](<../Movimento/«Colégio».md>) de «ano» a «ano». Animador desde «ano».

## História dentro do movimento

### Cargos

- **Nacionais:**
    - «ano»/«ano» «Cargo»
- **Locais:**
    - «ano»/«ano» «Cargo»

### Acampamentos

- **Participante:**
    - «ano» [«Acampamento»](<../Acampamentos/«ano»/«Acampamento».md>)
- **Formação:**
    - «ano» [«Acampamento»](<../Acampamentos/«ano»/«Acampamento».md>)
- **Animador:**
    - «ano» [«Acampamento»](<../Acampamentos/«ano»/«Acampamento».md>) - [«Cargo»](<../Cargos/«Cargo».md>)

## Páginas que ligam para aqui

- [«Acampamento»](<../Acampamentos/«ano»/«Acampamento».md>)

---

**Outros nomes:** «Alcunha» · «Outro nome»

| Categorias |
| --- |
| [Animadores](<../Categorias/Animadores.md>) |
| [Animadores do «Colégio»](<../Categorias/Animadores do «Colégio».md>) |
```

!!! warning "Cuidados"

    - Procure a pessoa pelo nome, pelas alcunhas e por nomes parecidos
      antes de criar o artigo: "Luís Onofre Pinto" já existe como
      "Luís Onofre", "Jonifa" é "João Freire de Andrade". Se já existe,
      não crie outro: acrescente ao artigo que existe.
    - Se já há um artigo com o mesmo nome e é outra pessoa, o artigo novo
      leva um nome diferente (o nome completo) e os dois artigos levam uma
      nota logo a seguir ao título:
      `*Nota: Este artigo é sobre «Nome», animadora do «Colégio». Se procura «Outro Nome», animador do «Colégio», consulte [«Outro Nome»](<«Outro Nome».md>).*`
    - O título, o nome do ficheiro e todas as ligações para a pessoa usam o
      mesmo nome. As alcunhas e as outras formas do nome vão para
      **Outros nomes**, não para o título.
    - Para uma animadora, a lista chama-se **Animadora:**.
    - Nos jesuítas, "sj" não entra no título nem no nome do ficheiro, e a
      categoria é [Jesuítas](../Categorias/Jesu%C3%ADtas.md).
    - Sem contactos, moradas nem datas de nascimento, a não ser que a
      própria pessoa os queira lá.

Depois de gravar, acrescente a pessoa também em:

1. `docs/Pessoas/«Inicial»/index.md`, por ordem alfabética, e o número da
   letra em `docs/Pessoas/index.md`.
2. As páginas das suas categorias (Animadores, Animadores do «Colégio»,
   Jesuítas…), somando 1 ao número de páginas.
3. `docs/Todos os artigos.md`, somando 1 ao número de artigos (e o mesmo
   número na página principal); cada alcunha, em itálico, também lá:
   `- *«Alcunha»* → [«Nome»](<Pessoas/«Inicial»/«Nome».md>)`.
4. Os artigos dos acampamentos onde esteve (ver
   [Pessoas em acampamentos](#pessoas-em-acampamentos)).

### Pessoas em acampamentos {#pessoas-em-acampamentos}

Para dizer que uma pessoa esteve num acampamento: como animador (com o
cargo), na formação ou como participante. A mesma informação escreve-se
**nos dois artigos**, no do acampamento e no da pessoa.

| Informação | Obrigatória? | Como se escreve |
| --- | --- | --- |
| Ano | sim | *2008* |
| Acampamento | sim | O título do artigo do acampamento: *OrienTu* |
| Pessoa | sim | O título do artigo da pessoa: *Maria Cortês Ferreira*, mesmo que no campo lhe chamassem "Maria Ferreira" |
| Papel | sim | O cargo (*Mamã*, *Director-Adjunto*, *Animador Livre*…), *Formação* ou *Participante* |

Para várias, uma por linha: `2008 - OrienTu - Maria Cortês Ferreira - Mamã`.

No artigo do acampamento (`docs/Acampamentos/«ano»/«Acampamento».md`):

```markdown
### Animadores

- [«Cargo»](<../Cargos/«Cargo».md>) - [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)

### Participantes

- [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)

## Páginas que ligam para aqui

- [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)
```

No artigo da pessoa (`docs/Pessoas/«Inicial»/«Nome».md`):

```markdown
### Acampamentos

- **Participante:**
    - «ano» [«Acampamento»](<../Acampamentos/«ano»/«Acampamento».md>)
- **Formação:**
    - «ano» [«Acampamento»](<../Acampamentos/«ano»/«Acampamento».md>)
- **Animador:**
    - «ano» [«Acampamento»](<../Acampamentos/«ano»/«Acampamento».md>) - [«Cargo»](<../Cargos/«Cargo».md>)

## Páginas que ligam para aqui

- [«Acampamento»](<../Acampamentos/«ano»/«Acampamento».md>)
```

!!! warning "Cuidados"

    - Os nomes da pessoa e do acampamento são os títulos dos artigos que já
      existem, sem abreviar nem trocar pela alcunha (a alcunha pode ser o
      texto da ligação, nunca o destino).
    - Se a pessoa já aparece no acampamento só com o nome, sem ligação,
      transforme esse nome em ligação em vez de o escrever outra vez.
    - O cargo é o mesmo nos dois artigos e escreve-se por extenso:
      "Director-Adjunto", "Animador Livre", "Animador de Equipa".
    - Se o cargo já tem uma linha no acampamento, acrescente o nome a essa
      linha ("Tios - A e B") em vez de repetir o cargo.
    - Num acampamento de Formação de Animadores, quem lá foi formar-se fica
      em **Formação** no seu artigo, não em **Participante**.
    - No artigo da pessoa, os acampamentos vão por ordem de ano; em
      *Páginas que ligam para aqui*, por ordem alfabética.
    - Se a pessoa ou o acampamento não tiver artigo, escreva o nome sem
      ligação.

### Local de acampamento {#local-de-acampamento}

As fichas dos locais de acampamento, com as indicações, os contactos e o
mapa, são [páginas restritas](Sobre%20este%20arquivo.md#páginas-restritas):
estão cifradas e só os Contribuidores as editam, com a palavra-passe. Quem
não é dos Contribuidores envia a informação **em privado** a alguém dos
Contribuidores, nunca num pedido (*issue*) do GitHub, que é público.

Ficheiro: `docs/Restrito/Locais de Acampamento/«Lugar» («Concelho»).md`,
criado cifrado (ver abaixo).

| Informação | Obrigatória? | Como se escreve |
| --- | --- | --- |
| Nome | sim | "Lugar (Concelho)", como as fichas que já existem: *Agroal (Tomar)* |
| Localização | sim | Coordenadas ou ligação para o mapa |
| Como chegar | não | Indicações a partir da estrada principal |
| Contactos | não | Proprietário ou responsável, e o telefone |
| Condições | não | Água, electricidade, casas de banho, sombra, rio, quantas tendas cabem |
| Autorizações | não | Quem é preciso avisar e com que antecedência: ver [Legislação](../Movimento/Legisla%C3%A7%C3%A3o.md) |
| Serviços perto | não | Centro de saúde ou hospital, GNR, bombeiros, farmácia, supermercado |
| Acampamentos que lá se fizeram | não | *2008 - OrienTu* |
| Observações | não | O que correu bem ou mal, o que levar |

O texto da ficha, antes de ser cifrado (o título fica de fora: é o nome do
ficheiro):

```markdown
**Localização:** «coordenadas ou ligação para o mapa»

## Como chegar

«Indicações»

## Contactos

- «Proprietário ou responsável» - «telefone»

## Condições

- Água: «da rede / de nascente / não há»
- Electricidade: «sim / não»
- Casas de banho: «sim / não»
- Sombra: «…»
- Capacidade: «quantas tendas ou participantes»

## Autorizações

«Quem é preciso avisar e com que antecedência»

## Serviços perto

- Centro de saúde ou hospital: «…»
- GNR: «…»
- Bombeiros: «…»
- Farmácia e supermercado: «…»

## Acampamentos

- «ano» [«Acampamento»](<../Acampamentos/«ano»/«Acampamento».md>)

## Observações

«…»

## Páginas que ligam para aqui

- [«Acampamento»](<../Acampamentos/«ano»/«Acampamento».md>)

---

| Categorias |
| --- |
| [Locais de Acampamento](<../Categorias/Locais de Acampamento.md>) |
| [Restrita](<../Categorias/Restrita.md>) |
```

Para a criar, com a palavra-passe:

```sh
python3 scripts/restrito.py abrir
# escreva a ficha em restrito-aberto/Restrito/Locais de Acampamento/«Lugar» («Concelho»).md
# e acrescente-a à lista em restrito-aberto/Categorias/Locais de Acampamento.md
python3 scripts/restrito.py fechar
```

O `fechar` cifra as fichas alteradas e as novas para `docs/` e apaga a
pasta `restrito-aberto/`.

!!! warning "Cuidados"

    - Só o nome do local ("Lugar (Concelho)") é público. Contactos,
      coordenadas, indicações e o mapa ficam só dentro da ficha cifrada:
      nunca numa página pública, num pedido do GitHub ou num ficheiro
      gravado sem cifra. O histórico do GitHub guarda tudo o que se grava,
      mesmo depois de apagado.
    - Nunca grave a pasta `restrito-aberto/` (o `.gitignore` já a deixa de
      fora) e corra sempre o `fechar` antes de gravar.
    - Veja primeiro se o local já tem ficha, às vezes com outro nome
      ("Alagoa" é "Alagoa (Arganil)"). Se é o mesmo sítio, acrescente à ficha
      que existe.
    - O nome do ficheiro é o título, com os parênteses e os acentos, e é
      igual em todas as ligações:
      `[Murtinheira](<../Restrito/Locais de Acampamento/Murtinheira (Vila Nova do Ceira).md>)`.
    - As fichas que já existem são o modelo (regra 2): se alguma coisa
      acima for diferente delas, siga as fichas.

Depois de gravar, acrescente o local também em:

1. `docs/Restrito/Locais de Acampamento/index.md`
   (`- [«Lugar» («Concelho»)](<«Lugar» («Concelho»).md>) 🔒`, por ordem
   alfabética) e o número em `docs/Restrito/index.md`.
2. `docs/Todos os artigos.md`, com 🔒, somando 1 ao número de artigos (e o
   mesmo número na página principal).
3. Os acampamentos que lá se fizeram: a ligação no texto do acampamento e
   na coluna *Locais de Acampamento* da tabela em
   `docs/Categorias/Acampamentos.md`.

### Participantes de um acampamento {#participantes}

Os participantes vão no artigo do acampamento, na secção `### Participantes`,
a seguir aos animadores; quem tem artigo ganha também a linha no seu artigo
(ver [Pessoas em acampamentos](#pessoas-em-acampamentos)). Exemplo:
[Esperança](../Acampamentos/2011/Esperan%C3%A7a.md).

| Informação | Obrigatória? | Como se escreve |
| --- | --- | --- |
| Acampamento e ano | sim | O título do artigo do acampamento: *Esperança, 2011* |
| Participantes | sim | Um por linha, com o nome e o apelido; quem já tem artigo, com o título do artigo |
| Acordo | sim | Só de quem é maior de idade e concorda em aparecer |

```markdown
### Participantes

- [«Nome»](<../Pessoas/«Inicial»/«Nome».md>)
- «Nome de quem não tem artigo»
```

!!! warning "Cuidados"

    - Só se escrevem os participantes dos Calhambeques e da Formação de
      Animadores, que já são ou vão ser animadores. Nunca nomes de
      participantes menores de idade.
    - Cada participante com artigo escreve-se como o título do artigo, com
      ligação; quem não tem artigo fica só com o nome. Não é preciso criar
      um artigo para cada participante.
    - Veja se a pessoa ainda não está na lista, às vezes com a alcunha ou
      só com um apelido, antes de a acrescentar.
    - Um participante por linha, de preferência por ordem alfabética.
    - Quem tem artigo ganha o acampamento na sua lista (**Participante**,
      ou **Formação** num acampamento de Formação de Animadores) e o
      acampamento em *Páginas que ligam para aqui*; e o acampamento ganha a
      pessoa na sua lista *Páginas que ligam para aqui*.
