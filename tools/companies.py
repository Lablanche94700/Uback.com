# -*- coding: utf-8 -*-
"""Sociétés et investisseurs de tous les classements, lus une seule fois pour tous les générateurs.
Source de vérité : les classements (pays : <code>/data/classement-*.json + couche anglaise ; segments : data/segments/*.json).
Rien n'est écrit ici, sauf par tools/build_companies.py (table des slugs figée, rapports) : les pages pays, segment et zone
ne font que lire la même table pour rendre les noms cliquables.

Une société = une fiche (/company/<slug>/), quel que soit le nombre de classements où elle apparaît :
  clé de fusion = nom normalisé (minuscules, sans accents, sans ponctuation ni mention entre parenthèses) ;
  exceptions dans data/companies/aliases.json ({"<slug>": ["Nom 1", "Nom 2"]}) ;
  slug figé dans data/companies/slugs.json : un slug publié ne change plus jamais (on n'y retire jamais une ligne).
Pas de fiche pour hors_classement (rachetées, cotées, sorties) ni reperes_cotes.
Investisseurs : extraits des parenthèses de derniere_levee (pays), de last_equity_round.investors et detail (segments)
et des tours d'enrichissement, normalisés par data/investors.json ; page à partir de 2 sociétés, indexée à partir de 3."""
import os, re, json, glob, copy, unicodedata, datetime
from urllib.parse import urlparse

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
DATA = os.path.join(ROOT, 'data')
import geo
import valuation

CO_DIR = os.path.join(DATA, 'companies')
SLUGS_FILE = os.path.join(CO_DIR, 'slugs.json')
ALIASES_FILE = os.path.join(CO_DIR, 'aliases.json')
INVESTORS_FILE = os.path.join(DATA, 'investors.json')
INV_PAGE, INV_INDEX = 2, 3                    # seuils : page à partir de 2 sociétés, indexée à partir de 3

def ascii_(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()

def norm(name):
    """Clé de fusion : « Dunamu (Upbit) » → « dunamu » ; « z.systems » → « z systems »."""
    s = re.sub(r'\([^)]*\)', ' ', name)
    s = ascii_(s).lower().replace('’', "'")
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', ascii_(re.sub(r'\([^)]*\)', ' ', name)).lower()).strip('-')

def family_of(sub):
    """« Fintech › B2B commerce… » → « Fintech »."""
    return (sub or '').split('›')[0].strip()

def domain(url):
    try:
        h = urlparse(url).netloc.lower()
    except ValueError:
        return url
    return h[4:] if h.startswith('www.') else h

# ---------------------------------------------------------------- dates de « dernière levée » (texte libre)
_MONTH = {'janv': 1, 'janvier': 1, 'jan': 1, 'january': 1, 'févr': 2, 'février': 2, 'feb': 2, 'february': 2,
          'mars': 3, 'mar': 3, 'march': 3, 'avr': 4, 'avril': 4, 'apr': 4, 'april': 4, 'mai': 5, 'may': 5,
          'juin': 6, 'jun': 6, 'june': 6, 'juil': 7, 'juillet': 7, 'jul': 7, 'july': 7, 'août': 8, 'aug': 8, 'august': 8,
          'sept': 9, 'septembre': 9, 'sep': 9, 'september': 9, 'oct': 10, 'octobre': 10, 'october': 10,
          'nov': 11, 'novembre': 11, 'november': 11, 'déc': 12, 'décembre': 12, 'dec': 12, 'december': 12}
_DATE = re.compile(r'(?:\b([A-Za-zÀ-ÿ]+)\.?\s+)?~?((?:19|20)\d\d)\b')

def text_date(txt):
    """Date la plus récente citée : « AAAA-MM » (ou « AAAA ») ; None sinon."""
    best = None
    for m in _DATE.finditer(txt or ''):
        mo = _MONTH.get((m.group(1) or '').lower(), 0)
        d = (int(m.group(2)), mo)
        best = d if best is None or d > best else best
    if not best:
        return None
    return f'{best[0]}-{best[1]:02d}' if best[1] else str(best[0])

