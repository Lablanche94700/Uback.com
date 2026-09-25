# -*- coding: utf-8 -*-
"""Génère les sites marchés d'Uback (un dossier par pays : ma/, pl/, vn/…).
Usage : python3 tools/build_site.py            (tous les marchés)
        python3 tools/build_site.py pl vn      (seulement ceux-là)
Chaque marché écrit UNIQUEMENT dans son dossier, à partir de <code>/data/<data>.
La racine (homepage monde, redirections, sitemap, robots, CNAME) se maintient à la main."""
import os, sys, runpy

TOOLS = os.path.dirname(os.path.abspath(__file__))

# lang      : 'fr' = gabarit complet (Backers, partenaire) ; 'en' = gabarit classement seul
# partner   : 'selection' (partenaire en cours de sélection) ou 'onboarding' (intentions pas encore ouvertes)
# top_n     : nombre de places du classement publié
# names     : nom du pays dans chaque langue de l'interface (sélecteur de pays)
MARKETS = [
    {'code': 'ma', 'lang': 'fr', 'data': 'classement-ma-2026-09.json', 'partner': 'selection', 'top_n': 20,
     'name': 'Maroc', 'names': {'fr': 'Maroc', 'en': 'Morocco'},
     'flag': '<svg viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#C1272D"/><polygon points="24,8.5 26.6,16.4 34.4,11.6 20,20.9 29.6,20.9 18.2,11.6 26,16.4" fill="none" stroke="#006233" stroke-width="1.6" stroke-linejoin="round" transform="translate(-2.2 1.2)"/></svg>'},
    {'code': 'pl', 'lang': 'en', 'data': 'classement-pl-2026-09.json', 'partner': 'onboarding', 'top_n': 15,
     'name': 'Poland', 'adjective': 'Polish', 'names': {'fr': 'Pologne', 'en': 'Poland'},
     'flag': '<svg viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="16" fill="#FFFFFF"/><rect y="16" width="48" height="16" fill="#DC143C"/><rect x=".5" y=".5" width="47" height="31" fill="none" stroke="#E4E8EE"/></svg>'},
    {'code': 'vn', 'lang': 'en', 'data': 'classement-vn-2026-09.json', 'partner': 'onboarding', 'top_n': 15,
     'name': 'Vietnam', 'adjective': 'Vietnamese', 'names': {'fr': 'Vietnam', 'en': 'Vietnam'},
     'flag': '<svg viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#DA251D"/><polygon points="24,7 26.47,14.6 34.46,14.6 28,19.3 30.47,26.9 24,22.2 17.53,26.9 20,19.3 13.54,14.6 21.53,14.6" fill="#FFFF00"/></svg>'},
]

UI = {'fr': {'all': 'Tous les marchés', 'choose': 'Changer de pays'},
      'en': {'all': 'All markets', 'choose': 'Change country'}}

def switcher(m):
    """Sélecteur de pays de l'en-tête : liens absolus écrits « @ROOT@… » pour échapper au préfixe du marché."""
    ui = UI[m['lang']]
    items = ''.join(
        f'<a href="@ROOT@{o["code"]}/"{" aria-current=\"page\"" if o is m else ""}>{o["flag"]}{o["names"][m["lang"]]}'
        f'<span class="l">{o["lang"].upper()}</span></a>' for o in MARKETS)
    return (f'<details class="mkt"><summary class="market" aria-label="{ui["choose"]}">{m["names"][m["lang"]]}</summary>'
            f'<div class="menu">{items}<hr><a href="@ROOT@">{ui["all"]}</a></div></details>')

wanted = set(sys.argv[1:])
for m in MARKETS:
    if wanted and m['code'] not in wanted:
        continue
    m['switcher'] = switcher(m)
    runpy.run_path(os.path.join(TOOLS, f"site_{m['lang']}.py"), init_globals={'M': m})
    print('ok', m['code'])
