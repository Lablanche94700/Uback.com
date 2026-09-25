# -*- coding: utf-8 -*-
"""English template: ranking-only market (no Backers sequence, no intentions, no partner page).
Do not run directly: tools/build_site.py runs it with the market configuration in M.
Writes ONLY into the market folder (e.g. pl/), never at the repository root."""
import json, html, os, shutil, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = '/' + M['code']                 # market path on uback.com (M is provided by build_site.py)
OUT = ROOT + P
D = json.load(open(f"{OUT}/data/{M['data']}", encoding='utf-8'))
BASE = 'https://uback.com' + P
NAME, ADJ, N = M['name'], M['adjective'], M['top_n']
RANKED = D['classement'][:N]
e = html.escape

# the stylesheet has a single source (ma/assets/style.css); each market gets its own copy
os.makedirs(f'{OUT}/assets', exist_ok=True)
shutil.copyfile(f'{ROOT}/ma/assets/style.css', f'{OUT}/assets/style.css')
OG = f'{BASE}/assets/og-image.png?v=1' if os.path.exists(f'{OUT}/assets/og-image.png') else 'https://uback.com/assets/og-image.png'

def a(url, label='source'):
    return f'<a href="{e(url)}" rel="nofollow noopener" target="_blank">{label}</a>'

def head(title, desc, path, extra=''):
    url = BASE + path
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
<meta property="og:image" content="{OG}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{P}/assets/style.css">
{extra}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="hdr">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Uback, home"><span class="u">U</span>Uback</a>
    {M['switcher'].replace('href="@ROOT@', 'href="/')}
    <button class="menu-toggle" aria-label="Menu" aria-expanded="false" onclick="var n=document.getElementById('nav');var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1E3A5F" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <nav class="main" id="nav" aria-label="Main navigation">
      <a href="{P}/#ranking">Ranking</a>
      <a href="{P}/#radar">Radar</a>
      <a href="{P}/method.html">Method</a>
    </nav>
    <span class="spacer"></span>
    <a class="btn" href="mailto:contact@uback.com?subject={e(f'Follow Uback {NAME}').replace(' ', '%20')}">Follow {e(NAME)}</a>
  </div>
</header>
<main id="main">
'''

FOOT = f'''
</main>
<footer>
  <div class="wrap">
    <div class="row">
      <span class="brand"><span class="u">U</span>Uback</span>
      <span>Powered by AI</span>
      <span>·</span><a href="{P}/method.html">Method and rules</a>
      <span>·</span><a href="{P}/method.html#correction">Request a correction</a>
      <span>·</span><a href="{P}/legal-notice.html">Legal notice</a>
      <span>·</span><a href="/">All markets</a>
      <span class="spacer"></span>
      <span>Uback.com · {datetime.date.today().year}</span>
    </div>
    <p>Uback is a content publisher. It provides no investment advice, receives no mandate and takes part in no transaction. Investing in non-listed companies carries a risk of losing all the capital invested.</p>
  </div>
</footer>
</body>
</html>
'''

def conf(n):
    dots = ''.join('<i class="f"></i>' if i < n else '<i></i>' for i in range(3))
    lab = {3: 'Solid sources', 2: 'Partial sources', 1: 'Weak sources'}[n]
    return f'<span class="conf" aria-hidden="true">{dots}</span><span class="conf-l">{lab}</span>'

def row(c):
    top = ' class="top"' if c['rang'] == 1 else ''
    jur = f'<span class="jur">{e(c["juridiction"])}</span>' if c.get('juridiction') and c['juridiction'] != NAME else ''
    note = f'<div class="src">{e(c["note"])}</div>' if c.get('note') else ''
    return f'''<tr{top}>