_CUR = re.compile(r'(USD|EUR|KRW|INR|JPY|PLN|VND|MAD|MDH|M\$|k\$|Md\$|M€|\$|undisclosed|not disclosed|non divulgué|no cash)', re.I)
_DATE_ONLY = re.compile(r'(?:(?:closed|from|since|~)\s+)?(?:[A-Za-zÀ-ÿ]+\.?\s+)?~?(?:19|20)\d\d', re.I)

def _split_outside(txt, ch):
    """Premier « ch » hors parenthèses : (avant, après)."""
    depth = 0
    for i, x in enumerate(txt):
        depth += x == '('
        depth -= x == ')'
        if x == ch and depth == 0:
            return txt[:i], txt[i + 1:]
    return txt, ''

def parse_round(txt):
    """« Series A · USD 12M · Oct 2025 (SPE Capital, Orange Ventures) » → label, montant, date, investisseurs, reste.
    Ce qui ne se laisse pas découper reste dans « label » ou « rest » (jamais perdu, jamais inventé)."""
    main, rest = _split_outside((txt or '').strip(), ';')
    main, rest = main.strip(), rest.strip()
    invs = []
    for p in re.finditer(r'\(([^()]*)\)', main):
        if re.search(r'(19|20)\d\d$', main[:p.start()].rstrip()):
            invs.append(p.group(1))
    for i in invs:
        main = main.replace(f'({i})', '').strip()
    label = amount = date_txt = ''
    other = []
    for p in (x.strip() for x in main.split('·')):
        if not p:
            continue
        if not date_txt and _DATE_ONLY.fullmatch(p):
            date_txt = p
        elif not amount and _CUR.search(p):
            amount = p
        elif not label:
            label = p
        else:
            other.append(p)
    if other:
        rest = ' · '.join(other) + ('; ' + rest if rest else '')
    return dict(label=label, amount=amount, date=text_date(date_txt or main), date_txt=date_txt,
                investors='; '.join(invs), rest=rest)

# ---------------------------------------------------------------- investisseurs
_BAD = re.compile(r"(existing investors|new and existing|^others?$|and others|not disclosed|not confirmed|not verified|undisclosed|"
                  r"founder vehicle|policy funds|closing pending|single source|implied|no cash|employees|buyback|angel investors|"
                  r"^lead$|^new$|several|investors?$|^[\d.,~\s]+$|USD|EUR|KRW|INR|JPY|%|\bcr\b|equity|debt|grant|secondary|primary|"
                  r"tranche|round|series|seed|valuation|existing|company|-backed|shareholders)", re.I)

def split_investors(s):
    """« led by Index Ventures, with Kleiner Perkins, Sequoia Capital » → noms ; le bruit (« and others »…) est écarté."""
    if not s:
        return []
    s = re.sub(r'\b(co-)?led by\b', ',', s, flags=re.I)
    s = re.sub(r'\b(with|incl\.?|including|among earlier backers|plus)\b', ',', s, flags=re.I)
    s = s.replace('(', ',').replace(')', ',')
    out = []
    for p in re.split(r',|;|\band\b| / (?=[A-Z])', s):
        p = p.strip(' .:')
        p = re.sub(r'^(backers?(\s+include)?|investors\s+include)\s*:?\s*', '', p, flags=re.I)
        p = re.sub(r'\s+(joined|since|via).*$', '', p)
        if len(p) < 2 or _BAD.search(p):
            continue
        out.append(p)
    return out

def detail_investors(detail):
    """detail des segments : « Seed: ConsenSys Mesh, Infinite Capital » → noms (seulement si le préfixe est un libellé)."""
    m = re.match(r'^([A-Za-z][A-Za-z0-9 \-+]{0,30}):\s*(.+)$', detail or '')
    if not m or re.search(r'\d{4}', m.group(1)):
        return []
    return split_investors(m.group(2))

_INV = None

