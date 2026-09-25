# -*- coding: utf-8 -*-
"""Génère les sites marchés d'Uback (un dossier par pays : ma/, pl/, vn/…), tous sur le même gabarit
(tools/site.py). Chaque marché ne diffère que par ses réglages ci-dessous et par ses données.
Usage : python3 tools/build_site.py            (tous les marchés)
        python3 tools/build_site.py pl vn      (seulement ceux-là)
Chaque marché écrit UNIQUEMENT dans son dossier, à partir de <code>/data/<data>.
La racine (homepage monde, redirections, sitemap, robots, CNAME) se maintient à la main."""
import os, sys, runpy, hashlib

TOOLS = os.path.dirname(os.path.abspath(__file__))

# Réglages par marché — les textes sont dans la langue du marché (lang).
#   top_n        nombre de places du classement publié
#   name / in / the / adj_*   « Maroc » / « au Maroc » / « le Maroc » / marocain, marocaine, marocaines
#   cities       villes de la diaspora (« Investir au Maroc, à plusieurs, depuis … »)
#   partner_*    profil du partenaire agréé recherché (régulateur local)
#   deals_phrase taille du marché, page partenaire (« Dans un marché comme le Maroc, avec … »)
#   press        sources de presse, page méthode
#   sectors      4 verticales (titre, description) ; sectors_soon : les suivantes
#   langs        langues affichées dans l'en-tête (code, disponible ?)
#   slug         nom du formulaire de suivi ; og_v : version de l'image de partage
MARKETS = [
    {'code': 'ma', 'lang': 'fr', 'data': 'classement-ma-2026-09.json', 'top_n': 20, 'slug': 'maroc', 'og_v': 2,
     'name': 'Maroc', 'in': 'au Maroc', 'the': 'le Maroc', 'adj_m': 'marocain', 'adj_f': 'marocaine', 'adj_fp': 'marocaines',
     'names': {'fr': 'Maroc', 'en': 'Morocco'},
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
     'langs': [('FR', True), ('EN', False), ('AR', False)],
     'flag': '<svg viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#C1272D"/><polygon points="24,8.5 26.6,16.4 34.4,11.6 20,20.9 29.6,20.9 18.2,11.6 26,16.4" fill="none" stroke="#006233" stroke-width="1.6" stroke-linejoin="round" transform="translate(-2.2 1.2)"/></svg>'},

    {'code': 'pl', 'lang': 'en', 'data': 'classement-pl-2026-09.json', 'top_n': 15, 'slug': 'poland', 'og_v': 1,
     'name': 'Poland', 'in': 'in Poland', 'the': 'Poland', 'adj_m': 'Polish', 'adj_f': 'Polish', 'adj_fp': 'Polish',
     'names': {'fr': 'Pologne', 'en': 'Poland'},
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
     'langs': [('EN', True), ('PL', False)],
     'flag': '<svg viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="16" fill="#FFFFFF"/><rect y="16" width="48" height="16" fill="#DC143C"/><rect x=".5" y=".5" width="47" height="31" fill="none" stroke="#E4E8EE"/></svg>'},

    {'code': 'vn', 'lang': 'en', 'data': 'classement-vn-2026-09.json', 'top_n': 15, 'slug': 'vietnam', 'og_v': 1,
     'name': 'Vietnam', 'in': 'in Vietnam', 'the': 'Vietnam', 'adj_m': 'Vietnamese', 'adj_f': 'Vietnamese', 'adj_fp': 'Vietnamese',
     'names': {'fr': 'Vietnam', 'en': 'Vietnam'},
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
     'langs': [('EN', True), ('VI', False)],
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

# version de la feuille de style (empreinte du fichier) : un changement de style est vu tout de suite,
# sans attendre l'expiration du cache des navigateurs
CSS_V = hashlib.sha1(open(os.path.join(TOOLS, '..', 'ma', 'assets', 'style.css'), 'rb').read()).hexdigest()[:8]

wanted = set(sys.argv[1:])
for m in MARKETS:
    if wanted and m['code'] not in wanted:
        continue
    m['switcher'] = switcher(m)
    m['css_v'] = CSS_V
    runpy.run_path(os.path.join(TOOLS, 'site.py'), init_globals={'M': m})
    print('ok', m['code'])
