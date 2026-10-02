# -*- coding: utf-8 -*-
"""Génère les fiches société (/company/<slug>/), les pages investisseur (/investor/<slug>/), l'annuaire /investors/,
le formulaire des fiches (/profile-form.html), l'index de recherche (assets/search-index.json) et les sitemaps
sitemap-companies.xml et sitemap-investors.xml. Anglais seulement.
Données : tools/companies.py (classements pays et segments, data/companies/, data/investors.json, data/analyses/,
data/connectors.json). Aucune page n'est écrite à la main.
Exception à la règle « aucun générateur ne supprime de fichier » : ce script reconstruit INTÉGRALEMENT company/ et
investor/ à chaque passage ; une société sortie des données n'a donc plus de page.
Ordre de génération : après tools/build_segments.py, avant tools/build_regions.py.
Le script échoue (et n'écrit rien de faux) si un contrôle échoue : champ interne affiché, tranche différente de la page
de classement, crochet de texte d'attente, slug publié modifié, sitemap incohérent avec la règle d'indexation."""
import os, sys, re, json, html, shutil, datetime
from urllib.parse import quote

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import companies as K
import geo, valuation, search
from build_site import NAMES, format_date_short
from build_segments import page_top, page_bottom, GM, GI, GC, VB, CONF_TXT, family_slug, SECTORS, REGION_NAME
from valuation import BRACKETS, BANDS, money, money2, range_txt, month
from forms import WEB3FORMS_KEY, w3f_js

e = html.escape
BASE = 'https://uback.com'
FORM = '/profile-form.html'
FAMILY_PAGES = {f['name']: family_slug(f['name']) for f in SECTORS['families']
                if os.path.exists(os.path.join(ROOT, 'sectors', family_slug(f['name']), 'index.html'))}
CONNECTORS = json.load(open(os.path.join(ROOT, 'data', 'connectors.json'), encoding='utf-8')) \
    if os.path.exists(os.path.join(ROOT, 'data', 'connectors.json')) else {}
INTERNAL = ('estimate_usd', 'note_internal', 'valuation_central_usd', 'valuation_low_usd', 'valuation_high_usd')
INV_TYPES = {'vc': 'Venture capital fund', 'cvc': 'Corporate venture capital', 'corporate': 'Corporate investor',
             'growth': 'Growth equity investor', 'pe': 'Private equity firm', 'sovereign': 'Sovereign wealth fund',
             'pension': 'Pension fund investor', 'dfi': 'Development finance institution', 'public': 'Public investment bank',
             'asset': 'Asset manager', 'accelerator': 'Accelerator', 'angel_network': 'Angel network'}
OPEN_TXT = {'cession': ('Shareholder selling', 'An existing shareholder has told Uback it is considering selling part of its stake.'),
            'levee': ('Raising soon', 'The company has told Uback it plans to raise funds soon.'),
            'secondary': ('Shareholder selling', 'An existing shareholder has told Uback it is considering selling part of its stake.'),
            'raise': ('Raising soon', 'The company has told Uback it plans to raise funds soon.')}
TIER_TXT = {'radar': 'Radar', 'born': 'Born here, based elsewhere'}

class CheckError(Exception):
    pass

# ---------------------------------------------------------------- outils
def country_name(code):
    code = (code or '').lower()
    if code in NAMES:
        return NAMES[code]['en']
    c = geo.COUNTRIES.get(code)
    return geo.name(c) if c else code.upper()

def startups_of(code):
    """« Moroccan startups » (adjectif du marché) ; sinon « startups in Kenya »."""
    from build_site import MARKETS
    m = next((x for x in MARKETS if x['code'] == (code or '').lower() and x['lang'] == 'en'), None)
    return (f"{m['adj_fp']} ", '') if m else ('', f' in {country_name(code)}')

def country_url(code):
    """Page du classement pays (version principale) quand elle est publiée."""
    c = geo.COUNTRIES.get((code or '').lower())
    return f'/{code.lower()}/' if c and c['status'] == 'live' and os.path.exists(os.path.join(ROOT, code.lower(), 'index.html')) else None

def link(href, txt, cls=''):
    return f'<a{f" class=\"{cls}\"" if cls else ""} href="{href}">{txt}</a>' if href else txt

def src_link(url, label=None):
    return f'<a href="{e(url)}" rel="nofollow noopener" target="_blank">{e(label or K.domain(url))}</a>'

def ym(d):
    """« 2025-10 » → « Oct 2025 » ; « 2023 » → « 2023 »."""
    return month(d, 'en') if d else ''

def date_key(d):
    if not d:
        return (0, 0)
    y, m = (d.split('-') + ['0'])[:2]
    return int(y), int(m)

def app_country(a):
    return a['code'] if a['kind'] == 'country' else (a['row'].get('country_code') or '').lower()

def form_url(t, company=None, investor=None, **kw):
    q = f'?type={t}'
    if company:
        q += f'&amp;company={quote(company)}'
    if investor:
        q += f'&amp;investor={quote(investor)}'
    for k, v in kw.items():
        q += f'&amp;{k}={quote(str(v))}'
    return FORM + q

# ---------------------------------------------------------------- modèle d'une fiche
def describe(c):
    """Tout ce que la fiche affiche, calculé une fois (aussi utilisé par les pages investisseur et les comparables)."""
    apps = c['apps']
    enr = K.enrichment(c['slug']) or {}
    ranked = [a for a in apps if a['list'] == 'ranked']
    cr = [a for a in ranked if a['kind'] == 'country']
    sr = [a for a in ranked if a['kind'] == 'segment']
    order = {('country', 'ranked'): 0, ('segment', 'ranked'): 1, ('country', 'radar'): 2, ('country', 'born'): 3, ('segment', 'radar'): 4}
    prim = sorted(apps, key=lambda a: (order[(a['kind'], a['list'])], a.get('rank') or 0))[0]
    code = app_country(prim)
    row = prim['row']
    sub = row.get('sous_secteur') if prim['kind'] == 'country' else ' › '.join(prim['src']['path'])
    if prim['kind'] == 'segment':
        family, subname = prim['src']['path'][0], prim['src']['name']
    else:
        family = K.family_of(sub)
        subname = sub.split('›', 1)[1].strip() if '›' in sub else ''
    # valorisation : celle du classement principal (pays d'abord), exactement comme sur la page de classement
    val = None
    if cr:
        r = cr[0]['row']
        if r.get('valuation_bracket') and r['valuation_bracket'] != 'not_estimated':
            val = dict(kind='country', central=r['valuation_central_usd'], low=r['valuation_low_usd'], high=r['valuation_high_usd'],
                       bracket=r['valuation_bracket'], conf=r['valuation_confidence'], vi=r.get('valuation_input') or {}, app=cr[0])
        else:
            val = dict(kind='country', bracket='not_estimated', app=cr[0], vi=r.get('valuation_input') or {})
    elif sr:
        r = sr[0]['row']
        val = dict(kind='segment', central=r['estimate_usd'], low=r['estimate_usd'] * BANDS[r['confidence']][0],
                   high=r['estimate_usd'] * BANDS[r['confidence']][1], bracket=r['tranche'], conf=r['confidence'], app=sr[0])
    # sources (URL distinctes)
    srcs = []
    for a in apps:
        r = a['row']
        if a['kind'] == 'country':
            srcs += [r.get('source'), r.get('source_valuation')]
        else:
            srcs += list(r.get('sources') or []) + [v.get('source') for v in (r.get('kpis') or {}).values()]
    srcs += list(enr.get('sources') or []) + [u for rd in enr.get('rounds', []) for u in rd.get('sources', [])]
    srcs = list(dict.fromkeys(u for u in srcs if u and u.startswith('http')))
    rounds = funding(c, enr)
    dated = any(rd.get('date') for rd in rounds)
    index = bool(ranked) or (dated and len(srcs) >= 2 and bool(family))
    best = min((a['rank'] for a in cr), default=None)
    return dict(c=c, enr=enr, prim=prim, code=code, family=family, subname=subname, sub=sub, val=val, srcs=srcs, rounds=rounds,
                index=index, ranked=ranked, cr=cr, sr=sr, best=best, row=row)

def funding(c, enr):
    """Historique des levées : l'enrichissement s'il existe, sinon le dernier tour cité par chaque classement."""
    if enr.get('rounds'):
        out = []
        for rd in enr['rounds']:
            out.append(dict(date=rd.get('date'), label=rd.get('label', ''), amount=rd.get('amount_label') or
                            (money(rd['amount_usd'], 'en') if rd.get('amount_usd') else ''), kind=rd.get('kind', ''),
                            investors=rd.get('investors', []), sources=rd.get('sources', []), rest=''))
        return sorted(out, key=lambda r: date_key(r['date']), reverse=True)
    out, seen = [], {}
    for a in c['apps']:
        r = a['row']
        if a['kind'] == 'country':
            p = K.parse_round(r.get('derniere_levee'))
            if not (p['label'] or p['amount'] or p['date']):
                continue
            txt = (r.get('derniere_levee') or '').lower()
            vi = r.get('valuation_input') or {}
            kind = ('debt' if re.search(r'\bdebt\b|convertible', p['label'].lower()) else 'grant' if 'grant' in txt[:40]
                    else 'equity' if vi.get('round_date') and p['date'] and vi['round_date'] == p['date'] else '')
            rd = dict(date=p['date'], label=p['label'], amount=p['amount'], kind=kind,
                      investors=K.split_investors(p['investors']), sources=[r['source']] if r.get('source') else [], rest=p['rest'])
        else:
            lr = r.get('last_equity_round') or {}
            amt = lr.get('amount_label') or (money(lr['amount_usd'], 'en') if lr.get('amount_usd') else '')
            rd = dict(date=lr.get('date'), label=lr.get('type', ''), amount=amt, kind='equity',
                      investors=list(dict.fromkeys(K.split_investors(lr.get('investors') or '') + K.detail_investors(lr.get('detail')))),
                      sources=(r.get('sources') or [])[:1], rest=lr.get('detail') or '')
        k = rd['date']
        if k in seen:                         # même tour vu par deux classements : on garde la ligne la plus complète
            old = seen[k]
            for f in ('label', 'amount', 'kind', 'rest'):
                old[f] = old[f] or rd[f]
            old['investors'] = list(dict.fromkeys(old['investors'] + rd['investors']))
            old['sources'] = list(dict.fromkeys(old['sources'] + rd['sources']))
            continue
        seen[k] = rd
        out.append(rd)
    return sorted(out, key=lambda r: date_key(r['date']), reverse=True)

def inv_link(raw, investors):
    """Nom d'investisseur → lien vers sa page si elle existe."""
    it = K.investor_table().get(K.norm_inv(raw))
    key = it['slug'] if it else 'raw:' + K.norm_inv(raw)
    inv = investors.get(key)
    if inv and inv['page']:
        return f'<a href="/investor/{inv["slug"]}/">{e(raw)}</a>'
    return e(raw)

