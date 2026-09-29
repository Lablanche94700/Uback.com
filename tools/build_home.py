# -*- coding: utf-8 -*-
"""Génère la homepage monde (/index.html, en anglais) à partir de data/sectors.json et des listes ci-dessous.
Usage : python3 tools/build_home.py
- À gauche : classements mondiaux par secteur (famille > secteur > segment ; seul le segment est classé).
- À droite : classements par pays (marchés domestiques) et régionaux.
Tout le contenu est écrit en HTML statique (SEO) ; le JavaScript ne sert qu'à la recherche, aux onglets mobiles
et à l'envoi du formulaire. Les sites marchés (/ma, /pl, /vn) sont générés par tools/build_site.py."""
import html, json, os, re, sys, unicodedata
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_site import MARKETS, NAMES, next_edition, format_date, months_txt   # même calendrier que les pages marchés
from pages_global import METHOD, LEGAL, INVEST

def next_ed(code):
    m = next(v for v in MARKETS if v['code'] == code and v['default'])
    return format_date(next_edition(m), 'en')
SECTORS = json.load(open(os.path.join(ROOT, 'data', 'sectors.json'), encoding='utf-8'))
FORM_MODE = 'soon'                  # 'soon' (inscriptions pas encore ouvertes : « Coming soon » au clic),
                                    # 'mailto' (message prérempli vers FORM_EMAIL) ou 'netlify' (Netlify Forms)
FORM_EMAIL = 'contact@uback.com'
METHOD_URL = '/method.html'         # méthode globale (anglais) ; version française : /fr/methode.html
THANKS_URL = '/pl/thank-you.html'
e = html.escape

FLAGS = {
 'ma': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#C1272D"/><polygon points="24,8.5 26.6,16.4 34.4,11.6 20,20.9 29.6,20.9 18.2,11.6 26,16.4" fill="none" stroke="#006233" stroke-width="1.6" stroke-linejoin="round" transform="translate(-2.2 1.2)"/></svg>',
 'pl': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="16" fill="#FFFFFF"/><rect y="16" width="48" height="16" fill="#DC143C"/><rect x=".5" y=".5" width="47" height="31" fill="none" stroke="#E4E8EE"/></svg>',
 'vn': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#DA251D"/><polygon points="24,7 26.47,14.6 34.46,14.6 28,19.3 30.47,26.9 24,22.2 17.53,26.9 20,19.3 13.54,14.6 21.53,14.6" fill="#FFFF00"/></svg>',
}

# Classements par pays, groupés par région. live : (code, nom, sous-ligne, url) ; soon : noms à venir.
REGIONS = [
 {'name': 'North Africa & Middle East', 'live': [('ma', 'Morocco', 'In English & French · next edition ' + next_ed('ma'), '/ma/')],
  'soon': ['Tunisia', 'Egypt', 'UAE', 'Saudi Arabia']},
 {'name': 'Europe', 'live': [('pl', 'Poland', 'In English · next edition ' + next_ed('pl'), '/pl/')],
  'soon': ['France', 'Romania', 'Ukraine']},
 {'name': 'Asia', 'live': [('vn', 'Vietnam', 'In English · next edition ' + next_ed('vn'), '/vn/')],
  'soon': ['Indonesia', 'Philippines']},
 {'name': 'Sub-Saharan Africa', 'live': [], 'soon': ['Nigeria', 'Kenya', 'Senegal', 'Côte d’Ivoire']},
 {'name': 'Latin America', 'live': [], 'soon': ['Mexico', 'Colombia', 'Chile']},
]
REGIONAL = ['Africa', 'Central & Eastern Europe', 'Southeast Asia', 'Middle East', 'Latin America']
OPEN_FAMILY = 'FIN'                 # famille ouverte au chargement

def norm(s):
    """Minuscules, sans accents : même normalisation que la recherche en JavaScript."""
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().lower()

def soon_pill(label, extra=''):
    return (f'<span class="pill soon" tabindex="0" aria-disabled="true"{extra}>{e(label)}'
            f'<span class="tip" role="tooltip">Coming soon</span></span>')

# segments publiés : ceux qui ont un fichier data/segments/<slug>.json (page générée par tools/build_segments.py)
for _f in SECTORS['families']:
    for _s in _f['sectors']:
        for _g in _s['segments']:
            if os.path.exists(os.path.join(ROOT, 'data', 'segments', _g['slug'] + '.json')):
                _g['status'], _g['url'] = 'published', f"/segments/{_g['slug']}/"

def segment(g):
    if g.get('status') == 'published' and g.get('url'):
        return f'<a class="pill pub" href="{e(g["url"])}" data-n="{e(norm(g["name"]))}">{e(g["name"])}</a>'
    return soon_pill(g['name'], f' data-n="{e(norm(g["name"]))}"')

def fam_link(f):
    """Lien vers la page de la famille (/sectors/<slug>/, générée par tools/build_segments.py) dès qu'elle a un segment publié."""
    if not any(g.get('status') == 'published' for s in f['sectors'] for g in s['segments']):
        return ''
    slug = re.sub(r'[^a-z0-9]+', '-', f['name'].lower()).strip('-')
    return f'<a class="fam-link" href="/sectors/{slug}/">All {e(f["name"])} rankings <span aria-hidden="true">→</span></a>'

def fam_slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

# Menu « Rankings » de l'en-tête (homepage et pages globales) : familles publiées (page /sectors/<famille>/) et pays en ligne,
# calculés depuis data/sectors.json, data/segments/ et REGIONS. Même mécanisme que les sélecteurs des pages pays et segment
# (<details>, sans JavaScript) ; un petit script le referme au clic à l'extérieur ou avec Échap.
RK_UI = {'en': dict(t='Rankings', sec='By sector', cty='By country', all_s='All sectors', all_c='All countries'),
         'fr': dict(t='Classements', sec='Par secteur', cty='Par pays', all_s='Tous les secteurs', all_c='Tous les pays')}

def rankings_menu(lang):
    u = RK_UI[lang]
    fams = ''.join(f'<a href="/sectors/{fam_slug(f["name"])}/">{e(f["name"])}</a>' for f in FAMS
                   if any(g.get('status') == 'published' for s in f['sectors'] for g in s['segments']))
    ctys = ''
    for r in REGIONS:
        for code, name, sub, url in r['live']:
            if lang == 'fr':                      # version française du pays si elle existe, sinon sa version principale
                v = next((m for m in MARKETS if m['code'] == code and m['lang'] == 'fr'), None)
                name, url = NAMES[code]['fr'], (v['path'] + '/' if v else url)
            ctys += f'<a href="{url}">{FLAGS[code]}{e(name)}</a>'
    return (f'<details class="rk"><summary>{u["t"]}</summary><div class="rk-menu">'
            f'<div class="rk-col"><span class="rk-h">{u["sec"]}</span>{fams}<a class="rk-all" href="/#sectors">{u["all_s"]} <span aria-hidden="true">→</span></a></div>'
            f'<div class="rk-col"><span class="rk-h">{u["cty"]}</span>{ctys}<a class="rk-all" href="/#countries">{u["all_c"]} <span aria-hidden="true">→</span></a></div>'
            f'</div></details>' + RK_JS)

