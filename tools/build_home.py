# -*- coding: utf-8 -*-
"""Génère la homepage monde (/index.html, en anglais) à partir de data/sectors.json et des listes ci-dessous.
Usage : python3 tools/build_home.py
- À gauche : classements mondiaux par secteur (famille > secteur > segment ; seul le segment est classé).
- À droite : classements par pays (marchés domestiques) et régionaux.
Tout le contenu est écrit en HTML statique (SEO) ; le JavaScript ne sert qu'à la recherche, aux onglets mobiles
et à l'envoi du formulaire. Les sites marchés (/ma, /pl, /vn) sont générés par tools/build_site.py."""
import html, json, os, unicodedata
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTORS = json.load(open(os.path.join(ROOT, 'data', 'sectors.json'), encoding='utf-8'))
FORM_MODE = 'mailto'                # 'mailto' (GitHub Pages) ou 'netlify' (Netlify Forms)
FORM_EMAIL = 'contact@uback.com'
METHOD_URL = '/pl/method.html'      # page méthode anglaise (à remplacer par une page globale quand elle existera)
THANKS_URL = '/pl/thank-you.html'
e = html.escape

FLAGS = {
 'ma': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#C1272D"/><polygon points="24,8.5 26.6,16.4 34.4,11.6 20,20.9 29.6,20.9 18.2,11.6 26,16.4" fill="none" stroke="#006233" stroke-width="1.6" stroke-linejoin="round" transform="translate(-2.2 1.2)"/></svg>',
 'pl': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="16" fill="#FFFFFF"/><rect y="16" width="48" height="16" fill="#DC143C"/><rect x=".5" y=".5" width="47" height="31" fill="none" stroke="#E4E8EE"/></svg>',
 'vn': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#DA251D"/><polygon points="24,7 26.47,14.6 34.46,14.6 28,19.3 30.47,26.9 24,22.2 17.53,26.9 20,19.3 13.54,14.6 21.53,14.6" fill="#FFFF00"/></svg>',
}

