# -*- coding: utf-8 -*-
"""Police Inter hébergée sur uback.com (/assets/fonts/), à la place de Google Fonts : aucune adresse IP de visiteur
n'est transmise à Google pour afficher le texte. Fichiers : paquet @fontsource-variable/inter 5 (Inter, SIL OFL 1.1,
licence dans assets/fonts/OFL.txt), police variable 100–900, sous-ensembles latin, latin-ext et vietnamese.
FONT_CSS : intégré à la CSS en ligne de tools/build_home.py et recopié dans ma/assets/style.css entre deux marqueurs
par sync_css() (appelé par tools/build_site.py). PRELOAD : dans le <head> de chaque page générée."""

FACES = [('latin', 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'), ('latin-ext', 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'), ('vietnamese', 'U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB')]

FONT_CSS = ''.join(
    "@font-face{font-family:Inter;font-style:normal;font-display:swap;font-weight:100 900;"
    f"src:url(/assets/fonts/inter-{sub}-wght-normal.woff2) format('woff2-variations'),url(/assets/fonts/inter-{sub}-wght-normal.woff2) format('woff2');"
    f"unicode-range:{ur}}}\n" for sub, ur in FACES)

PRELOAD = '<link rel="preload" href="/assets/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'

START, END = '/* fonts:start (généré par tools/fonts.py, ne pas modifier ici) */', '/* fonts:end */'

def sync_css(path):
    """Place FONT_CSS en tête de la feuille de style des marchés, entre les marqueurs."""
    s = open(path, encoding='utf-8').read()
    block = f'{START}\n{FONT_CSS}{END}\n'
    if START in s:
        new = s[:s.index(START)] + block + s[s.index(END) + len(END) + 1:]
    else:
        new = block + s
    if new != s:
        open(path, 'w', encoding='utf-8', newline='\n').write(new)
