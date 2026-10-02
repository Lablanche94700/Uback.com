# -*- coding: utf-8 -*-
"""En-tête UNIQUE de tout le site, et sous-menu des pages de classement.

1. header() : en-tête global, identique sur toutes les pages (homepage et pages globales : tools/build_home.py ;
   pages pays : tools/site.py ; segments, familles, zones, fiches : tools/build_segments.py page_top).
   Logo · Rankings ▾ (familles publiées, pays en ligne, méthode, FAQ) · Calendar · Invest · Backers ▾ · recherche ·
   langues (quand la page existe en plusieurs langues).
2. subnav() : sous-menu collant des pages de classement (pays, segment, famille, zone) : sélecteur du classement
   (changer de pays, de segment ou de zone sans repasser par la homepage) · ancres de la page · Follow / Declare.
   Les fiches société et pages investisseur n'en ont pas : leur fil d'Ariane joue ce rôle.
Styles : HEADER_CSS, recopié dans ma/assets/style.css entre deux marqueurs par sync_css() (appelé par build_site.py),
et intégré à la CSS en ligne des pages de tools/build_home.py : une seule source, un seul jeu de règles responsive."""
import os, re, json, html
import geo
import search

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = html.escape
START, END = '/* header:start (généré par tools/header.py, ne pas modifier ici) */', '/* header:end */'
SECTORS = json.load(open(os.path.join(ROOT, 'data', 'sectors.json'), encoding='utf-8'))

FLAGS = {
 'ma': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#C1272D"/><polygon points="24,8.5 26.6,16.4 34.4,11.6 20,20.9 29.6,20.9 18.2,11.6 26,16.4" fill="none" stroke="#006233" stroke-width="1.6" stroke-linejoin="round" transform="translate(-2.2 1.2)"/></svg>',
 'pl': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="16" fill="#FFFFFF"/><rect y="16" width="48" height="16" fill="#DC143C"/><rect x=".5" y=".5" width="47" height="31" fill="none" stroke="#E4E8EE"/></svg>',
 'vn': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#DA251D"/><polygon points="24,7 26.47,14.6 34.46,14.6 28,19.3 30.47,26.9 24,22.2 17.53,26.9 20,19.3 13.54,14.6 21.53,14.6" fill="#FFFF00"/></svg>',
 'fr': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="16" height="32" fill="#002654"/><rect x="16" width="16" height="32" fill="#FFFFFF"/><rect x="32" width="16" height="32" fill="#CE1126"/><rect x=".5" y=".5" width="47" height="31" fill="none" stroke="#E4E8EE"/></svg>',
 'in': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="10.7" fill="#FF9933"/><rect y="10.7" width="48" height="10.7" fill="#FFFFFF"/><rect y="21.3" width="48" height="10.7" fill="#138808"/><circle cx="24" cy="16" r="4.2" fill="none" stroke="#000080" stroke-width="1"/><circle cx="24" cy="16" r=".9" fill="#000080"/><rect x=".5" y=".5" width="47" height="31" fill="none" stroke="#E4E8EE"/></svg>',
 'kr': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="48" height="32" fill="#FFFFFF"/><g transform="translate(24 16)"><g transform="rotate(33.69)"><circle r="8" fill="#0047A0"/><path d="M-8 0A8 8 0 0 1 8 0A4 4 0 0 0 0 0A4 4 0 0 1-8 0Z" fill="#CD2E3A"/></g><g fill="#000"><g transform="rotate(-56.31)"><rect x="-4" y="-13.33" width="8" height="1.33"/><rect x="-4" y="-15.33" width="8" height="1.33"/><rect x="-4" y="-17.33" width="8" height="1.33"/></g><g transform="rotate(56.31)"><rect x="-4" y="-13.33" width="3.5" height="1.33"/><rect x="0.5" y="-13.33" width="3.5" height="1.33"/><rect x="-4" y="-15.33" width="8" height="1.33"/><rect x="-4" y="-17.33" width="3.5" height="1.33"/><rect x="0.5" y="-17.33" width="3.5" height="1.33"/></g><g transform="rotate(-123.69)"><rect x="-4" y="-13.33" width="8" height="1.33"/><rect x="-4" y="-15.33" width="3.5" height="1.33"/><rect x="0.5" y="-15.33" width="3.5" height="1.33"/><rect x="-4" y="-17.33" width="8" height="1.33"/></g><g transform="rotate(123.69)"><rect x="-4" y="-13.33" width="3.5" height="1.33"/><rect x="0.5" y="-13.33" width="3.5" height="1.33"/><rect x="-4" y="-15.33" width="3.5" height="1.33"/><rect x="0.5" y="-15.33" width="3.5" height="1.33"/><rect x="-4" y="-17.33" width="3.5" height="1.33"/><rect x="0.5" y="-17.33" width="3.5" height="1.33"/></g></g></g><rect x=".5" y=".5" width="47" height="31" fill="none" stroke="#E4E8EE"/></svg>',
 'ng': '<svg class="flag" viewBox="0 0 48 32" aria-hidden="true"><rect width="16" height="32" fill="#008751"/><rect x="16" width="16" height="32" fill="#FFFFFF"/><rect x="32" width="16" height="32" fill="#008751"/><rect x=".5" y=".5" width="47" height="31" fill="none" stroke="#E4E8EE"/></svg>',
}