RK_JS = ('<script>(function(){var d=document.querySelector("details.rk");if(!d)return;'
         'document.addEventListener("click",function(ev){if(d.open&&!d.contains(ev.target))d.open=false;});'
         'document.addEventListener("keydown",function(ev){if(ev.key==="Escape"&&d.open){d.open=false;d.querySelector("summary").focus();}});'
         'd.querySelectorAll(".rk-menu a").forEach(function(a){a.addEventListener("click",function(){d.open=false;});});})();</script>')

def family(f):
    n_sec = len(f['sectors'])
    n_seg = sum(len(s['segments']) for s in f['sectors'])
    body = ''.join(
        f'<div class="sect" data-n="{e(norm(s["name"]))}"><div class="sect-h">{e(f["name"])} › {e(s["name"])}</div>'
        f'<div class="pills">{"".join(segment(g) for g in s["segments"])}</div></div>' for s in f['sectors'])
    return (f'<details class="fam" data-n="{e(norm(f["name"]))}"{" open" if f["id"] == OPEN_FAMILY else ""}>'
            f'<summary><span class="chev" aria-hidden="true"></span><b>{e(f["name"])}</b>'
            f'<span class="cnt">{n_sec} sectors · {n_seg} segments</span></summary>'
            f'<div class="fam-body">{body}{fam_link(f)}</div></details>')

def region(r):
    live = ''.join(
        f'<div class="live-row">{FLAGS[c]}<div class="lr-txt"><b>{e(n)}</b><span>{e(sub)}</span></div>'
        f'<a class="btn-view" href="{url}">View <span aria-hidden="true">→</span></a></div>' for c, n, sub, url in r['live'])
    soon = f'<div class="pills">{"".join(soon_pill(s) for s in r["soon"])}</div>' if r['soon'] else ''
    return f'<div class="region"><h3 class="reg-h">{e(r["name"])}</h3>{live}{soon}</div>'

FAMS = SECTORS['families']
N_FAM = len(FAMS)
N_SEG = sum(len(s['segments']) for f in FAMS for s in f['sectors'])
DESC = ('Uback ranks funded, non-listed tech startups by AI-estimated valuation, by country and by global segment. '
        'The market sets the value; our AI estimates it. Investors can pool their intentions to invest.')
JSONLD = {"@context": "https://schema.org", "@graph": [
    {"@type": "Organization", "name": "Uback", "url": "https://uback.com/", "email": "contact@uback.com",
     "description": DESC,
     "logo": "https://uback.com/assets/favicon-192.png"},
    {"@type": "WebSite", "name": "Uback", "url": "https://uback.com/", "inLanguage": "en"},
    # liste des marchés en ligne : calculée depuis REGIONS, jamais écrite à la main
    {"@type": "ItemList", "name": "Uback markets", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": f"{n} — quarterly ranking", "url": f"https://uback.com{url}"}
        for i, (c, n, sub, url) in enumerate([x for r in REGIONS for x in r['live']], 1)]}]}
LIVE_NAMES = [n for r in REGIONS for (c, n, sub, url) in r['live']]
LIVE_TXT = ', '.join(LIVE_NAMES[:-1]) + ' and ' + LIVE_NAMES[-1] if len(LIVE_NAMES) > 1 else LIVE_NAMES[0]

