<p align="center">
  <a href="https://campinacios.pedrovicente.pt/">
    <img src="docs/assets/imagens/Campin%C3%A1cios_2025.png" alt="Logótipo dos Campinácios" width="180">
  </a>
</p>

<h1 align="center">Wikinácios</h1>

<p align="center">
  <strong>A enciclopédia dos Campinácios: acampamentos, pessoas, cargos e histórias desde 1989.</strong>
</p>

<p align="center">
  <a href="https://campinacios.pedrovicente.pt/"><img src="https://img.shields.io/badge/site-campinacios.pedrovicente.pt-2e7d32" alt="Site"></a>
  <a href="https://github.com/neteinstein/Campinacios/actions/workflows/pages.yml"><img src="https://github.com/neteinstein/Campinacios/actions/workflows/pages.yml/badge.svg" alt="Publicar site"></a>
  <a href="https://github.com/neteinstein/Campinacios/issues/new/choose"><img src="https://img.shields.io/badge/contribuir-formul%C3%A1rios-blue" alt="Contribuir"></a>
</p>

<p align="center">
  <a href="https://campinacios.pedrovicente.pt/">Abrir o site</a> ·
  <a href="https://github.com/neteinstein/Campinacios/issues/new/choose">Enviar informação</a> ·
  <a href="https://campinacios.pedrovicente.pt/Recentes.html">Alterações recentes</a> ·
  <a href="https://campinacios.pedrovicente.pt/Grafo.html">Grafo de ligações</a>
</p>

---

## O que é

Os **Campinácios** são um movimento de acampamentos de férias ligado à Companhia de Jesus e aos seus três colégios em Portugal: o Colégio das Caldinhas (CC), o Colégio S. João de Brito (CSJB) e o Colégio da Imaculada Conceição (CAIC). Desde 1989, todos os Verões, há campos de Triciclos, Trotinetas, Bicicletas, Lambretas, Calhambeques e de Formação de Animadores.

A **Wikinácios** nasceu em 2009 como a wiki do movimento e perdeu-se em 2013. Em 2026 foi [recuperada de um backup](docs/Wikin%C3%A1cios/Sobre%20este%20arquivo.md), convertida para Markdown e publicada como um site estático. Desde então volta a crescer com os contributos de quem lá esteve.

No site encontra:

| | |
| --- | --- |
| 🏕️ **[Acampamentos](docs/Acampamentos/index.md)** | todos os campos, ano a ano, com a equipa de animação, o tema e o local |
| 🙋 **[Pessoas](docs/Pessoas/index.md)** | animadores, jesuítas e direcções, com os campos e os cargos de cada um |
| 🎪 **[Encontros](docs/Encontros/index.md)** | Encontros Nacionais, Encontros de Animadores e Rockstock |
| 🎖️ **[Cargos](docs/Cargos/index.md)** | Director, Mamã, Capelão, Tio, Animador Livre… e quem os ocupou |
| 🎸 **[Cantinácio](docs/Movimento/Cantin%C3%A1cio.md)** | o cancioneiro, com letras, acordes, aplausos e o *Cantinácio Virtual* em PDF |
| 📚 **[Movimento](docs/Movimento/index.md)** | história, vocabulário, manuais e documentos |

## Como contribuir

Toda a ajuda conta: um campo que falta, a equipa de um ano, uma alcunha, um hino, uma correcção.

### Sem saber programar: os formulários

