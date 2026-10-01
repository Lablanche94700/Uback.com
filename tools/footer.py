# -*- coding: utf-8 -*-
"""Pied de page unique de tout le site : homepage et pages globales (tools/build_home.py), pages pays (tools/site.py),
pages segment, famille et zone (tools/build_segments.py, tools/build_regions.py).
Colonnes : marque (phrase + Contact us), Rankings, How it works (Method, Calendar, Request a correction, FAQ, qui se
suivent), Backers ; barre basse : ©, mentions légales, avertissement. Styles : FOOTER_CSS, recopié dans
ma/assets/style.css entre deux marqueurs par sync_css() (appelé par tools/build_site.py), et intégré à la CSS en ligne
des pages de tools/build_home.py : une seule source."""
import os, datetime

T = {
 'en': dict(tag='Funded startups, ranked by AI. Run by rules, not editors.', contact='Contact us',
            rk='Rankings', sec='By sector', cty='By country', col='Collections',
            how='How it works', method='Method', cal='Calendar', corr='Request a correction', faq='FAQ',
            back='Backers', invest='Invest with Uback', partner='Become a partner', legal='Legal notice', aria='Footer',
            disc='Uback is a content publisher. It provides no investment advice, receives no mandate and takes part in no transaction. '
                 'Introductions are made by local partners, currently being selected. Investing in non-listed companies carries a risk '
                 'of losing all the capital invested.',
            urls=dict(method='method.html', corr='correction.html', faq='faq/', invest='invest.html', legal='legal-notice.html',
                      contact='contact.html', partner='partner.html')),
 'fr': dict(tag='Des startups financées, classées par l’IA. Régi par des règles, pas par des rédacteurs.', contact='Nous contacter',
            rk='Classements', sec='Par secteur', cty='Par pays', col='Collections',
            how='Comment ça marche', method='Méthode', cal='Calendrier', corr='Demander une correction', faq='FAQ',
            back='Backers', invest='Investir avec Uback', partner='Devenir partenaire', legal='Mentions légales', aria='Pied de page',
            disc='Uback est un éditeur de contenu. Il ne fournit aucun conseil en investissement, ne reçoit aucun mandat et n’intervient '
                 'dans aucune transaction. Les mises en relation sont réalisées par des partenaires locaux, en cours de sélection. '
                 'Investir dans des sociétés non cotées comporte un risque de perte totale du capital investi.',
            urls=dict(method='fr/methode.html', corr='fr/correction.html', faq='fr/faq/', invest='fr/investir.html',
                      legal='mentions-legales.html', contact='fr/contact.html', partner='fr/partenaire.html')),
}

def footer(lang='en', root='/', country=None, disc=None):
    """root : préfixe des liens vers la racine du site (« @ROOT@ » dans le gabarit des pays, « / » ailleurs).
    country : pays de la page (pages pays) : la page partenaire, unique, s'ouvre sur ce pays (?country=ma).
    disc : avertissement propre à la page (pays : partenaire « en cours de sélection au Maroc ») ; sinon le texte général."""
    t = T[lang]
    u = {k: root + v for k, v in t['urls'].items()}
    link = lambda href, label: f'<a href="{href}">{label}</a>'
    cols = [
        (t['rk'], [link(root + '#sectors', t['sec']), link(root + '#countries', t['cty']), link(root + '#collections', t['col'])]),
        (t['how'], [link(u['method'], t['method']), link(root + 'calendar/', t['cal']), link(u['corr'], t['corr']), link(u['faq'], t['faq'])]),
        (t['back'], [link(u['invest'], t['invest'])]),
    ]
    nav = ''.join(f'<div class="ft-col"><p class="ft-h">{h}</p>{"".join(items)}</div>' for h, items in cols)
    return f'''<footer class="site-foot">
  <div class="wrap">
    <div class="ft-grid">
      <div class="ft-brand">
        <a class="ft-logo" href="{root}" aria-label="Uback"><span class="u" aria-hidden="true">U</span>Uback</a>
        <p>{t['tag']}</p>
        <a class="ft-contact" href="{u['contact']}">{t['contact']} <span aria-hidden="true">→</span></a>
        <a class="ft-contact" href="{u['partner']}{'?country=' + country if country else ''}">{t['partner']} <span aria-hidden="true">→</span></a>
      </div>
      <nav class="ft-nav" aria-label="{t['aria']}">{nav}</nav>
    </div>
    <div class="ft-bar">
      <span>© {datetime.date.today().year} Uback</span>
      <a href="{u['legal']}">{t['legal']}</a>
      <a href="#" data-cookies>Cookies</a>
      <p>{disc or t['disc']}</p>
    </div>
  </div>
</footer>'''

FOOTER_CSS = '''footer.site-foot{margin-top:auto;background:#fff;border-top:1px solid var(--line);font-size:14px;color:var(--muted);padding:0}
footer.site-foot .wrap{display:block;padding-top:36px;padding-bottom:24px}
.ft-grid{display:grid;grid-template-columns:minmax(0,1fr);gap:28px}
.ft-brand p{margin:10px 0 12px;max-width:300px;font-size:14px;line-height:1.5;color:var(--muted)}
.ft-logo{display:inline-flex;align-items:center;gap:10px;font-size:18px;font-weight:800;letter-spacing:-.02em;color:var(--navy);text-decoration:none}
.ft-logo .u{width:28px;height:28px;border-radius:7px;background:var(--navy);color:var(--gold);display:inline-flex;align-items:center;justify-content:center;font-size:16px;letter-spacing:0}
.ft-brand .ft-contact{display:flex;width:max-content;align-items:center;gap:6px;min-height:40px;font-weight:600;color:var(--navy);text-decoration:underline;text-decoration-color:var(--gold);text-decoration-thickness:2px;text-underline-offset:5px}
.ft-nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;align-items:start;font-size:14px;font-weight:400}
.ft-col{display:flex;flex-direction:column;align-items:flex-start}
.ft-h{margin:0 0 6px;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--navy)}
.ft-col a{display:inline-flex;align-items:center;min-height:36px;color:var(--muted);text-decoration:none}
.ft-col a:hover,.ft-bar a:hover{color:var(--navy);text-decoration:underline}
.ft-bar{margin-top:24px;padding-top:16px;border-top:1px solid var(--line);display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 20px;font-size:12.5px}
.ft-bar a{color:var(--muted)}
.ft-bar p{flex:1 1 100%;margin:4px 0 0;line-height:1.55;max-width:none}
@media (min-width:640px){.ft-nav{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (min-width:900px){.ft-grid{grid-template-columns:minmax(0,1.3fr) minmax(0,3fr);gap:48px}}
'''

START, END = '/* footer:start (généré par tools/footer.py, ne pas modifier ici) */', '/* footer:end */'

def sync_css(path):
    """Recopie FOOTER_CSS dans la feuille de style des marchés, entre les marqueurs (remplace l'ancien bloc « footer »)."""
    s = open(path, encoding='utf-8').read()
    block = f'{START}\n{FOOTER_CSS}{END}\n'
    if START in s:
        new = s[:s.index(START)] + block + s[s.index(END) + len(END) + 1:]
    else:
        old = s.index('/* footer */\n')
        end = s.index('footer p{', old)
        end = s.index('\n', end) + 1
        new = s[:old] + block + s[end:]
    if new != s:
        open(path, 'w', encoding='utf-8', newline='\n').write(new)