CSS = '''
:root{--navy:#1E3A5F;--navy-dark:#142842;--gold:#C8A052;--bg:#F7F8FA;--line:#E4E8EE;--muted:#5A6B82;--body:#4A5A70;--dim:#6B7A8F;--dash:#C9D1DC}
*{box-sizing:border-box}
html,body{margin:0}
body{font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg);color:var(--navy);min-height:100vh;display:flex;flex-direction:column;-webkit-font-smoothing:antialiased}
a{color:var(--navy)}a:hover{color:var(--navy-dark)}
.wrap{width:100%;max-width:1200px;margin:0 auto;padding:0 20px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
[hidden]{display:none!important}

/* bandeau bêta : identique à celui des pages marchés */
.beta{background:#fbf7ee;border-bottom:1px solid var(--line);font-size:12.5px;line-height:1.4;color:var(--navy)}
.beta .wrap{min-height:32px;display:flex;align-items:center;justify-content:center;gap:6px;padding-top:6px;padding-bottom:6px;text-align:center}
.beta b{color:var(--gold);font-weight:700;white-space:nowrap}
.beta a{color:var(--navy);font-weight:600;white-space:nowrap;margin-left:4px}
header{background:#fff;border-bottom:1px solid var(--line)}
header .wrap{height:64px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;font-size:22px;font-weight:800;letter-spacing:-.02em;color:var(--navy)}
.logo .u{width:34px;height:34px;border-radius:8px;background:var(--navy);color:var(--gold);display:inline-flex;align-items:center;justify-content:center;font-size:20px;letter-spacing:0}
nav{display:flex;gap:20px;align-items:center;font-size:15px;font-weight:500}
nav a{text-decoration:none;display:inline-flex;align-items:center;min-height:44px}
.rk{position:relative}
.rk summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:7px;min-height:44px;color:var(--navy)}
.rk summary::-webkit-details-marker{display:none}
.rk summary::after{content:"";width:6px;height:6px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg);margin-top:-4px}
.rk[open] summary::after{transform:rotate(-135deg);margin-top:3px}
.rk summary:focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:4px}
.rk-menu{position:absolute;top:calc(100% + 6px);right:-16px;z-index:60;display:grid;grid-template-columns:max-content max-content;gap:4px 32px;padding:16px 18px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 10px 30px rgba(30,58,95,.14);white-space:nowrap}
.rk-col{display:flex;flex-direction:column}
.rk-h{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:0 0 4px}
.rk-menu a{display:flex;align-items:center;gap:10px;min-height:40px;padding:0 8px;margin:0 -8px;border-radius:8px;font-size:15px;font-weight:500;color:var(--navy);text-decoration:none}
.rk-menu a:hover{background:var(--bg)}
.rk-menu .flag{width:21px;height:14px;border-radius:2px}
.rk-menu a.rk-all{margin-top:4px;font-size:14px;font-weight:600;text-decoration:underline;text-decoration-color:var(--gold);text-decoration-thickness:2px;text-underline-offset:5px}
/* pages globales (sélecteur de langue en plus) : sur petit écran, le menu passe sous le logo */
@media (max-width:479px){header.hdr-lang .wrap{height:auto;flex-wrap:wrap;row-gap:0;padding-top:8px;padding-bottom:4px}header.hdr-lang nav{width:100%;justify-content:space-between;gap:10px}}
@media (max-width:379px){header .wrap{height:auto;flex-wrap:wrap;row-gap:0;padding-top:8px;padding-bottom:4px}header nav{width:100%;justify-content:space-between;gap:10px}}
@media (max-width:359px){header nav{font-size:13px;gap:4px}.langsw{font-size:12px}}
@media (max-width:719px){header .wrap{position:relative}.rk{position:static}
  .rk-menu{left:16px;right:16px;top:calc(100% - 4px);grid-template-columns:1fr;gap:14px;white-space:normal}}

.hero{padding:56px 0 32px}
.hero .wrap{display:flex;flex-direction:column;gap:20px}
.eyebrow{display:flex;align-items:center;gap:10px;font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.eyebrow i{width:20px;height:2px;background:var(--gold);display:block;flex-shrink:0}
.eyebrow i.r{display:none}
h1{margin:0;font-size:38px;line-height:1.08;font-weight:800;letter-spacing:-.03em}
.lead{margin:0;font-size:17px;line-height:1.6;color:var(--body)}
/* homepage : deux colonnes Discover / Back sous le titre */
.duo{width:100%;max-width:1040px;margin:16px auto 0;display:grid;grid-template-columns:1fr;row-gap:16px;text-align:left}
.duo-col{display:flex;flex-direction:column;align-items:flex-start;gap:14px;min-width:0}
.duo-rule{height:1px;background:#DCC89A;margin:8px 0}
.duo-k{display:flex;align-items:center;gap:10px;font-size:13px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--navy)}
.duo-k::before{content:"";width:20px;height:2px;background:var(--gold);flex-shrink:0}
.duo p{margin:0;font-size:16px;line-height:1.6;color:var(--body)}
.duo p b{font-weight:600;color:var(--navy)}
.duo a{display:inline-flex;align-items:center;gap:6px;min-height:44px;font-size:15px;font-weight:600;color:var(--navy);text-decoration:underline;text-decoration-color:var(--gold);text-decoration-thickness:2px;text-underline-offset:6px}
.duo a:hover{color:var(--navy);text-decoration-color:var(--navy)}
@media (min-width:768px){.duo{grid-template-columns:minmax(0,1fr) 1px minmax(0,1fr);column-gap:64px;row-gap:0}.duo-rule{height:auto;width:1px;margin:0;align-self:stretch}.duo p{font-size:18px;line-height:1.65}}

.rankings{padding-bottom:32px}
.view-tabs{display:none;gap:6px;padding:4px;margin-bottom:14px;background:#fff;border:1px solid var(--line);border-radius:12px}
.view-tabs button{flex:1;min-height:44px;border:0;border-radius:9px;background:none;font:inherit;font-size:15px;font-weight:600;color:var(--muted);cursor:pointer}
.view-tabs button[aria-selected="true"]{background:var(--navy);color:#fff}
.cols{display:grid;grid-template-columns:minmax(0,1fr);gap:16px;align-items:start}
.panel{background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:0 1px 2px rgba(30,58,95,.04),0 8px 24px rgba(30,58,95,.06);min-width:0}
.p-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-start;gap:12px 20px}
.p-head>div:first-child{flex:1 1 220px;min-width:0}
.kicker{font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.panel h2{margin:6px 0 6px;font-size:24px;line-height:1.2;font-weight:800;letter-spacing:-.02em}
.panel .intro{margin:0;font-size:15px;line-height:1.55;color:var(--body)}
.freq{display:inline-flex;flex-direction:column;gap:2px;padding:8px 14px;border-radius:12px;font-size:12px;color:var(--muted);white-space:nowrap}
.freq b{font-size:14px;color:var(--navy)}
.freq.gold{border:1.5px solid var(--gold)}
.freq.navy{border:1.5px solid var(--navy)}

.search{margin-top:20px}
.search label{display:block;font-size:13px;font-weight:600;margin-bottom:6px}
.search input{width:100%;min-height:44px;padding:10px 14px;border:1px solid var(--dash);border-radius:10px;font:inherit;font-size:15px;color:var(--navy);background:#fff}
.search input:focus{outline:2px solid var(--gold);outline-offset:1px;border-color:var(--gold)}
.legend{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:14px 0 10px;font-size:13px;color:var(--muted)}
.legend .count{font-weight:600;color:var(--navy);margin-right:auto}
.no-match{margin:10px 0;font-size:14px;color:var(--body)}

.fam{border-top:1px solid var(--line)}
.fam:last-of-type{border-bottom:1px solid var(--line)}
.fam summary{list-style:none;display:flex;align-items:center;gap:10px;min-height:48px;padding:6px 2px;cursor:pointer}
.fam summary::-webkit-details-marker{display:none}
.fam summary:focus-visible{outline:2px solid var(--gold);outline-offset:2px;border-radius:6px}
.chev{width:8px;height:8px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);transform:rotate(-45deg);transition:transform .15s;flex-shrink:0;margin:0 4px}
.fam[open] .chev{transform:rotate(45deg)}
.fam summary b{font-size:16px;line-height:1.3}
.fam .cnt{margin-left:auto;font-size:12px;color:var(--muted);white-space:nowrap}
/* petits écrans : le compteur passe sous le nom de la famille (aligné sur le nom) */
@media (max-width:419px){.fam summary{flex-wrap:wrap;row-gap:0;padding:8px 2px}.fam summary b{flex:1 1 0;min-width:0}.fam .cnt{flex-basis:100%;margin-left:26px}}
.fam-body{padding:2px 0 16px 24px}
.sect{margin-top:10px}
.sect-h{font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin-bottom:6px}
.pills{display:flex;flex-wrap:wrap;gap:6px}
.pill{position:relative;display:inline-flex;align-items:center;min-height:34px;padding:4px 12px;border-radius:999px;font-size:13px;font-weight:500;line-height:1.25;text-decoration:none}
.pill.soon{border:1.5px dashed var(--dash);color:var(--body);background:#fff;cursor:default}
.pill.soon:hover,.pill.soon:focus,.pill.soon.show{border-style:solid;border-color:var(--gold);outline:none}
.pill.pub{background:var(--navy);color:#fff;border:1.5px solid var(--navy)}
.pill.pub:hover{background:var(--navy-dark);color:#fff}
.fam-link{display:inline-flex;align-items:center;gap:6px;min-height:44px;margin-top:6px;font-size:14px;font-weight:600;color:var(--navy);text-decoration:underline;text-decoration-color:var(--gold);text-decoration-thickness:2px;text-underline-offset:5px}
.fam-link:hover{text-decoration-color:var(--navy)}
.pill.static{min-height:26px;padding:2px 10px;font-size:12px}
.tip{display:none;position:absolute;left:50%;bottom:calc(100% + 6px);transform:translateX(-50%);background:var(--navy);color:#fff;font-size:11px;font-weight:600;padding:4px 8px;border-radius:6px;white-space:nowrap;z-index:5;pointer-events:none}
.pill.soon:hover .tip,.pill.soon:focus .tip,.pill.soon.show .tip{display:block}

.region{margin-top:18px}
.reg-h{margin:0 0 8px;font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--dim)}
.live-row{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--line);margin-bottom:10px}
.flag{width:42px;height:28px;border-radius:4px;flex-shrink:0}
.lr-txt{display:flex;flex-direction:column;min-width:0}
.lr-txt b{font-size:17px}
.lr-txt span{font-size:13px;color:var(--muted)}
.btn-view{margin-left:auto;display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 16px;border-radius:10px;background:var(--navy);color:#fff;font-size:14px;font-weight:600;text-decoration:none;white-space:nowrap}
.btn-view:hover{background:var(--navy-dark);color:#fff}
.regional{margin-top:22px;padding:16px;border-radius:12px;background:var(--bg)}
.regional h3{margin:0 0 4px;font-size:15px;font-weight:700}
.regional p{margin:0 0 10px;font-size:13px;color:var(--muted)}

.follow{margin:8px 0 56px}
.follow .box{display:flex;flex-direction:column;gap:16px;padding:22px;background:#fff;border:1px solid var(--line);border-top:3px solid var(--gold);border-radius:16px;box-shadow:0 1px 2px rgba(30,58,95,.04),0 8px 24px rgba(30,58,95,.06)}
.follow h2{margin:0 0 4px;font-size:20px;font-weight:800}
.follow p{margin:0;font-size:14px;line-height:1.5;color:var(--body)}
.follow p.fine{margin-top:6px;font-size:12.5px;color:var(--muted)}
.follow p.soon-msg{margin:8px 0 0;display:inline-block;padding:5px 12px;border-radius:999px;background:var(--navy);color:#fff;font-size:13px;font-weight:600}
.follow form{display:flex;flex-direction:column;gap:8px}
.follow input,.follow select{min-height:44px;padding:10px 12px;border:1px solid var(--dash);border-radius:10px;font:inherit;font-size:15px;color:var(--navy);background:#fff;min-width:0}
.follow button{min-height:44px;padding:0 22px;border:0;border-radius:10px;background:var(--navy);color:#fff;font:inherit;font-size:15px;font-weight:600;cursor:pointer}
.follow button:hover{background:var(--navy-dark)}
.skip{position:absolute;left:-9999px}

footer{margin-top:auto;background:#fff;border-top:1px solid var(--line);font-size:14px;color:var(--muted)}
footer .wrap{padding-top:28px;padding-bottom:36px;display:flex;flex-direction:column;gap:12px}
.foot-links{display:flex;flex-wrap:wrap;gap:8px 20px}
footer a{color:var(--muted)}
.disclaimer{font-size:13px;line-height:1.5}

@media (max-width:760px){.beta .beta-t{display:none}}
@media (max-width:899px){
  .js .view-tabs{display:flex}
  .js [data-view="countries"] #sectors,.js [data-view="sectors"] #countries{display:none}
  .pill.soon{min-height:44px}
}
@media (min-width:900px){
  .wrap{padding:0 48px}
  header .wrap{height:80px}
  .logo{font-size:24px;gap:12px}
  .logo .u{width:38px;height:38px;border-radius:9px;font-size:22px}
  nav{gap:28px}
  .hero{padding:104px 0 64px}
  .hero .wrap{align-items:center;text-align:center;gap:28px}
  .eyebrow{font-size:13px}.eyebrow i{width:24px}.eyebrow i.r{display:block}
  h1{font-size:68px;line-height:1.05;letter-spacing:-.035em;max-width:980px}
  .lead{font-size:20px;max-width:760px}
  .duo{margin-top:28px}
  .cols{grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);gap:24px}
  .panel{padding:32px}
  .panel h2{font-size:28px}
  .flag{width:48px;height:32px}
  .follow{margin:24px 0 96px}
  .follow .box{flex-direction:row;align-items:center;justify-content:space-between;padding:28px 32px;gap:32px}
  .follow .ftxt{flex:1 1 320px}
  .follow .fform{flex:0 1 560px}
  .follow form{flex-direction:row}
  .follow input{flex:1}
  footer .wrap{flex-direction:row;align-items:center;justify-content:space-between;padding-top:28px;padding-bottom:28px}
  .foot-links{gap:24px}
  .disclaimer{font-size:14px}
}
'''

