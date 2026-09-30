#!/usr/bin/env python3
"""Calendrier annuel théorique des publications Uback (mode LIVE).

Source : data/geo.json (pays, zones, collections) + data/sectors.json (segments). Sortie : data/calendar.json.
Aucune date n'est écrite à la main : le calendrier est une sortie de l'algorithme, recalculée à chaque changement
de la liste des pays ou des segments. Les dates sont FIXES d'une année sur l'autre (même jour, même mois).

Grille :
- jours 1 à 28 de chaque mois = jours de publication ; jours 29 à 31 = jamais de publication programmée
  (réservés aux mises à jour hors calendrier ; le 31 décembre publie la revue annuelle de couverture) ;
- chaque jour de publication porte au plus UNE édition pays ou régionale, et au plus UN segment mondial ;
- pays : trimestriel, un créneau (mois du trimestre, jour) répété 4 fois par an ;
- classements régionaux : semestriels, logés sur les créneaux pays restés libres (T1+T3 ou T2+T4) ;
- segments mondiaux : semestriels, un créneau (mois du semestre, jour) répété 2 fois par an ;
- ordre : alternance des régions (pays) et des familles (segments), pour que deux jours consécutifs ne se ressemblent pas ;
- ancres : les pays déjà publiés gardent leur date (Vietnam le 15 du 1er mois du trimestre, Maroc le 15 du 2e, Pologne le 15 du 3e).
"""
import json, os, itertools, calendar as cal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = json.load(open(os.path.join(ROOT, 'data', 'geo.json'), encoding='utf-8'))
SEC = json.load(open(os.path.join(ROOT, 'data', 'sectors.json'), encoding='utf-8'))
DAYS = 28
ANCHORS = {'vn': (0, 15), 'ma': (1, 15), 'pl': (2, 15)}   # (mois du trimestre 0-2, jour)
MONTHS = [cal.month_name[i] for i in range(1, 13)]

def round_robin(groups):
    """Entrelace des listes : a1 b1 c1 a2 b2 c2 …"""
    return [x for tup in itertools.zip_longest(*groups) for x in tup if x is not None]

zones = {z['slug']: z for z in GEO['zones']}
def top(slug):
    while zones[slug]['parent']: slug = zones[slug]['parent']
    return slug

# 1. pays classés, par région de premier niveau, les plus gros d'abord (tier puis densité)
ORDER = {'full': 0, 'standard': 1, 'short': 2}
ranked = [c for c in GEO['countries'] if c['tier'] in ORDER]
by_region = {}
for c in sorted(ranked, key=lambda c: (ORDER[c['tier']], -c['density']['low'])):
    by_region.setdefault(top(c['zone']), []).append(c)
countries = [c for c in round_robin(list(by_region.values())) if c['code'] not in ANCHORS]

# 2. classements régionaux : toute zone (ou collection) comptant au moins 3 pays classés ou radar
members = {}
for c in GEO['countries']:
    if c['status'] in ('excluded', 'analysis_only') or not c['zone']: continue
    z = c['zone']
    while z: members.setdefault(z, set()).add(c['code']); z = zones[z]['parent']
regional = [{'slug': z, 'name': zones[z]['name']['en'], 'n': len(m)} for z, m in members.items() if len(m) >= 3]
regional += [{'slug': k['slug'], 'name': k['name']['en'], 'n': len(k['countries'])} for k in GEO['collections']]

# 3. créneaux pays : 3 mois × 28 jours = 84 ; ancres d'abord, puis pays et régionaux répartis régulièrement
slots = [(m, d) for m in range(3) for d in range(1, DAYS + 1)]
free = [s for s in slots if s not in ANCHORS.values()]
n_reg_slots = -(-len(regional) // 2)                      # 2 régionaux par créneau (T1+T3 / T2+T4)
assert len(countries) + n_reg_slots <= len(free), 'grille pays pleine'
step = len(free) / max(n_reg_slots, 1)
reg_idx = {int(i * step + step / 2) for i in range(n_reg_slots)}
assign, ci, ri = {}, iter(countries), 0
for c, s in ANCHORS.items(): assign[s] = ('country', c)
reg_pairs = [regional[i:i + 2] for i in range(0, len(regional), 2)]
for i, s in enumerate(free):
    if i in reg_idx and ri < len(reg_pairs): assign[s] = ('regional', reg_pairs[ri]); ri += 1
    else:
        c = next(ci, None)
        if c: assign[s] = ('country', c['code'])

# 4. segments : 6 mois × 28 jours = 168 créneaux, familles entrelacées
segs = round_robin([[g for s in f['sectors'] for g in s['segments']] for f in SEC['families']])
seg_slots = [(m, d) for m in range(6) for d in range(1, DAYS + 1)]
assert len(segs) <= len(seg_slots), 'grille segments pleine'
# répartition régulière des segments sur les 168 créneaux (les créneaux libres sont espacés, pas groupés en fin)
seg_step = len(seg_slots) / len(segs)
seg_assign = {seg_slots[int(i * seg_step)]: g for i, g in enumerate(segs)}

# 5. déroulé sur l'année
cname = {c['code']: c['name']['en'] for c in GEO['countries']}
year = []
for month in range(12):
    for day in range(1, cal.monthrange(2027, month + 1)[1] + 1):
        items = []
        if day <= DAYS:
            a = assign.get((month % 3, day))
            if a and a[0] == 'country':
                items.append({'type': 'country', 'code': a[1], 'name': cname[a[1]]})
            elif a:
                pair = a[1]; r = pair[(month // 3) % 2] if len(pair) > (month // 3) % 2 else None
                if r: items.append({'type': 'regional', 'slug': r['slug'], 'name': r['name']})
            g = seg_assign.get((month % 6, day))
            if g: items.append({'type': 'segment', 'slug': g['slug'], 'name': g['name']})
        elif month == 11 and day == 31:
            items.append({'type': 'review', 'name': 'Annual coverage review (country list recomputed)'})
        year.append({'date': f'{month + 1:02d}-{day:02d}', 'items': items})

out = {'version': GEO['version'], 'mode': 'theoretical (applies when Uback leaves beta)',
       'rules': __doc__.strip().split('\n\n', 1)[1],
       'counts': {'countries': len(ranked), 'regional': len(regional), 'segments': len(segs),
                  'publications_per_year': sum(len(d['items']) for d in year)},
       'regional_rankings': regional, 'days': year}
json.dump(out, open(os.path.join(ROOT, 'data', 'calendar.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
k = out['counts']
print(f"ok data/calendar.json · {k['countries']} countries ×4 · {k['regional']} regional ×2 · {k['segments']} segments ×2 "
      f"· {k['publications_per_year']} publications/year")