def bracket_scale(b):
    return '<div class="pf-scale" role="img" aria-label="Valuation bracket: ' + e(VB[b]) + '">' + ''.join(
        f'<div class="{"on" if x == b else ""}"><i></i><span>{VB[x]}</span></div>' for x in BRACKETS) + '</div>'

# ---------------------------------------------------------------- fiche société
def ranking_rows(m):
    rows = ''
    for a in sorted(m['c']['apps'], key=lambda a: (a['list'] != 'ranked', a['kind'] != 'country')):
        if a['kind'] == 'country':
            cs = a['src']
            name = f"{e(cs['name'])} · all sectors"
            href = cs['path'] + '/' + ('#radar' if a['list'] != 'ranked' else '')
            tier = f"Top {cs['n']}" if a['list'] == 'ranked' else TIER_TXT[a['list']]
            ed = f"{e(cs['data'].get('edition') or '')} · {e(cs['data'].get('date_label') or ym(cs['data']['date']))}"
            nxt = geo.next_date(cs['code'])
        else:
            sd = a['src']
            name = f"{e(sd['name'])} · worldwide"
            href = f"/segments/{sd['segment_id']}/" + ('#radar' if a['list'] != 'ranked' else '')
            tier = f"Top {len(sd['ranked'])}" if a['list'] == 'ranked' else 'Radar'
            ed = f"{e(sd['edition_label'])} · {ym(sd['published'][:7])}"
            nxt = geo.next_date(sd['segment_id'])
        rk = f'<b class="pf-rk">#{a["rank"]}</b>' if a['list'] == 'ranked' else '<span class="mut">—</span>'
        rows += (f'<tr><td><a class="pf-strong" href="{href}">{name}</a></td><td>{tier}</td><td>{rk}</td><td>{ed}</td>'
                 f'<td>{format_date_short(nxt, "en") if nxt else ""}</td></tr>')
    return rows

def history(m):
    pts = []
    for code, d, r in m['c'].get('history', []):
        pts.append((d, f'{ym(d)} · #{r}'))
    for a in m['cr']:
        pts.append((a['src']['data']['date'], f"{ym(a['src']['data']['date'])} · #{a['rank']}{' ' + e(a['src']['name']) if m['sr'] else ''}"))
    for a in m['sr']:
        pts.append((a['src']['published'][:7], f"{ym(a['src']['published'][:7])} · #{a['rank']} {e(a['src']['name'])}"))
    if not pts:
        return ''
    dots = ''.join(f'<span class="pf-dot"><i></i>{t}</span>' for _, t in sorted(pts))
    first = '<span>First edition: no movements yet.</span>' if len({d for d, _ in pts}) == 1 else ''
    return f'<div class="pf-hist"><span class="lbl">Rank history</span>{dots}{first}</div>'

def valuation_block(m):
    v = m['val']
    name = e(m['c']['name'])
    if v is None:
        return ''
    if v['bracket'] == 'not_estimated':
        return f'''<section class="card pf-card">
  <div class="pf-h"><h2>Estimated valuation</h2><span class="lbl">AI</span></div>
  <p class="pf-big mut">Not estimated</p>
  <p class="pf-p">{e(v['app']['row'].get('valuation_basis') or '')}</p>
  <p class="pf-fine">An indicative editorial estimate, neither a financial valuation nor investment advice. <a href="{GM}#estimation">Method</a></p>
</section>'''
    rng = range_txt(v['low'], v['high'], 'en')
    dl = ''
    if v['kind'] == 'country':
        vi = v['vi']
        if vi.get('round_usd') and vi.get('round_date'):
            anchor = ' · '.join(p for p in (vi.get('round_label'), money(vi['round_usd'], 'en'), ym(vi['round_date'])) if p)
            dl += f'<dt>Anchor</dt><dd>Last known equity round: {e(anchor)}</dd>'
        elif vi.get('cumulative_usd'):
            dl += f'<dt>Anchor</dt><dd>Total raised: {e(money(vi["cumulative_usd"], "en"))} (last round undisclosed)</dd>'
        if vi.get('published_usd') and vi.get('published_date'):
            old = valuation.months_between(vi['published_date'], v['app']['src']['data']['date']) >= 24
            dl += (f'<dt>Published valuation</dt><dd>{e(money(vi["published_usd"], "en"))} · {ym(vi["published_date"])}'
                   f'{" · older than 24 months, shown for reference" if old else ""}</dd>')
        adj = int(vi.get('adjust') or 0)
        dl += f'<dt>AI adjustment</dt><dd>{e(("× 3: " if adj > 0 else "÷ 3: ") + vi.get("adjust_reason", "")) if adj else "None"}</dd>'
        where = f"{e(v['app']['src']['name'])} ranking"
    else:
        r = v['app']['row']
        lr = r.get('last_equity_round') or {}
        anchor = ' · '.join(p for p in (lr.get('type'), lr.get('amount_label') or (money(lr['amount_usd'], 'en') if lr.get('amount_usd') else ''), ym(lr.get('date'))) if p)
        if anchor:
            dl += f'<dt>Anchor</dt><dd>Last known equity round: {e(anchor)}</dd>'
        pv = r.get('published_valuation')
        if pv:
            old = valuation.months_between(pv['date'], v['app']['src']['published'][:7]) >= 24
            dl += (f'<dt>Published valuation</dt><dd>{e(pv.get("label") or money(pv["value_usd"], "en"))} · {ym(pv["date"])}'
                   f'{" · older than 24 months, shown for reference" if old else ""}</dd>')
        where = f"{e(v['app']['src']['name'])} ranking (worldwide)"
    other = ''
    if v['kind'] == 'country' and m['sr']:
        r = m['sr'][0]['row']
        o_rng = range_txt(r['estimate_usd'] * BANDS[r['confidence']][0], r['estimate_usd'] * BANDS[r['confidence']][1], 'en')
        other = (f'<p class="pf-p">In the {e(m["sr"][0]["src"]["name"])} ranking (worldwide): ≈ {money2(r["estimate_usd"], "en")} · '
                 f'{o_rng} · {VB[r["tranche"]]} · {CONF_TXT[r["confidence"]]} confidence.</p>')
    conf_cls = {'high': 'ok', 'medium': 'mid', 'low': 'low'}[v['conf']]
    return f'''<section class="card pf-card">
  <div class="pf-h"><h2>Estimated valuation</h2><span class="lbl">AI · {where}</span></div>
  <div class="pf-val"><span class="pf-big">≈ {money2(v['central'], 'en')}</span><span class="pf-range">{rng} · {VB[v['bracket']]}</span>
    <span class="chip {conf_cls}">{CONF_TXT[v['conf']]} confidence</span></div>
  {bracket_scale(v['bracket'])}
  <dl class="pf-dl">{dl}</dl>
  {other}
  <p class="pf-fine">An indicative editorial estimate produced by AI, imperfect by nature: neither a financial valuation nor investment advice. Only the market sets a company’s value. <a href="{GM}#estimation">Method</a></p>
</section>'''

def funding_block(m, investors):
    rounds = m['rounds']
    if not rounds:
        return ''
    rows, notes = '', []
    for rd in rounds:
        invs = ', '.join(inv_link(x, investors) for x in rd['investors']) or '<span class="mut">—</span>'
        src = ' · '.join(src_link(u) for u in rd['sources']) or '<span class="mut">—</span>'
        kind = f'<span class="chip sm">{rd["kind"].capitalize()}</span>' if rd['kind'] else '<span class="mut">—</span>'
        rows += (f'<tr><td data-l="Date">{ym(rd["date"]) or "<span class=mut>—</span>"}</td><td data-l="Round" class="pf-strong">{e(rd["label"]) or "<span class=mut>—</span>"}</td>'
                 f'<td data-l="Amount">{e(rd["amount"]) or "<span class=mut>—</span>"}</td><td data-l="Type">{kind}</td>'
                 f'<td data-l="Investors">{invs}</td><td data-l="Source">{src}</td></tr>')
        if rd.get('rest'):
            notes.append(rd['rest'])
    raised = m['row'].get('leve_cumule') if m['prim']['kind'] == 'country' else ''
    note = ''.join(f'<p class="pf-p">{e(n[:1].upper() + n[1:])}.</p>' for n in dict.fromkeys(notes))
    return f'''<section class="card pf-card">
  <div class="pf-h"><h2>Funding history</h2>{f'<span class="mut sm">{e(raised)} raised in total</span>' if raised else ''}</div>
  <div class="pf-scroll"><table class="pf-tbl"><thead><tr><th>Date</th><th>Round</th><th>Amount</th><th>Type</th><th>Investors</th><th>Source</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
  {note}
  <p class="pf-fine">Rounds as cited by Uback’s rankings and their sources. Equity, debt and grants are shown separately; only equity rounds count towards the valuation anchor.</p>
</section>'''

def ai_block(m):
    s = m['enr'].get('ai_summary')
    if not s or not s.get('text') or not m['best']:
        return ''
    return f'''<section class="card pf-card">
  <div class="pf-h"><h2>Why #{m['best']}: the AI’s reading</h2><span class="lbl">Generated at publication</span></div>
  <p class="pf-p">{e(s['text'])}</p>
  <p class="pf-fine">Order never changed by a human. Produced by Claude (Anthropic); multi-AI consensus in a future edition.</p>
</section>'''

ANGLES = [('valuation', 'Valuation', 'What is {n} worth?'), ('competitors', 'Versus competitors', '{r}'),
          ('acquirer', 'Who should acquire it', 'Strategic buyers, and why')]

def analyses_block(m):
    name = m['c']['name']
    p = os.path.join(ROOT, 'data', 'analyses', f"{m['c']['slug']}.json")
    items = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []
    rank_q = f"Is #{m['best']} the right rank?" if m['best'] else 'How does it compare?'
    cards = ''.join(f'<div class="pf-angle"><b>{t}</b><span>{e(d.format(n=name, r=rank_q))}</span></div>' for _, t, d in ANGLES)
    pub = ''
    for a in items:
        coi = a.get('conflict') or 'None declared'
        pub += f'''<article class="pf-an"><div class="pf-pdf">PDF</div><div class="pf-an-t"><b>{e(a['title'])}</b>
    <span>{e(a['author'])} · {e(a['role'])}, {e(a['firm'])} · Angle: {e(a['angle'])} · {ym(a['date'])}{f" · {a['pages']} pages" if a.get('pages') else ''}</span>
    <p>{e(a['summary'])}</p><span class="mut sm">Conflict of interest: {e(coi)}</span></div>
    <a class="btn" href="{e(a['url'])}" rel="noopener" target="_blank">Read</a></article>'''
    return f'''<section class="card pf-card">
  <div class="pf-h"><h2>Independent analyses</h2><span class="lbl">By industry professionals &amp; analysts</span></div>
  <p class="pf-p">Industry professionals and financial analysts can publish their own analysis of {e(name)} as a PDF, on one of three angles only:</p>
  <div class="pf-angles">{cards}</div>
  {pub}
  <div class="pf-row"><a class="btn navy" href="{form_url('analysis', name)}">Publish an analysis</a><span class="mut sm">Name, role and LinkedIn shown · public sources only</span></div>
  <p class="pf-fine">Analyses are the opinion of their authors, not of Uback. They are checked before publication and never change the rank.</p>
</section>'''