<td class="rank">{c['rang']}</td>
<td><span class="co">{e(c['nom'])}<small>{e(c['ville'])} · founded {e(str(c['creation']))}</small></span>{jur}{note}</td>
<td data-l="Sub-sector">{e(c['sous_secteur'])}</td>
<td data-l="Funding">{e(c['leve_cumule'])} raised<br><span class="src">{e(c['derniere_levee'])} · {a(c['source'])}</span></td>
<td data-l="Confidence">{conf(c['confiance'])}</td>
</tr>'''

def item(r, extra_key=None):
    sub = f'<br><span class="src">{e(r[extra_key])}</span>' if extra_key and r.get(extra_key) else ''
    return f'<li><span><b>{e(r["nom"])}</b> · {e(r["sous_secteur"])}{sub}</span><span>{e(r["derniere_levee"])} · {a(r["source"])}</span></li>'

mk = D['marche']
jsonld = {
  "@context": "https://schema.org", "@type": "ItemList",
  "name": f"{NAME}’s top {N} funded startups – {D['date_label']}",
  "description": f"Uback monthly ranking of non-listed {ADJ} startups, established by AI from public information.",
  "itemListOrder": "https://schema.org/ItemListOrderDescending",
  "itemListElement": [{"@type": "ListItem", "position": c['rang'], "name": c['nom'], "url": f"https://{c['site']}"} for c in RANKED]
}

index = head(
  f"{NAME}’s top {N} funded startups – {D['date_label']} | Uback {NAME}",
  f"Monthly ranking of non-listed {ADJ} startups that have already raised funds, established by AI from public information. Uback ranks, it does not value.",
  "/", f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>')

index += f'''
<div class="wrap">
  <div class="hero">
    <div>
      <div class="kicker">Funded startups, ranked by AI</div>
      <h1>{e(NAME)}’s top {N} funded startups</h1>
      <p class="lead">A monthly ranking of non-listed {e(ADJ)} startups that have already raised funds, established by artificial intelligence from public information. Uback does not calculate any valuation: it ranks.</p>
      <div class="meta">
        <span class="tag beta">{e(D['edition'])} · {e(D['date_label'])}</span>
        <span>Claude · multi-AI consensus from Edition 1</span><span>·</span>
        <a href="{P}/method.html">Published method</a><span>·</span>
        <span>Order never changed by a human</span>
      </div>
    </div>
    <div class="panel">
      <div class="k">The market at a glance</div>
      <div class="stats">
        <div><b>{len(RANKED)}</b><span>companies ranked</span></div>
        <div><b>{len(D['radar'])}</b><span>companies on the radar</span></div>
        <div><b>{e(mk['total_2025'])}</b><span>raised in 2025</span></div>
        <div><b>{e(mk['deals_2025'])}</b><span>rounds in 2025</span></div>
      </div>
      <div class="fine">{e(mk['commentaire'])} Sources: {', '.join(a(s['url'], e(s['label'])).replace('<a ', '<a style="color:#c7d0dc" ', 1) for s in mk.get('sources', []))}.</div>
    </div>
  </div>

  <div class="reperes">
    <span class="lab">Listed benchmarks</span>
    {''.join(f'<span class="pill">{e(r["nom"])} · {e(r["info"])} · {a(r["source"])}</span>' for r in D.get('reperes_cotes', []))}
    <span class="fine">Not ranked: listed companies are shown for reference only.</span>
  </div>
</div>

<section id="ranking" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head">
      <h2>National ranking · all sectors</h2>
      <div class="tabs"><a class="on" href="#ranking">Top {N}</a><a href="#radar">Radar</a><a href="#born-here">Born here, based elsewhere</a></div>
      <span class="spacer"></span>
      <span class="sub">First edition: no movements yet.</span>
    </div>
    <table class="tbl">
      <thead><tr><th>#</th><th>Company</th><th>Sub-sector</th><th>Known funding</th><th>Confidence</th></tr></thead>
      <tbody>
      {''.join(row(c) for c in RANKED)}
      </tbody>
    </table>
    <p style="margin:18px 0 0;padding:14px 16px;border:1px dashed #d9dee5;border-radius:10px;font-size:14px;color:#4b5563"><b style="color:#1E3A5F">Partner onboarding in progress.</b> Rankings are published monthly; investor intentions will open with our local partner.</p>
    <div class="disclaimer"><b>This ranking is an opinion, not a valuation.</b> {e(D['methode'])} It is based on public information (press, funding announcements), following a published method, with no human intervention on the order. Uback neither calculates nor estimates any valuation: ranking non-listed companies is inherently imprecise, depends on the information available and may be contradicted by non-public facts. The confidence index reflects the quality of the sources. Any company may <a href="{P}/method.html#correction">request a correction</a> or dispute its position. This ranking is editorial content: it is neither investment advice nor a solicitation. Eligibility threshold: at least {e(D['seuil_levee'])} raised, non-listed companies, main operations in {e(NAME)}.</div>
  </div>
