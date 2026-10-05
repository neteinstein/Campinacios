#!/usr/bin/env python3
"""Confirma que a página Recentes publicada mostra as páginas de um pull
request, e volta a publicar o site quando não mostra.

Para cada pedido indicado (por omissão, o último integrado no main):

- se ainda não foi integrado, gera a lista localmente (sem escrever
  docs/Recentes.md) e confirma que as páginas mexidas lá aparecem;
- se já foi integrado, confirma que a Action «Publicar site» correu com
  sucesso no commit de integração e que a página publicada lista cada página
  mexida com esse pedido (ou com um pedido integrado depois, que a voltou a
  mexer). Com --publicar, volta a correr a Action quando falta alguma coisa.

Uso:
    python3 .claude/skills/refrescar-recentes/scripts/verificar_recentes.py [N ...] [--publicar] [--esperar]

Sai com 0 se está tudo publicado, com 1 se falta alguma coisa.
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ / 'scripts'))
import actualizar_recentes as recentes  # noqa: E402

SITE = 'https://campinacios.pedrovicente.pt/Recentes.html'
WORKFLOW = 'pages.yml'


def gh(*args):
    saida = subprocess.run(['gh', *args], cwd=RAIZ, capture_output=True,
                           text=True)
    if saida.returncode != 0:
        sys.exit(f'Falhou `gh {" ".join(args)}`: {saida.stderr.strip()}')
    return saida.stdout


def pedido(numero):
    return json.loads(gh('pr', 'view', str(numero), '--json',
                         'number,state,files,mergeCommit,mergedAt'))


def ultimo_integrado():
    lista = json.loads(gh('pr', 'list', '--state', 'merged', '--base', 'main',
                          '--limit', '1', '--json', 'number'))
    if not lista:
        sys.exit('Não há pedidos integrados no main.')
    return lista[0]['number']


def paginas(dados):
    """Páginas de docs/ mexidas pelo pedido que entram na lista Recentes."""
    resultado = []
    for ficheiro in dados['files']:
        caminho = ficheiro['path']
        if not caminho.startswith('docs/'):
            continue
        rel = Path(caminho).relative_to('docs')
        if recentes.elegivel(rel) and (recentes.DOCS / rel).is_file():
            resultado.append(rel)
    return resultado


def linhas_publicadas():
    """{endereço da página: [números dos pedidos na linha]} da página no ar."""
    pedido_http = urllib.request.Request(SITE, headers={'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(pedido_http, timeout=30) as resposta:
        html = resposta.read().decode('utf-8')
    linhas = {}
    for linha in re.findall(r'<tr>(.*?)</tr>', html, re.S):
        endereco = re.search(r'<td><a href="([^"]+)"', linha)
        if endereco:
            linhas[endereco.group(1)] = re.findall(r'/pull/(\d+)"', linha)
    return linhas


def endereco(rel):
    return urllib.parse.quote(rel.with_suffix('.html').as_posix())


def verificar_local(numero, mexidas):
    listadas = {rel for _, rel, *_ in recentes.ultimas()}
    falta = [rel for rel in mexidas if rel not in listadas]
    for rel in falta:
        print(f'  ✗ {rel}: não aparece na lista gerada (falta um commit?)')
    if not falta:
        print(f'  ✓ as {len(mexidas)} páginas aparecem na lista gerada; '
              'depois da integração, corra de novo com este número.')
    return not falta


def execucao(sha):
    lista = json.loads(gh('run', 'list', '--workflow', WORKFLOW, '--commit', sha,
                          '--json', 'databaseId,status,conclusion', '--limit', '5'))
    return lista[0] if lista else None


def verificar_publicado(dados, mexidas, publicar, esperar):
    numero, sha = dados['number'], dados['mergeCommit']['oid']
    corrida = execucao(sha)
    if corrida and corrida['status'] != 'completed' and esperar:
        gh('run', 'watch', str(corrida['databaseId']), '--exit-status')
        corrida = execucao(sha)
    if not corrida:
        print('  ✗ a Action «Publicar site» não correu no commit de integração')
    elif corrida['status'] != 'completed':
        print(f'  … a Action «Publicar site» ainda está a correr '
              f'(execução {corrida["databaseId"]}); use --esperar')
        return False
    elif corrida['conclusion'] != 'success':
        print(f'  ✗ a Action «Publicar site» terminou com '
              f'«{corrida["conclusion"]}» (execução {corrida["databaseId"]})')
    publicadas = linhas_publicadas()
    falta = []
    for rel in mexidas:
        numeros = publicadas.get(endereco(rel))
        if numeros is None:
            falta.append(rel)
            print(f'  ✗ {rel}: não aparece na página publicada')
        elif str(numero) not in numeros:
            outro = numeros[0] if numeros else ''
            if outro and pedido(outro).get('mergedAt', '') > dados['mergedAt']:
                print(f'  ✓ {rel}: mexida depois por #{outro}')
            else:
                falta.append(rel)
                print(f'  ✗ {rel}: aparece com {"#" + outro if outro else "outro pedido"}')
    ok = not falta and corrida and corrida['conclusion'] == 'success'
    if ok:
        print(f'  ✓ as {len(mexidas)} páginas estão na página publicada')
    elif publicar:
        gh('workflow', 'run', WORKFLOW, '--ref', 'main')
        print('  → Action «Publicar site» lançada de novo no main; '
              'volte a verificar quando terminar.')
    return ok


def main():
    argumentos = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    argumentos.add_argument('pedidos', nargs='*', type=int)
    argumentos.add_argument('--publicar', action='store_true',
                            help='voltar a correr a Action se faltar alguma coisa')
    argumentos.add_argument('--esperar', action='store_true',
                            help='esperar que a Action em curso termine')
    args = argumentos.parse_args()
    tudo_bem = True
    for numero in args.pedidos or [ultimo_integrado()]:
        dados = pedido(numero)
        mexidas = paginas(dados)
        print(f'#{numero} ({dados["state"]}): {len(mexidas)} páginas na lista Recentes')
        if not mexidas:
            print('  ✓ não mexe em páginas que entrem na lista')
            continue
        if dados['state'] == 'MERGED':
            tudo_bem &= verificar_publicado(dados, mexidas, args.publicar, args.esperar)
        else:
            tudo_bem &= verificar_local(numero, mexidas)
    sys.exit(0 if tudo_bem else 1)


if __name__ == '__main__':
    main()