# Classements par pays, groupés par région. live : (code, nom, sous-ligne, url) ; soon : noms à venir.
REGIONS = [
 {'name': 'North Africa & Middle East', 'live': [('ma', 'Morocco', 'In French · by sector soon', '/ma/')],
  'soon': ['Tunisia', 'Egypt', 'UAE', 'Saudi Arabia']},
 {'name': 'Europe', 'live': [('pl', 'Poland', 'In English · by sector soon', '/pl/')],
  'soon': ['France', 'Romania', 'Ukraine']},
 {'name': 'Asia', 'live': [('vn', 'Vietnam', 'In English · by sector soon', '/vn/')],
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

def segment(g):
    if g.get('status') == 'published' and g.get('url'):
        return f'<a class="pill pub" href="{e(g["url"])}" data-n="{e(norm(g["name"]))}">{e(g["name"])}</a>'
    return soon_pill(g['name'], f' data-n="{e(norm(g["name"]))}"')

def family(f):
    n_sec = len(f['sectors'])
    n_seg = sum(len(s['segments']) for s in f['sectors'])
    body = ''.join(
        f'<div class="sect" data-n="{e(norm(s["name"]))}"><div class="sect-h">{e(f["name"])} › {e(s["name"])}</div>'
        f'<div class="pills">{"".join(segment(g) for g in s["segments"])}</div></div>' for s in f['sectors'])
    return (f'<details class="fam" data-n="{e(norm(f["name"]))}"{" open" if f["id"] == OPEN_FAMILY else ""}>'
            f'<summary><span class="chev" aria-hidden="true"></span><b>{e(f["name"])}</b>'
            f'<span class="cnt">{n_sec} sectors · {n_seg} segments</span></summary>'
            f'<div class="fam-body">{body}</div></details>')

def region(r):
    live = ''.join(
        f'<div class="live-row">{FLAGS[c]}<div class="lr-txt"><b>{e(n)}</b><span>{e(sub)}</span></div>'
        f'<a class="btn-view" href="{url}">View <span aria-hidden="true">→</span></a></div>' for c, n, sub, url in r['live'])
    soon = f'<div class="pills">{"".join(soon_pill(s) for s in r["soon"])}</div>' if r['soon'] else ''
    return f'<div class="region"><h3 class="reg-h">{e(r["name"])}</h3>{live}{soon}</div>'

FAMS = SECTORS['families']
N_FAM = len(FAMS)
N_SEG = sum(len(s['segments']) for f in FAMS for s in f['sectors'])
DESC = ('Uback ranks non-listed startups that have already raised funds, by global sector and by country, using public '
        'information. We don’t value companies. We rank them, and give an AI-estimated order of magnitude.')
JSONLD = {"@context": "https://schema.org", "@graph": [
    {"@type": "Organization", "name": "Uback", "url": "https://uback.com/", "email": "contact@uback.com",
     "description": "AI rankings of funded, non-listed startups, by global sector and by country. We don’t value companies. We rank them, and give an AI-estimated order of magnitude.",
     "logo": "https://uback.com/assets/favicon-192.png"},
    {"@type": "WebSite", "name": "Uback", "url": "https://uback.com/", "inLanguage": "en"},
    {"@type": "ItemList", "name": "Uback markets", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Morocco — monthly ranking (in French)", "url": "https://uback.com/ma/"},
        {"@type": "ListItem", "position": 2, "name": "Poland — monthly ranking", "url": "https://uback.com/pl/"},
        {"@type": "ListItem", "position": 3, "name": "Vietnam — monthly ranking", "url": "https://uback.com/vn/"}]}]}

CSS = '''
:root{--navy:#1E3A5F;--navy-dark:#142842;--gold:#C8A052;--bg:#F7F8FA;--line:#E4E8EE;--muted:#5A6B82;--body:#4A5A70;--dim:#6B7A8F;--dash:#C9D1DC}
*{box-sizing:border-box}
html,body{margin:0}
body{font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg);color:var(--navy);min-height:100vh;display:flex;flex-direction:column;-webkit-font-smoothing:antialiased}
a{color:var(--navy)}a:hover{color:var(--navy-dark)}
.wrap{width:100%;max-width:1200px;margin:0 auto;padding:0 20px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
[hidden]{display:none!important}

header{background:#fff;border-bottom:1px solid var(--line)}
header .wrap{height:64px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;font-size:22px;font-weight:800;letter-spacing:-.02em;color:var(--navy)}
.logo .u{width:34px;height:34px;border-radius:8px;background:var(--navy);color:var(--gold);display:inline-flex;align-items:center;justify-content:center;font-size:20px;letter-spacing:0}
nav{display:flex;gap:20px;align-items:center;font-size:15px;font-weight:500}
nav a{text-decoration:none;display:inline-flex;align-items:center;min-height:44px}
nav .nav-wide{display:none}

.hero{padding:56px 0 32px}
.hero .wrap{display:flex;flex-direction:column;gap:20px}
.eyebrow{display:flex;align-items:center;gap:10px;font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.eyebrow i{width:20px;height:2px;background:var(--gold);display:block;flex-shrink:0}
.eyebrow i.r{display:none}
h1{margin:0;font-size:40px;line-height:1.08;font-weight:800;letter-spacing:-.03em}
.lead{margin:0;font-size:17px;line-height:1.6;color:var(--body)}

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
.fam summary b{font-size:16px}
.fam .cnt{margin-left:auto;font-size:12px;color:var(--muted);white-space:nowrap}
.fam-body{padding:2px 0 16px 24px}
.sect{margin-top:10px}
.sect-h{font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin-bottom:6px}
.pills{display:flex;flex-wrap:wrap;gap:6px}
.pill{position:relative;display:inline-flex;align-items:center;min-height:34px;padding:4px 12px;border-radius:999px;font-size:13px;font-weight:500;line-height:1.25;text-decoration:none}
.pill.soon{border:1.5px dashed var(--dash);color:var(--body);background:#fff;cursor:default}
.pill.soon:hover,.pill.soon:focus,.pill.soon.show{border-style:solid;border-color:var(--gold);outline:none}
.pill.pub{background:var(--navy);color:#fff;border:1.5px solid var(--navy)}
.pill.pub:hover{background:var(--navy-dark);color:#fff}
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
  nav .nav-wide{display:inline-flex}
  .hero{padding:104px 0 64px}
  .hero .wrap{align-items:center;text-align:center;gap:28px}
  .eyebrow{font-size:13px}.eyebrow i{width:24px}.eyebrow i.r{display:block}
  h1{font-size:68px;line-height:1.05;letter-spacing:-.035em;max-width:980px}
  .lead{font-size:20px;max-width:760px}
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
  // formulaire d'abonnement (mailto)
  var f=document.querySelector('form[data-mailto]'); if(!f)return;
  f.addEventListener('submit',function(ev){ev.preventDefault();
    var em=f.email.value,pr=f.profil.options[f.profil.selectedIndex].text;
    var body='Hello,\\n\\nI would like to receive new Uback rankings.\\n\\nE-mail: '+em+'\\nProfile: '+pr+'\\n';
    window.location.href='mailto:'+f.dataset.mailto+'?subject='+encodeURIComponent('Follow Uback rankings')+'&body='+encodeURIComponent(body);
    setTimeout(function(){window.location.href=THANKS;},1500);});
})();
'''.replace('THANKS', json.dumps(THANKS_URL))

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Uback — Funded startups, ranked by AI</title>
<meta name="description" content="{e(DESC)} Country rankings in Morocco, Poland and Vietnam.">
<link rel="canonical" href="https://uback.com/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Uback">
<meta property="og:url" content="https://uback.com/">
<meta property="og:title" content="Uback — Funded startups, ranked by AI">
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

<header>
  <div class="wrap">
    <a class="logo" href="/" aria-label="Uback, home"><span class="u" aria-hidden="true">U</span>Uback</a>
    <nav aria-label="Main">
      <a class="nav-wide" href="#sectors">Sectors</a>
      <a class="nav-wide" href="#countries">Countries</a>
      <a href="{METHOD_URL}">Method</a>
      <a href="mailto:contact@uback.com">Contact</a>
    </nav>
  </div>
</header>

<main>
  <section class="hero">
    <div class="wrap">
      <div class="eyebrow"><i></i><span>Startup rankings · by global sector and by country</span><i class="r"></i></div>
      <h1>Funded startups, ranked by AI.</h1>
      <p class="lead">{e(DESC)}</p>
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
            <div class="freq navy"><b>Monthly</b><span>1st of each month</span></div>
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
          <h2>Get the rankings</h2>
          <p>Every new edition of the countries and sectors you follow. One-click unsubscribe. No data passed on to third parties.</p>
        </div>
        <div class="fform">
          <form name="follow-uback" method="POST" action="{THANKS_URL}" data-netlify="true" netlify-honeypot="bot-field"{' data-mailto="' + FORM_EMAIL + '"' if FORM_MODE == 'mailto' else ''}>
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
      <a href="mailto:contact@uback.com?subject={quote('Correction request')}">Request a correction</a>
      <a href="/ma/mentions-legales.html">Legal notice</a>
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
