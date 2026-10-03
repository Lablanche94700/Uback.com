# -*- coding: utf-8 -*-
"""Génère les classements mondiaux par segment (/segments/<id>/), un par fichier data/segments/<id>.json.
Même charte et mêmes composants que les pages pays (feuille de style unique ma/assets/style.css) ; trois différences :
bloc « Rankings by region » (filtres) à la place des secteurs, pays et zone de chaque société, disclaimer du segment.
Un nouveau segment = un nouveau JSON, sans nouveau code. La homepage publie automatiquement le segment
(tools/build_home.py lit data/segments/).
Usage : python3 tools/build_segments.py             (tous les segments)
        python3 tools/build_segments.py consumer-neobanks
estimate_usd est l'estimation centrale (affichée arrondie, avec sa fourchette selon la confiance : tools/valuation.py) ;
note_internal n'est jamais rendu (le script vérifie qu'il n'apparaît pas dans la page)."""
import os, sys, json, html, re, glob, shutil, hashlib, datetime, subprocess, tempfile, time
from urllib.parse import quote

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
from build_site import CSS_V, format_date, format_date_short
import geo
from valuation import BRACKETS, BANDS, bracket_index, money, money2, range_txt, month
from flags import flag
from footer import footer
from analytics import HEAD as GA_HEAD
from fonts import PRELOAD
import header
import companies

e = html.escape
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'   # rendu de l'image de partage (facultatif)
OG_CACHE = os.path.join(TOOLS, 'og-segments.json')                        # empreinte de la dernière image rendue
FORM_MODE = 'soon'                  # même réglage que les pages pays : inscriptions pas encore ouvertes

# Zones, dans l'ordre d'affichage des cartes (codes utilisés dans les JSON)
REGIONS = [('north-america', 'North America'), ('latin-america', 'Latin America'), ('europe', 'Europe'),
           ('mena', 'Middle East & North Africa'), ('sub-saharan-africa', 'Sub-Saharan Africa'), ('asia-pacific', 'Asia-Pacific')]
REGION_NAME = dict(REGIONS)
SECTORS = json.load(open(os.path.join(ROOT, 'data', 'sectors.json'), encoding='utf-8'))   # familles > secteurs > segments
CONF = {'high': 3, 'medium': 2, 'low': 1}
CONF_TXT = {'high': 'High', 'medium': 'Medium', 'low': 'Low'}
CONF_LAB = {3: 'Solid sources', 2: 'Partial sources', 1: 'Weak sources'}
VB = {'hundreds_k': 'Hundreds of k$', 'millions': 'Millions $', 'tens_m': 'Tens of M$', 'hundreds_m': 'Hundreds of M$',
      'unicorn': 'Unicorn', 'decacorn': 'Decacorn'}
GM, GI, GC, GL = '/method.html', '/invest.html', '/correction.html', '/legal-notice.html'
# société ouverte aux Backers (champ facultatif open_to_backers) : badge, phrase d'explication
OPEN = {'secondary': ('Shareholder selling', 'A shareholder has told Uback they are considering a sale.'),
        'raise': ('Raising soon', 'The company has told Uback it plans to raise funds soon.')}


class DataError(Exception):
    pass

def check(d):
    """Contrôles de cohérence : le générateur échoue plutôt que de publier un classement incohérent."""
    ranked = d['ranked']
    for c in ranked:
        if c['region'] not in REGION_NAME:
            raise DataError(f"{c['name']} : zone inconnue « {c['region']} »")
        if c['confidence'] not in CONF:
            raise DataError(f"{c['name']} : indice de confiance inconnu « {c['confidence']} »")
        if c['tranche'] != BRACKETS[bracket_index(c['estimate_usd'])]:
            raise DataError(f"{c['name']} : tranche « {c['tranche']} » incohérente avec l'estimation interne")
    # rang = ordre décroissant de l'estimation (égalité : ordre du fichier)
    order = sorted(ranked, key=lambda c: (-c['estimate_usd'], c['rank']))
    for i, c in enumerate(order, 1):
        if c['rank'] != i:
            raise DataError(f"{c['name']} : rang {c['rank']} publié, {i} attendu d'après l'estimation")
    for a, b in zip(order, order[1:]):
        if BRACKETS.index(b['tranche']) > BRACKETS.index(a['tranche']):
            raise DataError(f"{b['name']} (rang {b['rank']}) a une tranche plus haute que {a['name']} (rang {a['rank']})")
    for c in ranked:
        o = c.get('open_to_backers')
        if o is not None and (o.get('type') not in OPEN or not re.fullmatch(r'(19|20)\d\d-(0[1-9]|1[0-2])', str(o.get('since', '')))):
            raise DataError(f"{c['name']} : open_to_backers invalide (type secondary|raise, since AAAA-MM) : {o}")
    for r in d['radar']:
        if r['region'] not in REGION_NAME:
            raise DataError(f"Radar, {r['name']} : zone inconnue « {r['region']} »")
    d['ranked'] = order

def round_date(r):
    """Tri du Radar : date de dernière levée ; mois inconnu = 1er janvier de l'année."""
    dt = r['last_equity_round']['date']
    y, m = (dt.split('-') + ['1'])[:2]
    return int(y), int(m)

def amount(rd):
    if rd.get('amount_label'):
        return rd['amount_label']
    return money(rd['amount_usd'], 'en') if rd.get('amount_usd') else ''

