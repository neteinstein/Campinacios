#!/usr/bin/env python3
"""Escreve docs/Recentes.md: as 100 páginas do Wikinácios alteradas há menos
tempo, com a data da última alteração, o pull request que a fez e as issues
que esse trabalho resolveu, lidos do histórico do git.

O pull request sai da junção «Merge pull request #N» (ou do «(#N)» do título,
nas junções por «squash»); as issues saem das mensagens dos commits («issue
#N», «fecha #N»...). Alterações feitas directamente no main não têm pedido.

Ficam de fora as páginas restritas (Restrito/), os índices, as categorias,
as páginas geradas ("Todos os artigos", "Grafo", "Recentes") e as de
Wikinácios/. O histórico tem de estar completo (no GitHub Actions:
`fetch-depth: 0`); com um clone superficial a lista sairia errada.

Uso:
    python3 scripts/actualizar_recentes.py
"""
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
    """[(data, caminho, pedido ou '', [issues])] das páginas mais recentes."""
    if git('rev-parse', '--is-shallow-repository').strip() == 'true':
        sys.exit('Histórico incompleto: corra `git fetch --unshallow`.')
    saida = git('log', '--no-merges', '--name-only', '--date=format:%d/%m/%Y',
                '--format=%x01%H%x00%ad%x00%B%x00', '--', 'docs')
    vistas = {}
    for bloco in saida.split('\x01')[1:]:
        hash_, data, mensagem, nomes = bloco.split('\x00', 3)
        for linha in nomes.splitlines():
            if not linha.startswith('docs/'):
                continue
            rel = Path(linha).relative_to('docs')
            if rel in vistas or not (DOCS / rel).is_file() or not elegivel(rel):
                continue
            vistas[rel] = (data, hash_, mensagem)
        if len(vistas) >= LIMITE:
            break
    mapa = pedidos()
    resultado = []
    for rel, (data, hash_, mensagem) in vistas.items():  # por ordem decrescente
        issues = []
        for grupo in ISSUES.findall(mensagem):
            issues += [n for n in re.findall(r'\d+', grupo) if n not in issues]
        resultado.append((data, rel, mapa.get(hash_, ''), issues))
    return resultado


def main():
    linhas = [
        '# Recentes', '',
        f'As {LIMITE} páginas alteradas há menos tempo, com a data da última '
        'alteração, o pedido (pull request) que a fez e as issues resolvidas por '
        'ele. As páginas restritas não aparecem.', '',
        '| Página | Alterada em | Pedido | Issues |', '| --- | --- | --- | --- |']
    for data, rel, pedido, issues in ultimas():
        ligacao = urllib.parse.quote(rel.as_posix())
        pr = f'[#{pedido}]({REPO}/pull/{pedido})' if pedido else ''
        iss = ', '.join(f'[#{n}]({REPO}/issues/{n})' for n in issues)
        linhas.append(f'| [{titulo(DOCS / rel)}]({ligacao}) '
                      f'| {data} | {pr} | {iss} |')
    SAIDA.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print(f'{SAIDA.relative_to(RAIZ)} escrito.')


if __name__ == '__main__':
    main()
