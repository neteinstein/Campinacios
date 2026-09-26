#!/usr/bin/env python3
"""Password-protected pages of the Wikinácios.

Pages that were restricted on the wiki are published encrypted: the Markdown
file in docs/ holds only AES-256-GCM ciphertext (key derived from the
password with PBKDF2-SHA256), and docs/assets/restrito.js decrypts it in the
browser once the visitor types the password. Neither the repository nor the
site ever holds the plain text.

Usage:
    pip install cryptography mkdocs-material
    python3 scripts/restrito.py mudar-palavra-passe
    python3 scripts/restrito.py abrir    # decrypt into restrito-aberto/ to edit
    python3 scripts/restrito.py fechar   # encrypt restrito-aberto/ back into docs/

The password is asked for, or read from WIKINACIOS_PALAVRA_PASSE (and the new
one from WIKINACIOS_NOVA_PALAVRA_PASSE).
"""
import base64
import getpass
import hashlib
import html
import json
import os
import re
import secrets
import shutil
import sys
from pathlib import Path

import markdown
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pymdownx.slugs import slugify

ITERATIONS = 600_000
ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'
OPEN_DIR = ROOT / 'restrito-aberto'

NOTICE = ('🔒 Esta página era de acesso restrito na Wikinácios (Direcção '
          'Nacional e Directores). É precisa a palavra-passe para a ler.')
BLOCK = re.compile(r'<div class="wiki-restrito" data-salt="([^"]+)" '
                   r'data-iter="(\d+)" data-iv="([^"]+)" data-ct="([^"]+)">'
                   r'.*?</div>', re.S)


def b64(data):
    return base64.b64encode(data).decode()


def unb64(text):
    return base64.b64decode(text)


class Key:
    """An AES key derived from the password; one salt for the whole site, so
    the browser derives it once and can unlock every page with it."""

    def __init__(self, password, salt=None, iterations=ITERATIONS):
        self.salt = salt or secrets.token_bytes(16)
        self.iterations = iterations
        raw = hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt,
                                  iterations, 32)
        self.aes = AESGCM(raw)

    def seal(self, payload):
        iv = secrets.token_bytes(12)
        ct = self.aes.encrypt(iv, json.dumps(payload).encode(), None)
        return (f'<div class="wiki-restrito" data-salt="{b64(self.salt)}" '
                f'data-iter="{self.iterations}" data-iv="{b64(iv)}" '
                f'data-ct="{b64(ct)}">\n<p>{html.escape(NOTICE)}</p>\n</div>')

    def open(self, block):
        m = BLOCK.search(block)
        return json.loads(self.aes.decrypt(unb64(m.group(3)),
                                           unb64(m.group(4)), None))


def render(md_text):
    """Markdown -> HTML as mkdocs.yml renders it, with page links rewritten
    the way MkDocs rewrites them (use_directory_urls: false)."""
    out = markdown.markdown(md_text, extensions=[
        'tables', 'fenced_code', 'admonition', 'attr_list', 'md_in_html',
        'toc'],
        extension_configs={'toc': {'permalink': True, 'slugify': slugify(
            case='lower')}})
    return re.sub(r'href="([^":#]+)\.md(#[^"]*)?"',
                  lambda m: f'href="{m.group(1)}.html{m.group(2) or ""}"', out)


def seal_page(key, md_body):
    return key.seal({'md': md_body, 'html': render(md_body)})


def encrypted_files():
    for path in sorted(DOCS.rglob('*.md')):
        text = path.read_text(encoding='utf-8')
        if BLOCK.search(text):
            yield path, text


def site_key(password):
    """The key the site's pages are encrypted with, checked against them."""
    files = list(encrypted_files())
    if not files:
        sys.exit('Não há páginas cifradas em docs/.')
    m = BLOCK.search(files[0][1])
    key = Key(password, unb64(m.group(1)), int(m.group(2)))
    try:
        key.open(files[0][1])
    except InvalidTag:
        sys.exit('Palavra-passe errada.')
    return key, files


def ask(env, prompt):
    value = os.environ.get(env)
    if value is None:
        value = getpass.getpass(prompt)
        if env == 'WIKINACIOS_NOVA_PALAVRA_PASSE' and value != getpass.getpass(
                'Repita a nova palavra-passe: '):
            sys.exit('As palavras-passe não coincidem.')
    if not value:
        sys.exit('Palavra-passe vazia.')
    return value


def change_password():
    old, files = site_key(ask('WIKINACIOS_PALAVRA_PASSE',
                              'Palavra-passe actual: '))
    new = Key(ask('WIKINACIOS_NOVA_PALAVRA_PASSE', 'Nova palavra-passe: '))
    for path, text in files:
        payload = old.open(text)
        path.write_text(BLOCK.sub(lambda _: new.seal(payload), text, count=1),
                        encoding='utf-8')
    print(f'{len(files)} páginas cifradas de novo com a nova palavra-passe.')


def open_pages():
    key, files = site_key(ask('WIKINACIOS_PALAVRA_PASSE', 'Palavra-passe: '))
    for path, text in files:
        out = OPEN_DIR / path.relative_to(DOCS)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(key.open(text)['md'], encoding='utf-8')
    print(f'{len(files)} páginas decifradas em {OPEN_DIR.name}/ (fora do git).'
          ' Edite-as e corra "fechar" para as cifrar de novo.')


def close_pages():
    if not OPEN_DIR.exists():
        sys.exit(f'Não existe {OPEN_DIR.name}/: corra primeiro "abrir".')
    key, files = site_key(ask('WIKINACIOS_PALAVRA_PASSE', 'Palavra-passe: '))
    for path, text in files:
        src = OPEN_DIR / path.relative_to(DOCS)
        if src.exists():
            body = src.read_text(encoding='utf-8')
            path.write_text(BLOCK.sub(lambda _: seal_page(key, body), text,
                                      count=1), encoding='utf-8')
    shutil.rmtree(OPEN_DIR)
    print(f'{len(files)} páginas cifradas; {OPEN_DIR.name}/ apagada.')


if __name__ == '__main__':
    commands = {'mudar-palavra-passe': change_password, 'abrir': open_pages,
                'fechar': close_pages}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        sys.exit(__doc__)
    commands[sys.argv[1]]()