UI = {'en': dict(rk='Rankings', sec='By sector', cty='By country', all_s='All sectors', all_c='All countries',
                 m='Method', m_sub='How the AI ranks startups and estimates their valuation', m_url='/method.html',
                 faq='FAQ · questions about the rankings', faq_url='/faq/', cal='Calendar', inv='Invest', inv_url='/invest.html',
                 bk='Backers', login='Login / Register', terms='Terms and conditions', login_url='/login.html',
                 terms_url='/terms.html', home='Uback, home', main='Main navigation', page='On this page'),
      'fr': dict(rk='Classements', sec='Par secteur', cty='Par pays', all_s='Tous les secteurs', all_c='Tous les pays',
                 m='Méthode', m_sub='Comment l’IA classe les startups et estime leur valorisation', m_url='/fr/methode.html',
                 faq='FAQ · questions sur les classements', faq_url='/fr/faq/', cal='Calendrier', inv='Investir',
                 inv_url='/fr/investir.html', bk='Backers', login='Connexion / Inscription', terms='Conditions générales',
                 login_url='/fr/connexion.html', terms_url='/fr/conditions.html', home='Uback, accueil',
                 main='Navigation principale', page='Dans cette page')}

def fam_slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

def _families():
    """Familles qui ont au moins un segment publié (fichier data/segments/<slug>.json) : page /sectors/<famille>/."""
    return [f for f in SECTORS['families']
            if any(os.path.exists(os.path.join(ROOT, 'data', 'segments', g['slug'] + '.json')) for s in f['sectors'] for g in s['segments'])]

