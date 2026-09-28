# -*- coding: utf-8 -*-
"""Génère les classements mondiaux par segment (/segments/<id>/), un par fichier data/segments/<id>.json.
Même charte et mêmes composants que les pages pays (feuille de style unique ma/assets/style.css) ; trois différences :
bloc « Rankings by region » (filtres) à la place des secteurs, pays et zone de chaque société, disclaimer du segment.
Un nouveau segment = un nouveau JSON, sans nouveau code. La homepage publie automatiquement le segment
(tools/build_home.py lit data/segments/).
Usage : python3 tools/build_segments.py             (tous les segments)
        python3 tools/build_segments.py consumer-neobanks
Jamais rendus : estimate_usd et note_internal (le script vérifie qu'ils n'apparaissent pas dans la page)."""
import os, sys, json, html, re, glob, shutil, hashlib, datetime, subprocess, tempfile
from urllib.parse import quote

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
from build_site import CSS_V, format_date
from valuation import BRACKETS, bracket_index, money, month
from flags import flag

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
    return '<br>'.join(e(x) for x in lines)

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
            f'<span class="vl">{VB[c["tranche"]]}</span></button>'
            f'<span class="val-tip"><span id="{tid}">{tip_facts(c)}</span>'
            f'<a class="tip-more" href="{GM}#estimation">Method</a></span></span>')

def conf(c):
    n = CONF[c['confidence']]
    dots = ''.join('<i class="f"></i>' if i < n else '<i></i>' for i in range(3))
    return f'<span class="conf" aria-hidden="true">{dots}</span><span class="conf-l">{CONF_LAB[n]}</span>'

def where(x):
    return f'{flag(x.get("country_code"))}{e(x["country"])} · {e(REGION_NAME[x["region"]])}'

def row(c, defs=()):
    top = ' top' if c['rank'] == 1 else ''
    urls = list(c['sources'])
    urls += [u for u in dict.fromkeys(v.get('source') for v in (c.get('kpis') or {}).values()) if u and u not in urls]   # sources des KPIs
    srcs = ' · '.join(f'<a href="{e(u)}" rel="nofollow noopener" target="_blank">{i}</a>' for i, u in enumerate(urls, 1))
    report = f'<a class="report" href="{GC}?company={quote(c["name"])}&amp;country=global">Is this your company? Report an error</a>'
    return f'''<tr class="r{top}" data-region="{c['region']}">
<td class="rank">{c['rank']}</td>
<td><span class="co">{e(c['name'])}<small>{where(c)}</small></span><span class="src">Sources: {srcs}</span>{report}</td>
<td data-l="Last round · Key metrics">{e(last_round(c))}{kpi_line(c, defs)}</td>
<td data-l="Valuation (AI)">{val(c)}</td>
<td data-l="Confidence">{conf(c)}</td>
<td class="act"><a class="btn" href="{GI}#opening">Declare an intent</a></td>
</tr>'''

def radar_li(r):
    rd = r['last_equity_round']
    txt = ' · '.join(p for p in (month(rd['date'], 'en'), amount(rd)) if p)
    if rd.get('detail'):
        txt += f"; {rd['detail']}"
    return f'<li data-region="{r["region"]}"><span><b>{e(r["name"])}</b> · {where(r)}</span><span>{e(txt)}</span></li>'

def switcher(d):
    """Sélecteur de la famille (ex. « Fintech ») : les segments publiés de la famille, groupés par secteur,
    pour passer d'un segment à l'autre sans repasser par la homepage. Publié = un fichier data/segments/<slug>.json."""
    fam = next(f for f in SECTORS['families'] if f['name'] == d['path'][0])
    items = ''
    for sec in fam['sectors']:
        segs = [g for g in sec['segments'] if os.path.exists(os.path.join(ROOT, 'data', 'segments', g['slug'] + '.json'))]
        if not segs:
            continue
        items += f'<span class="grp">{e(sec["name"])}</span>'
        for g in segs:
            cur = ' aria-current="page"' if g['slug'] == d['segment_id'] else ''
            items += f'<a class="seg" href="/segments/{g["slug"]}/"{cur}>{e(g["name"])}</a>'
    return (f'<details class="mkt"><summary class="market" aria-label="Change segment">{e(fam["name"])}</summary>'
            f'<div class="menu">{items}<hr><a href="/#sectors">All sectors</a><a href="/#countries">Country rankings</a></div></details>')

