# -*- coding: utf-8 -*-
"""Génère les sites marchés d'Uback (un dossier par pays : ma/, pl/, vn/…), tous sur le même gabarit
(tools/site.py). Chaque marché ne diffère que par ses réglages ci-dessous et par ses données.
Un marché peut exister en plusieurs langues : une version principale à la racine du dossier (ex. /ma/, anglais)
et des versions secondaires dans un sous-dossier (ex. /ma/fr/), reliées par le sélecteur de langue.
Usage : python3 tools/build_site.py            (tous les marchés)
        python3 tools/build_site.py pl vn      (seulement ceux-là)
Chaque marché écrit UNIQUEMENT dans son dossier, à partir de <code>/data/<data> (+ couche de traduction <overlay>).
La racine (homepage monde : tools/build_home.py ; redirections, sitemap, robots, CNAME) est hors de ce script."""
import os, sys, runpy, hashlib, json

TOOLS = os.path.dirname(os.path.abspath(__file__))

FLAGS = {
 'ma': '<svg viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#C1272D"/><polygon points="24,8.5 26.6,16.4 34.4,11.6 20,20.9 29.6,20.9 18.2,11.6 26,16.4" fill="none" stroke="#006233" stroke-width="1.6" stroke-linejoin="round" transform="translate(-2.2 1.2)"/></svg>',
 'pl': '<svg viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="16" fill="#FFFFFF"/><rect y="16" width="48" height="16" fill="#DC143C"/><rect x=".5" y=".5" width="47" height="31" fill="none" stroke="#E4E8EE"/></svg>',
 'vn': '<svg viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#DA251D"/><polygon points="24,7 26.47,14.6 34.46,14.6 28,19.3 30.47,26.9 24,22.2 17.53,26.9 20,19.3 13.54,14.6 21.53,14.6" fill="#FFFF00"/></svg>',
}
NAMES = {'ma': {'fr': 'Maroc', 'en': 'Morocco'}, 'pl': {'fr': 'Pologne', 'en': 'Poland'}, 'vn': {'fr': 'Vietnam', 'en': 'Vietnam'}}

