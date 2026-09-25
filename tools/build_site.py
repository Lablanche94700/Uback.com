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
MARKETS = [
    {'code': 'ma', 'lang': 'fr', 'data': 'classement-ma-2026-09.json', 'partner': 'selection', 'top_n': 20,
     'name': 'Maroc'},
    {'code': 'pl', 'lang': 'en', 'data': 'classement-pl-2026-09.json', 'partner': 'onboarding', 'top_n': 15,
     'name': 'Poland', 'adjective': 'Polish'},
    {'code': 'vn', 'lang': 'en', 'data': 'classement-vn-2026-09.json', 'partner': 'onboarding', 'top_n': 15,
     'name': 'Vietnam', 'adjective': 'Vietnamese'},
]

wanted = set(sys.argv[1:])
for m in MARKETS:
    if wanted and m['code'] not in wanted:
        continue
    runpy.run_path(os.path.join(TOOLS, f"site_{m['lang']}.py"), init_globals={'M': m})
    print('ok', m['code'])