def rankings_menu(lang, current=None, root='/'):
    """Menu « Rankings » : familles publiées et pays en ligne (calculés depuis data/sectors.json, data/segments/, data/geo.json),
    la méthode en bandeau, la FAQ."""
    from build_site import MARKETS, NAMES
    u = UI[lang]
    R = lambda path: root + path.lstrip('/')     # liens depuis la racine (« @ROOT@ » dans le gabarit des pays)
    fams = ''.join(f'<a href="{R("/sectors/" + fam_slug(f["name"]) + "/")}">{e(f["name"])}</a>' for f in _families())
    ctys = ''
    for c in sorted(geo.live(), key=geo.name):
        code, name, url = c['code'], geo.name(c), c['url']
        if lang == 'fr':                      # version française du pays si elle existe, sinon sa version principale
            v = next((m for m in MARKETS if m['code'] == code and m['lang'] == 'fr'), None)
            name, url = NAMES[code]['fr'], (v['path'] + '/' if v else url)
        ctys += f'<a href="{R(url)}">{FLAGS.get(code, "")}{e(name)}</a>'
    cur = lambda k: ' aria-current="page"' if current == k else ''
    return (f'<details class="rk"><summary>{u["rk"]}</summary><div class="rk-menu">'
            f'<div class="rk-col"><span class="rk-h">{u["sec"]}</span>{fams}<a class="rk-all" href="{R("/#sectors")}">{u["all_s"]} <span aria-hidden="true">→</span></a></div>'
            f'<div class="rk-col"><span class="rk-h">{u["cty"]}</span>{ctys}<a class="rk-all" href="{R("/#countries")}">{u["all_c"]} <span aria-hidden="true">→</span></a></div>'
            f'<a class="rk-method" href="{R(u["m_url"])}"{cur("method")}>'
            f'<span class="rk-ic" aria-hidden="true"></span><span><b>{u["m"]}</b><small>{u["m_sub"]}</small></span>'
            f'<span class="rk-go" aria-hidden="true">→</span></a>'
            f'<a class="rk-faq" href="{R(u["faq_url"])}"{cur("faq")}>{u["faq"]} <span aria-hidden="true">→</span></a>'
            f'</div></details>')

def backers_menu(lang, current=None, root='/'):
    u = UI[lang]
    R = lambda path: root + path.lstrip('/')
    cur = lambda k: ' aria-current="page"' if current == k else ''
    return (f'<details class="rk"><summary>{u["bk"]}</summary><div class="rk-menu one">'
            f'<a href="{R(u["login_url"])}"{cur("login")}>{u["login"]}</a>'
            f'<a href="{R(u["terms_url"])}"{cur("terms")}>{u["terms"]}</a></div></details>')

# Script des menus (Rankings, Backers, sélecteur du sous-menu) : un seul ouvert à la fois, fermeture au clic extérieur et avec Échap
JS = ('<script>(function(){var ds=[].slice.call(document.querySelectorAll("details.rk,details.mkt"));if(!ds.length)return;'
      'document.addEventListener("click",function(ev){ds.forEach(function(d){if(d.open&&!d.contains(ev.target))d.open=false;});});'
      'document.addEventListener("keydown",function(ev){if(ev.key!=="Escape")return;ds.forEach(function(d){if(d.open){d.open=false;d.querySelector("summary").focus();}});});'
      'ds.forEach(function(d){d.addEventListener("toggle",function(){if(d.open)ds.forEach(function(o){if(o!==d)o.open=false;});});'
      'd.querySelectorAll(".rk-menu a").forEach(function(a){a.addEventListener("click",function(){d.open=false;});});});})();</script>')

def header(lang='en', current=None, langs='', root='/'):
    """En-tête global. langs : sélecteur de langue déjà construit (« EN · FR ») ou vide ; root : préfixe du script de
    recherche et des liens (« @ROOT@ » dans le gabarit des pays, dont les chemins absolus sont réécrits) ; current : page active (method, faq, calendar, invest, login, terms)."""
    u = UI[lang]
    R = lambda path: root + path.lstrip('/')
    cur = lambda k: ' aria-current="page"' if current == k else ''
    return f'''<header class="gh">
  <div class="gh-in">
    <a class="gh-logo" href="{root}" aria-label="{u['home']}"><span class="u" aria-hidden="true">U</span>Uback</a>
    <nav class="gh-nav" aria-label="{u['main']}">
      {rankings_menu(lang, current, root)}
      <a href="{R('/calendar/')}"{cur('calendar')}>{u['cal']}</a>
      <a href="{R(u['inv_url'])}"{cur('invest')}>{u['inv']}</a>
      {backers_menu(lang, current, root)}
    </nav>
    <span class="gh-sp"></span>
    {search.html(root, lang)}
    {f'<span class="gh-lang">{langs}</span>' if langs else ''}
  </div>
</header>
{JS}'''