JS = '''
document.documentElement.classList.add('js');
(function(){
  // onglets mobiles « By sector » / « By country »
  var main=document.getElementById('rankings'), tabs=document.querySelectorAll('.view-tabs button');
  tabs.forEach(function(b){b.addEventListener('click',function(){
    main.setAttribute('data-view',b.dataset.view);
    tabs.forEach(function(t){t.setAttribute('aria-selected',t===b?'true':'false');});
  });});
  // lien #sectors / #countries (menu Rankings) : affiche l'onglet correspondant sur mobile
  function syncView(){var v=location.hash.slice(1);if(v!=='sectors'&&v!=='countries')return;
    main.setAttribute('data-view',v);tabs.forEach(function(t){t.setAttribute('aria-selected',t.dataset.view===v?'true':'false');});}
  syncView();window.addEventListener('hashchange',syncView);
  // info-bulle « Coming soon » au tap
  document.querySelectorAll('.pill.soon').forEach(function(p){p.addEventListener('click',function(){
    document.querySelectorAll('.pill.soon.show').forEach(function(o){if(o!==p)o.classList.remove('show');});
    p.classList.toggle('show');
  });});
  // recherche de segment : insensible aux accents et aux majuscules
  var q=document.getElementById('seg-q'), fams=[].slice.call(document.querySelectorAll('.fam')),
      none=document.getElementById('no-match'), wasOpen=null;
  function norm(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim();}
  q.addEventListener('input',function(){
    var v=norm(q.value), total=0;
    if(v&&wasOpen===null){wasOpen=fams.map(function(f){return f.open;});}
    fams.forEach(function(f,i){
      var fm=!v||f.dataset.n.indexOf(v)>=0, fc=0;
      f.querySelectorAll('.sect').forEach(function(s){
        var sm=fm||s.dataset.n.indexOf(v)>=0, sc=0;
        s.querySelectorAll('.pills > .pill').forEach(function(p){
          var ok=sm||p.dataset.n.indexOf(v)>=0; p.hidden=!ok; if(ok)sc++;
        });
        s.hidden=sc===0; fc+=sc;
      });
      f.hidden=fc===0; total+=fc;
      if(v){f.open=fc>0;}else if(wasOpen){f.open=wasOpen[i];}
    });
    if(!v){wasOpen=null;}
    none.hidden=total>0;
  });
  // formulaire d'abonnement : inscriptions pas encore ouvertes → « Coming soon » au clic
  var s=document.querySelector('form[data-soon]');
  if(s){s.addEventListener('submit',function(ev){ev.preventDefault();document.getElementById('soon-msg').hidden=false;});}
  // formulaire d'abonnement (mailto)
  var f=document.querySelector('form[data-mailto]'); if(!f)return;
  f.addEventListener('submit',function(ev){ev.preventDefault();
    var em=f.email.value,pr=f.profil.options[f.profil.selectedIndex].text;
    var body='Hello,\\n\\nI would like to receive every new edition of the Uback rankings.\\n\\nE-mail: '+em+'\\nProfile: '+pr+'\\n';
    window.location.href='mailto:'+f.dataset.mailto+'?subject='+encodeURIComponent('Follow Uback rankings')+'&body='+encodeURIComponent(body);
    setTimeout(function(){window.location.href=THANKS;},1500);});
})();
'''.replace('THANKS', json.dumps(THANKS_URL))

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Uback — The most valuable startups, ranked by AI</title>
<meta name="description" content="{e(DESC)}">
<link rel="canonical" href="https://uback.com/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Uback">
<meta property="og:url" content="https://uback.com/">
<meta property="og:title" content="Uback — The most valuable startups, ranked by AI">
<meta property="og:description" content="{e(DESC)}">
<script type="application/ld+json">{json.dumps(JSONLD, ensure_ascii=False, separators=(',', ':'))}</script>
<meta name="twitter:card" content="summary">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<!-- Généré par tools/build_home.py à partir de data/sectors.json : ne pas modifier à la main. -->
<style>{CSS}</style>
</head>
<body>