def investor_table():
    """data/investors.json : alias normalisé → fiche ({slug, name, aliases, type, hq, website})."""
    global _INV
    if _INV is None:
        items = json.load(open(INVESTORS_FILE, encoding='utf-8')) if os.path.exists(INVESTORS_FILE) else []
        _INV = {}
        for it in items:
            for a in [it['name']] + it.get('aliases', []):
                _INV[norm_inv(a)] = it
    return _INV

def norm_inv(name):
    return re.sub(r'[^a-z0-9]+', ' ', ascii_(name.replace('’', "'")).lower()).strip()

# ---------------------------------------------------------------- collecte
def _country_sources():
    """Une édition par fichier de référence ; textes anglais (couche .en.json) quand elle existe."""
    from build_site import MARKETS, RANKING_CAP
    out = []
    for m in MARKETS:
        if not (m['lang'] == 'en' and m['default']):
            continue
        files = sorted(f for f in glob.glob(os.path.join(ROOT, m['code'], 'data', f"classement-{m['code']}-*.json"))
                       if not f.endswith('.en.json'))
        for f in files:
            d = json.load(open(f, encoding='utf-8'))
            ov = f[:-5] + '.en.json'
            if os.path.exists(ov):
                t = json.load(open(ov, encoding='utf-8'))
                for k in ('edition', 'date_label', 'radar', 'nees_ici'):
                    if k in t:
                        d[k] = t[k]
                for c in d['classement']:
                    tc = t['classement'].get(c['nom'], {})
                    for k in ('sous_secteur', 'ville', 'leve_cumule', 'derniere_levee', 'juridiction', 'note'):
                        if k in tc:
                            c[k] = tc[k]
                    if c.get('valuation_input'):
                        vi = c['valuation_input'] = copy.deepcopy(c['valuation_input'])
                        vi['round_label'], vi['adjust_reason'] = tc.get('round_label', vi.get('round_label')), tc.get('adjust_reason', '')
            for c in d['classement']:
                if c.get('valuation_input'):
                    c.update(valuation.estimate(c['valuation_input'], d['date'], 'en'))
            d['classement'] = sorted(d['classement'], key=valuation.rank_key)
            for i, c in enumerate(d['classement'], 1):
                c['rang'] = i
            n = min(RANKING_CAP[geo.COUNTRIES[m['code']]['tier']], len(d['classement']))
            out.append(dict(code=m['code'], name=m['name'], path=m['path'], file=os.path.relpath(f, ROOT).replace('\\', '/'),
                            data=d, n=n, current=(os.path.basename(f) == m['data'])))
    return out

