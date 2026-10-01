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
 'MA': '<rect width="48" height="32" fill="#C1272D"/><polygon points="24,8.5 26.6,16.4 34.4,11.6 20,20.9 29.6,20.9 18.2,11.6 26,16.4" fill="none" stroke="#006233" stroke-width="1.6" stroke-linejoin="round" transform="translate(-2.2 1.2)"/>',
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
 'IL': '<rect width="48" height="32" fill="#fff"/><rect y="4" width="48" height="4" fill="#0038B8"/><rect y="24" width="48" height="4" fill="#0038B8"/>'
       '<path d="M24,10.5 29,19 19,19ZM24,21.5 19,13 29,13Z" fill="none" stroke="#0038B8" stroke-width="1.3"/>',
 'NO': '<rect width="48" height="32" fill="#BA0C2F"/><path d="M17,0v32M0,16h48" stroke="#fff" stroke-width="8"/><path d="M17,0v32M0,16h48" stroke="#00205B" stroke-width="4"/>',
 'SG': _h('#EF3340', '#fff') + '<circle cx="11" cy="8" r="5" fill="#fff"/><circle cx="13" cy="8" r="4.5" fill="#EF3340"/>',
 'ID': _h('#CE1126', '#fff'),
 'CO': '<rect width="48" height="16" fill="#FCD116"/><rect y="16" width="48" height="8" fill="#003893"/><rect y="24" width="48" height="8" fill="#CE1126"/>',
 'IT': _v('#009246', '#fff', '#CE2B37'),
 'CH': '<rect width="48" height="32" fill="#DA291C"/><path d="M24,8v16M16,16h16" stroke="#fff" stroke-width="5"/>',
 'BE': _v('#000', '#FDDA24', '#EF3340'),
 'TW': '<rect width="48" height="32" fill="#FE0000"/><rect width="24" height="16" fill="#000095"/><circle cx="12" cy="8" r="4" fill="#fff"/>',
 'CN': '<rect width="48" height="32" fill="#EE1C25"/><polygon points="8,3 9.8,8.5 15.5,8.5 10.9,11.9 12.6,17.4 8,14 3.4,17.4 5.1,11.9 .5,8.5 6.2,8.5" fill="#FFFF00" transform="translate(1 1)"/>',
 'KR': '<rect width="48" height="32" fill="#FFFFFF"/><g transform="translate(24 16)"><g transform="rotate(33.69)"><circle r="8" fill="#0047A0"/><path d="M-8 0A8 8 0 0 1 8 0A4 4 0 0 0 0 0A4 4 0 0 1-8 0Z" fill="#CD2E3A"/></g><g fill="#000"><g transform="rotate(-56.31)"><rect x="-4" y="-13.33" width="8" height="1.33"/><rect x="-4" y="-15.33" width="8" height="1.33"/><rect x="-4" y="-17.33" width="8" height="1.33"/></g><g transform="rotate(56.31)"><rect x="-4" y="-13.33" width="3.5" height="1.33"/><rect x="0.5" y="-13.33" width="3.5" height="1.33"/><rect x="-4" y="-15.33" width="8" height="1.33"/><rect x="-4" y="-17.33" width="3.5" height="1.33"/><rect x="0.5" y="-17.33" width="3.5" height="1.33"/></g><g transform="rotate(-123.69)"><rect x="-4" y="-13.33" width="8" height="1.33"/><rect x="-4" y="-15.33" width="3.5" height="1.33"/><rect x="0.5" y="-15.33" width="3.5" height="1.33"/><rect x="-4" y="-17.33" width="8" height="1.33"/></g><g transform="rotate(123.69)"><rect x="-4" y="-13.33" width="3.5" height="1.33"/><rect x="0.5" y="-13.33" width="3.5" height="1.33"/><rect x="-4" y="-15.33" width="3.5" height="1.33"/><rect x="0.5" y="-15.33" width="3.5" height="1.33"/><rect x="-4" y="-17.33" width="3.5" height="1.33"/><rect x="0.5" y="-17.33" width="3.5" height="1.33"/></g></g></g>',
 'AT': _h('#ED2939', '#fff', '#ED2939'),
 'BH': '<rect width="48" height="32" fill="#CE1126"/><polygon points="0,0 14,0 19,3.2 14,6.4 19,9.6 14,12.8 19,16 14,19.2 19,22.4 14,25.6 19,28.8 14,32 0,32" fill="#fff"/>',
 'KE': _h('#000', '#BB0000', '#006600') + '<rect y="10" width="48" height="1.6" fill="#fff"/><rect y="20.4" width="48" height="1.6" fill="#fff"/>'
       '<ellipse cx="24" cy="16" rx="4" ry="8" fill="#BB0000" stroke="#000" stroke-width="1"/>',
 'BD': '<rect width="48" height="32" fill="#006A4E"/><circle cx="21.5" cy="16" r="8" fill="#F42A41"/>',
 'SN': _v('#00853F', '#FDEF42', '#E31B23') + '<polygon points="24,11 25.5,15 29.5,15 26.3,17.5 27.4,21.5 24,19 20.6,21.5 21.7,17.5 18.5,15 22.5,15" fill="#00853F"/>',
 'TH': '<rect width="48" height="32" fill="#A51931"/><rect y="5.33" width="48" height="21.33" fill="#F4F5F8"/><rect y="10.67" width="48" height="10.67" fill="#2D2A4A"/>',
 'GR': _h(*['#0D5EAF', '#fff'] * 4, '#0D5EAF') + '<rect width="17.8" height="17.8" fill="#0D5EAF"/><path d="M8.9,0v17.8M0,8.9h17.8" stroke="#fff" stroke-width="3.6"/>',
 'EC': '<rect width="48" height="16" fill="#FFDD00"/><rect y="16" width="48" height="8" fill="#034EA2"/><rect y="24" width="48" height="8" fill="#ED1C24"/><circle cx="24" cy="16" r="4" fill="#8C5A2B"/>',
 'IE': _v('#169B62', '#fff', '#FF883E'),
 'SV': _h('#0047AB', '#fff', '#0047AB') + '<circle cx="24" cy="16" r="3.2" fill="none" stroke="#C9A227" stroke-width="1.2"/>',
 'PT': '<rect width="48" height="32" fill="#FF0000"/><rect width="19.2" height="32" fill="#006600"/><circle cx="19.2" cy="16" r="6" fill="#FFE900"/><circle cx="19.2" cy="16" r="3.6" fill="#FF0000"/>',
 'PL': _h('#fff', '#DC143C'),
 'SE': '<rect width="48" height="32" fill="#006AA7"/><path d="M17,0v32M0,16h48" stroke="#FECC02" stroke-width="5"/>',
 'GH': _h('#CE1126', '#FCD116', '#006B3F') + '<polygon points="24,11.5 25.4,15 29,15 26.1,17.1 27.2,20.5 24,18.4 20.8,20.5 21.9,17.1 19,15 22.6,15" fill="#000"/>',
 'JO': _h('#000', '#fff', '#007A3D') + '<polygon points="0,0 22,16 0,32" fill="#CE1126"/><circle cx="7" cy="16" r="1.8" fill="#fff"/>',
 'PK': '<rect width="48" height="32" fill="#01411C"/><rect width="12" height="32" fill="#fff"/>'
       '<circle cx="31" cy="16" r="8" fill="#fff"/><circle cx="33.5" cy="14" r="7" fill="#01411C"/><circle cx="36" cy="11" r="1.6" fill="#fff"/>',
 # Australie, Nouvelle-Zélande : Union Jack en quart supérieur gauche, étoiles simplifiées
 'AU': '<rect width="48" height="32" fill="#012169"/><g transform="scale(.5)">' + '{UJ}' + '</g>'
       '<circle cx="12" cy="24.5" r="2.4" fill="#fff"/><circle cx="37" cy="7" r="1.3" fill="#fff"/><circle cx="32" cy="15" r="1.3" fill="#fff"/>'
       '<circle cx="42" cy="13" r="1.3" fill="#fff"/><circle cx="37" cy="26" r="1.5" fill="#fff"/>',
 'NZ': '<rect width="48" height="32" fill="#012169"/><g transform="scale(.5)">' + '{UJ}' + '</g>'
       '<g fill="#C8102E" stroke="#fff" stroke-width=".6"><circle cx="37" cy="8" r="1.5"/><circle cx="32" cy="15" r="1.5"/>'
       '<circle cx="41" cy="14" r="1.5"/><circle cx="37" cy="25" r="1.7"/></g>',
 'CL': '<rect width="48" height="32" fill="#fff"/><rect y="16" width="48" height="16" fill="#D52B1E"/><rect width="16" height="16" fill="#0039A6"/>'
       '<polygon points="8,3.5 9.4,7.1 13.2,7.1 10.1,9.4 11.3,13 8,10.8 4.7,13 5.9,9.4 2.8,7.1 6.6,7.1" fill="#fff"/>',
 'ES': '<rect width="48" height="32" fill="#AA151B"/><rect y="8" width="48" height="16" fill="#F1BF00"/>',
 'JP': '<rect width="48" height="32" fill="#fff"/><circle cx="24" cy="16" r="9.6" fill="#BC002D"/>',
}
for _c in ('AU', 'NZ'):
    SVG[_c] = SVG[_c].replace('{UJ}', SVG['GB'])

def flag(code, cls='flag-s'):
    """Drapeau en ligne (décoratif : le nom du pays est toujours écrit à côté)."""
    body = SVG.get((code or '').upper())
    if not body:
        return ''
    return (f'<svg class="{cls}" viewBox="0 0 48 32" aria-hidden="true">{body}'
            f'<rect x=".5" y=".5" width="47" height="31" fill="none" stroke="rgba(0,0,0,.12)"/></svg>')