# Une entrée par version (marché × langue) ; les textes sont dans la langue de la version (lang).
#   path         chemin sur uback.com ; default : version principale (liens depuis la homepage et le sélecteur de pays)
#   data         fichier de référence (chiffres, sources) ; overlay : couche de traduction des textes (optionnelle)
#   canonical    cette version écrit les champs de valorisation calculés dans le fichier de référence
#   top_n        nombre de places du classement publié
#   name / in / the / adj_*   « Maroc » / « au Maroc » / « le Maroc » / marocain, marocaine, marocaines
#   cities       villes de la diaspora (« Investir au Maroc, à plusieurs, depuis … »)
#   partner_*    profil du partenaire agréé recherché (régulateur local) ; partner_name : partenaire signé (None sinon)
#   deals_phrase taille du marché, page partenaire ; press : sources de presse, page méthode
#   sectors      4 verticales (titre, description) ; sectors_soon : les suivantes
#   langs_soon   langues annoncées mais pas encore disponibles (grisées dans l'en-tête)
#   slug         nom du formulaire de suivi ; og / og_v : image de partage et sa version
MARKETS = [
    {'code': 'ma', 'lang': 'en', 'path': '/ma', 'default': True, 'canonical': False,
     'data': 'classement-ma-2026-09.json', 'overlay': 'classement-ma-2026-09.en.json',
     'top_n': 20, 'slug': 'morocco', 'og': 'og-image-en.png', 'og_v': 1, 'partner_name': None,
     'name': 'Morocco', 'in': 'in Morocco', 'the': 'Morocco', 'adj_m': 'Moroccan', 'adj_f': 'Moroccan', 'adj_fp': 'Moroccan',
     'cities': 'Paris, Dubai or Montreal',
     'partner_short': 'Investment adviser licensed by the AMMC (Moroccan Capital Market Authority) or investment bank',
     'partner_long': 'investment adviser licensed by the AMMC, investment bank or M&amp;A boutique, with experience of private companies and of English',
     'deals_phrase': 'a few dozen venture rounds a year across all players',
     'press': 'Moroccan and international business and technology press (Médias24, Le Desk, TelQuel, L’Economiste, Challenge, LesEco, Le Matin, Agence Ecofin, TechCrunch, TechCabal, Wamda, Disrupt Africa), Partech Africa and UM6P Ventures reports, investor announcements.',
     'sectors': [('Fintech &amp; payments', 'Neobanks, merchant payments, credit and loyalty for retailers.'),
                 ('B2B commerce &amp; retail', 'Supplies for retailers, e-commerce, brands.'),
                 ('Agritech &amp; food', 'Agricultural distribution, precision farming, water.'),
                 ('Logistics &amp; mobility', 'Freight, last mile, shared transport, electric vehicles.')],
     'sectors_soon': ['Proptech', 'Healthtech', 'Education', 'Energy &amp; climate', 'B2B software'],
     'langs_soon': ['AR']},

    {'code': 'ma', 'lang': 'fr', 'path': '/ma/fr', 'default': False, 'canonical': True,
     'data': 'classement-ma-2026-09.json',
     'top_n': 20, 'slug': 'maroc', 'og': 'og-image.png', 'og_v': 3, 'partner_name': None,
     'name': 'Maroc', 'in': 'au Maroc', 'the': 'le Maroc', 'adj_m': 'marocain', 'adj_f': 'marocaine', 'adj_fp': 'marocaines',
     'cities': 'Paris, Dubaï ou Montréal',
     'partner_short': 'Conseiller en investissements financiers agréé par l’AMMC ou banque d’affaires',
     'partner_long': 'conseiller en investissements financiers agréé par l’AMMC, banque d’affaires ou boutique M&amp;A, avec une pratique du non-coté et de l’anglais',
     'deals_phrase': 'quelques dizaines de tours par an tous acteurs confondus',
     'press': 'Presse économique et technologique (Médias24, Le Desk, TelQuel, L’Economiste, Challenge, LesEco, Le Matin, Agence Ecofin, TechCrunch, TechCabal, Wamda, Disrupt Africa), rapports Partech Africa et UM6P Ventures, communiqués des investisseurs.',
     'sectors': [('Fintech &amp; paiement', 'Néobanques, paiement marchand, crédit et fidélité pour les commerçants.'),
                 ('Commerce &amp; retail B2B', 'Approvisionnement des commerçants, e-commerce, marques.'),
                 ('Agritech &amp; alimentation', 'Distribution agricole, agriculture de précision, eau.'),
                 ('Logistique &amp; mobilité', 'Fret, dernier kilomètre, transport partagé, véhicules électriques.')],
     'sectors_soon': ['Immobilier (proptech)', 'Santé', 'Éducation', 'Énergie &amp; climat', 'Logiciels B2B'],
     'langs_soon': ['AR']},

    {'code': 'pl', 'lang': 'en', 'path': '/pl', 'default': True, 'canonical': True,
     'data': 'classement-pl-2026-09.json',
     'top_n': 15, 'slug': 'poland', 'og': 'og-image.png', 'og_v': 2, 'partner_name': None,
     'name': 'Poland', 'in': 'in Poland', 'the': 'Poland', 'adj_m': 'Polish', 'adj_f': 'Polish', 'adj_fp': 'Polish',
     'cities': 'London, Chicago or Berlin',
     'partner_short': 'Investment firm licensed by the KNF (Polish Financial Supervision Authority) or investment bank',
     'partner_long': 'investment firm licensed by the KNF, investment bank or M&amp;A boutique, with experience of private companies and of English',
     'deals_phrase': 'around 180 venture rounds a year across all players',
     'press': 'Polish and international business and technology press (Rzeczpospolita, Puls Biznesu, Business Insider Polska, Bankier, Mamstartup, Brief, Sifted, TechCrunch, EU-Startups, Tech.eu), PFR Ventures and Inovo reports, investor announcements.',
     'sectors': [('Healthtech', 'Doctor booking, clinics, AI diagnostics and online pharmacy.'),
                 ('Fintech &amp; payments', 'Crypto on-ramps, payments, investing and lending.'),
                 ('B2B software &amp; AI', 'SaaS, developer tools, AI and marketing technology.'),
                 ('Commerce &amp; logistics', 'E-commerce, packaging, warehouse robotics and last mile.')],
     'sectors_soon': ['Mobility', 'Education', 'Energy &amp; climate', 'Proptech', 'Gaming'],
     'langs_soon': ['PL']},

    {'code': 'vn', 'lang': 'en', 'path': '/vn', 'default': True, 'canonical': True,
     'data': 'classement-vn-2026-09.json',
     'top_n': 15, 'slug': 'vietnam', 'og': 'og-image.png', 'og_v': 2, 'partner_name': None,
     'name': 'Vietnam', 'in': 'in Vietnam', 'the': 'Vietnam', 'adj_m': 'Vietnamese', 'adj_f': 'Vietnamese', 'adj_fp': 'Vietnamese',
     'cities': 'Singapore, Paris or California',
     'partner_short': 'Securities or fund management company licensed by the SSC (State Securities Commission of Vietnam) or investment bank',
     'partner_long': 'securities or fund management company licensed by the SSC, investment bank or M&amp;A boutique, with experience of private companies and of English',
     'deals_phrase': 'around 100 venture rounds a year across all players',
     'press': 'Vietnamese and international business and technology press (VnExpress, The Investor, Vietnam Investment Review, Tuoi Tre, DealStreetAsia, Tech in Asia, e27, KrASIA, TechCrunch), Do Ventures, NIC/VPCA/BCG and VinVentures reports, investor announcements.',
     'sectors': [('Fintech &amp; payments', 'E-wallets, payments, digital lending and investing.'),
                 ('Commerce &amp; logistics', 'E-commerce enablers, B2B distribution and delivery.'),
                 ('Education', 'K-12, English learning and online universities.'),
                 ('Mobility &amp; energy', 'Electric motorbikes, ride-hailing and solar financing.')],
     'sectors_soon': ['Healthtech', 'AI', 'Proptech', 'Gaming &amp; Web3', 'B2B software'],
     'langs_soon': ['VI']},
]

