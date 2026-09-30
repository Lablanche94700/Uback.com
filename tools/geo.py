# -*- coding: utf-8 -*-
"""Géographie et calendrier, lus une seule fois pour tous les générateurs.
Sources : data/geo.json (pays, zones, collections) et data/calendar.json (sortie de tools/build_calendar.py).
Rien n'est écrit à la main ici : toute règle d'affichage se calcule à partir de ces deux fichiers.
Ajouter un pays = passer son statut à « live » (et renseigner url) dans data/geo.json."""
import os, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = json.load(open(os.path.join(ROOT, 'data', 'geo.json'), encoding='utf-8'))
CAL = json.load(open(os.path.join(ROOT, 'data', 'calendar.json'), encoding='utf-8'))

ZONES = {z['slug']: z for z in GEO['zones']}
REGIONS = [z for z in GEO['zones'] if not z['parent']]                 # 7 régions, ordre du fichier
COLLECTIONS = {k['slug']: k for k in GEO['collections']}
COUNTRIES = {c['code']: c for c in GEO['countries']}
RANKED = ('live', 'planned')                                           # pays classés (publiés ou à venir)
TIER = {'full': 0, 'standard': 1, 'short': 2}
REGIONAL = {r['slug']: r for r in CAL['regional_rankings']}            # zones et collections qui ont un classement régional

def subzones(slug):
    return [z for z in GEO['zones'] if z['parent'] == slug]

def lineage(slug):
    """Chaîne des zones, de la région à la zone : ['europe', 'central-eastern-europe']."""
    out = []
    while slug:
        out.insert(0, slug)
        slug = ZONES[slug]['parent']
    return out

def in_zone(c, slug):
    return bool(c.get('zone')) and slug in lineage(c['zone'])

def countries_of(slug, statuses):
    """Pays d'une zone (sous-zones comprises) ou d'une collection, pour les statuts demandés."""
    if slug in COLLECTIONS:
        cs = [COUNTRIES[x] for x in COLLECTIONS[slug]['countries'] if x in COUNTRIES]
    else:
        cs = [c for c in GEO['countries'] if in_zone(c, slug)]
    return [c for c in cs if c['status'] in statuses]

def sort_ranked(cs):
    """Tri des pays classés : live d'abord, puis par tier (full, standard, short), puis par ordre alphabétique."""
    return sorted(cs, key=lambda c: (c['status'] != 'live', TIER.get(c['tier'], 9), c['name']['en']))

def live():
    return [c for c in GEO['countries'] if c['status'] == 'live']

def name(c, lang='en'):
    return c['name'].get(lang) or c['name']['en']

# ---------------------------------------------------------------- calendrier
# clé d'un classement dans data/calendar.json : code pays (« ma »), slug de segment ou de zone
def cal_dates(key):
    """Jours (mois, jour) où ce classement est publié chaque année."""
    return [(int(d['date'][:2]), int(d['date'][3:])) for d in CAL['days']
            for it in d['items'] if it.get('code', it.get('slug')) == key]

def next_date(key, today=None):
    """Prochaine date du calendrier pour ce classement (aujourd'hui compris) ; None s'il n'est pas au calendrier."""
    today = today or datetime.date.today()
    ds = [datetime.date(y, m, d) for y in (today.year, today.year + 1) for m, d in cal_dates(key)]
    ds = [d for d in ds if d >= today]
    return min(ds) if ds else None