def invest_block(m):
    name = m['c']['name']
    a = m['prim']
    code = m['code']
    fam = m['family']
    o = None
    for x in m['c']['apps']:
        if x['kind'] == 'country' and (x['row'].get('acces') in ('cession', 'levee')):
            o = x['row']['acces']
        elif x['kind'] == 'segment' and x['row'].get('open_to_backers'):
            o = x['row']['open_to_backers']['type']
    live = country_url(code)
    if a['kind'] == 'segment' and not live:
        pool_href, pool_txt = f"{GI}?pool=segment&amp;segment={a['sid']}#opening", f"Declare an interest in {e(a['src']['name'].lower())}"
        pool2 = ''
        pool_lbl = f"{e(a['src']['name'])} pool"
    else:
        cn = country_name(code)
        pre, post = startups_of(code)
        pool_href, pool_txt = f"{GI}?pool=country&amp;country={code}#opening", f"Declare an interest in {e(pre)}startups{e(post)}"
        fam_l = fam if fam.isupper() or fam[:2].isupper() else fam.lower()
        pool2 = (f'<a class="btn wide" data-pool href="{GI}?pool=country&amp;country={code}&amp;sector={quote(fam)}#opening">'
                 f'Declare an interest in {e(pre)}{e(fam_l)}{e(post)}</a>') if fam else ''
        pool_lbl = f'{e(cn)} pool'
    if o:
        badge, txt = OPEN_TXT[o]
        q = f"segment={a['sid']}" if a['kind'] == 'segment' else f"country={code}"
        body = f'''<div class="pf-open"><b>{badge}.</b> {txt} Price and volume are never published.</div>
  <a class="btn gold wide" href="{GI}?pool=company&amp;company={quote(name)}&amp;{q}#opening">Declare an intent on {e(name)}</a>
  <a class="btn wide" href="{pool_href}">Or back {e("".join(startups_of(code)[:1]))}startups{e(startups_of(code)[1])}</a>
  <p class="pf-fine">Shareholders’ agreements (pre-emption, approval) may restrict any sale.</p>'''
    else:
        body = f'''<p class="pf-p">{e(name)} is not open to Backers. A company opens only when a shareholder plans to sell or the company plans to raise.</p>
  <p class="pf-p">Back the market instead: your intention joins a pool, passed to the local partner once it reaches critical mass.</p>
  <a class="btn navy wide" data-pool href="{pool_href}">{pool_txt}</a>
  {pool2}
  <label class="pf-check"><input type="checkbox" data-pref="{e(name)}"> Name {e(name)} as a preferred company (measures demand, promises nothing)</label>'''
    return f'''<section class="card pf-card pf-invest">
  <h2>Invest</h2>
  {body}
  <div class="pf-counters"><div><span class="lbl">{pool_lbl}</span><b>Below threshold</b></div><div><span class="lbl">Backers</span><b>Below threshold</b></div></div>
  <p class="pf-fine">Paid intention · valid for life · movable until its pool is passed on. Investing in non-listed companies carries a risk of losing all the capital invested.</p>
</section>'''

def side_blocks(m):
    name = e(m['c']['name'])
    raw = m['c']['name']
    code = m['code']
    conn = ''.join(f'<div class="pf-kv"><span>{e(x["name"])}</span><span class="{"ok" if x["status"] == "live" else "mut"}">'
                   f'{"Connected" if x["status"] == "live" else "Planned"}</span></div>' for x in CONNECTORS.get(code.upper(), []))
    n = len(m['srcs'])
    return f'''<section class="card pf-card">
  <h2 class="sm">Do you run {name}?</h2>
  <p class="pf-p">Claim this profile to correct data, add your logo and description, or tell Uback about an upcoming round. Claiming never changes the rank.</p>
  <a class="btn navy" href="{form_url('claim', raw)}">Claim this profile</a>
  <a class="pf-more" href="{form_url('upcoming_round', raw)}">Report an upcoming round →</a>
</section>
<section class="card pf-card">
  <h2 class="sm">Are you a shareholder?</h2>
  <p class="pf-p">Considering selling some of your shares? Tell Uback privately. Nothing is published without your consent, and never a price or a volume.</p>
  <a class="btn" href="{form_url('shareholder_sale', raw)}">Tell Uback privately</a>
</section>
<section class="card pf-card">
  <h2 class="sm">What the AI reads</h2>
  <div class="pf-kv"><span>Press &amp; investor announcements</span><span class="ok">{n} source{'s' if n != 1 else ''}</span></div>
  {conn}
  <form class="pf-suggest" action="{FORM}" method="get">
    <input type="hidden" name="type" value="suggest_source"><input type="hidden" name="company" value="{name}">
    <label for="sg-url">Know a useful link about {name}?</label>
    <div class="pf-row nowrap"><input id="sg-url" name="url" type="url" placeholder="https://" required><button class="btn" type="submit">Suggest</button></div>
  </form>
  <p class="pf-fine">Read by the AI at the next edition.</p>
</section>'''

def comparables(m, models):
    """Même pays et même famille, par rang (4 au plus), complétés par les voisins de rang du même pays ;
    société vue seulement en segment mondial : les voisins du segment."""
    c = m['c']
    a = m['prim']
    if a['kind'] == 'country':
        cs = next(x for x in [a['src']])
        pool = [r for r in cs['data']['classement'][:cs['n']] if K.norm(r['nom']) != K.norm(c['name'])]
        fam = m['family']
        same = [r for r in pool if K.family_of(r.get('sous_secteur')) == fam]
        my = m['best'] or 0
        rest = sorted((r for r in pool if r not in same), key=lambda r: (abs(r['rang'] - my) if my else r['rang'], r['rang']))
        pick = (same + rest)[:4]
        title = f"Comparable companies in {e(cs['name'])}"
        full = f'<a class="pf-more" href="{cs["path"]}/">Full {e(cs["name"])} ranking →</a>'
        items = [(r['nom'], r['rang'], r.get('sous_secteur', ''), r.get('valuation_bracket', 'not_estimated')) for r in pick]
    else:
        sd = a['src']
        pool = [r for r in sd['ranked'] if K.norm(r['name']) != K.norm(c['name'])]
        my = a.get('rank') or 0
        pick = sorted(pool, key=lambda r: (abs(r['rank'] - my) if my else r['rank'], r['rank']))[:4]
        title = f"Comparable companies in {e(sd['name'].lower())}"
        full = f'<a class="pf-more" href="/segments/{sd["segment_id"]}/">Full {e(sd["name"].lower())} ranking →</a>'
        items = [(r['name'], r['rank'], f"{r['country']}", r['tranche']) for r in pick]
    if not items:
        return ''
    cards = ''
    for nm, rk, sub, b in items:
        s = K.company_slug(nm, a['code'] if a['kind'] == 'country' else a['sid'])
        cards += (f'<a class="card pf-cmp" href="/company/{s}/"><span class="pf-row sb"><b>{e(nm)}</b><span class="pf-rk sm">#{rk}</span></span>'
                  f'<span class="mut sm">{e(sub)}</span><span class="sm pf-strong">{VB.get(b, "Not estimated")}</span></a>')
    return f'<div class="pf-h"><h2>{title}</h2>{full}</div><div class="pf-cmps">{cards}</div>'

def page_head_extra(m, url, desc):
    c = m['c']
    org = {"@context": "https://schema.org", "@type": "Organization", "name": c['name'], "url": url}
    r = m['row']
    site = m['enr'].get('website') or r.get('site')
    if m['enr'].get('founded') or r.get('creation'):
        org['foundingDate'] = str(m['enr'].get('founded') or r.get('creation'))
    if r.get('ville'):
        org['address'] = {"@type": "PostalAddress", "addressLocality": r['ville']}
        if m['prim']['kind'] == 'country':
            org['address']['addressCountry'] = m['code'].upper()
    if site:
        org['sameAs'] = [site if site.startswith('http') else f'https://{site}']
    crumbs = breadcrumb_items(m)
    bl = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, **({"item": BASE + h} if h else {})} for i, (n, h) in enumerate(crumbs, 1)]}
    robots = '' if m['index'] else '<meta name="robots" content="noindex,follow">\n'
    return (robots + f'<link rel="stylesheet" href="/assets/profile.css?v={PROFILE_V}">\n'
            f'<script type="application/ld+json">{json.dumps(org, ensure_ascii=False)}</script>\n'
            f'<script type="application/ld+json">{json.dumps(bl, ensure_ascii=False)}</script>\n'
            '<!-- Généré par tools/build_companies.py : ne pas modifier à la main. -->')

def breadcrumb_items(m):
    code = m['code']
    out = [('Uback', '/')]
    out.append((country_name(code), country_url(code)))
    if m['family']:
        out.append((m['family'], f"/sectors/{FAMILY_PAGES[m['family']]}/" if m['family'] in FAMILY_PAGES else None))
    out.append((m['c']['name'], f"/company/{m['c']['slug']}/"))
    return out

