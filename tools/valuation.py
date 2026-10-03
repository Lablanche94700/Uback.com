# -*- coding: utf-8 -*-
"""Valorisation estimée par IA : estimation centrale, fourchette et ordre de grandeur — règle reproductible
(publiée sur la page méthode).

Entrée, par société classée, dans <code>/data/classement-*.json → "valuation_input" :
  published_usd / published_date   dernière valorisation publiée (USD, AAAA-MM), ou null
  round_usd / round_date / round_label   dernier tour EN FONDS PROPRES dont le montant est connu (jamais dette ni subvention)
  cumulative_usd                   fonds propres cumulés, utilisé seulement si aucun tour n'est chiffré
  sources      qualité de l'ancrage : cross (source primaire ou recoupée) | single (source unique) | weak (incertaine, ⚠️)
  contradictory  les sources divergent sur l'ancrage
  adjust / adjust_reason   ajustement IA d'au plus UNE tranche (−1, 0, +1), toujours justifié

Règle :
  a) Estimation centrale : valorisation publiée depuis moins de 24 mois ; sinon dernier tour en fonds propres chiffré,
     le tour représentant 15 à 25 % du capital (post-money au milieu géométrique : montant × ~5,16) ; à défaut le cumul
     levé (même multiple). Jamais dette ni subvention.
  b) Ajustement : au plus un facteur 3 (× 3 ou ÷ 3, champ adjust = +1 / −1), justifié par des faits publics.
  c) Fourchette d'incertitude autour de l'estimation, selon la confiance : élevée −20 % / +25 % ; moyenne × 2/3 à × 1,5 ;
     faible × 1/2 à × 2.
  d) Tranche (ordre de grandeur) = celle qui contient l'estimation centrale. Rang = ordre décroissant de l'estimation.
  e) Non estimé : aucun montant en fonds propres connu, ou ancrage de source faible (incertaine, ⚠️, non recoupée).
  f) Confiance : élevée = valorisation publiée < 24 mois, ou tour chiffré < 24 mois et recoupé ;
     moyenne = tour chiffré de plus de 24 mois, ou cumul seulement ; faible = source unique ou sources divergentes.
  g) Aucun chiffre inventé : en cas de doute, non estimé.
Sortie : valuation_central_usd, valuation_low_usd, valuation_high_usd (affichés), valuation_bracket, valuation_basis,
valuation_confidence."""
import math