</section>

<section class="soft" id="radar">
  <div class="wrap">
    <div class="two">
      <div class="box line">
        <h3>Radar · known eligible companies, not ranked</h3>
        <p>Companies just below the Top {N}, with no judgement and no AI call. Undisclosed amount: the round is confirmed by the press, not its amount.</p>
        <ul class="list">
        {''.join(item(r) for r in D['radar'])}
        </ul>
        <h3 id="born-here" style="margin-top:22px">Born in {e(NAME)}, based elsewhere</h3>
        <p>Companies of {e(ADJ)} origin whose main operations are now abroad: not ranked, shown with the law governing their shares.</p>
        <ul class="list">
        {''.join(item(r, 'lieu') for r in D.get('nees_ici', [])) or '<li><span>None identified in this edition.</span></li>'}
        </ul>
        {(f"""<h3 id="based-here" style="margin-top:22px">Born elsewhere, based in {e(NAME)}</h3>
        <p>Companies founded abroad whose main operations are in {e(NAME)}.</p>
        <ul class="list">
        {''.join(item(r, 'lieu') for r in D['nees_ailleurs'])}
        </ul>""") if D.get('nees_ailleurs') else ''}
        <h3 style="margin-top:22px">Not ranked</h3>
        <ul class="list">
        {''.join(f'<li><span><b>{e(r["nom"])}</b> · {e(r["motif"])}</span><span>{a(r["source"])}</span></li>' for r in D.get('hors_classement', []))}
        </ul>
      </div>
      <div>
        <div class="box line" id="follow">
          <h3>Get the ranking every month</h3>
          <p>Free. Movements, new entries, disagreements between AIs, and the opening of investor intentions in {e(NAME)}.</p>
          <a class="btn navy" href="mailto:contact@uback.com?subject={e(f'Follow Uback {NAME}').replace(' ', '%20')}">Follow {e(NAME)}</a>
          <p class="src" style="margin-top:10px">One e-mail a month. No data passed on to third parties.</p>
        </div>
        <div class="box" style="margin-top:20px">
          <h3>Do you run one of these companies?</h3>
          <p>Correct an information, dispute a position or ask to be removed. Free.</p>
          <a class="btn" href="{P}/method.html#correction">Correct a company profile</a>
        </div>
      </div>
    </div>
  </div>
</section>
''' + FOOT

# ---------------------------------------------------------------- method
method = head(f"Method and rules | Uback {NAME}", "How Uback ranks startups: AI consensus, eligibility, confidence index, right of reply. Uback ranks, it does not value.", "/method.html") + f'''
<div class="wrap prose">
<h1>Method and rules</h1>
<p class="lead">Uback is an algorithm before it is a website. Its credibility rests on simple, public rules, identical in every country and applied without exception.</p>

<h2>The rules</h2>
<ol>
<li><b>Uback ranks, it does not value.</b> Uback estimates no valuation; only public, dated and sourced figures are shown (amounts raised, last announced round).</li>
<li><b>A ranking is never for sale.</b> No payment, from a company, a partner or an analyst, influences a position.</li>
<li><b>No human changes the order.</b> A reviewer may exclude a company on a traced eligibility ground, or rerun the calculation; never reorder.</li>
<li><b>Uback never solicits.</b> Any outgoing contact with a company, a manager or a shareholder goes through the country’s licensed partner.</li>
<li><b>Uback is not a financial intermediary.</b> No mandate, no negotiation, no advice, no collection of funds intended for an investment.</li>
<li><b>Everything is published, everything is traced.</b> AIs queried, date, consensus rule and eligibility criteria are public; every company has a right of reply.</li>
</ol>

<h2>How the ranking is built</h2>
<p>Every month, the same question is put to several artificial intelligences for each country and each sector: which eligible companies rank highest, in order? The answers are merged into a consensus ranking (by points: 1st = 20 points, 2nd = 19, and so on). A confidence index is shown for each position: when the AIs agree, the ranking is solid; when they diverge, the divergence itself becomes information.</p>
<p><b>Edition 0 (beta).</b> This first edition was established by a single AI (Claude, Anthropic), from desk research on the press and funding announcements, each amount being sourced. Cumulative funding counts equity only: debt and grants are shown but not added up. The confidence index reflects the quality of the available sources. The multi-AI consensus applies from Edition 1.</p>