def subnav(selector, links, actions='', lang='en'):
    """Sous-menu collant d'une page de classement : sélecteur (<details class="mkt">), ancres de la page
    [(href, libellé)], actions (boutons déjà construits)."""
    items = ''.join(f'<a href="{h}">{l}</a>' for h, l in links)
    return f'''<div class="rsub">
  <div class="rsub-in">
    {selector}
    <nav class="rsub-links" aria-label="{UI[lang]['page']}">{items}</nav>
    {f'<div class="rsub-act">{actions}</div>' if actions else ''}
  </div>
</div>'''

HEADER_CSS = '''.gh{background:#fff;border-bottom:1px solid #E4E8EE;position:relative;z-index:40;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
.gh-in{position:relative;max-width:var(--gh-w,1280px);margin:0 auto;padding:0 var(--gh-pad,24px);min-height:72px;display:flex;align-items:center;gap:8px 20px;box-sizing:border-box}
.gh-logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;font-size:22px;font-weight:800;letter-spacing:-.02em;color:#1E3A5F;white-space:nowrap}
.gh-logo .u{width:34px;height:34px;border-radius:8px;background:#1E3A5F;color:#C8A052;display:inline-flex;align-items:center;justify-content:center;font-size:20px;letter-spacing:0}
.gh-nav{display:flex;gap:4px 24px;align-items:center;font-size:15px;font-weight:500;margin-left:28px}
.gh-nav>a,.gh .rk summary{color:#1E3A5F;text-decoration:none;display:inline-flex;align-items:center;min-height:44px}
.gh-nav>a:hover,.gh .rk summary:hover{color:#142842}
.gh-nav>a[aria-current]{box-shadow:inset 0 -2px 0 #C8A052}
.gh-sp{flex:1}
.gh-lang{display:flex;align-items:center;gap:6px;font-size:13px;font-weight:600;color:#5A6B82;white-space:nowrap}
.gh-lang a{color:#1E3A5F;text-decoration:none;display:inline-flex;align-items:center;min-height:44px}
.gh-lang a:hover{text-decoration:underline}
.gh-lang .on{color:#1E3A5F;text-decoration:underline;text-decoration-color:#C8A052;text-decoration-thickness:2px;text-underline-offset:4px}
.gh-lang .soon{color:#A3AFBF;cursor:default}
.rk{position:relative}
.rk summary{list-style:none;cursor:pointer;gap:7px}
.rk summary::-webkit-details-marker{display:none}
.rk summary::after{content:"";width:6px;height:6px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg);margin-top:-4px}
.rk[open] summary::after{transform:rotate(-135deg);margin-top:3px}
.rk summary:focus-visible{outline:2px solid #C8A052;outline-offset:3px;border-radius:4px}
.rk-menu{position:absolute;top:calc(100% + 6px);left:-18px;z-index:60;display:grid;grid-template-columns:max-content max-content;gap:4px 32px;padding:16px 18px;background:#fff;border:1px solid #E4E8EE;border-radius:12px;box-shadow:0 10px 30px rgba(30,58,95,.14);white-space:nowrap}
.rk-col{display:flex;flex-direction:column}
.rk-h{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#5A6B82;margin:0 0 4px}
.rk-menu a{display:flex;align-items:center;gap:10px;min-height:40px;padding:0 8px;margin:0 -8px;border-radius:8px;font-size:15px;font-weight:500;color:#1E3A5F;text-decoration:none}
.rk-menu a:hover{background:#F7F8FA}
.rk-menu .flag{width:21px;height:14px;border-radius:2px;flex-shrink:0}
.rk-menu.one{grid-template-columns:max-content;gap:2px;min-width:220px}
.rk-menu a.rk-method{grid-column:1/-1;display:flex;align-items:center;gap:12px;margin:12px -8px 0;padding:12px 14px;min-height:0;border-radius:10px;background:#FBF6EA;border:1px solid #EAD9B0;white-space:normal}
.rk-menu a.rk-method:hover,.rk-menu a.rk-method[aria-current]{background:#F6ECD2;border-color:#C8A052}
.rk-method b{display:block;font-size:15px;font-weight:700;color:#1E3A5F}
.rk-method small{display:block;margin-top:2px;font-size:12.5px;font-weight:500;line-height:1.4;color:#5A6B82}
.rk-ic{flex:0 0 30px;height:30px;border-radius:8px;background:#C8A052 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23fff' stroke-width='2' stroke-linecap='round'%3E%3Cpath d='M4 19h16M7 15V9M12 15V5M17 15v-4'/%3E%3C/svg%3E") center/18px no-repeat}
.rk-go{margin-left:auto;font-size:18px;font-weight:600;color:#C8A052}
.rk-menu a.rk-faq{grid-column:1/-1;min-height:36px;margin-top:4px;font-size:14px;font-weight:600;color:#5A6B82}
.rk-menu a.rk-all{margin-top:4px;font-size:14px;font-weight:600;text-decoration:underline;text-decoration-color:#C8A052;text-decoration-thickness:2px;text-underline-offset:5px}
html:has(.rsub){scroll-padding-top:68px}
.rsub{position:sticky;top:0;z-index:30;background:rgba(255,255,255,.97);border-bottom:1px solid #E4E8EE;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
.rsub-in{max-width:var(--gh-w,1280px);margin:0 auto;padding:0 var(--gh-pad,24px);min-height:56px;display:flex;align-items:center;gap:20px;box-sizing:border-box}
.rsub-links{display:flex;align-items:center;gap:22px;font-size:14px;font-weight:500;flex:1;min-width:0;overflow-x:auto;scrollbar-width:none;white-space:nowrap}
.rsub-links::-webkit-scrollbar{display:none}
.rsub-links a{color:#4A5A70;text-decoration:none;display:inline-flex;align-items:center;min-height:44px}
.rsub-links a:hover{color:#1E3A5F;box-shadow:inset 0 -2px 0 #C8A052}
.rsub-act{display:flex;gap:10px;flex-shrink:0}
.rsub-act .btn{white-space:nowrap}
@media (max-width:899px){
  .gh-in{flex-wrap:wrap;row-gap:0;padding-top:6px;padding-bottom:2px;min-height:0}
  .gh-nav{order:10;width:100%;margin-left:0;justify-content:space-between;gap:0 10px}
  .rsub-act{display:none}
  .rsub-in{gap:14px;min-height:52px}
}
@media (max-width:719px){.gh-in{--gh-pad:16px}.rsub-in{--gh-pad:16px}.rk{position:static}
  .rk-menu{left:16px;right:16px;top:calc(100% - 4px);grid-template-columns:1fr;gap:14px;white-space:normal}
  .rsub .mkt{position:static}.rsub .mkt .menu{left:16px;right:16px;min-width:0}}
@media (max-width:479px){.gh-nav{font-size:14px;gap:0 6px}.gh-logo{font-size:20px}.rsub-links{gap:16px;font-size:13.5px}}
@media (max-width:359px){.gh-nav{font-size:13px}}
'''

def sync_css(path):
    """Recopie HEADER_CSS dans la feuille de style des marchés, entre les marqueurs (ajouté en fin de fichier la première fois)."""
    s = open(path, encoding='utf-8').read()
    block = f'{START}\n{HEADER_CSS}{END}\n'
    if START in s:
        new = s[:s.index(START)] + block + s[s.index(END) + len(END) + 1:]
    else:
        new = s.rstrip('\n') + '\n' + block
    if new != s:
        open(path, 'w', encoding='utf-8', newline='\n').write(new)