<div class="beta"><div class="wrap"><b>Beta · prototype</b><span class="beta-t">— This site is under construction: rankings, texts and features change every week.</span></div></div>
<header>
  <div class="wrap">
    <a class="logo" href="/" aria-label="Uback, home"><span class="u" aria-hidden="true">U</span>Uback</a>
    <nav aria-label="Main">
      {rankings_menu('en')}
      <a href="/invest.html">Invest</a>
      <a href="{METHOD_URL}">Method</a>
    </nav>
  </div>
</header>

<main>
  <section class="hero">
    <div class="wrap">
      <div class="eyebrow"><i></i><span>Startup rankings · Public beta</span><i class="r"></i></div>
      <h1>The most valuable startups, ranked by AI.</h1>
      <div class="duo">
        <div class="duo-col">
          <div class="duo-k">Discover</div>
          <p>Uback ranks funded, non-listed tech startups by AI-estimated valuation, by country and by global segment. <b>The market sets the value; our AI estimates it.</b> We publish the rank and an order of magnitude, never a figure.</p>
          <a href="#rankings">See the rankings <span aria-hidden="true">↓</span></a>
        </div>
        <div class="duo-rule" aria-hidden="true"></div>
        <div class="duo-col">
          <div class="duo-k">Back</div>
          <p>Alone, an investor rarely gets a seat at the table. <b>Together, Backers form a pool startups can’t ignore.</b> Declare an interest in a sector or a country, or an intent on a company open to Backers: once the pool reaches critical mass, the country’s licensed partner takes it to the company.</p>
          <a href="/invest.html">How it works <span aria-hidden="true">→</span></a>
        </div>
      </div>
    </div>
  </section>

  <section class="rankings">
    <div class="wrap" id="rankings" data-view="sectors">
      <div class="view-tabs" role="tablist" aria-label="Rankings">
        <button type="button" role="tab" data-view="sectors" aria-selected="true" aria-controls="sectors">By sector</button>
        <button type="button" role="tab" data-view="countries" aria-selected="false" aria-controls="countries">By country</button>
      </div>
      <div class="cols">

        <section class="panel" id="sectors" aria-labelledby="sectors-h">
          <div class="p-head">
            <div>
              <div class="kicker">Worldwide</div>
              <h2 id="sectors-h">Global sector rankings</h2>
              <p class="intro">The world’s leading startups in each segment, ranked against their direct competitors.</p>
            </div>
            <div class="freq gold"><b>Twice a year</b><span>January 1 · July 1</span></div>
          </div>
          <div class="search">
            <label for="seg-q">Find a segment</label>
            <input id="seg-q" type="search" placeholder="e.g. carpooling, cold wallets, payroll…" autocomplete="off">
          </div>
          <div class="legend">
            <span class="count">{N_FAM} families · {N_SEG} ranked segments</span>
            <span class="pill soon static" aria-hidden="true">Coming soon</span>
            <span class="pill pub static" aria-hidden="true">Published</span>
          </div>
          <p class="no-match" id="no-match" hidden>No segment matches. <a href="mailto:contact@uback.com?subject={quote('Suggest a segment')}">Suggest a segment</a></p>
          <div class="acc">
{chr(10).join('            ' + family(f) for f in FAMS)}
          </div>
        </section>

        <section class="panel" id="countries" aria-labelledby="countries-h">
          <div class="p-head">
            <div>
              <div class="kicker">Domestic markets</div>
              <h2 id="countries-h">Country rankings</h2>
              <p class="intro">All sectors, then by sector.</p>
            </div>
            <div class="freq navy"><b>Quarterly</b></div>
          </div>
{chr(10).join('          ' + region(r) for r in REGIONS)}
          <div class="regional">
            <h3>Regional rankings</h3>
            <p>Multi-country rankings, as new markets open.</p>
            <div class="pills">{''.join(soon_pill(x) for x in REGIONAL)}</div>
          </div>
        </section>

      </div>
    </div>
  </section>

  <section class="follow" id="follow">
    <div class="wrap">
      <div class="box">
        <div class="ftxt">
          <h2>Get every new edition</h2>
          <p>New entries, exits and movements, every quarter.</p>
          <p class="fine">One e-mail per edition. One-click unsubscribe. No data passed on to third parties.</p>
        </div>
        <div class="fform">
          <form name="follow-uback" method="POST" action="{THANKS_URL}" data-netlify="true" netlify-honeypot="bot-field"{' data-mailto="' + FORM_EMAIL + '"' if FORM_MODE == 'mailto' else ''}{' data-soon="1" novalidate' if FORM_MODE == 'soon' else ''}>
            <input type="hidden" name="form-name" value="follow-uback">
            <p class="skip"><label>Do not fill: <input name="bot-field"></label></p>
            <label class="sr" for="email">Your e-mail</label>
            <input id="email" name="email" type="email" required placeholder="you@email.com" autocomplete="email">
            <select name="profil" aria-label="Your profile">
              <option value="investor">Investor</option>
              <option value="corporate">Corporate</option>
              <option value="startup">Startup</option>
              <option value="advisor">Advisor</option>
            </select>
            <button type="submit">Follow</button>
          </form>
          <p class="soon-msg" id="soon-msg" role="status" hidden>Coming soon: subscriptions will open shortly.</p>
        </div>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    <div class="foot-links">
      <span>© 2026 Uback</span>
      <a href="{METHOD_URL}">Method</a>
      <a href="/invest.html">Invest</a>
      <a href="/correction.html">Request a correction</a>
      <a href="/legal-notice.html">Legal notice</a>
      <a href="mailto:contact@uback.com">contact@uback.com</a>
    </div>
    <span class="disclaimer">Rankings are editorial content, not investment advice.</span>
  </div>
</footer>

