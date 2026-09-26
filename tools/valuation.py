# -*- coding: utf-8 -*-
"""Ordre de grandeur de valorisation estimé par IA — règle reproductible (publiée sur la page méthode).

Entrée, par société classée, dans <code>/data/classement-*.json → "valuation_input" :
  published_usd / published_date   dernière valorisation publiée (USD, AAAA-MM), ou null
  round_usd / round_date / round_label   dernier tour EN FONDS PROPRES dont le montant est connu (jamais dette ni subvention)
  cumulative_usd                   fonds propres cumulés, utilisé seulement si aucun tour n'est chiffré
  sources      qualité de l'ancrage : cross (source primaire ou recoupée) | single (source unique) | weak (incertaine, ⚠️)
  contradictory  les sources divergent sur l'ancrage
  adjust / adjust_reason   ajustement IA d'au plus UNE tranche (−1, 0, +1), toujours justifié

Règle :
  a) Ancrage : valorisation publiée depuis moins de 24 mois ; sinon dernier tour en fonds propres chiffré, fourchette
     post-money = montant / 0,25 à montant / 0,15 ; à défaut le cumul levé (même fourchette). Jamais dette ni subvention.
  b) Ajustement : au plus une tranche, justifié par des faits publics.
  c) Tranche affichée = celle qui contient la BORNE BASSE ; puis ajustement.
  d) Non estimé : aucun montant en fonds propres connu, ou ancrage de source faible (incertaine, ⚠️, non recoupée).
  e) Confiance : élevée = valorisation publiée < 24 mois, ou tour chiffré < 24 mois et recoupé ;
     moyenne = tour chiffré de plus de 24 mois, ou cumul seulement ; faible = source unique ou sources divergentes.
  f) Aucun chiffre inventé : en cas de doute, non estimé.
Sortie : valuation_bracket, valuation_basis, valuation_confidence, valuation_low_usd, valuation_high_usd
(la fourchette sert au calcul et à l'audit ; elle n'est jamais affichée)."""

BRACKETS = ['hundreds_k', 'millions', 'tens_m', 'hundreds_m', 'unicorn', 'decacorn']
LIMITS = [1e6, 1e7, 1e8, 1e9, 1e10]          # bornes hautes des tranches, en USD
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

def month(d, lang):
    if '-' not in d:                         # mois non publié : on n'affiche que l'année
        return d
    y, m = d.split('-')
    return f'{MONTHS[lang][int(m) - 1]} {y}'

T = {
 'fr': dict(pub='valorisation publiée de {v} ({d})', old=', plus de 24 mois', rnd='{l} de {v} ({d})', rnd_nolabel='tour de {v} ({d})',
            cum='cumul levé de {v}, montant du dernier tour non publié', adj='ajustement {s} tranche : {r}',
            single='source unique', contra='sources divergentes', none='aucun tour en fonds propres au montant publié',
            weak='ancrage de source incertaine ou non recoupée', not_est='non estimé'),
 'en': dict(pub='published valuation of {v} ({d})', old=', over 24 months old', rnd='{l} of {v} ({d})', rnd_nolabel='round of {v} ({d})',
            cum='total raised of {v}, last round undisclosed', adj='adjusted {s} bracket: {r}',
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

    pub_recent = pub and pub_d and months_between(pub_d, edition) < 24
    if pub_recent:
        low = high = pub
        conf = 'high'
        parts.append(t['pub'].format(v=money(pub, lang), d=month(pub_d, lang)))
    elif rnd and rnd_d:
        low, high = rnd / 0.25, rnd / 0.15
        conf = 'high' if months_between(rnd_d, edition) < 24 else 'medium'
        parts.append((t['rnd'].format(l=label, v=money(rnd, lang), d=month(rnd_d, lang)) if label
                      else t['rnd_nolabel'].format(v=money(rnd, lang), d=month(rnd_d, lang))))
    elif cum:
        low, high = cum / 0.25, cum / 0.15
        conf = 'medium'
        parts.append(t['cum'].format(v=money(cum, lang)))
    if pub and pub_d and not pub_recent:
        parts.append(t['pub'].format(v=money(pub, lang), d=month(pub_d, lang)) + t['old'])

    if low is None or sources == 'weak':
        parts.append(t['none'] if low is None else t['weak'])
        basis = '; '.join(parts) if lang == 'en' else ' ; '.join(parts)
        return dict(valuation_bracket='not_estimated', valuation_basis=cap(basis) + '.', valuation_confidence='low',
                    valuation_low_usd=None, valuation_high_usd=None)

    if sources == 'single' or contra:
        conf = 'low'
        parts.append(t['contra'] if contra else t['single'])
    elif sources != 'cross' and conf == 'high':
        conf = 'medium'
    idx = bracket_index(low)
    if adjust:
        if not reason:
            raise ValueError('ajustement sans justification')
        adjust = max(-1, min(1, adjust))
        idx = max(0, min(len(BRACKETS) - 1, idx + adjust))
        parts.append(t['adj'].format(s='+1' if adjust > 0 else '−1', r=reason))
    basis = '; '.join(parts) if lang == 'en' else ' ; '.join(parts)
    return dict(valuation_bracket=BRACKETS[idx], valuation_basis=cap(basis) + '.', valuation_confidence=conf,
                valuation_low_usd=round(low), valuation_high_usd=round(high))

def cap(s):
    return s[:1].upper() + s[1:]

def apply(data, lang):
    """Calcule les champs de valorisation de chaque société classée ; renvoie True si les données ont changé."""
    changed = False
    for c in data['classement']:
        vi = c.get('valuation_input')
        res = estimate(vi, data['date'], lang) if vi else dict(
            valuation_bracket='not_estimated', valuation_basis=cap(T[lang]['none']) + '.', valuation_confidence='low',
            valuation_low_usd=None, valuation_high_usd=None)
        for k, v in res.items():
            if k not in c or c[k] != v:
                c[k] = v
                changed = True
    return changed