def build_company(m, models, investors):
    c = m['c']
    name, slug = c['name'], c['slug']
    url = f'{BASE}/company/{slug}/'
    r, prim, code = m['row'], m['prim'], m['code']
    cname = country_name(code)
    # ---- en-tête
    chips = '<span class="chip ok">Active</span>'
    if m['best']:
        chips += f'<span class="chip gold">#{m["best"]} in {e(cname)}</span>'
    elif m['sr']:
        chips += f'<span class="chip gold">#{m["sr"][0]["rank"]} worldwide · {e(m["sr"][0]["src"]["name"])}</span>'
    elif prim['list'] == 'radar':
        where = e(prim['src']['name']) if prim['kind'] == 'segment' else e(cname)
        chips += f'<span class="chip">On the {where} Radar · not ranked</span>'
    elif prim['list'] == 'born':
        chips += f'<span class="chip">Born in {e(cname)}, based elsewhere</span>'
    for x in c['apps']:
        o = (x['row'].get('acces') if x['kind'] == 'country' else (x['row'].get('open_to_backers') or {}).get('type'))
        if o in OPEN_TXT:
            chips += f'<span class="chip navy">Open to Backers · {OPEN_TXT[o][0]}</span>'
            break
    one = m['enr'].get('one_liner') or (m['subname'][:1].upper() + m['subname'][1:] if m['subname'] else '')
    fam_href = f"/sectors/{FAMILY_PAGES[m['family']]}/" if m['family'] in FAMILY_PAGES else None
    sub_href = f"/segments/{prim['sid']}/" if prim['kind'] == 'segment' else prim['src']['path'] + '/'
    path = ''
    if m['family']:
        path = (link(fam_href, e(m['family']), 'chip') if fam_href else f'<span class="chip">{e(m["family"])}</span>')
        if m['subname']:
            path += f'<span class="mut">›</span><a class="chip" href="{sub_href}">{e(m["subname"])}</a>'
    facts = []
    founded = m['enr'].get('founded') or r.get('creation')
    if founded:
        facts.append(('Founded', str(founded)))
    hq = r.get('ville') or (r.get('lieu') if prim['list'] == 'born' else '') or (r.get('country') if prim['kind'] == 'segment' else '')
    if hq:
        facts.append(('HQ', hq))
    if r.get('leve_cumule'):
        facts.append(('Raised', r['leve_cumule']))
    last = m['rounds'][0] if m['rounds'] else None
    if last and (last['label'] or last['date']):
        facts.append(('Last round', ' · '.join(p for p in (last['label'], ym(last['date'])) if p)))
    note = r.get('note') or ''
    if re.search(r'licen[cs]', note, re.I):
        facts.append(('Licence', note.rstrip('.')))
    facts_html = ''.join(f'<div{" class=\"full\"" if k in ("Licence", "HQ") and len(v) > 28 else ""}><span class="lbl">{k}</span><b>{e(v)}</b></div>'
                         for k, v in facts)
    # ---- bande « trois pays »
    ctry = m['enr'].get('countries') or {}
    band = []
    if prim['kind'] == 'country':
        band.append(('Country of origin', country_name(ctry.get('origin') or code), 'Listed in the ' + cname + ' ranking' if prim['list'] == 'ranked'
                     else ('On the ' + cname + ' Radar' if prim['list'] == 'radar' else 'Born here, based elsewhere')))
    if ctry.get('operations'):
        band.append(('Operations', ' · '.join(country_name(x) for x in ctry['operations']), 'Decides the ranking and the partner'))
    elif prim['kind'] == 'segment':
        band.append(('Operations', r.get('country', ''), 'Country of main operations'))
    if ctry.get('investable_entity'):
        band.append(('Where would you invest?', f"{ctry['investable_entity']} · {country_name(ctry.get('legal_seat') or code)}",
                     'Shares under the law of the legal seat'))
    elif r.get('juridiction'):
        band.append(('Where would you invest?', r['juridiction'], 'Jurisdiction as cited by the ranking'))
    elif prim['list'] == 'born' and r.get('lieu'):
        band.append(('Based', r['lieu'], ''))
    band_html = ''
    if len(band) >= 2:
        band_html = '<section class="card pf-band">' + ''.join(
            f'<div><span class="lbl">{k}</span><b>{e(v)}</b>{f"<span class=\"mut sm\">{e(s)}</span>" if s else ""}</div>' for k, v, s in band) + '</section>'
    # ---- Radar : pourquoi pas classée
    why_not = ''
    if not m['ranked']:
        key = prim['code'] if prim['kind'] == 'country' else prim['sid']
        nxt = geo.next_date(key)
        where = f"{prim['src']['name']}" + (' worldwide' if prim['kind'] == 'segment' else '')
        why_not = f'''<section class="card pf-card">
  <div class="pf-h"><h2>Why {e(name)} is not ranked yet</h2><a class="pf-more" href="{GM}">How the Radar works →</a></div>
  <p class="pf-p">The Radar lists every known eligible company, sorted by date of last round, with no AI judgement. {e(name)} enters the ranking once its public data is sufficient for the AI to estimate it.{f" Next {e(where)} edition: {format_date_short(nxt, 'en')}." if nxt else ''}</p>
</section>''' if prim['list'] == 'radar' else f'''<section class="card pf-card">
  <div class="pf-h"><h2>Born in {e(cname)}, based elsewhere</h2></div>
  <p class="pf-p">{e(name)} is listed by the {e(cname)} ranking as a company founded by {e(cname)}-linked founders but headquartered abroad: it is not ranked in {e(cname)}.{f" {e(r['lieu'])}." if r.get('lieu') else ''}</p>
</section>'''
    # ---- investisseurs
    inv_names = []
    for k in c['investors']:
        inv = investors[k]
        inv_names.append(f'<a class="pf-strong" href="/investor/{inv["slug"]}/">{e(inv["name"])}</a>' if inv['page'] else e(inv['name']))
    inv_line = f'<p class="pf-p">Investors in {e(name)}: {" · ".join(inv_names)}</p>' if inv_names else ''
    # ---- sources, pied de fiche
    srcs = ' · '.join(src_link(u) for u in m['srcs'])
    last_upd = max([a['src']['data']['date'] for a in c['apps'] if a['kind'] == 'country'] +
                   [a['src']['published'][:7] for a in c['apps'] if a['kind'] == 'segment'])
    corr_country = code if prim['kind'] == 'country' else 'global'
    title = f'{name} – valuation, ranking and funding | Uback'
    desc = description(m)
    rk_tbl = f'''<section class="card pf-card">
  <div class="pf-h"><h2>Uback rankings</h2><a class="pf-more" href="{GM}">How the AI ranks →</a></div>
  <div class="pf-scroll"><table class="pf-tbl"><thead><tr><th>Ranking</th><th>Tier</th><th>Rank</th><th>Edition</th><th>Next update</th></tr></thead>
  <tbody>{ranking_rows(m)}</tbody></table></div>
  {history(m) if m['ranked'] else ''}
</section>'''
    crumbs = ''.join((f'<a href="{h}">{e(n)}</a>' if h and i < 3 else f'<span{" aria-current=\"page\"" if i == 3 else ""}>{e(n)}</span>')
                     + ('<span aria-hidden="true">›</span>' if i < 3 else '') for i, (n, h) in enumerate(breadcrumb_items(m)))
    if len(breadcrumb_items(m)) == 3:
        crumbs = ''.join((f'<a href="{h}">{e(n)}</a>' if h and i < 2 else f'<span>{e(n)}</span>') + ('<span aria-hidden="true">›</span>' if i < 2 else '')
                         for i, (n, h) in enumerate(breadcrumb_items(m)))
    cmp = comparables(m, models)
    page = page_top(title, desc, url, f'{BASE}/assets/og-image.png', '',
                    [('/#countries', 'Rankings'), (GM, 'Method'), ('/calendar/', 'Calendar'), (GI, 'Invest')],
                    'Follow the rankings', '/#follow', page_head_extra(m, url, desc), search_field=True) + f'''
<div class="wrap pf">
  <nav class="pf-crumbs" aria-label="Breadcrumb">{crumbs}</nav>
  <section class="pf-top">
    <div class="pf-ini" aria-hidden="true">{e(name[:1].upper())}</div>
    <div class="pf-id">
      <div class="pf-row"><h1>{e(name)}</h1>{chips}</div>
      {f'<p class="pf-one">{e(one)}</p>' if one else ''}
      {f'<div class="pf-row pf-path">{path}</div>' if path else ''}
    </div>
    {f'<div class="pf-facts">{facts_html}</div>' if facts else ''}
  </section>
  {band_html}
  <div class="pf-grid">
    <div class="pf-main">
      {rk_tbl if m['ranked'] else why_not}
      {valuation_block(m) if m['ranked'] else ''}
      {funding_block(m, investors)}
      {rk_tbl if not m['ranked'] else ''}
      {ai_block(m)}
      {analyses_block(m)}
    </div>
    <aside class="pf-side">
      {invest_block(m)}
      {side_blocks(m)}
    </aside>
  </div>
  {f'<section class="pf-sec">{cmp}{inv_line}</section>' if cmp or inv_line else ''}
  <section class="pf-foot">
    {f'<p><b>Sources.</b> {srcs}</p>' if srcs else ''}
    <p class="pf-row"><span>Last updated: {ym(last_upd)}</span><a href="{GC}?company={quote(name)}&amp;country={corr_country}">Report an error</a></p>
    <p>Uback is a content publisher. It provides no investment advice, receives no mandate and takes part in no transaction. Rankings, ranges and brackets are editorial estimates produced by AI, purely indicative.</p>
  </section>
</div>
''' + page_bottom(f'<script>{PROFILE_JS}</script>\n')
    check_page(page, m)
    out = os.path.join(ROOT, 'company', slug)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
    return last_upd

def description(m):
    name, cname = m['c']['name'], country_name(m['code'])
    last = m['rounds'][0] if m['rounds'] else None
    lr = (' Last round: ' + ' · '.join(p for p in (last['label'], last['amount'], ym(last['date'])) if p) + '.') if last else ''
    v = m['val']
    if m['best'] and v and v['bracket'] != 'not_estimated':
        return (f"{name} is #{m['best']} in Uback’s {cname} ranking of funded startups by AI-estimated valuation "
                f"(≈ {money2(v['central'], 'en')}, {VB[v['bracket']]}).{lr} Funding history, investors and sources.")
    if m['sr'] and v:
        return (f"{name} is #{m['sr'][0]['rank']} worldwide in Uback’s {m['sr'][0]['src']['name'].lower()} ranking by AI-estimated "
                f"valuation (≈ {money2(v['central'], 'en')}, {VB[v['bracket']]}).{lr} Funding history, investors and sources.")
    if m['best']:
        return f"{name} is #{m['best']} in Uback’s {cname} ranking of funded startups.{lr} Funding history, investors and sources."
    where = m['prim']['src']['name'] if m['prim']['kind'] == 'segment' else cname
    return f"{name} ({m['sub']}) is on Uback’s {where} Radar of funded startups.{lr} Funding history, investors and sources."

# ---------------------------------------------------------------- contrôles
_RAW_NUM = re.compile(r'\d{7,}')

def check_page(page, m):
    for f in INTERNAL:
        if f in page:
            raise CheckError(f"{m['c']['name']} : champ interne « {f} » présent dans la fiche")
    for a in m['c']['apps']:
        ni = a['row'].get('note_internal')
        if ni and ni in page:
            raise CheckError(f"{m['c']['name']} : note_internal présente dans la fiche")
    visible = re.sub(r'<script.*?</script>', '', page, flags=re.S)
    visible = re.sub(r'<[^>]+>', ' ', visible)
    if '[' in visible or ']' in visible:
        i = visible.find('[') if '[' in visible else visible.find(']')
        raise CheckError(f"{m['c']['name']} : crochet dans le texte de la fiche : …{visible[max(0, i - 40):i + 40]}…")
    if _RAW_NUM.search(visible):
        raise CheckError(f"{m['c']['name']} : nombre brut (valeur interne non arrondie ?) : {_RAW_NUM.search(visible).group(0)}")
    # tranche de la fiche = tranche de la page de classement (fichier de référence, écrit par tools/build_site.py)
    v = m['val']
    if v and v['kind'] == 'country':
        a = v['app']
        ref = json.load(open(os.path.join(ROOT, a['src']['file']), encoding='utf-8'))
        rr = next(x for x in ref['classement'] if x['nom'] == a['row']['nom'])
        if rr.get('valuation_bracket', 'not_estimated') != v['bracket']:
            raise CheckError(f"{m['c']['name']} : tranche {v['bracket']} ≠ {rr.get('valuation_bracket')} (page de classement)")
    elif v and v['kind'] == 'segment':
        if v['bracket'] != BRACKETS[valuation.bracket_index(v['app']['row']['estimate_usd'])]:
            raise CheckError(f"{m['c']['name']} : tranche incohérente avec le segment")