BRACKETS = ['hundreds_k', 'millions', 'tens_m', 'hundreds_m', 'unicorn', 'decacorn', 'hectocorn']
LIMITS = [1e6, 1e7, 1e8, 1e9, 1e10, 1e11]    # bornes hautes des tranches, en USD (hectocorn : 100 Md$ et plus)
ROUND_MULT = 1 / math.sqrt(0.25 * 0.15)      # le tour = 15 à 25 % du capital : milieu géométrique, ~5,16
ADJ_FACTOR = 3                               # ajustement IA : au plus × 3 ou ÷ 3
BANDS = {'high': (0.8, 1.25), 'medium': (2 / 3, 1.5), 'low': (0.5, 2.0)}   # fourchette autour de l'estimation
MONTHS = {'fr': ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'],
          'en': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']}

def bracket_index(usd):
    return next((i for i, lim in enumerate(LIMITS) if usd < lim), len(LIMITS))

def months_between(a, b):                    # 'AAAA-MM' (ou 'AAAA' : janvier, par prudence) → mois de a à b
    ya, ma = (map(int, a.split('-')) if '-' in a else (int(a), 1)); yb, mb = map(int, b.split('-'))
    return (yb - ya) * 12 + (mb - ma)

def money(x, lang):
    def num(v):
        s = f'{v:.1f}'.rstrip('0').rstrip('.')
        return s.replace('.', ',') if lang == 'fr' else s
    if x >= 1e9:
        return f'{num(x / 1e9)} Md$' if lang == 'fr' else f'USD {num(x / 1e9)}bn'
    if x >= 1e6:
        return f'{num(x / 1e6)} M$' if lang == 'fr' else f'USD {num(x / 1e6)}M'
    return f'{num(x / 1e3)} k$' if lang == 'fr' else f'USD {num(x / 1e3)}k'

def sig2(v):
    """Arrondi à 2 chiffres significatifs (464,5 → 460 ; 1,47 → 1,5 ; 24,3 → 24)."""
    if v <= 0:
        return 0
    d = 1 - int(math.floor(math.log10(v)))
    r = round(v, d)
    return int(r) if r == int(r) else r

def _unit(x):
    return (1e9, 'bn', 'Md$') if x >= 1e9 else (1e6, 'M', 'M$') if x >= 1e6 else (1e3, 'k', 'k$')

def _num(v, lang):
    s = f'{v}'
    return s.replace('.', ',') if lang == 'fr' else s

def money2(x, lang):
    """Montant arrondi pour l'affichage : « USD 1.5bn » / « 1,5 Md$ »."""
    x = sig2(x / _unit(x)[0]) * _unit(x)[0]     # arrondi d'abord : 999,6 M → 1 000 M, affiché « 1 bn »
    div, en, fr = _unit(x)
    v = sig2(x / div)
    return f'USD {_num(v, lang)}{en}' if lang == 'en' else f'{_num(v, lang)} {fr}'

def range_txt(lo, hi, lang):
    """Fourchette compacte : « USD 1.2–1.9bn » ; unités différentes : « USD 780M–1.2bn » / « 780 M$–1,2 Md$ »."""
    a, b = money2(lo, lang), money2(hi, lang)
    if lang == 'en':
        ua, ub = a[4:], b[4:]
        ka, kb = ua.lstrip('0123456789.'), ub.lstrip('0123456789.')
        return f'USD {ua[:-len(ka)]}–{ub}' if ka == kb else f'USD {ua}–{ub}'
    na, ka = a.split(' ')
    nb, kb = b.split(' ')
    return f'{na}–{nb} {kb}' if ka == kb else f'{a}–{b}'

def month(d, lang):
    if '-' not in d:                         # mois non publié : on n'affiche que l'année
        return d
    y, m = d.split('-')
    return f'{MONTHS[lang][int(m) - 1]} {y}'

T = {
 'fr': dict(pub='valorisation publiée de {v} ({d})', old=', plus de 24 mois', rnd='{l} de {v} ({d})', rnd_nolabel='tour de {v} ({d})',
            cum='cumul levé de {v}, montant du dernier tour non publié', adj='ajustement {s} : {r}',
            single='source unique', contra='sources divergentes', none='aucun tour en fonds propres au montant publié',
            weak='ancrage de source incertaine ou non recoupée', not_est='non estimé'),
 'en': dict(pub='published valuation of {v} ({d})', old=', over 24 months old', rnd='{l} of {v} ({d})', rnd_nolabel='round of {v} ({d})',
            cum='total raised of {v}, last round undisclosed', adj='adjusted {s}: {r}',
            single='single source', contra='conflicting sources', none='no equity round with a disclosed amount',
            weak='anchor from an uncertain or unconfirmed source', not_est='not estimated'),
}

def estimate(vi, edition, lang):
    t = T[lang]
    pub, pub_d = vi.get('published_usd'), vi.get('published_date')
    rnd, rnd_d, label = vi.get('round_usd'), vi.get('round_date'), vi.get('round_label')
    cum = vi.get('cumulative_usd')
    sources, contra = vi.get('sources', 'weak'), vi.get('contradictory', False)
    adjust, reason = int(vi.get('adjust') or 0), (vi.get('adjust_reason') or '').strip()
    parts, low, high, conf = [], None, None, None

    central = None
    pub_recent = pub and pub_d and months_between(pub_d, edition) < 24
    if pub_recent:
        central = pub
        conf = 'high'
        parts.append(t['pub'].format(v=money(pub, lang), d=month(pub_d, lang)))
    elif rnd and rnd_d:
        central = rnd * ROUND_MULT
        conf = 'high' if months_between(rnd_d, edition) < 24 else 'medium'
        parts.append((t['rnd'].format(l=label, v=money(rnd, lang), d=month(rnd_d, lang)) if label
                      else t['rnd_nolabel'].format(v=money(rnd, lang), d=month(rnd_d, lang))))
    elif cum:
        central = cum * ROUND_MULT
        conf = 'medium'
        parts.append(t['cum'].format(v=money(cum, lang)))
    low = central
    if pub and pub_d and not pub_recent:
        parts.append(t['pub'].format(v=money(pub, lang), d=month(pub_d, lang)) + t['old'])

    if low is None or sources == 'weak':
        parts.append(t['none'] if low is None else t['weak'])
        basis = '; '.join(parts) if lang == 'en' else ' ; '.join(parts)
        return dict(valuation_bracket='not_estimated', valuation_basis=cap(basis) + '.', valuation_confidence='low',
                    valuation_central_usd=None, valuation_low_usd=None, valuation_high_usd=None)

    if sources == 'single' or contra:
        conf = 'low'
        parts.append(t['contra'] if contra else t['single'])
    elif sources != 'cross' and conf == 'high':
        conf = 'medium'
    if adjust:
        if not reason:
            raise ValueError('ajustement sans justification')
        adjust = max(-1, min(1, adjust))
        central *= ADJ_FACTOR ** adjust
        parts.append(t['adj'].format(s='× 3' if adjust > 0 else '÷ 3', r=reason))
    lo_f, hi_f = BANDS[conf]
    basis = '; '.join(parts) if lang == 'en' else ' ; '.join(parts)
    return dict(valuation_bracket=BRACKETS[bracket_index(central)], valuation_basis=cap(basis) + '.', valuation_confidence=conf,
                valuation_central_usd=round(central), valuation_low_usd=round(central * lo_f), valuation_high_usd=round(central * hi_f))

def rank_key(c):
    """Ordre du classement : estimation centrale décroissante ; les sociétés non estimées en dernier."""
    v = c.get('valuation_central_usd')
    return -(v if v is not None else -1)

def cap(s):
    return s[:1].upper() + s[1:]

def apply(data, lang):
    """Calcule les champs de valorisation de chaque société classée, puis range le classement par estimation centrale
    décroissante et renumérote les rangs ; renvoie True si les données ont changé."""
    changed = False
    for c in data['classement']:
        vi = c.get('valuation_input')
        res = estimate(vi, data['date'], lang) if vi else dict(
            valuation_bracket='not_estimated', valuation_basis=cap(T[lang]['none']) + '.', valuation_confidence='low',
            valuation_central_usd=None, valuation_low_usd=None, valuation_high_usd=None)
        for k, v in res.items():
            if k not in c or c[k] != v:
                c[k] = v
                changed = True
    order = sorted(data['classement'], key=rank_key)          # tri stable : à estimation égale, ordre du fichier
    for i, c in enumerate(order, 1):
        if c.get('rang') != i:
            c['rang'] = i
            changed = True
    if order != data['classement']:
        data['classement'] = order
        changed = True
    return changed