<script>{JS}</script>
</body>
</html>
'''

open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
print('ok index.html', N_FAM, 'families,', N_SEG, 'segments')

# ---------------------------------------------------------------- pages globales (communes à tous les pays)
# Méthode et mentions légales, en anglais et en français (texte : tools/pages_global.py), avec la charte de la homepage.
GLOBAL = {'method': {'en': 'method.html', 'fr': 'fr/methode.html'}, 'legal': {'en': 'legal-notice.html', 'fr': 'mentions-legales.html'},
          'invest': {'en': 'invest.html', 'fr': 'fr/investir.html'},
          'correction': {'en': 'correction.html', 'fr': 'fr/correction.html'}, 'thanks': {'en': 'thank-you.html', 'fr': 'fr/merci.html'}}
G_UI = {
 'en': dict(skip='Skip to content', sectors='Sectors', countries='Countries', method='Method',
            beta='Beta · prototype', beta_t='— This site is under construction: rankings, texts and features change every week.',
            legal='Legal notice', corr='Request a correction', disc='Rankings are editorial content, not investment advice.',
            cal_country='Country', cal_months='Published on the 15th', cal_next='Next edition',
            t_method='Method and rules of the game | Uback', d_method='How Uback ranks non-listed startups in descending order of AI-estimated valuation: consensus, confidence index, order of magnitude, eligibility, how human input is taken into account, corrections.',
            invest='Invest', t_invest='Invest with Uback | Uback', d_invest='Declare an investment intention on a sector, a country, or a company open to Backers. Backers’ intentions form a pool; once it reaches its critical mass, the pool is passed to the licensed partner, who presents the demand to the company.',
            opening_soon='In the meantime, write to <a href="mailto:contact@uback.com?subject=Intentions%20opening">contact@uback.com</a> to be notified when they open.',
            opening_form='In the meantime, you can <a href="/#follow">sign up to be notified when they open</a>.',
            t_correction='Request a correction | Uback', d_correction='Report inaccurate information or dispute a rank in a Uback ranking.',
            t_thanks='Thank you | Uback', d_thanks='Request prepared.',
            t_legal='Legal notice | Uback', d_legal='Legal notice of the Uback website.'),
 'fr': dict(skip='Aller au contenu', sectors='Secteurs', countries='Pays', method='Méthode',
            beta='Bêta · prototype', beta_t='— Ce site est en construction : classements, textes et fonctionnalités évoluent chaque semaine.',
            legal='Mentions légales', corr='Demander une correction', disc='Les classements sont des contenus éditoriaux, pas des conseils en investissement.',
            cal_country='Pays', cal_months='Publié le 15', cal_next='Prochaine édition',
            t_method='Méthode et règles du jeu | Uback', d_method='Comment Uback classe les startups non cotées par ordre décroissant de valorisation estimée par IA : consensus, indice de confiance, ordre de grandeur, éligibilité, prise en compte des avis humains, corrections.',
            invest='Investir', t_invest='Investir avec Uback | Uback', d_invest='Déclarez une intention d’investissement sur un secteur, un pays, ou une société ouverte aux Backers. Les intentions des Backers forment un pool ; quand il atteint sa masse critique, le pool est transmis au partenaire agréé, qui présente la demande à la société.',
            opening_soon='En attendant, écrivez-nous à <a href="mailto:contact@uback.com?subject=Ouverture%20des%20intentions">contact@uback.com</a> pour être prévenu de l’ouverture.',
            opening_form='En attendant, vous pouvez <a href="/#follow">vous inscrire pour être prévenu de l’ouverture</a>.',
            t_correction='Demander une correction | Uback', d_correction='Signalez une information inexacte ou contestez un rang dans un classement Uback.',
            t_thanks='Merci | Uback', d_thanks='Demande préparée.',
            t_legal='Mentions légales | Uback', d_legal='Mentions légales du site Uback.'),
}
G_CSS = '''
.prose-main{padding:24px 0 72px}
.prose{max-width:820px;font-size:16px;line-height:1.7;color:var(--body)}
.prose h1{margin:28px 0 12px;font-size:40px;line-height:1.1;font-weight:800;letter-spacing:-.03em;color:var(--navy)}
.prose h2{margin:36px 0 10px;font-size:24px;line-height:1.25;color:var(--navy)}
.prose .lead{font-size:18px}
.prose b{color:var(--navy)}
.prose ol,.prose ul{padding-left:22px}.prose li{margin-bottom:8px}
.prose table{width:100%;border-collapse:collapse;margin:12px 0;font-size:15px;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.prose th,.prose td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
.prose th{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.prose .table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
.prose .table-wrap table{min-width:520px}
.callout{margin:20px 0;padding:14px 18px;background:#fff;border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:10px}
.callout p{margin:0}
.callout.warn{border-left-color:var(--navy);background:var(--bg)}
.callout.warn h2{margin:0 0 6px;font-size:18px}
.prose .steps4{list-style:none;counter-reset:st;padding:0;display:grid;gap:12px;margin:12px 0}
.steps4 li{counter-increment:st;position:relative;margin:0;padding:16px 18px 16px 58px;border-radius:12px;background:var(--navy);color:#DCE3EC}
.steps4 li::before{content:counter(st);position:absolute;left:18px;top:10px;font-size:28px;font-weight:800;color:var(--gold)}
.steps4 li b{color:#fff}
@media (min-width:900px){.steps4{grid-template-columns:repeat(2,minmax(0,1fr))}}
.cform{display:grid;gap:16px;max-width:640px;margin-top:24px}
.cform label{display:block;font-size:14px;font-weight:600;color:var(--navy);margin-bottom:6px}
.cform .req{color:var(--gold)}
.cform input[type=text],.cform input[type=url],.cform input[type=email],.cform select,.cform textarea{width:100%;min-height:44px;padding:10px 12px;border:1px solid var(--dash);border-radius:10px;font:inherit;font-size:15px;color:var(--navy);background:#fff}
.cform textarea{min-height:120px;resize:vertical}
.cform .hint{font-size:12.5px;color:var(--muted);margin-top:4px}
.cform .consent{display:flex;gap:10px;align-items:flex-start;font-weight:500}
.cform .consent input{width:20px;height:20px;margin-top:2px;flex-shrink:0}
.cform button{justify-self:start;min-height:48px;padding:0 24px;border:0;border-radius:10px;background:var(--navy);color:#fff;font:inherit;font-size:16px;font-weight:600;cursor:pointer}
.cform button:hover{background:var(--navy-dark)}
.langsw{display:inline-flex;align-items:center;gap:4px;font-size:14px;font-weight:600;color:var(--muted)}
.langsw a{color:var(--muted);text-decoration:none;min-height:44px;display:inline-flex;align-items:center}
.langsw .on{color:var(--navy)}
@media (max-width:899px){.prose h1{font-size:32px}.prose table{font-size:14px}}
'''

def calendar(lang):
    """Tableau des éditions pays : mois de publication et prochaine date, lien vers la version dans la langue de la page."""
    rows, seen = '', []
    for m in MARKETS:
        if m['code'] in seen or not m['default']:
            continue
        seen.append(m['code'])
        v = next((x for x in MARKETS if x['code'] == m['code'] and x['lang'] == lang), m)
        name = v['name'] if v['lang'] == lang else {'fr': {'Poland': 'Pologne', 'Vietnam': 'Vietnam'}}.get(lang, {}).get(m['name'], m['name'])
        months = months_txt(m, lang).split(' ', 1)[1] if lang == 'en' else months_txt(m, lang)[3:].lstrip("’ ")
        rows += (f'<tr><td><a href="{v["path"]}/">{e(name)}</a></td><td>{e(months)}</td>'
                 f'<td>{e(format_date(next_edition(m), lang))}</td></tr>')
    u = G_UI[lang]
    return f'<table><tr><th>{u["cal_country"]}</th><th>{u["cal_months"]}</th><th>{u["cal_next"]}</th></tr>{rows}</table>'

def global_page(key, lang, body):
    u, path = G_UI[lang], GLOBAL[key][lang]
    other = 'fr' if lang == 'en' else 'en'
    alt = ''.join(f'\n<link rel="alternate" hreflang="{l}" href="https://uback.com/{GLOBAL[key][l]}">' for l in ('en', 'fr'))
    alt += f'\n<link rel="alternate" hreflang="x-default" href="https://uback.com/{GLOBAL[key]["en"]}">'
    sw = (f'<span class="langsw"><span class="on">{lang.upper()}</span><span>·</span>'
          f'<a href="/{GLOBAL[key][other]}" hreflang="{other}">{other.upper()}</a></span>')
    title, desc = u['t_' + key], u['d_' + key]
    method_url = '/' + GLOBAL['method'][lang]
    cur = lambda k: ' aria-current="page"' if k == key else ''
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">{'<meta name="robots" content="noindex">' if key == 'thanks' else ''}
<link rel="canonical" href="https://uback.com/{path}">{alt}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Uback">
<meta property="og:url" content="https://uback.com/{path}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<!-- Généré par tools/build_home.py (texte : tools/pages_global.py) : ne pas modifier à la main. -->
<style>{CSS}{G_CSS}</style>
</head>
<body>

<div class="beta"><div class="wrap"><b>{u['beta']}</b><span class="beta-t">{u['beta_t']}</span></div></div>
<header class="hdr-lang">
  <div class="wrap">
    <a class="logo" href="/" aria-label="Uback, home"><span class="u" aria-hidden="true">U</span>Uback</a>
    <nav aria-label="Main">
      {rankings_menu(lang)}
      <a href="/{GLOBAL['invest'][lang]}"{cur('invest')}>{u['invest']}</a>
      <a href="{method_url}"{cur('method')}>{u['method']}</a>
      {sw}
    </nav>
  </div>
</header>

<main class="prose-main">
{body.replace('@CAL@', calendar(lang))}
</main>

<footer>
  <div class="wrap">
    <div class="foot-links">
      <span>© 2026 Uback</span>
      <a href="{method_url}">{u['method']}</a>
      <a href="/{GLOBAL['invest'][lang]}">{u['invest']}</a>
      <a href="/{GLOBAL['correction'][lang]}">{u['corr']}</a>
      <a href="/{GLOBAL['legal'][lang]}">{u['legal']}</a>
      <a href="mailto:contact@uback.com">contact@uback.com</a>
    </div>
    <span class="disclaimer">{u['disc']}</span>
  </div>
</footer>

</body>
</html>
'''

# ---------------------------------------------------------------- formulaire de correction
# Envoi : 'mailto' (message structuré vers contact@uback.com, lisible par un agent IA) ou 'netlify' (formulaire natif
# nommé « correction »). Réglage distinct de FORM_MODE (newsletter, en « soon ») : les corrections restent ouvertes.
CORRECTION_MODE = 'mailto'
C_UI = {
 'fr': dict(h1='Demander une correction',
    intro='Signalez une information inexacte ou contestez un rang. Chaque demande reçoit une réponse motivée. Une société ne peut pas demander son retrait d’un classement (<a href="/fr/methode.html#correction">voir la méthode</a>).',
    company='Société', country='Pays du classement', global_seg='Classement mondial par segment', type='Type de demande',
    t_inacc='Information inexacte', t_disp='Contestation du rang', info='Information concernée',
    infos=['Montant levé', 'Date', 'Secteur ou segment', 'Statut (active, rachetée, fermée)', 'Siège / pays', 'Autre'],
    current='Valeur actuellement affichée', proposed='Valeur proposée', source='Source (lien)',
    source_hint='Obligatoire pour une information inexacte.', comment='Commentaire', comment_hint='1 000 caractères maximum.',
    name='Nom', role='Fonction et lien avec la société', email='E-mail', box='Case',
    consent='J’accepte que ces informations soient utilisées pour traiter ma demande.', yes='oui', choose='Choisir…',
    send='Envoyer la demande', sep=' : ',
    thanks_h='Merci, votre demande est prête.',
    thanks_p='Si votre messagerie s’est ouverte, envoyez simplement le message préparé : votre demande nous parviendra et recevra une réponse motivée. Sinon, écrivez-nous à <a href="mailto:contact@uback.com">contact@uback.com</a>.',
    back='Retour à la méthode'),
 'en': dict(h1='Request a correction',
    intro='Report inaccurate information or dispute a rank. Every request receives a reasoned reply. A company cannot ask to be removed from a ranking (<a href="/method.html#correction">see the method</a>).',
    company='Company', country='Ranking country', global_seg='Global ranking by segment', type='Request type',
    t_inacc='Inaccurate information', t_disp='Rank dispute', info='Information concerned',
    infos=['Amount raised', 'Date', 'Sector or segment', 'Status (active, acquired, closed)', 'Seat / country', 'Other'],
    current='Value currently shown', proposed='Proposed value', source='Source (link)',
    source_hint='Required for inaccurate information.', comment='Comment', comment_hint='1,000 characters maximum.',
    name='Name', role='Role and relationship to the company', email='E-mail', box='Checkbox',
    consent='I agree that this information may be used to process my request.', yes='yes', choose='Choose…',
    send='Send request', sep=': ',
    thanks_h='Thank you, your request is ready.',
    thanks_p='If your e-mail app opened, simply send the prepared message: your request will reach us and receive a reasoned reply. Otherwise, write to us at <a href="mailto:contact@uback.com">contact@uback.com</a>.',
    back='Back to the method'),
}

def country_options(lang):
    """Pays du classement : générés depuis la configuration des marchés (une entrée par pays)."""
    opts, seen = [], []
    for m in MARKETS:
        if m['code'] in seen:
            continue
        seen.append(m['code'])
        v = next((x for x in MARKETS if x['code'] == m['code'] and x['lang'] == lang), None)
        name = v['name'] if v else {'fr': {'Poland': 'Pologne'}}.get(lang, {}).get(m['name'], m['name'])
        opts.append((m['code'], name))
    return opts

def correction_body(lang):
    c = C_UI[lang]
    req = ' <span class="req" aria-hidden="true">*</span>'
    opt = lambda items: f'<option value="">{c["choose"]}</option>' + ''.join(f'<option value="{e(v)}">{e(t)}</option>' for v, t in items)
    countries = opt(country_options(lang) + [('global', c['global_seg'])])
    thanks = '/' + GLOBAL['thanks'][lang]
    mailto = ' data-mailto="contact@uback.com"' if CORRECTION_MODE == 'mailto' else ''
    labels = json.dumps([c[k] for k in ('company', 'country', 'type', 'info', 'current', 'proposed', 'source', 'comment',
                                        'name', 'role', 'email', 'box')], ensure_ascii=False)
    return f'''<div class="wrap prose">
<h1>{c['h1']}</h1>
<p class="lead">{c['intro']}</p>
<form class="cform" name="correction" method="POST" action="{thanks}" data-netlify="true" netlify-honeypot="bot-field"{mailto}>
  <input type="hidden" name="form-name" value="correction">
  <p class="skip"><label>Ne pas remplir : <input name="bot-field"></label></p>
  <div><label for="c-company">{c['company']}{req}</label><input id="c-company" name="company" type="text" required autocomplete="organization"></div>
  <div><label for="c-country">{c['country']}{req}</label><select id="c-country" name="country" required>{countries}</select></div>
  <div><label for="c-type">{c['type']}{req}</label><select id="c-type" name="type" required>{opt([('inaccurate', c['t_inacc']), ('dispute', c['t_disp'])])}</select></div>
  <div><label for="c-info">{c['info']}{req}</label><select id="c-info" name="info" required>{opt([(x, x) for x in c['infos']])}</select></div>
  <div><label for="c-current">{c['current']}</label><input id="c-current" name="current" type="text"></div>
  <div><label for="c-proposed">{c['proposed']}{req}</label><input id="c-proposed" name="proposed" type="text" required></div>
  <div><label for="c-source">{c['source']}<span class="req" id="c-source-req" aria-hidden="true"> *</span></label><input id="c-source" name="source" type="url" placeholder="https://" aria-describedby="c-source-hint"><div class="hint" id="c-source-hint">{c['source_hint']}</div></div>
  <div><label for="c-comment">{c['comment']}</label><textarea id="c-comment" name="comment" maxlength="1000" aria-describedby="c-comment-hint"></textarea><div class="hint" id="c-comment-hint">{c['comment_hint']}</div></div>
  <div><label for="c-name">{c['name']}{req}</label><input id="c-name" name="name" type="text" required autocomplete="name"></div>
  <div><label for="c-role">{c['role']}{req}</label><input id="c-role" name="role" type="text" required></div>
  <div><label for="c-email">{c['email']}{req}</label><input id="c-email" name="email" type="email" required autocomplete="email"></div>
  <div><label class="consent"><input type="checkbox" name="consent" value="{c['yes']}" required> {c['consent']}</label></div>
  <button type="submit">{c['send']}</button>
</form>
<script>
(function(){{
  var f=document.querySelector('form.cform'), t=f.type, s=f.source, star=document.getElementById('c-source-req');
  function syncSource(){{ var need=t.value==='inaccurate'; s.required=need; star.hidden=!need; }}
  t.addEventListener('change',syncSource); syncSource();
  // préremplissage depuis les pages classements : ?company=…&country=…
  var q=new URLSearchParams(location.search);
  if(q.get('company'))f.company.value=q.get('company');
  if(q.get('country'))f.country.value=q.get('country');
  if(!f.dataset.mailto)return;
  f.addEventListener('submit',function(ev){{ev.preventDefault();
    var L={labels}, sep={json.dumps(c['sep'])};
    function txt(el){{return el.tagName==='SELECT'?(el.value?el.options[el.selectedIndex].text:''):el.value.trim();}}
    var vals=[txt(f.company),txt(f.country),txt(f.type),txt(f.info),txt(f.current),txt(f.proposed),txt(f.source),
              txt(f.comment),txt(f.name),txt(f.role),txt(f.email),f.consent.checked?{json.dumps(c['yes'])}:''];
    var body=L.map(function(l,i){{return l+sep+vals[i];}}).join('\\n');
    var subject='[Correction] '+vals[0]+' – '+vals[1]+' – '+vals[2];
    window.location.href='mailto:'+f.dataset.mailto+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
    setTimeout(function(){{window.location.href={json.dumps(thanks)};}},1500);}});
}})();
</script>
</div>
'''

def thanks_body(lang):
    c = C_UI[lang]
    return f'''<div class="wrap prose">
<h1>{c['thanks_h']}</h1>
<p class="lead">{c['thanks_p']}</p>
<p><a href="/{GLOBAL['method'][lang]}">{c['back']}</a></p>
</div>
'''

# « Où en est-on ? » : inscriptions désactivées (FORM_MODE 'soon') → simple lien e-mail, jamais de formulaire inactif
OPENING = {l: G_UI[l]['opening_soon' if FORM_MODE == 'soon' else 'opening_form'] for l in ('en', 'fr')}
# Page Invest : ligne « Vous êtes sur le point de rejoindre le pool … », d'après les paramètres du lien (pool, segment, country,
# company). Tables en dur, générées ici : slug → nom de segment (data/sectors.json), code → pool du pays (MARKETS).
POOL_SEGMENTS = {g['slug']: g['name'] for f in SECTORS['families'] for s in f['sectors'] for g in s['segments']}
POOL_COUNTRIES = {
    'en': {m['code']: m['startups_label'] for m in MARKETS if m['lang'] == 'en'},
    'fr': {m['code']: ('des ' + m['startups_label'][4:] if m['startups_label'].startswith('les ') else m['startups_label'])
           if m['lang'] == 'fr' else NAMES[m['code']]['fr'] for m in MARKETS if m['default'] or m['lang'] == 'fr'},
}
POOL_TXT = {'en': {'lead': 'You are about to join ', 'seg': 'the {} pool.', 'cty': 'the {} pool.', 'co': 'the pool for {}.',
                   'pref': 'You can also name a preferred company in it.'},
            'fr': {'lead': 'Vous êtes sur le point de rejoindre ', 'seg': 'le pool {}.', 'cty': 'le pool {}.', 'co': 'le pool de la société {}.',
                   'pref': 'Vous pourrez aussi indiquer une société préférée.'}}

def pool_ctx(lang):
    """Ligne de contexte (masquée par défaut) + script : texte seulement (textContent), jamais d'HTML injecté ;
    paramètres absents ou inconnus → rien ne s'affiche."""
    data = json.dumps({'seg': POOL_SEGMENTS, 'cty': POOL_COUNTRIES[lang], 'txt': POOL_TXT[lang]}, ensure_ascii=False)
    return ('<p class="callout" id="pool-ctx" hidden></p>\n<script>(function(){var D=' + data + ';'
            'var q=new URLSearchParams(location.search),p=q.get("pool"),t=null,T=D.txt;'
            'if(p==="segment"&&D.seg[q.get("segment")])t=T.seg.split("{}").join(D.seg[q.get("segment")]);'
            'else if(p==="country"&&D.cty[q.get("country")])t=T.cty.split("{}").join(D.cty[q.get("country")]);'
            'else if(p==="company"&&q.get("company"))t=T.co.split("{}").join(q.get("company").slice(0,80));'
            'if(!t)return;var el=document.getElementById("pool-ctx");el.textContent=T.lead+t;'
            'if(p!=="company"){var b=document.createElement("br"),s=document.createElement("span");s.textContent=T.pref;el.appendChild(b);el.appendChild(s);}'
            'el.hidden=false;'
            'if(location.hash)el.scrollIntoView();})();</script>')

BODIES = {'method': METHOD, 'legal': LEGAL, 'invest': {l: INVEST[l].replace('@OPENING@', OPENING[l]).replace('@POOLCTX@', pool_ctx(l)) for l in ('en', 'fr')},
          'correction': {l: correction_body(l) for l in ('en', 'fr')}, 'thanks': {l: thanks_body(l) for l in ('en', 'fr')}}
for key, texts in BODIES.items():
    for lang in ('en', 'fr'):
        out = os.path.join(ROOT, *GLOBAL[key][lang].split('/'))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8', newline='\n').write(global_page(key, lang, texts[lang]))
        print('ok', GLOBAL[key][lang])
