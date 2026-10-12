---
name: refrescar-recentes
description: Garantir que a página Recentes do site (https://campinacios.pedrovicente.pt/Recentes.html, gerada por scripts/actualizar_recentes.py) fica refrescada e certa a cada pull request do Wikinácios — um commit por issue com «(issue #N)», um «Closes #N» por issue, e logo a seguir a abrir o pedido confirmar que as páginas e as issues entram na lista; depois de integrado no main, confirmar que a Action «Publicar site» correu e que a página publicada mostra as páginas com esse pedido, e voltar a publicar se não mostrar. Usar sempre que se abre, actualiza ou integra um pull request que mexe em docs/, quando alguém diz "a página Recentes não mostra o meu pedido", "refresca os Recentes", "o site não está actualizado" ou semelhante, e quando se mexe em scripts/actualizar_recentes.py, em .github/workflows/pages.yml ou em .github/workflows/verificar-recentes.yml.
---

# Refrescar a página Recentes a cada pedido

A página [Recentes](https://campinacios.pedrovicente.pt/Recentes.html) lista
as 100 páginas alteradas há menos tempo, com os pedidos (issues), quem os
propôs, a edição (pull request) e quem a executou. Não se edita à mão: é
escrita por `scripts/actualizar_recentes.py` a partir do histórico do git e
da API do GitHub, e a Action «Publicar site» (`.github/workflows/pages.yml`)
corre esse script e publica o site a cada push para o `main` — ou seja, a
cada pull request integrado.

O que pode correr mal, e que este skill apanha:

- a alteração não ficou num commit (a página não aparece na lista);
- os commits não referem as issues (`(issue #N)`), ou juntam várias issues
  num só commit, e a coluna «Pedidos» fica vazia ou errada;
- a Action não correu, falhou ou foi cancelada depois da integração;
- a página foi publicada sem o histórico completo ou sem `GH_TOKEN`
  (faltam o pedido ou os autores);
- o site no ar ainda mostra a versão anterior (o GitHub Pages guarda as
  páginas em cache durante 10 minutos).

## Regras

1. **Um commit por issue**, com `(issue #N)` na mensagem e só as páginas
   dessa issue. Uma página de várias issues vai num commit que as refere
   todas (`(issues #290 e #293)`); as listas partilhadas (índices,
   categorias, `Todos os artigos`, grafo, Contribuidores) num commit final
   sem issue. Um intervalo («issues #276 a #299») é ignorado pelo script,
   porque não diz que issue mexeu em que página. Se o pedido fecha uma só
   issue, os commits sem issue ficam com ela.
2. **Um `Closes #N` por issue** na descrição do pedido.
3. **Logo a seguir a abrir o pedido**, `verificar_recentes.py <N>` tem de
   passar (secção 1).
4. **Depois da integração**, a Action «Verificar Recentes»
   (`.github/workflows/verificar-recentes.yml`) corre sozinha quando a
   «Publicar site» termina: lê a página no ar (sem cache) até 12 minutos,
   confirma as páginas e as issues do pedido e, se faltarem páginas, volta a
   publicar uma vez. Uma execução vermelha é para ler e corrigir (secção 2).
5. **O topo da página** diz quando foi gerada e até que pedido vai
   («Actualizada a …, até ao pedido #N»). Quem diz que a página «não está
   actualizada» deve ver primeiro esse número: se é o último pedido
   integrado, é só a cache do navegador ou do GitHub Pages.

## 1. Antes de abrir (ou actualizar) o pull request

Com as alterações já em commits no ramo:

```bash
python3 scripts/actualizar_recentes.py
git diff docs/Recentes.md   # as páginas mexidas têm de aparecer no topo
git restore docs/Recentes.md
```

Nunca se faz commit de `docs/Recentes.md`: é reescrito na publicação. Num
ramo ainda não integrado a coluna «Edição» fica vazia para as páginas novas,
o que é normal — o número do pedido só existe depois da junção.

Com o pedido já aberto, o mesmo se confirma com:

```bash
python3 .claude/skills/refrescar-recentes/scripts/verificar_recentes.py <N>
```

## 2. Depois de o pull request ser integrado

```bash
python3 .claude/skills/refrescar-recentes/scripts/verificar_recentes.py <N> --esperar
```

Sem número, verifica o último pedido integrado no `main`. O script:

1. lê os ficheiros do pedido e fica com as páginas que entram na lista
   (sem `Restrito/`, índices, categorias, `Wikinácios/`...);
2. confirma que a Action «Publicar site» correu com sucesso no commit de
   integração (com `--esperar`, espera que termine);
3. lê a página publicada e confirma que cada página aparece com esse pedido
   — ou com um pedido integrado depois, que a voltou a mexer.

Confirma também que cada issue do `Closes` aparece em alguma página. Sai
com 0 se estiver tudo publicado. Se faltar alguma coisa, corra de novo
com `--publicar`: lança outra vez a Action no `main`
(`gh workflow run pages.yml --ref main`). Espere que termine e verifique
de novo. Se a Action falhar, leia o registo (`gh run view <id> --log-failed`)
e corrija a causa — quase sempre uma ligação partida que o
`mkdocs build --strict` recusa.

## 3. Quando se mexe na própria página

Se a alteração é a `scripts/actualizar_recentes.py`, a
`.github/workflows/pages.yml` ou a `.github/workflows/verificar-recentes.yml`:

- o workflow tem de manter `fetch-depth: 0` no checkout, `GH_TOKEN` no passo
  do script e as permissões `issues: read` e `pull-requests: read`;
- gere a página localmente, veja o cabeçalho e algumas linhas, e
  descarte-a com `git restore docs/Recentes.md`;
- depois da integração, confirme no site que a tabela publicada tem o
  formato novo (o script de verificação não depende da ordem das colunas).