def tip_facts(c):
    """Faits publics uniquement : dernier tour en fonds propres, valorisation publiée, indice de confiance."""
    rd, lines = c['last_equity_round'], []
    txt = ' · '.join(p for p in (rd.get('type'), amount(rd), month(rd['date'], 'en')) if p)
    if rd.get('investors'):
        txt += f" ({rd['investors']})"
    if rd.get('detail'):
        txt += f"; {rd['detail']}"
    lines.append('Last known equity round: ' + txt)
    pv = c.get('published_valuation')
    if pv:
        lines.append(f"Published valuation: {pv.get('label') or money(pv['value_usd'], 'en')} ({month(pv['date'], 'en')})")
    else:
        lines.append('No confirmed published valuation')
    lines.append('Confidence index: ' + CONF_TXT[c['confidence']])
    return '<br>'.join(companies.link_investors(e(x), parens_only=False) if x.startswith('Last known') else e(x) for x in lines)

def last_round(c):
    """Colonne « Last round » : type, montant et date du dernier tour, rien d'autre (les valorisations publiées
    ne s'affichent que dans l'infobulle de la tranche)."""
    rd = c['last_equity_round']
    return ' · '.join(p for p in (rd.get('type'), amount(rd), month(rd['date'], 'en')) if p)

ND = 'not disclosed'

def kpi_line(c, defs):
    """Indicateurs clés du segment (ordre de kpi_definitions), tels que publiés et datés, jamais recalculés.
    Période affichée une seule fois si elle est commune, sinon à côté de chaque valeur ; non publiée : « Label: n/d »."""
    if not defs:
        return ''
    shown, periods = [], []
    for d in defs:
        v = (c.get('kpis') or {}).get(d['id']) or {}
        if not v.get('value_text') or v['value_text'] == ND:
            shown.append((f"{d['label']}: n/d", None, True))
        else:
            txt = (d['label'] + ' ' if d.get('prefix') else '') + v['value_text']
            shown.append((txt, v.get('period'), False))
            periods.append(v.get('period'))
    if not periods:
        return '<span class="kpi"><span class="nd">Key metrics not disclosed</span></span>'
    common = periods[0] if len(set(periods)) == 1 and periods[0] else None
    parts = [f'<span class="nd">{e(t)}</span>' if nd else e(t if common or not per else f'{t} ({per})') for t, per, nd in shown]
    if common:
        parts.append(e(common))
    return '<span class="kpi">' + ' · '.join(parts) + '</span>'

def val(c):
    tid = f"vb-{c['rank']}"
    toggle = "var p=this.parentNode;this.setAttribute('aria-expanded',p.classList.toggle('open'))"   # tap sur mobile
    return (f'<span class="val"><button type="button" class="val-b" aria-describedby="{tid}" aria-expanded="false" onclick="{toggle}">'
            f'<span class="vl">≈ {money2(c["estimate_usd"], "en")}</span>'
            f'<span class="vr">{range_txt(c["estimate_usd"] * BANDS[c["confidence"]][0], c["estimate_usd"] * BANDS[c["confidence"]][1], "en")} · {VB[c["tranche"]]}</span></button>'
            f'<span class="val-tip"><span id="{tid}">{tip_facts(c)}</span>'
            f'<a class="tip-more" href="{GM}#estimation">Method</a></span></span>')

def conf(c):
    n = CONF[c['confidence']]
    dots = ''.join('<i class="f"></i>' if i < n else '<i></i>' for i in range(3))
    return f'<span class="conf" aria-hidden="true">{dots}</span><span class="conf-l">{CONF_LAB[n]}</span>'

def where(x):
    return f'{flag(x.get("country_code"))}{e(x["country"])} · {e(REGION_NAME[x["region"]])}'

def open_cell(c, sid):
    """Cellule « Open to Backers » : vide par défaut (l'intérêt porte sur le pool du segment)."""
    o = c.get('open_to_backers')
    if not o:
        return ''
    badge, note = OPEN[o['type']]
    href = f"{GI}?pool=company&amp;company={quote(c['name'])}&amp;segment={sid}#opening"
    return (f'<span class="inv-badge gold">{badge}</span><span class="inv-note">{note}</span>'
            f'<a class="btn" href="{href}">Declare an intent</a>')

def row(c, defs=(), sid='', show_inv=False):
    top = ' top' if c['rank'] == 1 else ''
    urls = list(c['sources'])
    urls += [u for u in dict.fromkeys(v.get('source') for v in (c.get('kpis') or {}).values()) if u and u not in urls]   # sources des KPIs
    srcs = ' · '.join(f'<a href="{e(u)}" rel="nofollow noopener" target="_blank">{i}</a>' for i, u in enumerate(urls, 1))
    return f'''<tr class="r{top}" data-region="{c['region']}">
<td class="rank">{c['rank']}</td>
<td><span class="co">{companies.link_company(c['name'], sid)}<small>{where(c)}</small></span><span class="src">Sources: {srcs}</span></td>
<td data-l="Last round · Key metrics">{e(last_round(c))}{kpi_line(c, defs)}</td>
<td data-l="Valuation (AI)">{val(c)}</td>
<td data-l="Confidence">{conf(c)}</td>
{f'<td class="act">{open_cell(c, sid)}</td>' if show_inv else ''}
</tr>'''