def check_visible_brackets(page, what):
    visible = re.sub(r'<script.*?</script>', '', page, flags=re.S)
    visible = re.sub(r'<[^>]+>', ' ', visible)
    if '[' in visible or ']' in visible:
        raise CheckError(f'{what} : crochet dans le texte')

# ---------------------------------------------------------------- pages investisseur
def inv_country(inv, models):
    from collections import Counter
    cnt = Counter(models[k]['code'] for k in inv['companies'])
    return cnt.most_common(1)[0][0] if cnt else ''

def build_investor(inv, models, investors):
    name, slug = inv['name'], inv['slug']
    url = f'{BASE}/investor/{slug}/'
    ms = [models[k] for k in inv['companies']]
    ranked = sorted([m for m in ms if m['ranked']], key=lambda m: (m['best'] or 999, m['sr'][0]['rank'] if m['sr'] else 999))
    radar = sorted([m for m in ms if not m['ranked']], key=lambda m: date_key(m['rounds'][0]['date'] if m['rounds'] else None), reverse=True)
    codes = sorted({m['code'] for m in ms})
    main = inv_country(inv, models)
    cnames = [country_name(c) for c in codes]
    where = cnames[0] if len(cnames) == 1 else f'{len(cnames)} countries'
    # tour suivi par société (celui où l'investisseur est cité)
    deal_of = {}
    for d in inv['deals']:
        k = d['company']['key']
        if d.get('app'):
            a = d['app']
            if a['kind'] == 'country':
                p = K.parse_round(a['row'].get('derniere_levee'))
                deal_of.setdefault(k, (p['date'], ' · '.join(x for x in (p['label'], p['amount'], ym(p['date'])) if x)))
            else:
                lr = a['row'].get('last_equity_round') or {}
                amt = lr.get('amount_label') or (money(lr['amount_usd'], 'en') if lr.get('amount_usd') else '')
                deal_of.setdefault(k, (lr.get('date'), ' · '.join(x for x in (lr.get('type'), amt, ym(lr.get('date'))) if x)))
        else:
            rd = d['round']
            deal_of[k] = (rd.get('date'), ' · '.join(x for x in (rd.get('label'), rd.get('amount_label'), ym(rd.get('date'))) if x))
    rows = ''
    for m in ranked + radar:
        k = m['c']['key']
        if m['best']:
            rk = f'#{m["best"]} {e(country_name(m["code"]))}'
        elif m['sr']:
            rk = f'#{m["sr"][0]["rank"]} {e(m["sr"][0]["src"]["name"])}'
        else:
            rk = 'Radar'
        v = m['val']
        vb = VB[v['bracket']] if v and v['bracket'] != 'not_estimated' else 'Not estimated'
        rows += (f'<tr><td data-l="Company"><a class="pf-strong" href="/company/{m["c"]["slug"]}/">{e(m["c"]["name"])}</a></td>'
                 f'<td data-l="Uback">{rk}</td><td data-l="Sector">{e(m["sub"])}</td><td data-l="Round backed">{e(deal_of.get(k, ("", ""))[1])}</td>'
                 f'<td data-l="Valuation (AI)">{vb}</td></tr>')
    # secteurs, années
    from collections import Counter
    fams = Counter(m['family'] or 'Other' for m in ms)
    mx = max(fams.values())
    bars = ''.join(f'<div class="pf-bar"><span>{e(f)}</span><i style="width:{max(8, round(100 * n / mx))}%"></i><b>{n}</b></div>'
                   for f, n in sorted(fams.items(), key=lambda x: (-x[1], x[0])))
    years = Counter((deal_of.get(m['c']['key'], ('', ''))[0] or '')[:4] for m in ms)
    years.pop('', None)
    ycols = ''
    if years:
        y0, y1 = int(min(years)), int(max(years))
        ym_ = max(years.values())
        ycols = ''.join(f'<div class="pf-yr"><b>{years.get(str(y), 0)}</b><i style="height:{round(56 * years.get(str(y), 0) / ym_)}px"></i><span>{y}</span></div>'
                        for y in range(y0, y1 + 1))
    # co-investisseurs
    co = Counter()
    for k in inv['companies']:
        for other in models[k]['c']['investors']:
            if other != inv['key']:
                co[other] += 1
    co_html = ' · '.join((f'<a href="/investor/{investors[o]["slug"]}/">{e(investors[o]["name"])}</a>' if investors[o]['page'] else e(investors[o]['name']))
                         + (f' <span class="mut sm">×{n}</span>' if n > 1 else '') for o, n in co.most_common(24))
    # investisseurs semblables dans le pays principal
    sim = []
    for o in investors.values():
        if o['key'] == inv['key'] or not o['page']:
            continue
        n = sum(1 for k in o['companies'] if models[k]['code'] == main)
        if n:
            sim.append((n, o))
    sim = sorted(sim, key=lambda x: (-x[0], x[1]['name']))[:3]
    sim_html = ''.join(f'<div class="pf-kv"><a href="/investor/{o["slug"]}/">{e(o["name"])}</a><span class="mut">{n} startup{"s" if n > 1 else ""}</span></div>'
                       for n, o in sim)
    latest = max(((deal_of.get(m['c']['key'], ('', ''))[0] or '', m) for m in ms), key=lambda x: date_key(x[0]))
    info = inv['info'] or {}
    typ = INV_TYPES.get(info.get('type'), '')
    n_rank = len(ranked)
    sentence = (f'Portfolio in {e(" · ".join(cnames)) if len(cnames) <= 3 else e(where)}: {len(ms)} funded startup{"s" if len(ms) > 1 else ""} tracked by Uback, '
                f'{n_rank} of them in a ranking.')
    extra_facts = ' · '.join(x for x in (e(info['hq']) if info.get('hq') else '', src_link(info['website']) if info.get('website') else '') if x)
    live = country_url(main)
    pool = f'{GI}?pool=country&amp;country={main}#opening' if live else f'{GI}#opening'
    pool_txt = f'Declare an interest in {e(startups_of(main)[0])}startups{e(startups_of(main)[1])}' if live else 'Declare an interest'
    srcs = list(dict.fromkeys(u for m in ms for u in m['srcs']))
    doms = ', '.join(sorted({K.domain(u) for u in srcs})[:12])
    title = f'{name} portfolio – {len(ms)} startups | Uback'
    desc = (f"{name}: {len(ms)} funded startups tracked by Uback in {where}, {n_rank} of them in a ranking. "
            f"Portfolio, rounds, AI-estimated valuation brackets and co-investors.")
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": name, "url": url}
    if info.get('website'):
        ld['sameAs'] = [info['website']]
    il = {"@context": "https://schema.org", "@type": "ItemList", "name": f"{name} portfolio on Uback",
          "itemListElement": [{"@type": "ListItem", "position": i, "name": m['c']['name'], "url": f"{BASE}/company/{m['c']['slug']}/"}
                              for i, m in enumerate(ranked + radar, 1)]}
    bl = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Uback", "item": BASE + '/'},
        {"@type": "ListItem", "position": 2, "name": "Investors", "item": BASE + '/investors/'},
        {"@type": "ListItem", "position": 3, "name": name, "item": url}]}
    extra = (('' if inv['index'] else '<meta name="robots" content="noindex,follow">\n')
             + f'<link rel="stylesheet" href="/assets/profile.css?v={PROFILE_V}">\n'
             + ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in (ld, il, bl))
             + '<!-- Généré par tools/build_companies.py : ne pas modifier à la main. -->')
    page = page_top(title, desc, url, f'{BASE}/assets/og-image.png', '',
                    [('/#countries', 'Rankings'), (GM, 'Method'), ('/calendar/', 'Calendar'), (GI, 'Invest')],
                    'Follow the rankings', '/#follow', extra, search_field=True) + f'''
<div class="wrap pf">
  <nav class="pf-crumbs" aria-label="Breadcrumb"><a href="/">Uback</a><span aria-hidden="true">›</span><a href="/investors/">Investors</a><span aria-hidden="true">›</span><span aria-current="page">{e(name)}</span></nav>
  <section class="pf-top">
    <div class="pf-ini" aria-hidden="true">{e(name[:1].upper())}</div>
    <div class="pf-id">
      <div class="pf-row"><h1>{e(name)}</h1>{f'<span class="chip">{typ}</span>' if typ else ''}</div>
      <p class="pf-one">{sentence}</p>
      {f'<p class="mut sm">{extra_facts}</p>' if extra_facts else ''}
    </div>
  </section>
  <div class="pf-stats">
    <div class="card"><span class="lbl">Portfolio on Uback</span><b>{len(ms)}</b><span class="mut sm">startups, {len(codes)} countr{'ies' if len(codes) > 1 else 'y'}</span></div>
    <div class="card"><span class="lbl">In a ranking</span><b>{n_rank}</b><span class="mut sm">ranked by AI-estimated valuation</span></div>
    <div class="card"><span class="lbl">On the Radar</span><b>{len(radar)}</b><span class="mut sm">eligible, not ranked</span></div>
    <div class="card"><span class="lbl">Latest deal tracked</span><b class="sm2">{ym(latest[0]) or '—'}</b><span class="mut sm">{e(latest[1]['c']['name'])}</span></div>
  </div>
  <div class="pf-grid">
    <div class="pf-main">
      <section class="card pf-card">
        <div class="pf-h"><h2>Portfolio on Uback</h2><span class="mut sm">Sorted by Uback rank, then Radar by last round</span></div>
        <div class="pf-scroll"><table class="pf-tbl"><thead><tr><th>Company</th><th>Uback</th><th>Sector</th><th>Round backed</th><th>Valuation (AI)</th></tr></thead>
        <tbody>{rows}</tbody></table></div>
        <p class="pf-fine">Only startups that meet Uback’s eligibility rules are shown. Amounts are round sizes, not the fund’s share. Rounds as reported by public sources.</p>
      </section>
      <div class="pf-two">
        <section class="card pf-card"><h2 class="sm">By sector</h2>{bars}</section>
        {f'<section class="card pf-card"><h2 class="sm">Deals tracked per year</h2><div class="pf-yrs">{ycols}</div></section>' if ycols else ''}
      </div>
      {f'<section class="card pf-card"><h2 class="sm">Co-investors</h2><p class="pf-p">{co_html}</p><p class="pf-fine">Investors that joined the same rounds, as reported by public sources.</p></section>' if co_html else ''}
    </div>
    <aside class="pf-side">
      <section class="card pf-card">
        <h2 class="sm">Do you manage this fund?</h2>
        <p class="pf-p">Claim this page to complete your portfolio, add your thesis and report new deals. Claiming never changes any rank.</p>
        <a class="btn navy" href="{form_url('investor_claim', investor=name)}">Claim this page</a>
      </section>
      <section class="card pf-card">
        <h2 class="sm">Considering a partial exit?</h2>
        <p class="pf-p">Tell Uback privately which portfolio company you would sell shares in. Backers interested in that market are pooled for you. Never a price, never a volume in public.</p>
        <a class="btn" href="{form_url('fund_partial_exit', investor=name)}">Tell Uback privately</a>
      </section>
      <section class="card pf-card pf-invest">
        <h2 class="sm">Invest alongside</h2>
        <p class="pf-p">Back the market this investor backs. Your intention joins a pool, passed to the local partner once it reaches critical mass.</p>
        <a class="btn navy wide" href="{pool}">{pool_txt}</a>
      </section>
      {f'<section class="card pf-card"><h2 class="sm">Similar investors in {e(country_name(main))}</h2>{sim_html}<a class="pf-more" href="/investors/#{main}">All investors in {e(country_name(main))} →</a></section>' if sim_html else ''}
    </aside>
  </div>
  <section class="pf-foot">
    {f'<p><b>Sources.</b> {e(doms)}, as cited on each company’s profile.</p>' if doms else ''}
    <p class="pf-row"><span>Last updated: {ym(max(K_last(m) for m in ms))}</span><a href="{form_url('missing_deal', investor=name)}">Report a missing deal</a><a href="{GC}?company={quote(name)}&amp;country=global">Report an error</a></p>
    <p>Uback is a content publisher. It provides no investment advice, receives no mandate and takes part in no transaction.</p>
  </section>
</div>
''' + page_bottom()
    check_visible_brackets(page, name)
    for f in INTERNAL:
        if f in page:
            raise CheckError(f'{name} : champ interne « {f} »')
    out = os.path.join(ROOT, 'investor', slug)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
    return max(K_last(m) for m in ms)

