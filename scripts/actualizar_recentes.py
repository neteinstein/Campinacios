#!/usr/bin/env python3
"""Escreve docs/Recentes.md: as 100 páginas do Wikinácios alteradas há menos
tempo, com a data da última alteração, o pull request que a fez, as issues
que esse trabalho resolveu, quem as propôs e quem fez a alteração, lidos do
histórico do git e da API do GitHub.

O pull request sai da junção «Merge pull request #N» (ou do «(#N)» do título,
nas junções por «squash»); as issues saem das mensagens dos commits («issue
#N», «fecha #N»...). Alterações feitas directamente no main não têm pedido.

Quem propôs é o autor de cada issue no GitHub; quem fez a alteração é o autor
do pull request no GitHub ou, sem pedido, o autor do commit. Os autores lêem-se
com o `gh` (no GitHub Actions, com `GH_TOKEN`); sem ele, ou sem rede, a coluna
de quem propôs fica vazia e a de quem alterou mostra o autor do commit.

Ficam de fora as páginas restritas (Restrito/), os índices, as categorias,
as páginas geradas ("Todos os artigos", "Grafo", "Recentes") e as de
Wikinácios/. O histórico tem de estar completo (no GitHub Actions:
`fetch-depth: 0`); com um clone superficial a lista sairia errada.

Uso:
    python3 scripts/actualizar_recentes.py
"""
import functools
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / 'docs'
SAIDA = DOCS / 'Recentes.md'
LIMITE = 100
REPO = 'https://github.com/neteinstein/Campinacios'
PEDIDO = re.compile(r'^Merge pull request #(\d+)|\(#(\d+)\)\s*$')
ISSUES = re.compile(
    r'\b(?:issues?|fecha|fechar|resolve|resolver|closes?|fix(?:es)?)\s+'
    r'(#\d+(?:(?:,|\s+e|\s+and)\s*#\d+)*)', re.IGNORECASE)
EXCLUIDAS = {'Todos os artigos.md', 'Grafo.md', 'Recentes.md', 'index.md'}
PASTAS_EXCLUIDAS = {'Restrito', 'Categorias', 'Wikinácios', 'assets'}


def titulo(caminho):
    for linha in caminho.read_text(encoding='utf-8').splitlines():
        if linha.startswith('# '):
            return linha[2:].strip()
    return caminho.stem


def elegivel(rel):
    return (rel.suffix == '.md' and rel.name != 'index.md'
            and rel.as_posix() not in EXCLUIDAS
            and rel.parts[0] not in PASTAS_EXCLUIDAS)


def git(*args):
    return subprocess.run(['git', '-c', 'core.quotepath=off', *args], cwd=RAIZ,
                          capture_output=True, text=True, check=True).stdout


@functools.cache
def autor_github(tipo, numero):
    """Login de quem abriu a issue ou o pull request, ou '' se não se souber."""
    try:
        saida = subprocess.run(
            ['gh', 'api', f'repos/neteinstein/Campinacios/{tipo}/{numero}'],
            cwd=RAIZ, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return ''
    if saida.returncode != 0:
        return ''
    return (json.loads(saida.stdout).get('user') or {}).get('login', '')


def utilizador(login):
    return f'[{login}](https://github.com/{login})'


def pedidos():
    """{hash de um commit: número do pull request que o trouxe para o main}."""
    mapa = {}
    for linha in git('log', '--first-parent', '--format=%H %P%x00%s').splitlines():
        info, assunto = linha.split('\x00', 1)
        hashes = info.split()
        encontrado = PEDIDO.search(assunto)
        if not encontrado:
            continue
        numero = encontrado.group(1) or encontrado.group(2)
        mapa.setdefault(hashes[0], numero)
        if len(hashes) == 3:  # junção: os commits do ramo vieram com ela
            for h in git('rev-list', f'{hashes[1]}..{hashes[2]}').split():
                mapa.setdefault(h, numero)
    return mapa


def ultimas():
    """[(data, caminho, pedido ou '', [issues], autor do commit)] das páginas
    mais recentes."""
    if git('rev-parse', '--is-shallow-repository').strip() == 'true':
        sys.exit('Histórico incompleto: corra `git fetch --unshallow`.')
    saida = git('log', '--no-merges', '--name-only', '--date=format:%d/%m/%Y',
                '--format=%x01%H%x00%ad%x00%an%x00%B%x00', '--', 'docs')
    vistas = {}
    for bloco in saida.split('\x01')[1:]:
        hash_, data, autor, mensagem, nomes = bloco.split('\x00', 4)
        for linha in nomes.splitlines():
            if not linha.startswith('docs/'):
                continue
            rel = Path(linha).relative_to('docs')
            if rel in vistas or not (DOCS / rel).is_file() or not elegivel(rel):
                continue
            vistas[rel] = (data, hash_, autor, mensagem)
        if len(vistas) >= LIMITE:
            break
    mapa = pedidos()
    resultado = []
    for rel, (data, hash_, autor, mensagem) in vistas.items():  # por ordem decrescente
        issues = []
        for grupo in ISSUES.findall(mensagem):
            issues += [n for n in re.findall(r'\d+', grupo) if n not in issues]
        resultado.append((data, rel, mapa.get(hash_, ''), issues, autor))
    return resultado


def main():
    linhas = [
        '# Recentes', '',
        f'As {LIMITE} páginas alteradas há menos tempo, com a data da última '
        'alteração, os pedidos (issues) que ela resolveu, a edição (pull request) '
        'que a fez, quem propôs os pedidos e quem executou a edição. As páginas '
        'restritas não aparecem.', '',
        '| Página | Alterada em | Pedidos | Edição | Proposta de | Executada por |',
        '| --- | --- | --- | --- | --- | --- |']
    for data, rel, pedido, issues, autor in ultimas():
        ligacao = urllib.parse.quote(rel.as_posix())
        pr = f'[#{pedido}]({REPO}/pull/{pedido})' if pedido else ''
        iss = ', '.join(f'[#{n}]({REPO}/issues/{n})' for n in issues)
        propostas = []
        for n in issues:
            login = autor_github('issues', n)
            if login and utilizador(login) not in propostas:
                propostas.append(utilizador(login))
        login = autor_github('pulls', pedido) if pedido else ''
        alterado = utilizador(login) if login else autor
        linhas.append(f'| [{titulo(DOCS / rel)}]({ligacao}) '
                      f'| {data} | {iss} | {pr} | {", ".join(propostas)} '
                      f'| {alterado} |')
    SAIDA.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print(f'{SAIDA.relative_to(RAIZ)} escrito.')


if __name__ == '__main__':
    main()