A maneira mais fácil é [abrir uma issue](https://github.com/neteinstein/Campinacios/issues/new/choose) com um dos formulários:

| Formulário | Para quê |
| --- | --- |
| 🏕️ Acampamento | acrescentar ou corrigir um campo (equipa, datas, tema, local) |
| 🙋 Pessoa | acrescentar ou completar uma pessoa |
| 🔗 Pessoas em Acampamentos | ligar várias pessoas a vários campos de uma vez |
| 🙋 Participantes de um Acampamento | participantes de Calhambeques ou de Formação de Animadores |
| 🏞️ Local de Acampamento | um sítio onde se acampou |
| 🔒 Remoção de Informação | retirar ou corrigir os seus próprios dados |

Os Contribuidores revêem cada pedido, passam-no para o site e respondem na issue. Quem envia fica na lista de [Contribuidores](docs/Wikin%C3%A1cios/Contribuidores.md).

> [!IMPORTANT]
> O site é público e a maioria dos participantes dos campos é menor de idade. **Nunca envie** telefones, e-mails, moradas, indicações para chegar a um local de acampamento, nem nomes de participantes menores. As indicações dos locais vão em privado aos Contribuidores e ficam em páginas cifradas.

### Editar directamente

Quem prefere editar as páginas no GitHub encontra os modelos e as regras em [Conteúdos](docs/Wikin%C3%A1cios/Conte%C3%BAdos.md). Cada página é um ficheiro Markdown em `docs/`, e um pull request para o `main` é revisto antes de ser publicado.

Tudo no projecto se escreve em **português europeu, com a ortografia anterior a 1990** (*acção*, *direcção*, *actividade*): as páginas, as mensagens de commit, as issues e os pull requests.

## Montar o projecto

É preciso Python 3.12 (ou mais recente) e git.

```bash
git clone https://github.com/neteinstein/Campinacios.git
```

```bash
cd Campinacios
```

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Para ver o site em <http://127.0.0.1:8000>, com recarregamento automático:

```bash
.venv/bin/mkdocs serve
```

Para o construir como na publicação (falha se houver ligações partidas):

```bash
.venv/bin/mkdocs build --strict
```

As versões das dependências estão fixadas em [`requirements.txt`](requirements.txt). Não as suba sem testar com `mkdocs build --strict`.

### Estrutura

```text
docs/
├── Acampamentos/<ano>/      um ficheiro por campo
├── Pessoas/<inicial>/       um ficheiro por pessoa
├── Encontros/               encontros nacionais, de animadores e Rockstock
├── Cargos/                  os cargos de um campo
├── Categorias/              listas e índices (Animadores do CC, Acampamentos de 2012…)
├── Movimento/               história, vocabulário, Cantinácio, manuais
├── Restrito/                páginas cifradas (locais de acampamento, relatórios)
├── Wikinácios/              sobre o próprio site: regras, contribuidores, arquivo
└── assets/                  imagens, estilos, scripts e o grafo
overrides/                   personalização do tema Material for MkDocs
scripts/                     ferramentas de manutenção (ver abaixo)
.claude/skills/              os procedimentos escritos para cada tarefa
```

### Ferramentas

| Comando | O que faz |
| --- | --- |
| `python3 .claude/skills/novo-acampamento/scripts/validar.py --todos` | confirma que cada campo aparece em todas as listas |
| `python3 .claude/skills/nova-pessoa/scripts/pessoas.py procurar "Nome"` | procura nomes iguais ou parecidos antes de criar uma pessoa |
| `python3 .claude/skills/nova-pessoa/scripts/pessoas.py reciprocas --todos` | confere que campos e pessoas se ligam nos dois sentidos |
| `python3 .claude/skills/nova-pessoa/scripts/pessoas.py secoes` | escreve as listas geradas dos cargos e dos campos |
| `python3 scripts/actualizar_grafo.py` | reconstrói o grafo de ligações (`docs/assets/graph.json`) |
| `python3 scripts/actualizar_recentes.py` | gera a página Recentes a partir do histórico do git |
| `python3 scripts/restrito.py abrir` / `fechar` | decifra e volta a cifrar as páginas restritas (pede a palavra-passe) |
| `python3 .claude/skills/conteudo-em-portugues/scripts/verificar_portugues.py` | procura texto em inglês ou em português do Brasil |

O passo a passo de cada tarefa (acrescentar um campo, uma pessoa, processar um contributo, publicar) está em [`.claude/skills/`](.claude/skills) e em [`AGENTS.md`](AGENTS.md), e serve tanto para pessoas como para agentes de programação.

## Publicação

Cada push para o `main` corre a Action [**Publicar site**](.github/workflows/pages.yml), que gera a página Recentes, constrói o site com `mkdocs build --strict` e publica-o no GitHub Pages, em <https://campinacios.pedrovicente.pt/>. Quando um pull request é integrado, a Action [**Fechar issues do PR integrado**](.github/workflows/fechar-issues.yml) fecha as issues que ele indicava com `Closes #N`.

## Páginas restritas

Os locais de acampamento (com as indicações e os contactos) e os relatórios de campo são publicados **cifrados** com AES-256-GCM. Nem o repositório nem o site guardam o texto às claras: o navegador decifra-os quando o visitante escreve a palavra-passe. As páginas restritas destinam-se à Direcção Nacional e aos directores; como se editam: [Sobre este arquivo](docs/Wikin%C3%A1cios/Sobre%20este%20arquivo.md).

## Contactos

- Sobre o movimento: [Contactos](docs/Movimento/Contactos.md)
- Sobre o site: [Pedro Vicente](https://www.pedrovicente.pt/pt#contact)

<p align="center"><sub>Feito com carinho por animadores, para animadores. Uma salva de palmas a todos os <a href="docs/Wikin%C3%A1cios/Contribuidores.md">Contribuidores</a>! 👏</sub></p>