def radar_li(r, sid=''):
    rd = r['last_equity_round']
    txt = ' · '.join(p for p in (month(rd['date'], 'en'), amount(rd)) if p)
    if rd.get('detail'):
        txt += f"; {rd['detail']}"
    return (f'<li data-region="{r["region"]}"><span><b>{companies.link_company(r["name"], sid)}</b> · {where(r)}</span>'
            f'<span>{companies.link_investors(e(txt), parens_only=False)}</span></li>')

def family_slug(name):
    """« Fintech » → « fintech » (adresse de la page famille : /sectors/<slug>/)."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

def published(g):
    return os.path.exists(os.path.join(ROOT, 'data', 'segments', g['slug'] + '.json'))

def switcher(family, current=None):
    """Sélecteur de la famille (ex. « Fintech ») : la page de la famille, puis ses segments publiés groupés par secteur,
    pour passer d'un segment à l'autre sans repasser par la homepage. Publié = un fichier data/segments/<slug>.json."""
    fam = next(f for f in SECTORS['families'] if f['name'] == family)
    cur = ' aria-current="page"' if current is None else ''
    items = f'<a href="/sectors/{family_slug(fam["name"])}/"{cur}>All {e(fam["name"])} rankings</a>'
    for sec in fam['sectors']:
        segs = [g for g in sec['segments'] if published(g)]
        if not segs:
            continue
        items += f'<span class="grp">{e(sec["name"])}</span>'
        for g in segs:
            cur = ' aria-current="page"' if g['slug'] == current else ''
            items += f'<a class="seg" href="/segments/{g["slug"]}/"{cur}>{e(g["name"])}</a>'
    return (f'<details class="mkt"><summary class="market" aria-label="Change segment">{e(fam["name"])}</summary>'
            f'<div class="menu">{items}<hr><a href="/#sectors">All sectors</a><a href="/#countries">Country rankings</a></div></details>')

def og_html(kicker, title_html, foot_html):
    """Image de partage 1200 × 630, même charte pour les segments et les familles."""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&display=block" rel="stylesheet">
<style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{background:#1E3A5F;font-family:Inter,sans-serif;color:#fff;position:relative}}
.top{{position:absolute;left:64px;right:64px;top:64px;height:52px;display:flex;align-items:center;justify-content:space-between}}
.logo{{display:flex;align-items:center;gap:14px;font-size:34px;font-weight:800;letter-spacing:-.02em}}
.logo .u{{width:52px;height:52px;border-radius:12px;background:#fff;color:#C8A052;display:flex;align-items:center;justify-content:center;font-size:30px;letter-spacing:0}}
.market{{font-size:20px;font-weight:700;letter-spacing:.2em;color:#C8A052}}
.kicker{{position:absolute;left:64px;top:218px;font-size:20px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#C8A052}}
h1{{position:absolute;left:64px;top:262px;margin:0;font-size:62px;line-height:1.1;font-weight:800;letter-spacing:-.025em;width:1080px}}
.foot{{position:absolute;left:64px;right:64px;top:500px;line-height:1.45;font-size:21px;font-weight:600;color:#C7D0DC}}
</style>
</head>
<body>
<div class="top"><div class="logo"><span class="u">U</span>Uback</div><div class="market">WORLDWIDE</div></div>
<div class="kicker">{kicker}</div>
<h1>{title_html}</h1>
<div class="foot">{foot_html}</div>
</body>
</html>
'''

def og_image(key, src, out_dir):
    """Rend l'image de partage (src = og_html(...)) ; version = empreinte du contenu, rendue seulement si elle change."""
    v = hashlib.sha1(src.encode('utf-8')).hexdigest()[:8]
    png = os.path.join(out_dir, 'og-image.png')
    cache = json.load(open(OG_CACHE, encoding='utf-8')) if os.path.exists(OG_CACHE) else {}
    if cache.get(key) != v or not os.path.exists(png):
        if not os.path.exists(EDGE):
            print('  ! image de partage non rendue (Edge introuvable)')
            return v
        for _ in range(4):                 # Edge headless échoue parfois : profil temporaire neuf, nouvel essai
            with tempfile.TemporaryDirectory() as tmp:
                f = os.path.join(tmp, 'og.html')
                open(f, 'w', encoding='utf-8').write(src)
                subprocess.run([EDGE, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                                f'--user-data-dir={os.path.join(tmp, "profile")}', '--no-first-run',
                                '--window-size=1200,630', '--virtual-time-budget=5000', f'--screenshot={png}',
                                'file:///' + f.replace('\\', '/')], capture_output=True, timeout=90)
                # le lanceur d'Edge rend la main avant la fin du rendu : attendre l'image avant d'effacer la page source
                for _ in range(60):
                    if os.path.exists(png) and os.path.getsize(png) > 0:
                        break
                    time.sleep(0.5)
                time.sleep(1)
            if os.path.exists(png):
                break
        if not os.path.exists(png):
            print('  ! image de partage non rendue (Edge n’a rien produit) : relancer le script')
            return v
        cache[key] = v
        open(OG_CACHE, 'w', encoding='utf-8', newline='\n').write(json.dumps(cache, indent=2, sort_keys=True) + '\n')
        print('  image de partage rendue')
    return v

