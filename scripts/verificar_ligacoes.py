#!/usr/bin/env python3
"""Check every external link in docs/ and find a Web Archive copy of it.

Run by .github/workflows/verificar-ligacoes.yml (the sandbox that edits the
site usually can't reach these hosts). Prints, and writes to the job
summary, one row per URL: the HTTP status, where it ends up, the page title
and the Web Archive snapshot closest to 2010. It only reports; it changes
nothing.
"""
import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / 'docs'
OWN = ('neteinstein.github.io', 'github.com/neteinstein', 'docs.github.com',
       'squidfunk.github.io', 'obsidian.md', 'exemplo.pt')
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/120 Safari/537.36')
socket.setdefaulttimeout(20)


def urls():
    found = defaultdict(set)
    for page in sorted(DOCS.rglob('*.md')):
        for u in re.findall(r'https?://[^\s)<>\]"\'`]+',
                            page.read_text(encoding='utf-8')):
            u = u.rstrip('.,;')
            if not any(o in u for o in OWN):
                found[u].add(str(page.relative_to(DOCS)))
    return found


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read(200_000).decode('utf-8', 'replace')
            title = re.search(r'<title[^>]*>(.*?)</title>', body, re.S | re.I)
            return (r.status, r.geturl(),
                    ' '.join(title.group(1).split())[:80] if title else '')
    except urllib.error.HTTPError as e:
        return e.code, url, ''
    except Exception as e:  # DNS failure, timeout, TLS…
        return type(e).__name__, url, str(e)[:80]


def archived(url):
    api = ('https://archive.org/wayback/available?timestamp=20100101&url='
           + urllib.parse.quote(url, safe=''))
    try:
        with urllib.request.urlopen(api) as r:
            snap = json.load(r).get('archived_snapshots', {}).get('closest')
            return snap['url'] if snap and snap.get('available') else ''
    except Exception:
        return ''


def main():
    rows = ['| URL | Páginas | Estado | Destino | Título | Arquivo (~2010) |',
            '| --- | --- | --- | --- | --- | --- |']
    for url, pages in sorted(urls().items()):
        status, final, title = fetch(url)
        rows.append(f'| {url} | {", ".join(sorted(pages))} | {status} | '
                    f'{final if final != url else ""} | '
                    f'{title.replace("|", "/")} | {archived(url)} |')
        print(rows[-1], flush=True)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as f:
            f.write('## Ligações externas\n\n' + '\n'.join(rows) + '\n')


if __name__ == '__main__':
    main()