<h2>Eligibility</h2>
<table>
<tr><th>Rule</th><th>Application</th></tr>
<tr><td>Technology or innovative company</td><td>Starting scope; the sector tree is public and evolving.</td></tr>
<tr><td>One main activity, one sector</td><td>Conglomerates and multi-activity companies are excluded. A company appears in one ranking only.</td></tr>
<tr><td>Has raised funds</td><td>At least {e(D['seuil_levee'])} (or equivalent), verifiable (public announcement, register, or partner attestation). A grant is not a funding round. Debt is distinguished from equity.</td></tr>
<tr><td>Non-listed</td><td>Listed companies are benchmarks, shown separately, never ranked.</td></tr>
<tr><td>Active and independent</td><td>A company acquired, closed or in insolvency proceedings leaves the ranking; history keeps its positions.</td></tr>
<tr><td>Main operations in the country</td><td>A ranking’s country is the country of operations (team, market), whatever the legal seat. The legal seat and the law governing the shares are shown on each profile. Companies of local origin operated abroad appear in “Born here, based elsewhere”.</td></tr>
</table>

<h2>Investor intentions</h2>
<p>In {e(NAME)}, Uback currently publishes the ranking only. Investor intentions will open once our local licensed partner is on board: until then, no intention can be declared and no company status is shown.</p>

<h2 id="correction">Right of reply and corrections</h2>
<p>Any company mentioned may request the correction of an information (amount, date, sector, status), dispute its position or ask to be removed, by writing to <a href="mailto:corrections@uback.com">corrections@uback.com</a>. Every request receives a reasoned answer.</p>

<h2>Sources</h2>
<p>Business and technology press, investor announcements and market reports ({', '.join(e(s['label']) for s in mk.get('sources', []))}). Every amount in the ranking links to its source.</p>
</div>
''' + FOOT

# ---------------------------------------------------------------- legal notice
legal = head(f"Legal notice | Uback {NAME}", "Legal notice of the Uback website.", "/legal-notice.html") + '''
<div class="wrap prose">
<h1>Legal notice</h1>
<h2>Publisher</h2>
<p>DEALING-ROOM SARL, a French limited liability company (SARL) with a share capital of EUR 50,000, registered with the Créteil Trade and Companies Register under number 485313712. Publication director: Sebastien Blanchard. Contact: <a href="mailto:contact@uback.com">contact@uback.com</a>.</p>
<h2>Hosting</h2>
<p>GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, United States. Website: <a href="https://github.com">github.com</a>.</p>
<h2>Nature of the service</h2>
<p>Uback is a content publisher. The rankings published are opinions produced by artificial intelligence systems from public information, following a published method. They constitute neither investment advice, nor a personal recommendation, nor a solicitation or an offer of securities. Uback receives no mandate, negotiates no transaction and collects no funds intended for an investment. Introductions, when they open, are made by a licensed partner identified in each market, under its sole regulatory responsibility.</p>
<h2>Right of reply</h2>
<p>Any company mentioned may request the correction or removal of information about it at <a href="mailto:corrections@uback.com">corrections@uback.com</a>.</p>
<h2>Personal data</h2>
<p>E-mail addresses sent to us are used only to send the monthly ranking and information about the opening of the service. They are neither sold nor passed on to third parties. You may unsubscribe at any time. Data controller: DEALING-ROOM SARL. Rights of access, rectification and erasure: <a href="mailto:privacy@uback.com">privacy@uback.com</a>.</p>
<h2>Intellectual property</h2>
<p>The rankings, texts and graphic elements of the website are the property of DEALING-ROOM SARL. Reproducing a ranking is allowed with credit to the source and a link to the original page. Company names belong to their owners.</p>
</div>
''' + FOOT

for name, content in [('index.html', index), ('method.html', method), ('legal-notice.html', legal)]:
    open(f'{OUT}/{name}', 'w', encoding='utf-8', newline='\n').write(content)