def og_html(d, n):
    t = d['texts']
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
<div class="kicker">{e(' › '.join(d['path'][:-1]))} · {n} companies ranked</div>
<h1>{t['og_title']}</h1>
<div class="foot">{e(d['edition_label'])} · {e(format_date(datetime.date.fromisoformat(d['published']), 'en'))}<br>The market sets the value; our AI estimates it.</div>
</body>
</html>
'''

def og_image(d, n, out_dir):
    """Image de partage (titre + nombre de sociétés classées) ; version = empreinte du contenu, rendue seulement si elle change."""
    src = og_html(d, n)
    v = hashlib.sha1(src.encode('utf-8')).hexdigest()[:8]
    png = os.path.join(out_dir, 'og-image.png')
    cache = json.load(open(OG_CACHE, encoding='utf-8')) if os.path.exists(OG_CACHE) else {}
    if cache.get(d['segment_id']) != v or not os.path.exists(png):
        if not os.path.exists(EDGE):
            print('  ! image de partage non rendue (Edge introuvable)')
            return v
        with tempfile.TemporaryDirectory() as tmp:
            f = os.path.join(tmp, 'og.html')
            open(f, 'w', encoding='utf-8').write(src)
            subprocess.run([EDGE, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                            '--window-size=1200,630', '--virtual-time-budget=5000', f'--screenshot={png}',
                            'file:///' + f.replace('\\', '/')], capture_output=True)
        if not os.path.exists(png):
            print('  ! image de partage non rendue (Edge n’a rien produit) : relancer le script')
            return v
        cache[d['segment_id']] = v
        open(OG_CACHE, 'w', encoding='utf-8', newline='\n').write(json.dumps(cache, indent=2, sort_keys=True) + '\n')
        print('  image de partage rendue')
    return v

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
    og_v = og_image(d, N, out)
    url = f'https://uback.com/segments/{sid}/'
    published = format_date(datetime.date.fromisoformat(d['published']), 'en')
    nxt = format_date(datetime.date.fromisoformat(d['next_edition']), 'en')
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

    defs = d.get('kpi_definitions') or []
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

    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t['title'])}</title>
<meta name="description" content="{e(t['description'])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Uback">
<meta property="og:title" content="{e(t['title'])}">
<meta property="og:description" content="{e(t['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{url}og-image.png?v={og_v}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/segments/assets/style.css?v={CSS_V}">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<!-- Généré par tools/build_segments.py à partir de data/segments/{sid}.json : ne pas modifier à la main. -->
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="beta"><div class="wrap"><b>Beta · prototype</b><span class="beta-t">— This site is under construction: rankings, texts and features change every week.</span><a href="mailto:contact@uback.com">Contact us</a></div></div>
<header class="hdr">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Uback, home"><span class="u">U</span>Uback</a>
    {switcher(d)}
    <button class="menu-toggle" aria-label="Menu" aria-expanded="false" onclick="var n=document.getElementById('nav');var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1E3A5F" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <nav class="main" id="nav" aria-label="Main navigation">
      <a href="#ranking">Ranking</a>
      <a href="#regions">Regions</a>
      <a href="{GM}">Method</a>
      <a href="#backers">Backers</a>
      <a href="{GI}">Invest</a>
    </nav>
    <span class="spacer"></span>
    <span class="langs"><span class="on">EN</span></span>
    <a class="btn" href="#follow">Follow this ranking</a>
    <a class="btn gold" href="{GI}#opening">Declare an intention</a>
  </div>
</header>
<main id="main">

<div class="wrap">
  <div class="hero">
    <div>
      <div class="kicker">Global segment ranking · {e(' › '.join(d['path'][:-1]))}</div>
      <h1>{e(t['h1'])}</h1>
      <p class="lead">{e(t['intro'])}</p>
      <div class="meta">
        <span class="tag beta">{e(d['edition_label'])} · Published {published}</span>
        <span class="tag cad">{e(d['cadence'])}</span><span>Next edition: {nxt}</span><span>·</span>
        <span>Claude · multi-AI consensus in a future edition</span><span>·</span>
        <a href="{GM}">Published method</a><span>·</span>
        <span>Order never changed by a human</span>
      </div>
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
    <div class="sec-head"><h2>Rankings by region</h2><span class="sub">Filter the ranking and the Radar. Ranks stay worldwide.</span></div>
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
      <thead><tr><th>#</th><th>Company</th><th>Last round · Key metrics</th><th>Estimated valuation (AI, order of magnitude)</th><th>Confidence</th><th class="th-inv">Invest</th></tr></thead>
      <tbody>
      {''.join(row(c, defs) for c in ranked)}
      </tbody>
    </table>
    <p class="list-empty" id="no-rank" hidden>No ranked company in this region yet: see the <a href="#radar">Radar</a>.</p>
    <div class="disclaimer">Ranking in descending order of AI-estimated valuation, based on public information, following a published method, with no human intervention on the order. Valuation ranges are indicative editorial estimates: neither a financial valuation, nor an offer, nor investment advice. Only the market sets a company’s value, through a funding round or a sale. {ed0}Eligibility: at least $1M raised including one equity round, non-listed company, main activity in this segment ({e(t['activity'])}). Country shown is the country of main operations. <a href="{GC}">Request a correction</a></div>

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
      <div class="card"><h3>Range</h3><p>An order of magnitude, never a figure.</p>
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
      <div class="card dark"><span class="num">1</span><h3>Declare an intention</h3><p>On a company or a sector, with a ticket range. Paid, to show you are serious; transferable as long as it has not been converted.</p></div>
      <div class="card dark"><span class="num">2</span><h3>Critical mass is reached</h3><p>When the number of Backers and the total of their intentions cross a threshold, the licensed partner contacts the company and presents this demand.</p></div>
      <div class="card dark"><span class="num">3</span><h3>The licensed partner structures</h3><p>If the company’s expectations and the Backers’ converge, the partner builds a transaction and presents it directly to the Backers concerned.</p></div>
      <div class="card dark"><span class="num">4</span><h3>Closing</h3><p>Capital raise or sale of existing shares: small tickets are pooled in a common vehicle set up by the licensed partner. Each Backer decides whether to take part.</p></div>
    </div>
    <p class="steps-note">Uback does not advise, does not negotiate, collects nothing. Each transaction is run by the licensed partner of the company’s country, under the law that governs its shares.</p>
    <div class="cta-row">
      <a class="btn gold" href="#follow">Get notified when intentions open</a>
      <a class="btn ghost" href="{GI}#steps">What happens after my declaration?</a>
      <span>Intention declarations open once the licensed partner signs · price per ticket band · valid 12 months · transferable credit</span>
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
      {''.join(radar_li(r) for r in radar)}
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

</main>
<footer>
  <div class="wrap">
    <div class="row">
      <span class="brand"><span class="u">U</span>Uback</span>
      <span>Powered by AI</span>
      <span>·</span><a href="{GM}">Method and rules</a>
      <span>·</span><a href="{GI}">Invest</a>
      <span>·</span><a href="{GC}">Request a correction</a>
      <span>·</span><a href="{GL}">Legal notice</a>
      <span class="spacer"></span>
      <span>Uback.com · {datetime.date.today().year}</span>
    </div>
    <p>Uback is a content publisher. It provides no investment advice, receives no mandate and takes part in no transaction. Introductions are made by licensed partners, currently being selected. Investing in non-listed companies carries a risk of losing all the capital invested.</p>
  </div>
</footer>
<script>{js}</script>
</body>
</html>
'''
    # garde-fou : les champs internes ne doivent jamais apparaître dans la page
    for c in ranked:
        if c.get('note_internal') and c['note_internal'] in page:
            raise DataError(f"{c['name']} : note_internal présente dans la page")
    if 'estimate_usd' in page or 'note_internal' in page:
        raise DataError('champ interne présent dans la page')
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
    by_region = ', '.join(f"{title} {sum(c['region'] == code for c in ranked)}" for code, title in REGIONS)
    print(f'ok /segments/{sid}/ · {N} ranked ({by_region}) · {M_} on radar')

def main():
    # feuille de style : même source que les pages pays
    os.makedirs(os.path.join(ROOT, 'segments', 'assets'), exist_ok=True)
    shutil.copyfile(os.path.join(ROOT, 'ma', 'assets', 'style.css'), os.path.join(ROOT, 'segments', 'assets', 'style.css'))
    wanted = set(sys.argv[1:])
    for p in sorted(glob.glob(os.path.join(ROOT, 'data', 'segments', '*.json'))):
        if not wanted or os.path.splitext(os.path.basename(p))[0] in wanted:
            build(p)

if __name__ == '__main__':
    main()
