# -*- coding: utf-8 -*-
"""Génère les pages de zone (/regions/<slug>/ : 7 régions et 14 sous-régions) et de collection
(/collections/<slug>/ : Union européenne, UEMOA), à partir de data/geo.json et data/calendar.json.
Même gabarit et même charte que les pages famille (/sectors/<slug>/, tools/build_segments.py).
Aucune page pays n'est créée ici : un pays n'a sa page qu'à sa première édition (statut « live » dans data/geo.json).
Usage : python3 tools/build_regions.py"""
import os, sys, json, html, datetime

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import geo
from build_site import MARKETS, format_date_short, MONTHS
from build_segments import page_top, page_bottom, GM, GI, FORM_MODE
from flags import flag

e = html.escape
RADAR_TXT = 'Fewer than 15 funded startups: their companies appear in this zone’s regional ranking.'
CHINA_ZONES = ('east-asia', 'asia')
OG_IMG = 'https://uback.com/assets/og-image.png'

def plural(n, word):
    return f'{n} {word if n == 1 else ("countries" if word == "country" else word + "s")}'

LANGS = {'en': 'English', 'fr': 'French'}

def languages(code):
    """Langues du classement d'un pays (versions dans MARKETS, version principale d'abord) : « In English & French »."""
    vs = sorted((m for m in MARKETS if m['code'] == code), key=lambda m: not m['default'])
    return 'In ' + ' & '.join(LANGS[m['lang']] for m in vs)

def country_dates(code):
    """Dates d'un pays en ligne : dernière édition (donnée du classement) et prochaine date du calendrier."""
    m = next(v for v in MARKETS if v['code'] == code and v['default'])
    d = json.load(open(os.path.join(ROOT, code, 'data', m['data']), encoding='utf-8'))
    pub = d.get('snapshot_date') or d['date']
    return format_date_short(pub, 'en'), format_date_short(geo.next_date(code), 'en')

def cal_txt(slug):
    """Dates théoriques d'un classement régional (deux par an) : « 4 January and 4 July »."""
    ds = sorted(geo.cal_dates(slug))
    return ' and '.join(f'{d} {MONTHS["en"][m - 1]}' for m, d in ds)

def switcher(current):
    """Sélecteur de zone : régions, leurs sous-régions, puis les collections."""
    items = ''
    for r in geo.REGIONS:
        for z in [r] + geo.subzones(r['slug']):
            cur = ' aria-current="page"' if z['slug'] == current else ''
            cls = ' class="seg"' if z['parent'] else ''
            items += f'<a{cls} href="/regions/{z["slug"]}/"{cur}>{e(z["name"]["en"])}</a>'
    items += '<span class="grp">Collections</span>'
    for k in geo.GEO['collections']:
        cur = ' aria-current="page"' if k['slug'] == current else ''
        items += f'<a class="seg" href="/collections/{k["slug"]}/"{cur}>{e(k["name"]["en"])}</a>'
    label = (geo.ZONES.get(current) or geo.COLLECTIONS[current])['name']['en']
    return (f'<details class="mkt"><summary class="market" aria-label="Change zone">{e(label)}</summary>'
            f'<div class="menu zones">{items}<hr><a href="/#countries">All country rankings</a><a href="/calendar/">Calendar</a></div></details>')

def counts(slug):
    ranked = geo.countries_of(slug, geo.RANKED)
    radar = geo.countries_of(slug, ('radar',))
    return ranked, radar

def country_cards(ranked):
    live = ''
    soon = ''
    for c in geo.sort_ranked(ranked):
        if c['status'] == 'live':
            pub, nxt = country_dates(c['code'])
            live += (f'<a class="card fam-seg" href="{e(c["url"])}"><span class="k">Live ranking</span>'
                     f'<h3>{flag(c["code"], "flag-s")}{e(geo.name(c))}</h3>'
                     f'<p>Published {pub} · Next scheduled update {nxt}<br>{e(languages(c["code"]))}</p></a>')
        else:
            soon += (f'<span class="pill soon" tabindex="0" aria-disabled="true">{e(geo.name(c))}'
                     f'<span class="tip" role="tooltip">Coming soon</span></span>')
    out = f'<div class="grid4">{live}</div>' if live else ''
    if soon:
        out += f'<div class="pills-wrap zone-soon">{soon}</div>'
    return out or '<p class="list-empty">No ranked country in this zone yet.</p>'