def _segment_sources():
    out = []
    for f in sorted(glob.glob(os.path.join(DATA, 'segments', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        d['ranked'] = sorted(d['ranked'], key=lambda c: (-c['estimate_usd'], c['rank']))
        out.append(d)
    return out

_CACHE = None

def load():
    """Toutes les sociétés et tous les investisseurs. Renvoie dict(companies, by_key, investors, countries, segments, slugs_new)."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    countries, segments = _country_sources(), _segment_sources()
    aliases = json.load(open(ALIASES_FILE, encoding='utf-8')) if os.path.exists(ALIASES_FILE) else {}
    # « Nom » fusionne partout ; « Nom@<code pays ou slug de segment> » ne vise que ce classement (homonymes)
    alias_key = {(norm(n.split('@')[0]) + ('@' + n.split('@')[1] if '@' in n else '')): 'alias:' + s
                 for s, names in aliases.items() for n in names}
    companies = {}

    def get(name, scope=''):
        k = alias_key.get(norm(name) + '@' + scope, alias_key.get(norm(name), norm(name)))
        if k not in companies:
            companies[k] = dict(key=k, names=[], apps=[], alias_slug=k[6:] if k.startswith('alias:') else None)
        c = companies[k]
        if name not in c['names']:
            c['names'].append(name)
        return c

    for cs in countries:
        d = cs['data']
        if not cs['current']:
            # éditions antérieures : seulement l'historique des rangs des sociétés classées
            for r in d['classement'][:cs['n']]:
                get(r['nom'], cs['code']).setdefault('history', []).append((cs['code'], d['date'], r['rang']))
            continue
        for r in d['classement'][:cs['n']]:
            get(r['nom'], cs['code'])['apps'].append(dict(kind='country', list='ranked', code=cs['code'], src=cs, row=r, rank=r['rang']))
        for r in d.get('radar') or []:
            get(r['nom'], cs['code'])['apps'].append(dict(kind='country', list='radar', code=cs['code'], src=cs, row=r))
        for r in d.get('nees_ici') or []:
            get(r['nom'], cs['code'])['apps'].append(dict(kind='country', list='born', code=cs['code'], src=cs, row=r))
    for sd in segments:
        for r in sd['ranked']:
            get(r['name'], sd['segment_id'])['apps'].append(dict(kind='segment', list='ranked', sid=sd['segment_id'], src=sd, row=r, rank=r['rank']))
        for r in sd['radar']:
            get(r['name'], sd['segment_id'])['apps'].append(dict(kind='segment', list='radar', sid=sd['segment_id'], src=sd, row=r))
    for k in list(companies):
        if not companies[k]['apps']:
            del companies[k]                  # seulement dans une édition passée : plus de fiche

    # ---------------- slugs figés
    frozen = json.load(open(SLUGS_FILE, encoding='utf-8')) if os.path.exists(SLUGS_FILE) else {}
    used = {v: k for k, v in frozen.items()}
    new = {}
    for k in sorted(companies, key=lambda k: (k.startswith('alias:'), k)):
        c = companies[k]
        c['name'] = display_name(c)
        if k in frozen:
            c['slug'] = frozen[k]
            continue
        base = c['alias_slug'] or slugify(c['name']) or 'company'
        s = base
        if s in used:
            s = f"{base}-{primary_code(c)}"
            i = 2
            while s in used:
                s, i = f"{base}-{primary_code(c)}-{i}", i + 1
        c['slug'] = s
        used[s] = k
        new[k] = s

    # ---------------- investisseurs
    table = investor_table()
    investors = {}
    for c in companies.values():
        c['investors'] = []
        for a in c['apps']:
            for raw in round_investors(a):
                it = table.get(norm_inv(raw))
                if it and it.get('type') == 'skip':
                    continue
                key = it['slug'] if it else 'raw:' + norm_inv(raw)
                if key not in investors:
                    investors[key] = dict(key=key, slug=it['slug'] if it else slugify(raw), name=it['name'] if it else raw,
                                          info=it, raws=set(), deals=[], known=bool(it))
                inv = investors[key]
                inv['raws'].add(raw)
                inv['deals'].append(dict(company=c, app=a))
                if key not in c['investors']:
                    c['investors'].append(key)
        enr = enrichment(c['slug'])
        for rd in (enr or {}).get('rounds', []):
            for raw in rd.get('investors', []):
                it = table.get(norm_inv(raw))
                if it and it.get('type') == 'skip':
                    continue
                key = it['slug'] if it else 'raw:' + norm_inv(raw)
                if key not in investors:
                    investors[key] = dict(key=key, slug=it['slug'] if it else slugify(raw), name=it['name'] if it else raw,
                                          info=it, raws=set(), deals=[], known=bool(it))
                inv = investors[key]
                inv['raws'].add(raw)
                inv['deals'].append(dict(company=c, app=None, round=rd))
                if key not in c['investors']:
                    c['investors'].append(key)
    for inv in investors.values():
        inv['companies'] = list(dict.fromkeys(d['company']['key'] for d in inv['deals']))
        inv['page'] = len(inv['companies']) >= INV_PAGE and (inv['info'] or {}).get('type') != 'individual'
        inv['index'] = inv['page'] and len(inv['companies']) >= INV_INDEX
    # slugs d'investisseurs : uniques (une collision garde le premier, l'autre reçoit un suffixe)
    seen = set()
    for inv in sorted(investors.values(), key=lambda i: (not i['known'], -len(i['companies']), i['key'])):
        if not inv['page']:
            continue
        s, i = inv['slug'], 2
        while s in seen:
            s, i = f"{inv['slug']}-{i}", i + 1
        inv['slug'] = s
        seen.add(s)

    # résolution d'un nom cité dans un classement : (nom normalisé @ classement) d'abord, puis nom seul
    lookup = {}
    for c in companies.values():
        for a in c['apps']:
            nm = a['row']['nom'] if a['kind'] == 'country' else a['row']['name']
            scope = a['code'] if a['kind'] == 'country' else a['sid']
            lookup[norm(nm) + '@' + scope] = c['slug']
            lookup.setdefault(norm(nm), c['slug'])
    by_key = companies
    _CACHE = dict(companies=list(companies.values()), by_key=by_key, investors=investors, countries=countries, lookup=lookup,
                  segments=segments, slugs_new=new, frozen=frozen, aliases=aliases)
    return _CACHE

def display_name(c):
    """Nom affiché : celui du classement pays s'il existe (le plus local), sinon le premier rencontré."""
    for a in c['apps']:
        if a['kind'] == 'country':
            return a['row']['nom']
    return c['apps'][0]['row']['name'] if c['apps'] else c['names'][0]

def primary_code(c):
    for a in c['apps']:
        if a['kind'] == 'country':
            return a['code']
    return (c['apps'][0]['row'].get('country_code') or 'xx').lower()

def round_investors(a):
    r = a['row']
    if a['kind'] == 'country':
        return split_investors(parse_round(r.get('derniere_levee'))['investors'])
    rd = r.get('last_equity_round') or {}
    return list(dict.fromkeys(split_investors(rd.get('investors') or '') + detail_investors(rd.get('detail'))))

_ENR = {}

def enrichment(slug):
    if slug not in _ENR:
        p = os.path.join(CO_DIR, f'{slug}.json')
        _ENR[slug] = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None
    return _ENR[slug]

# ---------------------------------------------------------------- liens, pour tous les générateurs
def company_slug(name, scope=''):
    """Slug de la fiche d'une société citée dans un classement (scope : code pays ou slug de segment) ; None sinon."""
    lk = load()['lookup']
    return lk.get(norm(name) + '@' + scope) or lk.get(norm(name))

_LINK_RE = None

def _inv_regex():
    """Expression des noms d'investisseurs qui ont une page (alias compris), du plus long au plus court."""
    global _LINK_RE
    if _LINK_RE is None:
        import html
        names = {}
        for inv in load()['investors'].values():
            if not inv['page']:
                continue
            for raw in list(inv['raws']) + ([inv['name']] + (inv['info'] or {}).get('aliases', []) if inv['info'] else []):
                names[html.escape(raw)] = inv['slug']
        alts = sorted(names, key=len, reverse=True)
        _LINK_RE = (re.compile(r'(?<![\w>])(' + '|'.join(re.escape(a) for a in alts) + r')(?![\w<])'), names) if alts else (None, {})
    return _LINK_RE

def link_investors(escaped, root='/', parens_only=True):
    """Texte déjà échappé : chaque investisseur qui a une page devient un lien (dans les parenthèses seulement si parens_only)."""
    rx, names = _inv_regex()
    if not rx:
        return escaped
    sub = lambda m: f'<a class="inv-l" href="{root}investor/{names[m.group(1)]}/">{m.group(1)}</a>'
    if not parens_only:
        return rx.sub(sub, escaped)
    return re.sub(r'\(([^()]*)\)', lambda p: '(' + rx.sub(sub, p.group(1)) + ')', escaped)

def link_company(name, scope='', escaped=None, root='/', cls='co-l'):
    """« <a href="/company/<slug>/">Nom</a> » si la société a une fiche, sinon le nom échappé."""
    import html
    s = company_slug(name, scope)
    txt = escaped if escaped is not None else html.escape(name)
    return f'<a class="{cls}" href="{root}company/{s}/">{txt}</a>' if s else txt