def dates_line(edition, published, nxt, ooc=None):
    """Ligne datée sous le H1, commune aux classements : édition · Published · Next scheduled update ;
    mise à jour hors calendrier (out_of_cycle {date, reason}, facultative) en dessous : l'édition prévue reste due."""
    line = (f'<div class="meta" style="margin-bottom:16px"><span>{e(edition)}</span><span>·</span>'
            f'<span>Published {format_date_short(published, "en")}</span><span>·</span>'
            f'<span>Next scheduled update {format_date_short(nxt, "en")}</span></div>')
    if ooc:
        line += ('\n      <div class="meta" style="margin:-8px 0 16px"><span>Out-of-cycle update</span><span>·</span>'
                 f'<span>{format_date_short(ooc["date"], "en")}</span><span>·</span><span>{e(ooc["reason"])}</span></div>')
    return line

def next_scheduled(slug):
    """Prochaine date du calendrier (data/calendar.json) : la seule date de prochaine édition affichée."""
    d = geo.next_date(slug)
    if d is None:
        raise DataError(f'{slug} : absent de data/calendar.json (relancer tools/build_calendar.py)')
    return d

def page_top(title, desc, url, og_img, sw, nav, follow_label, follow_href, extra, declare_href=f'{GI}#opening', search_field=False):
    """Début de page commun aux classements mondiaux (segments et familles), aux zones et aux fiches : <head>,
    bandeau bêta, en-tête unique (tools/header.py), puis le sous-menu du classement : sélecteur (sw), ancres de la
    page (nav) et boutons Follow / Declare. Sans sélecteur ni ancres (fiches) : pas de sous-menu.
    search_field : conservé pour compatibilité (le champ de recherche est désormais dans l'en-tête unique)."""
    sub = ''
    if sw or nav:
        acts = (f'<a class="btn" href="{follow_href}">{follow_label}</a>' if follow_label else '') +                f'<a class="btn gold" href="{declare_href}">Declare an interest</a>'
        sub = header.subnav(sw, nav, acts)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Uback">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon-192.png">
{PRELOAD}
<link rel="stylesheet" href="/segments/assets/style.css?v={CSS_V}">
{extra}
{GA_HEAD}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="beta"><div class="wrap"><b>Beta · prototype</b><span class="beta-t">— This site is under construction: rankings, texts and features change every week.</span></div></div>
{header.header('en')}
{sub}
<main id="main">
'''

def page_bottom(script=''):
    return '</main>\n' + footer('en') + f'\n{script}</body>\n</html>\n'

JS = '''
(function(){
  var NAMES=@NAMES@, TOTAL=@TOTAL@;
  var btns=[].slice.call(document.querySelectorAll('.card.reg')), rows=[].slice.call(document.querySelectorAll('.tbl tr.r')),
      items=[].slice.call(document.querySelectorAll('#radar-list li')), head=document.getElementById('filter-h'),
      noRank=document.getElementById('no-rank'), noRadar=document.getElementById('no-radar');
  function apply(r,write){
    if(!NAMES[r])r='world';
    btns.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.region===r?'true':'false');});
    var n=0,m=0;
    rows.forEach(function(tr){var ok=r==='world'||tr.dataset.region===r;tr.hidden=!ok;if(ok)n++;});
    items.forEach(function(li){var ok=r==='world'||li.dataset.region===r;li.hidden=!ok;if(ok)m++;});
    noRank.hidden=n>0;noRadar.hidden=m>0;
    head.textContent=r==='world'?'World · '+TOTAL+' ranked companies':NAMES[r]+' · '+n+' of '+TOTAL+' ranked companies';
    if(write&&history.replaceState){history.replaceState(null,'',r==='world'?location.pathname+location.search:'#region='+r);}
  }
  function fromHash(){var m=location.hash.match(/^#region=([a-z-]+)$/);return m?m[1]:null;}
  btns.forEach(function(b){b.addEventListener('click',function(){apply(b.dataset.region,true);});});
  document.querySelectorAll('.mkt a.seg').forEach(function(a){a.addEventListener('click',function(){
    if(/^#region=/.test(location.hash)){a.href=a.href.split('#')[0]+location.hash;}});});
  window.addEventListener('hashchange',function(){var r=fromHash();if(r)apply(r,false);});
  var start=fromHash();
  apply(start||'world',false);
  if(start&&NAMES[start]){document.getElementById('regions').scrollIntoView();}
  var s=document.querySelector('form[data-soon]');
  if(s){s.addEventListener('submit',function(ev){ev.preventDefault();s.parentNode.querySelector('.soon-msg').hidden=false;});}
})();
'''

def build(path):
    d = json.load(open(path, encoding='utf-8'))
    check(d)
    sid, t = d['segment_id'], d['texts']
    ranked = d['ranked']
    radar = sorted(d['radar'], key=round_date, reverse=True)      # tri stable : à date égale, ordre du fichier
    N, M_ = len(ranked), len(radar)
    out = os.path.join(ROOT, 'segments', sid)
    os.makedirs(out, exist_ok=True)
    og_v = og_image(sid, og_html(f"{e(' › '.join(d['path'][:-1]))} · {N} companies ranked", t['og_title'],
                                 f"{e(d['edition_label'])} · {e(format_date(datetime.date.fromisoformat(d['published']), 'en'))}"
                                 '<br>The market sets the value; our AI estimates it.'), out)
    url = f'https://uback.com/segments/{sid}/'
    published = datetime.date.fromisoformat(d['published'])
    nxt_d = next_scheduled(sid)                     # calendrier, pas le champ next_edition du JSON
    nxt = format_date(nxt_d, 'en')
    name_l = d['name'][:1].lower() + d['name'][1:]

    # cartes « Rankings by region » : comptes calculés depuis le JSON
    def card(code, title, rk, rd, txt):
        return (f'<button type="button" class="card reg" data-region="{code}" aria-pressed="{"true" if code == "world" else "false"}">'
                f'<span class="k">{len(rk)} ranked · {len(rd)} on radar</span><h3>{e(title)}</h3><p>{txt}</p></button>')
    cards = [card('world', 'World', ranked, radar, f'#1 worldwide: {e(ranked[0]["name"])}')]
    for code, title in REGIONS:
        rk = [c for c in ranked if c['region'] == code]
        rd = [r for r in radar if r['region'] == code]
        txt = f'#1 in region: {e(rk[0]["name"])} (#{rk[0]["rank"]} worldwide)' if rk else 'No ranked company yet'
        cards.append(card(code, title, rk, rd, txt))

    # pages de zone (/regions/<slug>/) des sociétés classées, quand la zone existe dans data/geo.json
    zs = [(code, geo.ZONES[code]['name']['en']) for code, _ in REGIONS if code in geo.ZONES and any(c['region'] == code for c in ranked)]
    zone_links = (' Regional pages: ' + ' · '.join(f'<a href="/regions/{code}/">{e(n)}</a>' for code, n in zs) + '.') if zs else ''
    defs = d.get('kpi_definitions') or []
    show_inv = any(c.get('open_to_backers') for c in ranked)          # colonne masquée si aucune société ouverte
    pool = f'{GI}?pool=segment&amp;segment={sid}#opening'              # intérêt pour le pool du segment
    kpi_note = (f'<p class="kpi-note">Key metrics for this segment: {e(", ".join(k["label"].lower() for k in defs))}. '
                'Figures as published by each company or the press, dated, not recalculated. '
                'The AIs weigh them alongside funding history and comparables.</p>') if defs else ''
    countries = len({c['country'] for c in ranked})
    jsonld = {"@context": "https://schema.org", "@type": "ItemList",
              "name": f"{t['h1']} – {d['edition_label']}", "description": t['intro'],
              "itemListOrder": "https://schema.org/ItemListOrderDescending",
              "itemListElement": [{"@type": "ListItem", "position": c['rank'], "name": c['name']} for c in ranked]}
    js = JS.replace('@NAMES@', json.dumps(dict(REGIONS, world='World'), ensure_ascii=False)).replace('@TOTAL@', str(N))
    ed0 = (f"Edition 0: produced by {e(d['established_by'])}; a consensus of several AI models will apply in a future edition. "
           if d['edition'] == 0 else '')

    page = page_top(t['title'], t['description'], url, f'{url}og-image.png?v={og_v}', switcher(d['path'][0], sid),
                    [('#ranking', 'Ranking'), ('#regions', 'Regions'), ('#radar', 'Radar'), ('#backers', 'Backers'), ('#segment-method', 'Method')],
                    'Follow this ranking', '#follow',
                    f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n'
                    f'<!-- Généré par tools/build_segments.py à partir de data/segments/{sid}.json : ne pas modifier à la main. -->',
                    pool) + f'''
<div class="wrap">
  <div class="hero">
    <div>
      <div class="kicker">Global segment ranking · {e(' › '.join(d['path'][:-1]))}</div>
      <h1>{e(t['h1'])}</h1>
      {dates_line(d['edition_label'], published, nxt_d, d.get('out_of_cycle'))}
      <p class="lead">{e(t['intro'])}</p>
      <div class="meta">
        <span class="tag cad">{e(d['cadence'])}</span>
        <span>Claude · multi-AI consensus in a future edition</span><span>·</span>
        <a href="{GM}">Method</a><span>·</span>
        <span>Order never changed by a human</span>
      </div>
      <p class="hero-cta"><a class="btn gold" href="{pool}">Declare an interest in {e(d['name'])}</a></p>
      {kpi_note}
      <p class="notin"><b>Not in this segment.</b> {e(t['not_in_segment'])} <a href="{GM}#eligibility">Method</a></p>
    </div>
    <div class="panel">
      <div class="k">The segment at a glance</div>
      <div class="stats">
        <div><b>{N}</b><span>companies ranked</span></div>
        <div><b>{M_}</b><span>companies on the radar</span></div>
        <div><b>{countries}</b><span>countries in the ranking</span></div>
        <div><b>{len(d['listed_benchmarks'])}</b><span>listed benchmarks</span></div>
      </div>
      <div class="fine">Sources: {e(t['sources'])} Intention counters will be shown above a threshold of amount and number of Backers.</div>
    </div>
  </div>
</div>

<section id="regions" style="padding-top:8px">
  <div class="wrap">
    <div class="sec-head"><h2>Rankings by region</h2><span class="sub">Filter the ranking and the Radar. Ranks stay worldwide.{zone_links}</span></div>
    <div class="regions">
      {(chr(10) + '      ').join(cards)}
    </div>
  </div>
</section>

<section id="ranking" style="padding-top:12px">
  <div class="wrap">
    <div class="sec-head">
      <h2>Global ranking · {e(d['name'])}</h2>
      <div class="tabs"><a class="on" href="#ranking">Top {N}</a><a href="#radar">Radar</a><a href="#challengers">Challengers</a></div>
      <span class="spacer"></span>
      <span class="sub">First edition: no movements yet.</span>
    </div>
    <p class="filter-h" id="filter-h" aria-live="polite">World · {N} ranked companies</p>
    <table class="tbl">
      <thead><tr><th>#</th><th>Company</th><th>Last round · Key metrics</th><th>Estimated valuation (AI) · range</th><th>Confidence</th>{'<th class="th-inv">Open to Backers</th>' if show_inv else ''}</tr></thead>
      <tbody>
      {''.join(row(c, defs, sid, show_inv) for c in ranked)}
      </tbody>
    </table>
    <p class="list-empty" id="no-rank" hidden>No ranked company in this region yet: see the <a href="#radar">Radar</a>.</p>
    <div class="disclaimer">Ranking in descending order of AI-estimated valuation, based on public information, with no human intervention on the order. The valuations, ranges and brackets shown are editorial estimates produced by AI, purely indicative and imperfect by nature: neither a financial valuation, nor an offer, nor investment advice. Only the market sets a company’s value, through a funding round or a sale. {ed0}Eligibility: at least $1M raised including one equity round, non-listed company, main activity in this segment ({e(t['activity'])}). Country shown is the country of main operations. <a href="{GC}">Request a correction</a></div>

    <div class="follow-band" id="follow">
      <div class="fb-text">
        <h3>Get every new edition</h3>
        <p>New entries, exits and movements, twice a year.</p>
      </div>
      <div class="fb-form">
        <form class="follow" name="follow-{sid}" method="POST" action="/thank-you.html" data-netlify="true" netlify-honeypot="bot-field"{' data-soon="1" novalidate' if FORM_MODE == 'soon' else ''}>
          <input type="hidden" name="form-name" value="follow-{sid}">
          <p class="skip"><label>Do not fill: <input name="bot-field"></label></p>
          <label class="skip" for="email">Your e-mail</label>
          <input id="email" name="email" type="email" required placeholder="you@email.com" autocomplete="email">
          <select name="profil" aria-label="Your profile">
            <option value="investisseur">Investor</option>
            <option value="dirigeant">Startup manager</option>
            <option value="banque">Investment bank / adviser</option>
            <option value="autre">Other</option>
          </select>
          <button class="btn navy" type="submit">Follow</button>
        </form>
        <p class="src">One e-mail per edition. One-click unsubscribe. No data passed on to third parties.</p>
        <p class="soon-msg" role="status" hidden>Coming soon: subscriptions will open shortly.</p>
      </div>
    </div>
  </div>
</section>

<section class="soft" id="read">
  <div class="wrap">
    <div class="sec-head"><h2>How to read this ranking</h2></div>
    <div class="grid3">
      <div class="card"><h3>Rank</h3><p>Companies are ranked by AI-estimated valuation, highest first. The market sets the value; our AI estimates it.</p></div>
      <div class="card"><h3>Estimate</h3><p>An AI-estimated valuation, its uncertainty range and its order of magnitude. Indicative, and imperfect by nature.</p>
        <ol class="scale">{''.join(f'<li>{VB[b]}</li>' for b in BRACKETS)}</ol></div>
      <div class="card"><h3>Confidence</h3><ul class="read-list"><li><b>High:</b> recent published valuation or round (under 24 months).</li><li><b>Medium:</b> older data.</li><li><b>Low:</b> single or unconfirmed source.</li></ul></div>
    </div>
    <p class="read-more"><a href="{GM}#estimation">Full method →</a></p>
  </div>
</section>

<section class="navy" id="backers">
  <div class="wrap">
    <div class="sec-head"><h2>Invest in {e(name_l)}, together</h2></div>
    <p class="lead">Uback aggregates investment intentions from business angels, family offices, corporates and sector specialists worldwide. Every ranked company already has professional investors on its cap table, who have negotiated a shareholders’ agreement: you don’t start from a blank page.</p>
    <div class="steps-head">
      <h3>Strength in numbers</h3>
      <p>Alone, a small ticket opens no doors. Together, Backers carry weight.</p>
    </div>
    <div class="grid4">
      <div class="card dark"><span class="num">1</span><h3>Declare an interest</h3><p>In this segment, with a ticket range, and if you wish a preferred company in it. Paid, to show you are serious; valid for life, and movable to another pool until its pool is passed to the partner.</p></div>
      <div class="card dark"><span class="num">2</span><h3>Critical mass is reached</h3><p>When the pool’s combined amount reaches its critical mass, a floor amount estimated by the AI, the pool is passed to the local partner, who presents this demand to the company.</p></div>
      <div class="card dark"><span class="num">3</span><h3>The local partner structures</h3><p>If the company’s expectations and the Backers’ converge, the partner builds a transaction and presents it directly to the Backers concerned.</p></div>
      <div class="card dark"><span class="num">4</span><h3>Closing</h3><p>Capital raise or sale of existing shares: small tickets are pooled in a common vehicle set up by the local partner. Each Backer decides whether to take part.</p></div>
    </div>
    <p class="steps-note">Uback does not advise, does not negotiate, collects nothing. Each transaction is run by the local partner of the company’s country, under the law that governs its shares.</p>
    <div class="cta-row">
      <a class="btn gold" href="#follow">Get notified when intentions open</a>
      <a class="btn ghost" href="{GI}#steps">What happens after my declaration?</a>
      <span>Intention declarations open once the local partner signs · price per ticket band · valid for life · movable until the pool is passed on</span>
    </div>
  </div>
</section>

<section class="soft" id="radar">
  <div class="wrap">
    <div class="box line">
      <h3 id="challengers">Challengers</h3>
      <p>A registered company raising funds that is not in the ranking will be able, for a fee, to appear in a separate list labelled “Challengers”, for a set period, with a memo available to verified Backers. The listing has no effect on the ranking. Not open yet.</p>
      <div class="slot">Sponsored space · no Challenger listed yet</div>
      <h3 style="margin-top:22px">Radar · known eligible companies, not ranked</h3>
      <p>Sorted by date of last round, with no judgement and no AI call.</p>
      <ul class="list" id="radar-list">
      {''.join(radar_li(r, sid) for r in radar)}
      </ul>
      <p class="list-empty" id="no-radar" hidden>No company on the radar in this region yet.</p>
      <h3 style="margin-top:22px">Listed benchmarks</h3>
      <p>Not ranked: no intention is possible on a listed company.</p>
      <ul class="list">
      {''.join(f'<li><span><b>{e(r["name"])}</b> · {e(r["country"])}</span><span>{e(r["listing"])}</span></li>' for r in d['listed_benchmarks'])}
      </ul>
    </div>
    <div class="box local" id="segment-method">
      <h3>Sources and method for this segment</h3>
      <p><b>Calendar.</b> Global segment rankings are published {e(d['cadence'].lower())}. Next edition: {nxt}.</p>
      <p><b>Eligibility.</b> At least $1M raised including one equity round, non-listed company, main activity in this segment ({e(t['activity'])}). A company appears in one segment only.</p>
      <p><b>Sources.</b> {e(t['sources'])}</p>
      <p><a href="{GM}">Method and rules, common to all rankings →</a></p>
    </div>
  </div>
</section>

''' + page_bottom(f'<script>{js}</script>\n')
    # garde-fou : les champs internes ne doivent jamais apparaître dans la page
    for c in ranked:
        if c.get('note_internal') and c['note_internal'] in page:
            raise DataError(f"{c['name']} : note_internal présente dans la page")
    if 'note_internal' in page:
        raise DataError('champ interne présent dans la page')
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
    by_region = ', '.join(f"{title} {sum(c['region'] == code for c in ranked)}" for code, title in REGIONS)
    print(f'ok /segments/{sid}/ · {N} ranked ({by_region}) · {M_} on radar')
    return d

def build_family(fam, datas):
    """Page d'une famille (/sectors/<slug>/) : tous ses segments, publiés ou à venir, et les licornes et décacornes
    de ses classements. Aucun classement entre segments : chaque société n'est classée que dans le sien."""
    slug = family_slug(fam['name'])
    out = os.path.join(ROOT, 'sectors', slug)
    os.makedirs(out, exist_ok=True)
    url = f'https://uback.com/sectors/{slug}/'
    name, name_l = fam['name'], fam['name'].lower()
    pub = [datas[g['slug']] for sec in fam['sectors'] for g in sec['segments'] if g['slug'] in datas]
    total = sum(len(sec['segments']) for sec in fam['sectors'])
    ranked = [(c, d) for d in pub for c in d['ranked']]
    nxt_d = min(next_scheduled(d['segment_id']) for d in pub)        # prochaine mise à jour d'un de ses segments
    last = max(datetime.date.fromisoformat(d['published']) for d in pub)
    labels = {d['edition_label'] for d in pub}
    edition = labels.pop() if len(labels) == 1 else 'Edition 0 (beta)'
    names = [d['name'] for d in pub]
    title = f'{name} startup rankings, segment by segment | Uback'
    desc = (f'Uback ranks the world’s non-listed {name_l} startups by AI-estimated valuation, segment by segment: '
            f'{", ".join(names[:4])} and more.')

    # segments, groupés par secteur : publiés (lien, n° 1, tranche) ou à venir
    blocks = ''
    for sec in fam['sectors']:
        cards = ''
        for g in sec['segments']:
            d = datas.get(g['slug'])
            if d:
                top = d['ranked'][0]
                cards += (f'<a class="card fam-seg" href="/segments/{g["slug"]}/"><span class="k">{len(d["ranked"])} ranked</span>'
                          f'<h3>{e(g["name"])}</h3><p>#1: {e(top["name"])} · {VB[top["tranche"]]}</p></a>')
            else:
                cards += f'<div class="card fam-seg soon"><span class="k">Coming soon</span><h3>{e(g["name"])}</h3></div>'
        n_pub = sum(g['slug'] in datas for g in sec['segments'])
        blocks += (f'<div class="fam-sec"><h3 class="fam-h">{e(sec["name"])} <span>{n_pub} of {len(sec["segments"])} published</span></h3>'
                   f'<div class="grid4">{cards}</div></div>')

    # licornes et décacornes des classements publiés : par tranche, ordre alphabétique (pas de classement entre segments)
    def corn_list(tranche):
        items = sorted(((c, d) for c, d in ranked if c['tranche'] == tranche), key=lambda x: x[0]['name'].lower())
        return len(items), ''.join(
            f'<a class="pill corn" href="/segments/{d["segment_id"]}/">{e(c["name"])}<span> · {e(d["name"])}</span></a>' for c, d in items)
    n_deca, deca = corn_list('decacorn')
    n_uni, uni = corn_list('unicorn')
    countries = len({c['country'] for c, d in ranked})

    og_v = og_image(f'family-{slug}', og_html(f'{e(name)} · {len(pub)} segment{"s" if len(pub) > 1 else ""} published',
                                              f'The world’s most valuable<br>{e(name_l)} startups',
                                              f'{len(ranked)} companies ranked · {e(edition)}<br>The market sets the value; our AI estimates it.'), out)
    jsonld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc, "url": url,
              "mainEntity": {"@type": "ItemList", "itemListElement": [
                  {"@type": "ListItem", "position": i, "name": d['texts']['h1'], "url": f"https://uback.com/segments/{d['segment_id']}/"}
                  for i, d in enumerate(pub, 1)]}}
    page = page_top(title, desc, url, f'{url}og-image.png?v={og_v}', switcher(name),
                    [('#segments', 'Segments'), ('#unicorns', 'Unicorns'), (GM, 'Method')],
                    'Follow the rankings', '/#follow',
                    f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n'
                    f'<!-- Généré par tools/build_segments.py à partir de data/sectors.json et data/segments/ : ne pas modifier à la main. -->',
                    f'{GI}?pool=segment#opening') + f'''
<div class="wrap">
  <div class="hero">
    <div>
      <div class="kicker">Global sector rankings · {e(name)}</div>
      <h1>The world’s most valuable {e(name_l)} startups, segment by segment</h1>
      {dates_line(edition, last, nxt_d)}
      <p class="lead">Each segment ranks non-listed startups worldwide against their direct competitors, by AI-estimated valuation. The market sets the value; our AI estimates it.</p>
      <div class="meta">
        <span class="tag beta">{len(pub)} of {total} segments published</span>
        <span class="tag cad">Twice a year</span>
        <a href="{GM}">Method</a><span>·</span>
        <span>Order never changed by a human</span>
      </div>
      <p class="notin"><b>One company, one segment.</b> Each company is ranked in the segment of its main activity only, against its direct competitors. There is no ranking across segments. <a href="{GM}#eligibility">Method</a></p>
    </div>
    <div class="panel">
      <div class="k">{e(name)} at a glance</div>
      <div class="stats">
        <div><b>{len(pub)}</b><span>segment{'s' if len(pub) > 1 else ''} published</span></div>
        <div><b>{len(ranked)}</b><span>companies ranked</span></div>
        <div><b>{countries}</b><span>countries in the rankings</span></div>
        <div><b>{n_deca + n_uni}</b><span>unicorns and decacorns</span></div>
      </div>
      <div class="fine">Counts cover published segments only. Each company appears in one segment. Intention counters will be shown above a threshold of amount and number of Backers.</div>
    </div>
  </div>
</div>

<section id="segments" style="padding-top:8px">
  <div class="wrap">
    <div class="sec-head"><h2>{e(name)} segments</h2><span class="sub">{len(pub)} of {total} published · the others open edition by edition.</span></div>
    {blocks}
  </div>
</section>

<section class="soft" id="unicorns">
  <div class="wrap">
    <div class="sec-head"><h2>Decacorns and unicorns in the {e(name_l)} rankings</h2><span class="sub">Grouped by valuation range, in alphabetical order. Each company is ranked only within its own segment.</span></div>
    <div class="box line">
      <h3>Decacorns · estimated at $10B or more <span class="cnt">{n_deca}</span></h3>
      <div class="pills-wrap">{deca}</div>
      <h3 style="margin-top:22px">Unicorns · estimated between $1B and $10B <span class="cnt">{n_uni}</span></h3>
      <div class="pills-wrap">{uni}</div>
    </div>
    <p class="read-more"><a href="{GM}#estimation">How valuations are estimated →</a></p>
  </div>
</section>
''' + page_bottom()
    for c, d in ranked:
        if c.get('note_internal') and c['note_internal'] in page:
            raise DataError(f"{c['name']} : note_internal présente dans la page famille")
    if 'estimate_usd' in page or 'note_internal' in page:
        raise DataError('champ interne présent dans la page famille')
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
    print(f'ok /sectors/{slug}/ · {len(pub)}/{total} segments · {len(ranked)} ranked · {n_deca} decacorns · {n_uni} unicorns')

def main():
    # feuille de style : même source que les pages pays
    os.makedirs(os.path.join(ROOT, 'segments', 'assets'), exist_ok=True)
    shutil.copyfile(os.path.join(ROOT, 'ma', 'assets', 'style.css'), os.path.join(ROOT, 'segments', 'assets', 'style.css'))
    wanted = set(sys.argv[1:])
    datas = {}
    for p in sorted(glob.glob(os.path.join(ROOT, 'data', 'segments', '*.json'))):
        slug = os.path.splitext(os.path.basename(p))[0]
        if not wanted or slug in wanted:
            datas[slug] = build(p)
        else:                                   # page non régénérée : ses données servent quand même à la page famille
            datas[slug] = json.load(open(p, encoding='utf-8'))
            check(datas[slug])
    # pages famille (/sectors/<slug>/) : toute famille qui a au moins un segment publié
    for fam in SECTORS['families']:
        if any(g['slug'] in datas for sec in fam['sectors'] for g in sec['segments']):
            build_family(fam, datas)

if __name__ == '__main__':
    main()