def build(slug, kind):
    """kind : 'region', 'subregion' ou 'collection'."""
    z = geo.COLLECTIONS[slug] if kind == 'collection' else geo.ZONES[slug]
    name = z['name']['en']
    ranked, radar = counts(slug)
    live = [c for c in ranked if c['status'] == 'live']
    base = 'collections' if kind == 'collection' else 'regions'
    url = f'https://uback.com/{base}/{slug}/'
    out = os.path.join(ROOT, base, slug)
    os.makedirs(out, exist_ok=True)

    # fil d'Ariane : Home › Région › Sous-région (une collection n'est jamais un parent : Home › Collections › Nom)
    if kind == 'collection':
        trail = [('Home', '/'), ('Collections', None), (name, None)]
    else:
        trail = [('Home', '/')] + [(geo.ZONES[s]['name']['en'], f'/regions/{s}/' if s != slug else None) for s in geo.lineage(slug)]
    crumbs = ' <span class="sep" aria-hidden="true">›</span> '.join(
        f'<a href="{h}">{e(t)}</a>' if h else f'<span aria-current="page">{e(t)}</span>' if i == len(trail) - 1 else f'<span>{e(t)}</span>'
        for i, (t, h) in enumerate(trail))
    crumbs_ld = [{"@type": "ListItem", "position": i, "name": t, **({"item": "https://uback.com" + h} if h else {})}
                 for i, (t, h) in enumerate(trail, 1)]
    crumbs_ld[-1]['item'] = url

    counted = plural(len(ranked), 'country') + ' ranked'
    if radar:
        counted += f' · {len(radar)} more tracked in the regional radar'
    lead = z['pitch']['en'] if kind == 'collection' else counted
    title = f'Startup rankings in {name} · Uback'
    live_txt = f' ({", ".join(geo.name(c) for c in live)} live)' if live else ''
    desc = (f'Startup rankings in {name}: {plural(len(ranked), "country")} ranked by AI-estimated valuation{live_txt}'
            + (f', {len(radar)} more in the regional radar' if radar else '')
            + ('. Regional ranking twice a year.' if slug in geo.REGIONAL else '.'))

    # sous-régions (pages de région seulement)
    subs = ''
    if kind == 'region' and geo.subzones(slug):
        cards = ''
        for s in geo.subzones(slug):
            rk, rd = counts(s['slug'])
            lv = [c for c in rk if c['status'] == 'live']
            p = ('Live: ' + ', '.join(geo.name(c) for c in geo.sort_ranked(lv))) if lv else 'No live ranking yet'
            cards += (f'<a class="card fam-seg" href="/regions/{s["slug"]}/"><span class="k">{len(rk)} ranked · {len(rd)} on radar</span>'
                      f'<h3>{e(s["name"]["en"])}</h3><p>{e(p)}</p></a>')
        subs = f'''
<section id="subregions" style="padding-top:8px">
  <div class="wrap">
    <div class="sec-head"><h2>Sub-regions</h2></div>
    <div class="grid4">{cards}</div>
  </div>
</section>
'''

    # classement régional (zones et collections listées dans data/calendar.json › regional_rankings)
    regional = ''
    if slug in geo.REGIONAL:
        regional = (f'<div class="box line" id="regional"><h3>Regional ranking · Coming soon</h3>'
                    f'<p>One ranking across the {plural(geo.REGIONAL[slug]["n"], "country")} of {e(name)}, ranked and radar alike, '
                    f'published twice a year. Theoretical dates: {cal_txt(slug)}, every year '
                    f'(<a href="/calendar/">see the calendar</a>).</p></div>')
    radar_box = ''
    if radar:
        pills = ''.join(f'<span class="pill radar">{e(geo.name(c))}</span>' for c in sorted(radar, key=lambda c: geo.name(c)))
        radar_box = (f'<div class="box line" id="radar"><h3>Also tracked (regional radar) <span class="cnt">{len(radar)}</span></h3>'
                     f'<p>{RADAR_TXT}</p><div class="pills-wrap">{pills}</div></div>')
    china = ''
    if slug in CHINA_ZONES:
        china = ('<p class="notin"><b>China — analysis only.</b> Chinese companies are analysed as valuation comparables and competitors, '
                 'never ranked. <a href="/faq/#china">Why?</a></p>')

    reg_nav = [('#countries', 'Countries')] + ([('#radar', 'Radar')] if radar else []) + [(GM, 'Method')]
    if subs:
        reg_nav.insert(0, ('#subregions', 'Sub-regions'))
    jsonld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": title, "description": desc, "url": url},
        {"@type": "BreadcrumbList", "itemListElement": crumbs_ld}]}
    page = page_top(title, desc, url, OG_IMG, switcher(slug), reg_nav, 'Follow this zone', '#follow',
                    f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n'
                    f'<!-- Généré par tools/build_regions.py à partir de data/geo.json et data/calendar.json : ne pas modifier à la main. -->',
                    f'{GI}?pool=country#opening') + f'''
<div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
  <div class="hero">
    <div>
      <div class="kicker">{'Collection' if kind == 'collection' else 'Startup rankings by zone'}</div>
      <h1>{e(name)}</h1>
      <p class="lead">{e(lead)}</p>
      <div class="meta">
        {'<span class="tag cad">' + e(counted) + '</span>' if kind == 'collection' else ''}
        <span class="tag cad">Country rankings: quarterly</span>
        {'<span class="tag cad">Regional ranking: twice a year</span>' if slug in geo.REGIONAL else ''}
        <a href="/calendar/">Calendar</a><span>·</span><a href="{GM}">Published method</a>
      </div>
      {china}
    </div>
    <div class="panel">
      <div class="k">{e(name)} at a glance</div>
      <div class="stats">
        <div><b>{len(live)}</b><span>live {'ranking' if len(live) == 1 else 'rankings'}</span></div>
        <div><b>{len(ranked) - len(live)}</b><span>coming soon</span></div>
        <div><b>{len(radar)}</b><span>on the regional radar</span></div>
        <div><b>{len(geo.subzones(slug)) if kind == 'region' else ('1' if slug in geo.REGIONAL else '0')}</b><span>{'sub-regions' if kind == 'region' else 'regional ranking'}</span></div>
      </div>
      <div class="fine">Counts from Uback’s country list, recomputed every year and published on 31 December. <a href="/faq/#countries" style="color:inherit;text-decoration:underline">How countries are chosen</a>.</div>
    </div>
  </div>
</div>
{subs}
<section id="countries" style="padding-top:8px">
  <div class="wrap">
    <div class="sec-head"><h2>Ranked countries</h2><span class="sub">Quarterly national rankings. Live first, then by size of the startup pool.</span></div>
    {country_cards(ranked)}
  </div>
</section>

<section class="soft" id="more">
  <div class="wrap">
    {regional}
    {radar_box}
    <div class="follow-band" id="follow">
      <div class="fb-text">
        <h3>Follow {e(name)}</h3>
        <p>Be notified when a country or the regional ranking of {e(name)} opens.</p>
      </div>
      <div class="fb-form">
        <form class="follow" name="follow-zone-{slug}" method="POST" action="/thank-you.html" data-netlify="true" netlify-honeypot="bot-field"{' data-soon="1" novalidate' if FORM_MODE == 'soon' else ''}>
          <input type="hidden" name="form-name" value="follow-zone-{slug}">
          <input type="hidden" name="zone" value="{slug}">
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
        <p class="src">One e-mail per opening. One-click unsubscribe. No data passed on to third parties.</p>
        <p class="soon-msg" role="status" hidden>Coming soon: subscriptions will open shortly.</p>
      </div>
    </div>
  </div>
</section>
''' + page_bottom('<script>(function(){var s=document.querySelector("form[data-soon]");if(s){s.addEventListener("submit",function(ev){'
                  'ev.preventDefault();s.parentNode.querySelector(".soon-msg").hidden=false;});}'
                  'document.querySelectorAll(".pill.soon").forEach(function(p){p.addEventListener("click",function(){p.classList.toggle("show");});});})();</script>\n')
    # garde-fou : aucun lien vers une page pays qui n'existe pas
    for c in geo.GEO['countries']:
        if c['status'] != 'live' and f'/{c["code"]}/"' in page:
            raise SystemExit(f'{slug} : lien vers la page pays {c["code"]}, qui n’existe pas')
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
    print(f'ok /{base}/{slug}/ · {len(ranked)} ranked ({len(live)} live) · {len(radar)} radar')
    return f'/{base}/{slug}/'

def main():
    # contrôle : chaque pays (sauf exclus) a une zone qui existe
    for c in geo.GEO['countries']:
        if c['status'] != 'excluded' and c['zone'] not in geo.ZONES:
            raise SystemExit(f"{c['code']} : zone inconnue « {c['zone']} »")
    pages = []
    for r in geo.REGIONS:
        pages.append(build(r['slug'], 'region'))
        for s in geo.subzones(r['slug']):
            pages.append(build(s['slug'], 'subregion'))
    for k in geo.GEO['collections']:
        pages.append(build(k['slug'], 'collection'))
    print(f'{len(pages)} pages')

if __name__ == '__main__':
    main()