def K_last(m):
    return max([a['src']['data']['date'] for a in m['c']['apps'] if a['kind'] == 'country'] +
               [a['src']['published'][:7] for a in m['c']['apps'] if a['kind'] == 'segment'])

def build_directory(investors, models):
    by = {}
    for inv in investors.values():
        if not inv['page']:
            continue
        for k in inv['companies']:
            by.setdefault(models[k]['code'], {}).setdefault(inv['key'], set()).add(k)
    secs = ''
    nav = []
    for code in sorted(by, key=lambda c: country_name(c)):
        items = sorted(by[code].items(), key=lambda x: investors[x[0]]['name'].lower())
        nav.append(f'<a href="#{code}">{e(country_name(code))} <span class="mut">{len(items)}</span></a>')
        lis = ''.join(f'<li><a href="/investor/{investors[k]["slug"]}/">{e(investors[k]["name"])}</a>'
                      f'<span class="mut sm">{len(v)} in {e(country_name(code))} · {len(investors[k]["companies"])} in total</span></li>' for k, v in items)
        secs += f'<section class="pf-dir" id="{code}"><h2>{e(country_name(code))}</h2><ul>{lis}</ul></section>'
    n = sum(1 for i in investors.values() if i['page'])
    title = 'Startup investors by country – portfolios tracked by Uback | Uback'
    desc = f'{n} investors in the startups ranked or tracked by Uback, by country: venture capital funds, corporates, development finance institutions. Portfolios, rounds and co-investors.'
    page = page_top(title, desc, f'{BASE}/investors/', f'{BASE}/assets/og-image.png', '',
                    [('/#countries', 'Rankings'), (GM, 'Method'), ('/calendar/', 'Calendar'), (GI, 'Invest')],
                    'Follow the rankings', '/#follow',
                    f'<link rel="stylesheet" href="/assets/profile.css?v={PROFILE_V}">\n<!-- Généré par tools/build_companies.py : ne pas modifier à la main. -->', search_field=True) + f'''
<div class="wrap pf">
  <nav class="pf-crumbs" aria-label="Breadcrumb"><a href="/">Uback</a><span aria-hidden="true">›</span><span aria-current="page">Investors</span></nav>
  <div class="kicker">Investors</div>
  <h1 class="pf-h1">Startup investors, by country</h1>
  <p class="pf-one">{n} investors that appear in at least two startups ranked or tracked by Uback. Listed by the country of the startups they back, then alphabetically.</p>
  <nav class="pf-dirnav" aria-label="Countries">{''.join(nav)}</nav>
  {secs}
  <p class="pf-fine">Rounds as reported by public sources and cited in Uback’s rankings. An investor gets a page from two startups tracked by Uback. <a href="{form_url('missing_deal')}">Report a missing deal</a></p>
</div>
''' + page_bottom()
    os.makedirs(os.path.join(ROOT, 'investors'), exist_ok=True)
    open(os.path.join(ROOT, 'investors', 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)

# ---------------------------------------------------------------- formulaire des fiches (Web3Forms)
F_TYPES = [('claim', 'Claim a company profile'), ('upcoming_round', 'Report an upcoming round'),
           ('shareholder_sale', 'Tell Uback privately: shareholder considering a sale'), ('suggest_source', 'Suggest a source'),
           ('analysis', 'Publish an independent analysis'), ('fund_partial_exit', 'Fund considering a partial exit'),
           ('investor_claim', 'Claim an investor page'), ('missing_deal', 'Report a missing deal')]

def build_form():
    T = 'claim upcoming_round shareholder_sale suggest_source analysis'
    I = 'fund_partial_exit investor_claim missing_deal'
    req = ' <span class="req" aria-hidden="true">*</span>'
    fields = f'''
  <div data-t="{T} missing_deal"><label for="f-company">Company<span data-star>{req}</span></label><input id="f-company" name="company" type="text" autocomplete="organization"></div>
  <div data-t="{I}"><label for="f-investor">Investor (fund)<span data-star>{req}</span></label><input id="f-investor" name="investor" type="text"></div>
  <div data-t="fund_partial_exit" data-req><label for="f-portfolio">Portfolio company concerned{req}</label><input id="f-portfolio" name="portfolio" type="text"></div>
  <div data-t="suggest_source missing_deal" data-req><label for="f-url">Link (URL){req}</label><input id="f-url" name="url" type="url" placeholder="https://"></div>
  <div data-t="missing_deal"><label for="f-round">Round (type, amount, date)</label><input id="f-round" name="round" type="text"></div>
  <div data-t="upcoming_round" data-req><label for="f-timing">Expected timing{req}</label><select id="f-timing" name="timing"><option value="">Choose…</option><option>Within 3 months</option><option>3 to 6 months</option><option>6 to 12 months</option></select></div>
  <div data-t="shareholder_sale" data-req><label for="f-holder">You are{req}</label><select id="f-holder" name="holder"><option value="">Choose…</option><option>Founder</option><option>Employee</option><option>Business angel</option><option>Fund</option><option>Other shareholder</option></select></div>
  <div data-t="analysis" data-req><label for="f-angle">Angle{req}</label><select id="f-angle" name="angle"><option value="">Choose…</option><option>Valuation</option><option>Versus competitors</option><option>Who should acquire it</option></select></div>
  <div data-t="analysis" data-req><label for="f-title">Title of the analysis{req}</label><input id="f-title" name="title" type="text"></div>
  <div data-t="analysis" data-req><label for="f-pdf">Link to the PDF{req}</label><input id="f-pdf" name="pdf" type="url" placeholder="https://"><div class="hint">File upload will come later: share a link to the PDF for now.</div></div>
  <div data-t="analysis" data-req><label for="f-coi">Conflict of interest{req}</label><select id="f-coi" name="coi"><option value="">Choose…</option><option>None</option><option>I hold shares in the company or a competitor</option><option>I advise a party</option><option>Other</option></select></div>
  <div data-t="analysis"><label for="f-coi2">Details of the conflict of interest</label><input id="f-coi2" name="coi_details" type="text"></div>
  <div data-t="{T} {I}"><label for="f-name">Name{req}</label><input id="f-name" name="name" type="text" required autocomplete="name"></div>
  <div data-t="analysis" data-req><label for="f-li">LinkedIn profile (URL){req}</label><input id="f-li" name="linkedin" type="url" placeholder="https://www.linkedin.com/in/…"></div>
  <div data-t="claim upcoming_round analysis fund_partial_exit investor_claim" data-req><label for="f-role">Role and organisation{req}</label><input id="f-role" name="role" type="text"></div>
  <div data-t="claim investor_claim"><label for="f-web">Official website</label><input id="f-web" name="website" type="url" placeholder="https://"></div>
  <div data-t="{T} {I}"><label for="f-email">E-mail{req}</label><input id="f-email" name="email" type="email" required autocomplete="email"></div>
  <div data-t="{T} {I}"><label for="f-msg">Message</label><textarea id="f-msg" name="message" maxlength="2000"></textarea><div class="hint">2,000 characters maximum. Never published.</div></div>
  <div data-t="analysis" data-req data-check><label class="consent"><input type="checkbox" name="public_only" value="yes"> My analysis relies on public sources only.</label></div>
  <div data-t="{T} {I}"><label class="consent"><input type="checkbox" name="consent" value="yes" required> I agree that this information may be used to process my request. Nothing is published without my consent.</label></div>'''
    opts = ''.join(f'<option value="{k}">{e(v)}</option>' for k, v in F_TYPES)
    js = '''(function(){
  var f=document.querySelector('form.cform'),t=f.querySelector('#f-type'),q=new URLSearchParams(location.search);
  if(q.get('type'))t.value=q.get('type');
  ['company','investor','url'].forEach(function(k){if(q.get(k))f.querySelector('[name='+k+']').value=q.get(k);});
  function sync(){var v=t.value;document.getElementById('f-h').textContent=t.options[t.selectedIndex].text;
    f.querySelectorAll('[data-t]').forEach(function(d){var on=(' '+d.getAttribute('data-t')+' ').indexOf(' '+v+' ')>=0;d.hidden=!on;
      d.querySelectorAll('input,select,textarea').forEach(function(x){x.disabled=!on;
        if(d.hasAttribute('data-req'))x.required=on;});});
    var star=(v==='missing_deal'||v.indexOf('fund')===0||v==='investor_claim')?'investor':'company';
    f.company.required=star==='company'||v==='missing_deal';f.investor.required=star==='investor';}
  t.addEventListener('change',sync);sync();
  f.addEventListener('submit',function(ev){ev.preventDefault();
    var lines=['Type: '+t.options[t.selectedIndex].text];
    f.querySelectorAll('[data-t]:not([hidden])').forEach(function(d){d.querySelectorAll('input,select,textarea').forEach(function(x){
      var l=(d.querySelector('label')||{}).textContent||x.name;l=l.replace('*','').trim();
      var v=x.type==='checkbox'?(x.checked?'yes':'no'):(x.tagName==='SELECT'?(x.value?x.options[x.selectedIndex].text:''):x.value.trim());
      if(x.type!=='checkbox')lines.push(l+': '+v);else lines.push(l+' '+v);});});
    var who=f.company.value.trim()||f.investor.value.trim();
    window.ubackSend(f,'['+t.value+'] '+who,lines.join('\\n'));});
})();'''
    body = f'''<div class="wrap pf pf-form">
  <nav class="pf-crumbs" aria-label="Breadcrumb"><a href="/">Uback</a><span aria-hidden="true">›</span><span aria-current="page">Profile request</span></nav>
  <h1 class="pf-h1" id="f-h">Profile request</h1>
  <p class="pf-one">Private: nothing you send here is published. Uback replies to every request. Claiming a profile or sharing information never changes a rank.</p>
  {w3f_js('en')}<form class="cform" name="profile" method="POST" action="https://api.web3forms.com/submit" data-w3f="1">
  <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
  <input type="hidden" name="from_name" value="Uback.com">
  <input type="hidden" name="redirect" value="https://uback.com/thank-you.html">
  <input type="hidden" name="subject" value="[Profile] Uback">
  <input type="checkbox" name="botcheck" class="skip" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div><label for="f-type">Request</label><select id="f-type" name="type">{opts}</select></div>{fields}
  <button class="btn navy" type="submit">Send</button>
  </form>
</div>
<script>{js}</script>
'''
    page = page_top('Profile request | Uback', 'Claim a profile, report a round, suggest a source or publish an analysis on Uback.',
                    f'{BASE}{FORM}', f'{BASE}/assets/og-image.png', '',
                    [('/#countries', 'Rankings'), (GM, 'Method'), ('/calendar/', 'Calendar'), (GI, 'Invest')],
                    'Follow the rankings', '/#follow',
                    f'<meta name="robots" content="noindex">\n<link rel="stylesheet" href="/assets/profile.css?v={PROFILE_V}">\n'
                    '<!-- Généré par tools/build_companies.py : ne pas modifier à la main. -->') + body + page_bottom()
    open(os.path.join(ROOT, FORM.lstrip('/')), 'w', encoding='utf-8', newline='\n').write(page)

# ---------------------------------------------------------------- styles et script des fiches
PROFILE_CSS = '''.pf{display:flex;flex-direction:column;gap:24px;padding-top:20px;padding-bottom:56px}
.pf .lbl{display:block;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#5b6472}
.pf .mut{color:#5b6472}.pf .sm{font-size:13px}.pf .ok{color:#166534;font-weight:600}
.pf h2{font-size:22px;color:#1E3A5F;letter-spacing:-.02em;margin:0;line-height:1.25}.pf h2.sm{font-size:18px}
.pf-h1{font-size:clamp(28px,4vw,40px);line-height:1.1;color:#1E3A5F;letter-spacing:-.03em;margin:0}
.pf-crumbs{font-size:13px;color:#5b6472;display:flex;gap:8px;flex-wrap:wrap}.pf-crumbs a{color:#1E3A5F}
.pf-crumbs [aria-current]{color:#1f2937;font-weight:600}
.pf-row{display:flex;align-items:center;gap:10px 12px;flex-wrap:wrap}.pf-row.sb{justify-content:space-between}.pf-row.nowrap{flex-wrap:nowrap}
.pf-top{display:flex;gap:24px;align-items:flex-start;flex-wrap:wrap}
.pf-ini{width:88px;height:88px;border-radius:16px;border:1px solid #e5e9ef;background:#f3f5f8;display:flex;align-items:center;justify-content:center;font-size:34px;font-weight:800;color:#1E3A5F;flex-shrink:0}
.pf-id{flex:1 1 480px;display:flex;flex-direction:column;gap:12px;min-width:0}
.pf-id h1{margin:0;font-size:clamp(30px,4vw,40px);line-height:1.1;color:#1E3A5F;letter-spacing:-.03em;overflow-wrap:anywhere}
.pf-one{margin:0;font-size:18px;color:#374151;max-width:760px}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;padding:5px 10px;border-radius:999px;background:#f3f5f8;color:#1E3A5F;border:1px solid #e5e9ef;text-decoration:none;line-height:1.3}
.chip.ok{background:#e6f4ea;color:#166534;border-color:#cfe8d6}.chip.gold{background:#fbf7ee;color:#7a5a1e;border-color:#ecdcb8}
.chip.navy{background:#1E3A5F;color:#fff;border-color:#1E3A5F}.chip.mid{background:#fff4d6;color:#7c5a00;border-color:#f1e0a8}.chip.low{background:#fdecec;color:#9b1c1c;border-color:#f6caca}
.chip.sm{font-size:12px;padding:3px 8px}
a.chip:hover{border-color:#1E3A5F}
.pf-path{font-size:13px}
.pf-facts{flex:0 1 320px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px 20px;font-size:14px;padding:16px 18px;background:#f8f9fb;border:1px solid #e5e9ef;border-radius:12px}
.pf-facts b{font-weight:600;color:#1f2937;overflow-wrap:anywhere}.pf-facts .full{grid-column:1/-1}
.pf-band{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px!important;padding:20px 24px!important}
.pf-band b{display:block;font-weight:700;color:#1E3A5F;font-size:16px}.pf-band .mut{display:block}
.pf-grid{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:24px;align-items:start}
.pf-main,.pf-side{display:flex;flex-direction:column;gap:24px;min-width:0}
.pf-card{gap:14px!important}
.pf-h{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px}
.pf-p{margin:0;font-size:15px;color:#374151}.pf-fine{margin:0;font-size:12.5px;color:#5b6472}.pf-fine a{text-decoration:underline}
.pf-more{font-size:14px;font-weight:600;color:#1E3A5F}
.pf-strong{font-weight:600;color:#1E3A5F}
.pf-scroll{overflow-x:auto}
.pf-tbl{width:100%;border-collapse:collapse;font-size:14px}
.pf-tbl th{text-align:left;font-size:12px;font-weight:600;color:#5b6472;text-transform:uppercase;letter-spacing:.05em;padding:10px 12px;border-bottom:1px solid #e5e9ef;background:#f8f9fb;white-space:nowrap}
.pf-tbl td{padding:12px;border-bottom:1px solid #e5e9ef;vertical-align:top}
.pf-tbl a{color:#1E3A5F}
.pf-rk{font-weight:800;color:#1E3A5F;font-size:18px}.pf-rk.sm{font-size:15px;color:#9a7432}
.pf-hist{display:flex;align-items:center;gap:8px 14px;font-size:13px;color:#5b6472;flex-wrap:wrap}
.pf-dot{display:inline-flex;align-items:center;gap:6px}.pf-dot i{width:10px;height:10px;border-radius:50%;background:#1E3A5F}
.pf-val{display:flex;align-items:baseline;gap:8px 14px;flex-wrap:wrap}
.pf-big{font-size:34px;font-weight:800;color:#1E3A5F;letter-spacing:-.02em;margin:0}.pf-big.mut{color:#5b6472;font-size:28px}
.pf-range{font-size:15px;font-weight:600;color:#374151}
.pf-scale{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:4px;font-size:11.5px;text-align:center}
.pf-scale i{display:block;height:8px;border-radius:4px;background:#e5e9ef}.pf-scale span{display:block;margin-top:6px;color:#5b6472;line-height:1.25}
.pf-scale .on i{background:#1E3A5F}.pf-scale .on span{color:#1E3A5F;font-weight:700}
.pf-dl{margin:0;display:grid;grid-template-columns:max-content 1fr;gap:8px 16px;font-size:14px}.pf-dl dt{color:#5b6472}.pf-dl dd{margin:0}
.pf-angles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.pf-angle{background:#f3f5f8;border-radius:10px;padding:14px;display:flex;flex-direction:column;gap:2px}.pf-angle b{color:#1E3A5F;font-size:15px}.pf-angle span{font-size:13px;color:#5b6472}
.pf-an{border:1px solid #e5e9ef;border-radius:10px;padding:14px 16px;display:flex;gap:14px;align-items:flex-start;flex-wrap:wrap}
.pf-pdf{width:40px;height:48px;border-radius:6px;background:#fbf7ee;border:1px solid #ecdcb8;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#9a7432;flex-shrink:0}
.pf-an-t{flex:1 1 260px;display:flex;flex-direction:column;gap:4px}.pf-an-t b{color:#1E3A5F}.pf-an-t span{font-size:13px;color:#5b6472}.pf-an-t p{margin:4px 0;font-size:14px}
.pf .btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 18px;border-radius:10px;white-space:normal;text-align:center;line-height:1.25;text-decoration:none}
.pf .btn.navy{background:#1E3A5F;color:#fff}.pf .btn.gold{background:#C8A052;border-color:#C8A052;color:#1E3A5F}.pf .btn.wide{width:100%;box-sizing:border-box}
.pf-invest{border-color:#1E3A5F!important;border-width:1.5px!important}
.pf-open{background:#fbf7ee;border:1px solid #ecdcb8;border-radius:10px;padding:14px;font-size:14px;color:#374151}.pf-open b{color:#1E3A5F}
.pf-check{display:flex;gap:10px;align-items:flex-start;font-size:13px;color:#374151;cursor:pointer}.pf-check input{margin-top:3px;width:16px;height:16px;flex-shrink:0}
.pf-counters{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;font-size:13px}
.pf-counters div{background:#f3f5f8;border-radius:10px;padding:12px}.pf-counters .lbl{font-size:11px}.pf-counters b{color:#1E3A5F}
.pf-kv{display:flex;justify-content:space-between;gap:10px;font-size:14px}.pf-kv a{color:#1E3A5F;font-weight:600}
.pf-suggest{display:flex;flex-direction:column;gap:8px}.pf-suggest label{font-size:13px;font-weight:600;color:#1E3A5F}
.pf-suggest input[type=url]{flex:1;min-width:0;min-height:44px;border:1px solid #d9dee5;border-radius:10px;padding:0 12px;font:inherit;font-size:16px}
.pf-sec{display:flex;flex-direction:column;gap:16px}
.pf-cmps{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}
.pf-cmp{padding:18px!important;gap:6px!important;color:#1f2937;text-decoration:none}.pf-cmp:hover{border-color:#1E3A5F}.pf-cmp b{color:#1E3A5F;font-size:16px}
.pf-foot{border-top:1px solid #e5e9ef;padding-top:20px;display:flex;flex-direction:column;gap:10px;font-size:13px;color:#5b6472}
.pf-foot p{margin:0;overflow-wrap:anywhere}.pf-foot b{color:#1f2937}.pf-foot a{color:#1E3A5F;text-decoration:underline}
.pf-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}
.pf-stats .card{gap:4px;padding:18px}.pf-stats b{font-size:30px;font-weight:800;color:#1E3A5F;line-height:1.1}.pf-stats b.sm2{font-size:22px}
.pf-two{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}
.pf-bar{display:grid;grid-template-columns:minmax(0,9em) 1fr 2em;align-items:center;gap:10px;font-size:13px}
.pf-bar span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.pf-bar i{display:block;height:10px;border-radius:5px;background:#1E3A5F}.pf-bar b{text-align:right;color:#1E3A5F}
.pf-yrs{display:flex;align-items:flex-end;gap:10px;min-height:96px;flex-wrap:wrap}
.pf-yr{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:12px;min-width:36px}.pf-yr i{display:block;width:26px;border-radius:4px 4px 0 0;background:#C8A052;min-height:2px}.pf-yr b{color:#1E3A5F}
.pf-dirnav{display:flex;flex-wrap:wrap;gap:8px}.pf-dirnav a{font-size:14px;font-weight:600;color:#1E3A5F;border:1px solid #e5e9ef;border-radius:999px;padding:6px 12px;text-decoration:none}
.pf-dir ul{list-style:none;margin:12px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:4px 24px}
.pf-dir li{display:flex;flex-direction:column;padding:8px 0;border-bottom:1px solid #e5e9ef}.pf-dir li a{color:#1E3A5F;font-weight:600}
.pf-dir{scroll-margin-top:90px}
.pf-form .cform{display:flex;flex-direction:column;gap:14px;max-width:640px}
.pf-form .cform>div{display:flex;flex-direction:column;gap:6px}
.pf-form label{font-size:14px;font-weight:600;color:#1E3A5F}.pf-form .req{color:#9b1c1c}
.pf-form input[type=text],.pf-form input[type=url],.pf-form input[type=email],.pf-form select,.pf-form textarea{min-height:44px;border:1px solid #d9dee5;border-radius:10px;padding:8px 12px;font:inherit;font-size:16px;background:#fff;box-sizing:border-box;width:100%}
.pf-form textarea{min-height:120px}.pf-form .hint{font-size:12.5px;color:#5b6472}
.pf-form .consent{display:flex;gap:10px;align-items:flex-start;font-weight:500;color:#374151}.pf-form .consent input{margin-top:3px}
.pf-form .form-err{color:#9b1c1c;font-size:14px}
.co-l,.inv-l{color:inherit;text-decoration:none}.co-l:hover,.inv-l:hover{text-decoration:underline;text-underline-offset:3px}
@media (max-width:1023px){.pf-grid{grid-template-columns:minmax(0,1fr)}.pf-stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:639px){.pf-ini{width:56px;height:56px;font-size:24px;border-radius:12px}.pf-top{gap:16px}.pf-id{flex-basis:calc(100% - 72px)}
  .pf-facts{flex:1 1 100%}.pf-one{font-size:16px}.pf-big{font-size:28px}.pf-scale{font-size:10px}
  .pf-tbl{font-size:13px}.pf-tbl thead{display:none}.pf-tbl tr{display:block;padding:10px 0;border-bottom:1px solid #e5e9ef}
  .pf-tbl td{display:flex;gap:10px;padding:3px 0;border:0}.pf-tbl td::before{content:attr(data-l);flex:0 0 7.5em;color:#5b6472;font-size:12px}
  .pf-tbl td:not([data-l])::before{display:none}
  .pf-card{padding:18px!important}}
'''
PROFILE_JS = '''(function(){
  var c=document.querySelector('[data-pref]');if(!c)return;
  var bs=document.querySelectorAll('a[data-pool]');
  bs.forEach(function(b){b.dataset.base=b.getAttribute('href');});
  function upd(){bs.forEach(function(b){var h=b.dataset.base,i=h.indexOf('#'),q=c.checked?'&preferred='+encodeURIComponent(c.getAttribute('data-pref')):'';
    b.setAttribute('href',i>=0?h.slice(0,i)+q+h.slice(i):h+q);});}
  c.addEventListener('change',upd);
})();'''
import hashlib
PROFILE_V = hashlib.sha1(PROFILE_CSS.encode('utf-8')).hexdigest()[:8]

# ---------------------------------------------------------------- sitemaps, index, rapports
def sitemap(path, entries):
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += ''.join(f'  <url><loc>{e(u)}</loc><lastmod>{d}</lastmod></url>\n' for u, d in sorted(entries))
    xml += '</urlset>\n'
    open(os.path.join(ROOT, path), 'w', encoding='utf-8', newline='\n').write(xml)

def report(data, models, investors):
    os.makedirs(os.path.join(TOOLS, 'reports'), exist_ok=True)
    L = ['Fiches société — rapport de tools/build_companies.py', '']
    idx = [m for m in models.values() if m['index']]
    L.append(f'{len(models)} fiches · {len(idx)} indexées · {len(models) - len(idx)} noindex · {len(data["slugs_new"])} nouveaux slugs')
    L += ['', '== Fusions (une fiche, plusieurs classements)']
    for m in sorted(models.values(), key=lambda m: m['c']['name'].lower()):
        if len(m['c']['apps']) > 1:
            where = ', '.join(f"{a['code'] if a['kind'] == 'country' else a['sid']}:{a['list']}" for a in m['c']['apps'])
            names = ' / '.join(m['c']['names'])
            L.append(f"  {m['c']['slug']} ← {names} ({where})")
    L += ['', '== Noms proches non fusionnés (à décider : data/companies/aliases.json)']
    keys = sorted(models)
    norms = {k: K.norm(models[k]['c']['name']) for k in keys}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            na, nb = norms[a], norms[b]
            if na and nb and na != nb and (na.split()[0] == nb.split()[0] and (na.startswith(nb) or nb.startswith(na))
                                         or na.replace(' ', '') == nb.replace(' ', '')):
                L.append(f"  {models[a]['c']['name']}  ~  {models[b]['c']['name']}")
    for title, test in (('sans secteur', lambda m: not m['family']), ('sans date de tour', lambda m: not any(r['date'] for r in m['rounds'])),
                        ('sans source', lambda m: not m['srcs'])):
        bad = sorted(m['c']['name'] for m in models.values() if test(m))
        L += ['', f'== Sociétés {title} ({len(bad)})'] + [f'  {n}' for n in bad]
    L += ['', '== Noindex (Radar ou Born here sous le seuil : un tour daté, deux sources, un secteur)']
    L += [f"  {m['c']['name']} · {len(m['srcs'])} source(s)" for m in sorted(models.values(), key=lambda m: m['c']['name'].lower()) if not m['index']]
    open(os.path.join(TOOLS, 'reports', 'companies.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')

    P = [i for i in investors.values() if i['page']]
    L = ['Investisseurs — rapport de tools/build_companies.py', '',
         f'{len(investors)} noms · {len(P)} pages (≥ {K.INV_PAGE} sociétés) · {sum(i["index"] for i in P)} indexées (≥ {K.INV_INDEX})', '',
         '== Pages']
    L += [f"  {i['slug']} · {len(i['companies'])} · {'' if i['known'] else 'inconnu de data/investors.json · '}{' / '.join(sorted(i['raws']))}"
          for i in sorted(P, key=lambda i: (-len(i['companies']), i['name']))]
    L += ['', '== Noms inconnus de data/investors.json (pour ajout d’alias), avec le nombre de sociétés']
    L += [f"  {i['name']} · {len(i['companies'])}" for i in sorted(investors.values(), key=lambda i: i['name'].lower()) if not i['known']]
    open(os.path.join(TOOLS, 'reports', 'investors.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')

def main():
    data = K.load()
    # ---- slugs : un slug publié ne change jamais
    frozen = data['frozen']
    for c in data['companies']:
        if c['key'] in frozen and frozen[c['key']] != c['slug']:
            raise CheckError(f"{c['name']} : slug publié modifié ({frozen[c['key']]} → {c['slug']})")
    slugs = [c['slug'] for c in data['companies']]
    if len(slugs) != len(set(slugs)):
        raise CheckError('deux fiches ont le même slug')
    models = {c['key']: describe(c) for c in data['companies']}
    investors = data['investors']
    # ---- reconstruction intégrale de company/ et investor/
    for d in ('company', 'investor'):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            shutil.rmtree(p)
    os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)
    old = open(os.path.join(ROOT, 'assets', 'profile.css'), encoding='utf-8').read() if os.path.exists(os.path.join(ROOT, 'assets', 'profile.css')) else ''
    if old != PROFILE_CSS:
        open(os.path.join(ROOT, 'assets', 'profile.css'), 'w', encoding='utf-8', newline='\n').write(PROFILE_CSS)
    search.write_js()
    lastmods = {}
    for k, m in models.items():
        lastmods[k] = build_company(m, models, investors)
    inv_last = {}
    for inv in investors.values():
        if inv['page']:
            inv_last[inv['key']] = build_investor(inv, models, investors)
    build_directory(investors, models)
    build_form()
    # ---- sitemaps (pages indexées seulement)
    sitemap('sitemap-companies.xml', [(f"{BASE}/company/{m['c']['slug']}/", lastmods[k]) for k, m in models.items() if m['index']])
    sitemap('sitemap-investors.xml', [(f"{BASE}/investor/{i['slug']}/", inv_last[i['key']]) for i in investors.values() if i['index']])
    # contrôle : sitemaps ↔ règle d'indexation ↔ balise robots
    sm = open(os.path.join(ROOT, 'sitemap-companies.xml'), encoding='utf-8').read() + open(os.path.join(ROOT, 'sitemap-investors.xml'), encoding='utf-8').read()
    for k, m in models.items():
        u = f"{BASE}/company/{m['c']['slug']}/"
        page = open(os.path.join(ROOT, 'company', m['c']['slug'], 'index.html'), encoding='utf-8').read()
        noindex = 'noindex' in page
        if (u in sm) == noindex or m['index'] == noindex:
            raise CheckError(f"{m['c']['name']} : sitemap / noindex incohérents")
    for i in investors.values():
        if i['page']:
            u = f"{BASE}/investor/{i['slug']}/"
            page = open(os.path.join(ROOT, 'investor', i['slug'], 'index.html'), encoding='utf-8').read()
            if (u in sm) == ('noindex' in page):
                raise CheckError(f"{i['name']} : sitemap / noindex incohérents")
    # ---- index de recherche : startups seulement (les fiches noindex sont trouvables), jamais les investisseurs
    idx = []
    for m in models.values():
        r = m['best'] or (m['sr'][0]['rank'] if m['sr'] else None)
        where = country_name(m['code']) if (m['best'] or not m['sr']) else m['sr'][0]['src']['name']
        idx.append({'n': m['c']['name'], 's': m['c']['slug'], 'c': where, **({'r': r} if r else {})})
    idx.sort(key=lambda x: x['n'].lower())
    open(os.path.join(ROOT, 'assets', 'search-index.json'), 'w', encoding='utf-8', newline='\n').write(
        json.dumps(idx, ensure_ascii=False, separators=(',', ':')) + '\n')
    # ---- table des slugs figée : on ajoute, on ne retire jamais
    if data['slugs_new']:
        frozen = dict(frozen, **data['slugs_new'])
        os.makedirs(K.CO_DIR, exist_ok=True)
        open(K.SLUGS_FILE, 'w', encoding='utf-8', newline='\n').write(json.dumps(dict(sorted(frozen.items())), ensure_ascii=False, indent=1) + '\n')
    report(data, models, investors)
    n_idx = sum(m['index'] for m in models.values())
    P = [i for i in investors.values() if i['page']]
    print(f'ok /company/ · {len(models)} fiches · {n_idx} indexées · {len(models) - n_idx} noindex')
    print(f'ok /investor/ · {len(P)} pages investisseur · {sum(i["index"] for i in P)} indexées · /investors/ · {FORM}')

if __name__ == '__main__':
    main()
