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

Em ambos os casos confirma também que cada issue que o pedido fecha
(«Closes #N» na descrição) aparece em pelo menos uma página: se não
aparece, os commits não a referem («(issue #N)» na mensagem).

A própria Action «Publicar site» corre-o depois de publicar, com
--na-action (não procura a execução, que é ela própria) e --tentativas
(volta a ler a página enquanto a cache do GitHub Pages não a mostrar).

Uso:
    python3 .claude/skills/refrescar-recentes/scripts/verificar_recentes.py [N ...] [--publicar] [--esperar]
    python3 .claude/skills/refrescar-recentes/scripts/verificar_recentes.py N --na-action --tentativas 10

Sai com 0 se está tudo publicado, com 1 se falta alguma coisa.
"""
import argparse
import json
import re
import subprocess
import sys
import time
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
                         'number,state,files,mergeCommit,mergedAt,closingIssuesReferences,body'))


def issues_fechadas(dados):
    """As issues que o pedido fecha (as que o GitHub reconheceu e as da descrição)."""
    numeros = [str(i['number']) for i in dados.get('closingIssuesReferences') or []]
    numeros += recentes.FECHA.findall(dados.get('body') or '')
    return sorted(set(numeros), key=int)


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


ISSUES_NA_LINHA = {}  # endereço da página -> [issues], da última leitura


def linhas_publicadas():
    """{endereço da página: [números dos pedidos na linha]} da página no ar.
    O GitHub Pages guarda as páginas em cache 10 minutos: um parâmetro novo
    no endereço obriga a ler a versão publicada."""
    endereco_site = f'{SITE}?v={int(time.time())}'
    pedido_http = urllib.request.Request(endereco_site, headers={'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(pedido_http, timeout=30) as resposta:
        html = resposta.read().decode('utf-8')
    linhas = {}
    ISSUES_NA_LINHA.clear()
    for linha in re.findall(r'<tr>(.*?)</tr>', html, re.S):
        endereco = re.search(r'<td><a href="([^"]+)"', linha)
        if endereco:
            linhas[endereco.group(1)] = re.findall(r'/pull/(\d+)"', linha)
            ISSUES_NA_LINHA[endereco.group(1)] = re.findall(r'/issues/(\d+)"', linha)
    return linhas


def verificar_issues(fechadas, presentes):
    """Cada issue que o pedido fecha tem de aparecer em alguma página."""
    falta = [n for n in fechadas if n not in presentes]
    for n in falta:
        print(f'  ✗ a issue #{n} não aparece em nenhuma página: faça um commit por '
              f'issue, com «(issue #{n})» na mensagem')
    return not falta


def endereco(rel):
    return urllib.parse.quote(rel.with_suffix('.html').as_posix())


def verificar_local(numero, mexidas, fechadas):
    geradas = recentes.ultimas()
    listadas = {rel for _, rel, *_ in geradas}
    presentes = {n for _, rel, _, issues, _ in geradas if rel in mexidas for n in issues}
    if len(fechadas) == 1:  # depois da junção, a issue única do pedido vai para todas
        presentes |= set(fechadas)
    falta = [rel for rel in mexidas if rel not in listadas]
    for rel in falta:
        print(f'  ✗ {rel}: não aparece na lista gerada (falta um commit?)')
    if not falta:
        print(f'  ✓ as {len(mexidas)} páginas aparecem na lista gerada; '
              'depois da integração, corra de novo com este número.')
    return verificar_issues(fechadas, presentes) and not falta


def execucao(sha):
    lista = json.loads(gh('run', 'list', '--workflow', WORKFLOW, '--commit', sha,
                          '--json', 'databaseId,status,conclusion', '--limit', '5'))
    return lista[0] if lista else None


def verificar_publicado(dados, mexidas, fechadas, publicar, esperar, na_action, tentativas):
    numero, sha = dados['number'], dados['mergeCommit']['oid']
    if na_action:
        corrida = {'status': 'completed', 'conclusion': 'success', 'databaseId': 'esta'}
    else:
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
    for tentativa in range(max(tentativas, 1)):
        publicadas = linhas_publicadas()
        if all(str(numero) in (publicadas.get(endereco(rel)) or []) for rel in mexidas):
            break
        if tentativa + 1 < tentativas:
            print(f'  … a página publicada ainda não mostra o #{numero}; nova leitura em 60 s')
            time.sleep(60)
    # A lista só tem as 100 páginas mais recentes: com ela cheia e já com este
    # pedido (ou um posterior), uma página que falta saiu por ser mais antiga.
    no_ar = {n for ns in publicadas.values() for n in ns}
    chegou = str(numero) in no_ar or any(
        pedido(n).get('mergedAt', '') > dados['mergedAt'] for n in no_ar if int(n) != numero)
    cheia = len(publicadas) >= recentes.LIMITE
    falta = []
    for rel in mexidas:
        numeros = publicadas.get(endereco(rel))
        if numeros is None and cheia and chegou:
            print(f'  ✓ {rel}: já saiu da lista (só entram as {recentes.LIMITE} mais recentes)')
        elif numeros is None:
            falta.append(rel)
            print(f'  ✗ {rel}: não aparece na página publicada')
        elif str(numero) not in numeros:
            outro = numeros[0] if numeros else ''
            if outro and pedido(outro).get('mergedAt', '') > dados['mergedAt']:
                print(f'  ✓ {rel}: mexida depois por #{outro}')
            else:
                falta.append(rel)
                print(f'  ✗ {rel}: aparece com {"#" + outro if outro else "outro pedido"}')
    presentes = {n for rel in mexidas for n in ISSUES_NA_LINHA.get(endereco(rel), [])}
    na_lista = [rel for rel in mexidas if str(numero) in (publicadas.get(endereco(rel)) or [])]
    if not na_lista:
        fechadas = []  # nenhuma página ainda com este pedido: nada a dizer das issues
    ok = (verificar_issues(fechadas, presentes) and not falta and corrida
          and corrida['conclusion'] == 'success')
    if ok:
        print(f'  ✓ a página publicada está certa para as {len(mexidas)} páginas do pedido')
    elif publicar and (falta or not corrida or corrida['conclusion'] != 'success'):
        # Só vale a pena publicar de novo se faltam páginas; issues por
        # referir nos commits não se resolvem assim.
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
    argumentos.add_argument('--na-action', action='store_true',
                            help='corre dentro da Action «Publicar site»: não procura a execução')
    argumentos.add_argument('--tentativas', type=int, default=1,
                            help='quantas vezes ler a página publicada, um minuto entre cada')
    args = argumentos.parse_args()
    tudo_bem = True
    for numero in args.pedidos or [ultimo_integrado()]:
        dados = pedido(numero)
        mexidas = paginas(dados)
        print(f'#{numero} ({dados["state"]}): {len(mexidas)} páginas na lista Recentes')
        if not mexidas:
            print('  ✓ não mexe em páginas que entrem na lista')
            continue
        fechadas = issues_fechadas(dados)
        if dados['state'] == 'MERGED':
            tudo_bem &= verificar_publicado(dados, mexidas, fechadas, args.publicar,
                                            args.esperar, args.na_action, args.tentativas)
        else:
            tudo_bem &= verificar_local(numero, mexidas, fechadas)
    sys.exit(0 if tudo_bem else 1)


if __name__ == '__main__':
    main()
