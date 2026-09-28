# -*- coding: utf-8 -*-
"""Petits drapeaux SVG (48 × 32, simplifiés) par code pays ISO à deux lettres, en majuscules.
Utilisés par les classements mondiaux par segment (tools/build_segments.py). Un pays absent : pas de drapeau, le nom suffit."""

def _h(*colors):                     # bandes horizontales égales
    n = len(colors)
    return ''.join(f'<rect y="{32 * i / n:g}" width="48" height="{32 / n + .1:g}" fill="{c}"/>' for i, c in enumerate(colors))

def _v(*colors):                     # bandes verticales égales
    n = len(colors)
    return ''.join(f'<rect x="{48 * i / n:g}" width="{48 / n + .1:g}" height="32" fill="{c}"/>' for i, c in enumerate(colors))

_STAR = '<polygon points="24,7 26.47,14.6 34.46,14.6 28,19.3 30.47,26.9 24,22.2 17.53,26.9 20,19.3 13.54,14.6 21.53,14.6" fill="{}"/>'

SVG = {
 'GB': '<rect width="48" height="32" fill="#012169"/><path d="M0,0 48,32M48,0 0,32" stroke="#fff" stroke-width="6"/>'
       '<path d="M0,0 48,32M48,0 0,32" stroke="#C8102E" stroke-width="2"/><path d="M24,0v32M0,16h48" stroke="#fff" stroke-width="10"/>'
       '<path d="M24,0v32M0,16h48" stroke="#C8102E" stroke-width="6"/>',
 'US': _h(*['#B22234', '#fff'] * 3, '#B22234') + '<rect width="21" height="17.2" fill="#3C3B6E"/>',
 'MX': _v('#006847', '#fff', '#CE1126') + '<circle cx="24" cy="16" r="4" fill="#8C5A2B"/>',
 'BR': '<rect width="48" height="32" fill="#009C3B"/><polygon points="24,4 44,16 24,28 4,16" fill="#FFDF00"/><circle cx="24" cy="16" r="6.5" fill="#002776"/>',
 'DE': _h('#000', '#DD0000', '#FFCE00'),
 'AR': _h('#74ACDF', '#fff', '#74ACDF') + '<circle cx="24" cy="16" r="3.2" fill="#F6B40E"/>',
 'NL': _h('#AE1C28', '#fff', '#21468B'),
 'PH': _h('#0038A8', '#CE1126') + '<polygon points="0,0 27.7,16 0,32" fill="#fff"/><circle cx="9" cy="16" r="3.2" fill="#FCD116"/>',
 'SA': '<rect width="48" height="32" fill="#006C35"/><path d="M13,13h22M13,21h20" stroke="#fff" stroke-width="2.2"/>',
 'ZA': _h('#E03C31', '#001489') + '<path d="M0,0 20,16 0,32M20,16h28" stroke="#fff" stroke-width="10"/>'
       '<path d="M0,0 20,16 0,32M20,16h28" stroke="#007749" stroke-width="6"/><polygon points="0,4 15,16 0,28" fill="#FFB81C"/>'
       '<polygon points="0,7 11.5,16 0,25" fill="#000"/>',
 'HK': '<rect width="48" height="32" fill="#DE2910"/><circle cx="24" cy="16" r="7" fill="#fff"/><circle cx="24" cy="16" r="2.4" fill="#DE2910"/>',
 'CA': '<rect width="48" height="32" fill="#fff"/><rect width="12" height="32" fill="#D52B1E"/><rect x="36" width="12" height="32" fill="#D52B1E"/>'
       '<polygon points="24,8 26,13 30,12 28,17 31,19 25,20 25,25 23,25 23,20 17,19 20,17 18,12 22,13" fill="#D52B1E"/>',
 'IN': _h('#FF9933', '#fff', '#138808') + '<circle cx="24" cy="16" r="3.8" fill="none" stroke="#000080" stroke-width="1.2"/>',
 'DK': '<rect width="48" height="32" fill="#C8102E"/><path d="M17,0v32M0,16h48" stroke="#fff" stroke-width="5"/>',
 'CI': _v('#F77F00', '#fff', '#009E60'),
 'EG': _h('#CE1126', '#fff', '#000') + '<circle cx="24" cy="16" r="3" fill="#C09300"/>',
 'VN': '<rect width="48" height="32" fill="#DA251D"/>' + _STAR.format('#FFFF00'),
 'FR': _v('#0055A4', '#fff', '#EF4135'),
 'AE': _h('#00732F', '#fff', '#000') + '<rect width="12" height="32" fill="#FF0000"/>',
 'NG': _v('#008751', '#fff', '#008751'),
}

def flag(code, cls='flag-s'):
    """Drapeau en ligne (décoratif : le nom du pays est toujours écrit à côté)."""
    body = SVG.get((code or '').upper())
    if not body:
        return ''
    return (f'<svg class="{cls}" viewBox="0 0 48 32" aria-hidden="true">{body}'
            f'<rect x=".5" y=".5" width="47" height="31" fill="none" stroke="rgba(0,0,0,.12)"/></svg>')