UI = {'fr': {'all': 'Tous les marchés', 'choose': 'Changer de pays'},
      'en': {'all': 'All markets', 'choose': 'Change country'}}

def switcher(m):
    """Sélecteur de pays : chaque pays mène à sa version dans la langue de la page si elle existe, sinon à sa version
    principale. Liens absolus écrits « @ROOT@… » pour échapper au préfixe de la version."""
    ui, items, seen = UI[m['lang']], '', []
    for o in MARKETS:
        if o['code'] in seen:
            continue
        seen.append(o['code'])
        vs = [v for v in MARKETS if v['code'] == o['code']]
        v = next((x for x in vs if x['lang'] == m['lang']), next(x for x in vs if x['default']))
        cur = ' aria-current="page"' if o['code'] == m['code'] else ''
        items += (f'<a href="@ROOT@{v["path"][1:]}/"{cur}>{FLAGS[o["code"]]}{NAMES[o["code"]][m["lang"]]}'
                  f'<span class="l">{v["lang"].upper()}</span></a>')
    return (f'<details class="mkt"><summary class="market" aria-label="{ui["choose"]}">{NAMES[m["code"]][m["lang"]]}</summary>'
            f'<div class="menu">{items}<hr><a href="@ROOT@">{ui["all"]}</a></div></details>')

# version de la feuille de style (empreinte du fichier) : un changement de style est vu tout de suite,
# sans attendre l'expiration du cache des navigateurs
CSS_V = hashlib.sha1(open(os.path.join(TOOLS, '..', 'ma', 'assets', 'style.css'), 'rb').read()).hexdigest()[:8]

sys.path.insert(0, TOOLS)
import valuation

wanted = set(sys.argv[1:])
for m in MARKETS:
    if wanted and m['code'] not in wanted:
        continue
    if m['canonical']:
        # ordre de grandeur de valorisation : recalculé depuis "valuation_input" (règle dans tools/valuation.py)
        path = os.path.join(TOOLS, '..', m['code'], 'data', m['data'])
        data = json.load(open(path, encoding='utf-8'))
        if valuation.apply(data, m['lang']):
            open(path, 'w', encoding='utf-8', newline='\n').write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    m['variants'] = [{'lang': v['lang'], 'path': v['path'], 'default': v['default']} for v in MARKETS if v['code'] == m['code']]
    m['switcher'] = switcher(m)
    m['css_v'] = CSS_V
    runpy.run_path(os.path.join(TOOLS, 'site.py'), init_globals={'M': m})
    print('ok', m['path'])
