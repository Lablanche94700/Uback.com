# -*- coding: utf-8 -*-
"""Gabarit français (site Maroc, avec Backers et partenaire).
Ne pas lancer directement : tools/build_site.py l'exécute avec la configuration du marché dans M.
Écrit uniquement dans le dossier du marché (ex. ma/), jamais à la racine."""
import json, html, os, re, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # racine du dépôt = dossier publié
PREFIX = '/' + M['code']            # chemin du marché sur uback.com (M est fourni par build_site.py)
OUT = ROOT + PREFIX                 # seul dossier écrit par ce gabarit
D = json.load(open(f"{OUT}/data/{M['data']}", encoding='utf-8'))
BASE = 'https://uback.com' + PREFIX
FORM_MODE = 'mailto'                # 'mailto' (GitHub Pages) ou 'netlify' (Netlify Forms)
FORM_EMAIL = 'contact@uback.com'
e = html.escape

LOGO_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C8A052" stroke-width="2" aria-hidden="true">{}</svg>'
IC_AI = LOGO_SVG.format('<rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 20h8M12 18v2M7 9h4M7 13h10"/>')
IC_HUM = LOGO_SVG.format('<path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/><circle cx="12" cy="8" r="4"/>')
IC_MON = LOGO_SVG.format('<path d="M12 3v18M7 8h7a3 3 0 0 1 0 6H8a3 3 0 0 0 0 6h9"/>')

def head(title, desc, path, extra=''):
    url = BASE + path
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Uback">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/og-image.png?v=2">
<meta property="og:locale" content="fr_FR">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{extra}
</head>
<body>
<a class="skip" href="#main">Aller au contenu</a>
<header class="hdr">
  <div class="wrap">
    <a class="brand" href="@HOME@" aria-label="Uback, accueil"><span class="u">U</span>Uback</a>
    {M['switcher']}
    <button class="menu-toggle" aria-label="Menu" aria-expanded="false" onclick="var n=document.getElementById('nav');var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1E3A5F" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <nav class="main" id="nav" aria-label="Navigation principale">
      <a href="/#classement">Classement</a>
      <a href="/#secteurs">Secteurs</a>
      <a href="/#backers">Backers</a>
      <a href="/partenaire.html">Partenaire</a>
      <a href="/methode.html">Méthode</a>
    </nav>
    <span class="spacer"></span>
    <span class="langs"><span class="on">FR</span><span>·</span><span class="soon" title="Bientôt disponible">EN</span><span>·</span><span class="soon" title="Bientôt disponible">AR</span></span>
    <a class="btn" href="/#suivre">Suivre le Maroc</a>
    <a class="btn gold" href="/#backers">Déclarer une intention</a>
  </div>
</header>
<main id="main">
'''

FOOT = f'''
</main>
<footer>
  <div class="wrap">
    <div class="row">
      <span class="brand"><span class="u">U</span>Uback</span>
      <span>Powered by AI</span>
      <span>·</span><a href="/methode.html">Méthode et règles du jeu</a>
      <span>·</span><a href="/partenaire.html">Devenir partenaire</a>
      <span>·</span><a href="/methode.html#correction">Demander une correction</a>
      <span>·</span><a href="/mentions-legales.html">Mentions légales</a>
      <span class="spacer"></span>
      <span>Uback.com · {datetime.date.today().year}</span>
    </div>
    <p>Uback est un éditeur de contenu. Il ne fournit aucun conseil en investissement, ne reçoit aucun mandat et n’intervient dans aucune transaction. Les mises en relation sont réalisées par un partenaire agréé, en cours de sélection au Maroc. Investir dans des sociétés non cotées comporte un risque de perte totale du capital investi.</p>
  </div>
</footer>
</body>
</html>
'''

def conf(n):
    dots = ''.join('<i class="f"></i>' if i < n else '<i></i>' for i in range(3))
    lab = {3: 'Sources solides', 2: 'Sources partielles', 1: 'Sources faibles'}[n]
    return f'<span class="conf" aria-hidden="true">{dots}</span><span class="conf-l">{lab}</span>'

def row(c):
    top = ' class="top"' if c['rang'] == 1 else ''
    jur = ''
    if not c['juridiction'].startswith('Maroc') or ';' in c['juridiction']:
        jur = f'<span class="jur">{e(c["juridiction"])}</span>'
    note = f'<div class="src">{e(c["note"])}</div>' if c['note'] else ''
    return f'''<tr{top}>
<td class="rank">{c['rang']}</td>
<td><span class="co">{e(c['nom'])}<small>{e(c['ville'])} · fondée en {c['creation']}</small></span>{jur}{note}</td>
<td data-l="Sous-secteur">{e(c['sous_secteur'])}</td>
<td data-l="Levées">{e(c['leve_cumule'])} cumulés<br><span class="src">{e(c['derniere_levee'])} · <a href="{e(c['source'])}" rel="nofollow noopener" target="_blank">source</a></span></td>
<td data-l="Confiance">{conf(c['confiance'])}</td>
<td data-l="Accès"><span class="st" title="Aucune intention de lever ou de céder n’a été déclarée sur Uback. Les dirigeants peuvent revendiquer leur fiche.">Non déclaré</span></td>
<td class="act"><a class="btn" href="/#backers">Déclarer une intention</a></td>
</tr>'''

jsonld = {
  "@context": "https://schema.org", "@type": "ItemList",
  "name": f"Les 20 startups marocaines les mieux valorisées – {D['date_label']}",
  "description": "Classement mensuel Uback des startups marocaines, établi par IA à partir d'informations publiques.",
  "itemListOrder": "https://schema.org/ItemListOrderDescending",
  "itemListElement": [{"@type": "ListItem", "position": c['rang'], "name": c['nom'], "url": f"https://{c['site']}"} for c in D['classement']]
}

index = head(
  f"Top 20 des startups marocaines les mieux valorisées – {D['date_label']} | Uback Maroc",
  "Classement mensuel des startups marocaines non cotées ayant déjà levé des fonds, établi par IA à partir d'informations publiques. Uback classe, ne valorise pas.",
  "/", f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>')

index += f'''
<div class="wrap">
  <div class="hero">
    <div>
      <div class="kicker">Funded startups, ranked by AI</div>
      <h1>Les 20 startups marocaines les mieux valorisées</h1>
      <p class="lead">Un classement mensuel des startups marocaines non cotées ayant déjà levé des fonds, établi par intelligence artificielle à partir d’informations publiques. Uback ne calcule aucune valorisation : il classe.</p>
      <div class="meta">
        <span class="tag beta">{e(D['edition'])} · {e(D['date_label'])}</span>
        <span>Claude · consensus multi-IA à partir de l’édition 1</span><span>·</span>
        <a href="/methode.html">Méthode publiée</a><span>·</span>
        <span>Ordre jamais modifié par un humain</span>
      </div>
    </div>
    <div class="panel">
      <div class="k">Le marché en un coup d’œil</div>
      <div class="stats">
        <div><b>{len(D['classement'])}</b><span>sociétés classées</span></div>
        <div><b>{len(D['radar'])}</b><span>sociétés sur le radar</span></div>
        <div><b>{e(D['marche']['total_2025'])}</b><span>levés en 2025</span></div>
        <div><b>{e(D['marche']['deals_2025'])}</b><span>tours en 2025</span></div>
      </div>
      <div class="fine">{e(D['marche']['commentaire'])} Sources : <a href="{e(D['marche']['source_partech'])}" style="color:#c7d0dc" rel="nofollow noopener" target="_blank">Partech</a>, <a href="{e(D['marche']['source_um6p'])}" style="color:#c7d0dc" rel="nofollow noopener" target="_blank">UM6P Ventures</a>. Les compteurs d’intentions s’afficheront au-delà d’un seuil de montant et de nombre de Backers.</div>
    </div>
  </div>

  <div class="reperes">
    <span class="lab">Repères cotés</span>
    {''.join(f'<span class="pill">{e(r["nom"])} · {e(r["info"])} · <a href="{e(r["source"])}" rel="nofollow noopener" target="_blank">source</a></span>' for r in D['reperes_cotes'])}
    <span class="fine">Hors classement : aucune intention possible sur une société cotée.</span>
  </div>
</div>

<section id="classement" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head">
      <h2>Classement national · tous secteurs</h2>
      <div class="tabs"><a class="on" href="#classement">Top 20</a><a href="#radar">Radar</a><a href="#nees-ici">Nées ici, établies ailleurs</a><a href="/partenaire.html#challengers">Challengers</a></div>
      <span class="spacer"></span>
      <span class="sub">Première édition : pas encore de mouvements.</span>
    </div>
    <table class="tbl">
      <thead><tr><th>#</th><th>Société</th><th>Sous-secteur</th><th>Levées connues</th><th>Confiance</th><th>Accès</th><th></th></tr></thead>
      <tbody>
      {''.join(row(c) for c in D['classement'])}
      </tbody>
    </table>
    <div class="disclaimer"><b>Ce classement est une opinion, pas une évaluation.</b> {e(D['methode'])} Il est établi à partir d’informations publiques (presse, annonces de levées de fonds), selon une méthode publiée, sans intervention humaine sur l’ordre. Uback ne calcule ni n’estime de valorisation : classer des sociétés non cotées est un exercice par nature imprécis, qui dépend des informations disponibles et peut être contredit par des faits non publics. L’indice de confiance reflète la qualité des sources. Toute société peut <a href="/methode.html#correction">demander une correction</a> ou contester sa position. Ce classement ne constitue ni un conseil en investissement, ni une sollicitation. Seuil d’éligibilité : au moins {e(D['seuil_levee'])} levés, sociétés non cotées, opérations principales au Maroc.</div>
  </div>
</section>

<section class="soft" id="regards">
  <div class="wrap">
    <div class="sec-head"><h2>Trois regards, jamais un seul</h2></div>
    <div class="grid3">
      <div class="card"><div class="ic">{IC_AI}</div><h3>Ce que pensent les IA</h3><p>Chaque mois, la même question est posée à plusieurs IA. Les réponses sont fusionnées en un classement de consensus, avec un indice de confiance par position. L’édition 0 est établie par une seule IA ; le consensus arrive avec l’édition 1.</p></div>
      <div class="card"><div class="ic">{IC_HUM}</div><h3>Ce que défendent les experts</h3><p>Le partenaire agréé et des analystes contestent le classement : « pourquoi ce leader est absent », « pourquoi ce n° 3 est surévalué ». Les résumés sont gratuits.</p></div>
      <div class="card"><div class="ic">{IC_MON}</div><h3>Ce que veut l’argent</h3><p>Les sociétés les plus convoitées : celles qui cumulent le plus d’intentions d’investissement payantes. Montants agrégés, jamais d’intention individuelle.</p></div>
    </div>
  </div>
</section>

<section id="secteurs">
  <div class="wrap">
    <div class="sec-head"><h2>Classements par secteur</h2><span class="sub">Quatre verticales au lancement, d’autres quand le test de faisabilité le permet.</span></div>
    <div class="grid4">
      <div class="card"><span class="k">Bientôt · Top 10</span><h3>Fintech &amp; paiement</h3><p>Néobanques, paiement marchand, crédit et fidélité pour les commerçants.</p></div>
      <div class="card"><span class="k">Bientôt · Top 10</span><h3>Commerce &amp; retail B2B</h3><p>Approvisionnement des commerçants, e-commerce, marques.</p></div>
      <div class="card"><span class="k">Bientôt · Top 10</span><h3>Agritech &amp; alimentation</h3><p>Distribution agricole, agriculture de précision, eau.</p></div>
      <div class="card"><span class="k">Bientôt · Top 10</span><h3>Logistique &amp; mobilité</h3><p>Fret, dernier kilomètre, transport partagé, véhicules électriques.</p></div>
    </div>
    <div class="soon-list"><span>Immobilier (proptech)</span><span>Santé</span><span>Éducation</span><span>Énergie &amp; climat</span><span>Logiciels B2B</span></div>
  </div>
</section>

<section class="navy" id="backers">
  <div class="wrap">
    <div class="sec-head"><h2>Investir au Maroc, à plusieurs, depuis Paris, Dubaï ou Montréal</h2></div>
    <p class="lead">Uback agrège les intentions d’investisseurs qualifiés (business angels, family offices, diaspora) et les confie à un partenaire agréé, qui construit le deal. Vous entrez au capital aux côtés d’investisseurs professionnels déjà présents. Vous bénéficiez du même pacte d’associés.</p>
    <div class="steps-head">
      <h3>Le nombre fait la force</h3>
      <p>Seul, un petit ticket n’ouvre aucune porte. Regroupés, les Backers pèsent.</p>
    </div>
    <div class="grid4">
      <div class="card dark"><span class="num">1</span><h3>Déclarez une intention</h3><p>Sur une société ou sur un secteur, avec un ticket minimum et maximum. Payante, pour qualifier le sérieux&nbsp;; transférable tant qu’elle n’est pas transformée.</p></div>
      <div class="card dark"><span class="num">2</span><h3>La masse critique est atteinte</h3><p>Quand le nombre de Backers et le cumul de leurs intentions franchissent un seuil, le partenaire agréé contacte la société et lui présente cette demande.</p></div>
      <div class="card dark"><span class="num">3</span><h3>Le partenaire agréé structure</h3><p>Si les attentes de la société et celles des Backers convergent, il construit une opération et la présente directement aux Backers concernés.</p></div>
      <div class="card dark"><span class="num">4</span><h3>Closing</h3><p>Levée ou cession de titres existants&nbsp;: les petits tickets sont regroupés dans un véhicule commun créé par le partenaire agréé. Chaque Backer décide d’y participer ou non.</p></div>
    </div>
    <p class="steps-note">Uback ne conseille pas, ne négocie pas, n’encaisse rien. Chaque opération est menée par le partenaire agréé, sous le droit indiqué sur la fiche de la société.</p>
    <div class="cta-row">
      <a class="btn gold" href="#suivre">Être prévenu à l’ouverture des intentions</a>
      <a class="btn ghost" href="/methode.html#apres">Que se passe-t-il après ma déclaration ?</a>
      <span>Ouverture des déclarations d’intention dès la signature du partenaire agréé · prix par tranche de ticket · validité 12 mois · crédit transférable</span>
    </div>
  </div>
</section>

<section id="partenaire-home">
  <div class="wrap">
    <div class="partner">
      <div>
        <span class="k">Le partenaire Uback au Maroc</span>
        <h2>Mises en relation assurées par un partenaire agréé, en cours de sélection</h2>
        <p>Conseiller en investissements financiers agréé par l’AMMC ou banque d’affaires, seul habilité à contacter les sociétés et à structurer les deals. Uback reste un média : il classe et agrège les intentions, il n’intervient dans aucune transaction.</p>
        <div class="pstats"><div><b>—</b>dossiers travaillés</div><div><b>—</b>deals conclus</div><div><b>—</b>délai moyen de réponse</div></div>
      </div>
      <div class="offer">
        <span class="k">Banques d’affaires, boutiques M&amp;A, conseils agréés</span>
        <h3>Devenez le partenaire exclusif Uback au Maroc</h3>
        <ul>
          <li>Des investisseurs étrangers que vous ne trouveriez pas seul</li>
          <li>Votre nom sur chaque classement du pays</li>
          <li>Un tableau des intentions par secteur et par société, réservé à vous</li>
          <li>Un kit de prospection trimestriel pour vos propres clients</li>
        </ul>
        <a class="btn navy" href="/partenaire.html">Découvrir le partenariat</a>
        <span class="fine">Contrat annuel, exclusivité par pays. Uback apporte des investisseurs et de la visibilité, pas un flux de deals garanti.</span>
      </div>
    </div>
  </div>
</section>

<section class="soft" id="radar">
  <div class="wrap">
    <div class="two">
      <div class="box line">
        <h3>Radar · sociétés éligibles connues, non classées</h3>
        <p>Triées par date de dernière levée, sans jugement ni appel d’IA. Montant non divulgué : la levée est confirmée par la presse, pas son montant.</p>
        <ul class="list">
        {''.join(f'<li><span><b>{e(r["nom"])}</b> · {e(r["sous_secteur"])}</span><span>{e(r["derniere_levee"])} · <a href="{e(r["source"])}" rel="nofollow noopener" target="_blank">source</a></span></li>' for r in D['radar'])}
        </ul>
        <h3 id="nees-ici" style="margin-top:22px">Nées au Maroc, établies ailleurs</h3>
        <p>Sociétés d’origine marocaine dont les opérations principales sont désormais à l’étranger : hors classement, avec le droit qui régit leurs titres.</p>
        <ul class="list">
        {''.join(f'<li><span><b>{e(r["nom"])}</b> · {e(r["sous_secteur"])}<br><span class="src">{e(r["lieu"])}</span></span><span>{e(r["derniere_levee"])} · <a href="{e(r["source"])}" rel="nofollow noopener" target="_blank">source</a></span></li>' for r in D['nees_ici'])}
        </ul>
        <h3 style="margin-top:22px">Hors classement</h3>
        <ul class="list">
        {''.join(f'<li><span><b>{e(r["nom"])}</b> · {e(r["motif"])}</span><span><a href="{e(r["source"])}" rel="nofollow noopener" target="_blank">source</a></span></li>' for r in D['hors_classement'])}
        </ul>
      </div>
      <div>
        <div class="box line" id="suivre">
          <h3>Recevoir le classement chaque mois</h3>
          <p>Gratuit. Les mouvements, les entrées, les désaccords entre IA, et l’ouverture des déclarations d’intention.</p>
          <form class="follow" name="suivre-maroc" method="POST" action="/merci.html" data-netlify="true" netlify-honeypot="bot-field"{' data-mailto="' + FORM_EMAIL + '"' if FORM_MODE == 'mailto' else ''}>
            <input type="hidden" name="form-name" value="suivre-maroc">
            <input type="hidden" name="marche" value="ma">
            <p class="skip"><label>Ne pas remplir : <input name="bot-field"></label></p>
            <label class="skip" for="email">Votre e-mail</label>
            <input id="email" name="email" type="email" required placeholder="votre@email.com" autocomplete="email">
            <select name="profil" aria-label="Votre profil" style="padding:11px 12px;border:1px solid #d9dee5;border-radius:8px;font-size:14px;font-family:inherit">
              <option value="investisseur">Investisseur</option>
              <option value="dirigeant">Dirigeant de startup</option>
              <option value="banque">Banque d’affaires / conseil</option>
              <option value="autre">Autre</option>
            </select>
            <button class="btn navy" type="submit">Suivre</button>
          </form>
          <p class="src" style="margin-top:10px">Un e-mail par mois. Désinscription en un clic. Aucune donnée transmise à des tiers.</p>
          <script>
          (function(){{var f=document.querySelector('form[data-mailto]');if(!f)return;
          f.addEventListener('submit',function(ev){{ev.preventDefault();
            var em=f.email.value,pr=f.profil.options[f.profil.selectedIndex].text;
            var body='Bonjour,\\n\\nJe souhaite recevoir chaque mois le classement Uback Maroc.\\n\\nE-mail : '+em+'\\nProfil : '+pr+'\\n';
            window.location.href='mailto:'+f.dataset.mailto+'?subject='+encodeURIComponent('Suivre le classement Uback Maroc')+'&body='+encodeURIComponent(body);
            setTimeout(function(){{window.location.href='/merci.html';}},1500);}});}})();
          </script>
        </div>
        <div class="box" style="margin-top:20px">
          <h3>Vous dirigez l’une de ces sociétés ?</h3>
          <p>Revendiquez votre fiche pour publier vos KPI, corriger une information ou déclarer une intention de lever des fonds. Gratuit.</p>
          <a class="btn" href="/methode.html#correction">Revendiquer ou corriger une fiche</a>
        </div>
      </div>
    </div>
  </div>
</section>
''' + FOOT

# ---------------------------------------------------------------- méthode
methode = head("Méthode et règles du jeu | Uback Maroc", "Comment Uback classe les startups : consensus d'IA, éligibilité, indice de confiance, droit de réponse. Uback classe, ne valorise pas.", "/methode.html") + '''
<div class="wrap prose">
<h1>Méthode et règles du jeu</h1>
<p class="lead">Uback est un algorithme avant d’être un site. Sa crédibilité repose sur des règles simples, publiques, identiques dans tous les pays et appliquées sans exception.</p>

<h2>Les règles du jeu</h2>
<ol>
<li><b>Uback classe, ne valorise pas.</b> Aucune valorisation n’est estimée par Uback ; seules des valeurs publiques, datées et sourcées sont affichées (montants levés, dernière levée annoncée).</li>
<li><b>Un classement n’est jamais à vendre.</b> Aucun paiement, d’une société, d’un partenaire ou d’un analyste, n’influence une position. Le référencement payant (« Challengers ») est affiché à part, étiqueté comme tel, et n’entre jamais dans le classement.</li>
<li><b>Aucun humain ne modifie l’ordre.</b> Un validateur peut exclure une société pour un motif d’éligibilité, tracé, ou relancer le calcul ; jamais réordonner.</li>
<li><b>Uback ne démarche jamais.</b> Tout contact sortant vers une société, un dirigeant ou un actionnaire passe par le partenaire agréé du pays.</li>
<li><b>Uback n’est pas un intermédiaire financier.</b> Aucun mandat, aucune négociation, aucun conseil, aucun encaissement de fonds destinés à un investissement.</li>
<li><b>Les données ne sortent pas.</b> Les intentions de cession sont confidentielles ; aucune donnée n’est vendue ni transmise à des tiers, hors le partenaire local avec le consentement du déclarant.</li>
<li><b>Tout est publié, tout est tracé.</b> IA interrogées, date, règle de consensus, critères d’éligibilité sont publics ; chaque société dispose d’un droit de réponse.</li>
<li><b>Aucune fausse promesse.</b> Chaque société affiche son statut d’accès. Une intention non transformée est un crédit transférable.</li>
</ol>

<h2>Comment le classement est établi</h2>
<p>Chaque mois, la même question est posée à plusieurs intelligences artificielles pour chaque pays et chaque secteur : quelles sont les sociétés éligibles les mieux valorisées, dans l’ordre ? Les réponses sont fusionnées en un classement de consensus (par points : 1er = 20 points, 2e = 19, etc.). Un indice de confiance est affiché pour chaque position : quand les IA sont d’accord, le classement est solide ; quand elles divergent, la divergence devient elle-même une information.</p>
<p><b>Édition 0 (bêta).</b> Cette première édition a été établie par une seule IA (Claude, Anthropic), à partir d’une recherche documentaire sur la presse et les annonces de levées de fonds, chaque montant étant sourcé. L’indice de confiance y reflète la qualité des sources disponibles. Le consensus multi-IA s’applique à partir de l’édition 1.</p>

<h2>Règles d’éligibilité</h2>
<table>
<tr><th>Règle</th><th>Application</th></tr>
<tr><td>Société technologique ou innovante</td><td>Périmètre de départ ; l’arborescence des secteurs est publique et évolutive.</td></tr>
<tr><td>Une activité principale, un seul secteur</td><td>Les conglomérats et sociétés multi-activités sont exclus. Une société n’apparaît que dans un seul classement.</td></tr>
<tr><td>A levé des fonds</td><td>Au moins 500 k$ (ou l’équivalent) en fonds propres ou en dette, vérifiables (annonce publique, registre, ou attestation du partenaire). Une subvention n’est pas une levée. La dette est distinguée des fonds propres.</td></tr>
<tr><td>Non cotée</td><td>Les sociétés cotées sont des repères, affichés séparément, jamais classées.</td></tr>
<tr><td>Active</td><td>Une société rachetée, fermée ou en procédure collective sort du classement ; l’historique conserve ses positions.</td></tr>
<tr><td>Opérations principales dans le pays</td><td>Le pays d’un classement est celui des opérations (équipe, marché), quel que soit le siège juridique. Le siège et le droit applicable aux titres sont indiqués sur la fiche. Les sociétés d’origine locale opérées à l’étranger figurent dans « Nées ici, établies ailleurs ».</td></tr>
</table>

<h2>Le statut d’accès</h2>
<table>
<tr><th>Statut</th><th>Signification</th></tr>
<tr><td>Cotée</td><td>En bourse : aucune intention possible.</td></tr>
<tr><td>Non déclaré</td><td>Aucun signal d’ouverture du capital sur Uback. Un Backer qui déclare une intention le fait en connaissance de cause, et pourra déplacer son crédit.</td></tr>
<tr><td>Ouverte</td><td>Un dirigeant a déclaré une intention de lever des fonds, ou un actionnaire une intention de céder.</td></tr>
<tr><td>Travaillée</td><td>Le partenaire agréé a un dossier en cours.</td></tr>
</table>

<h2 id="apres">Que se passe-t-il après ma déclaration ?</h2>
<p>Une déclaration d’intention est payante (prix par pays et par tranche de ticket), valable douze mois, et transférable : tant qu’elle n’a pas été transformée, vous pouvez la supprimer et reporter son crédit sur une autre société ou un secteur. Uback ne promet pas un deal. Il promet que votre intention, agrégée à celles des autres Backers, compte dans la masse critique&nbsp;: quand le nombre de Backers et le cumul de leurs intentions franchissent un seuil, le partenaire agréé du pays contacte la société et lui présente cette demande. Si les attentes de la société et celles des Backers convergent, il structure une opération et la présente directement aux Backers concernés, sous son nom et sous sa responsabilité réglementaire. Les petits tickets sont regroupés dans un véhicule commun créé par le partenaire agréé&nbsp;; chaque Backer décide d’y participer ou non. Au Maroc, les déclarations d’intention ouvriront dès la signature du partenaire.</p>

<h2 id="correction">Droit de réponse et corrections</h2>
<p>Toute société citée peut demander la correction d’une information (montant, date, secteur, statut), contester sa position ou demander son retrait, en écrivant à <a href="mailto:corrections@uback.com">corrections@uback.com</a>. Chaque demande reçoit une réponse motivée. Les dirigeants peuvent revendiquer la fiche de leur société pour y publier leurs indicateurs et déclarer une intention de lever des fonds.</p>

<h2>Sources</h2>
<p>Presse économique et technologique (Médias24, Le Desk, TelQuel, L’Economiste, Challenge, LesEco, Le Matin, Agence Ecofin, TechCrunch, TechCabal, Wamda, Disrupt Africa), rapports Partech Africa et UM6P Ventures, communiqués des investisseurs. Chaque montant du classement renvoie à sa source.</p>
</div>
''' + FOOT

# ---------------------------------------------------------------- partenaire
partenaire = head("Devenir le partenaire exclusif Uback au Maroc | Uback", "Banques d'affaires, boutiques M&A, conseils agréés : Uback vous apporte des investisseurs étrangers et de la visibilité, en exclusivité par pays.", "/partenaire.html") + '''
<div class="wrap prose">
<h1>Devenir le partenaire exclusif Uback au Maroc</h1>
<p class="lead">Uback classe les startups d’un pays et agrège les intentions d’investissement de business angels, family offices et diasporas, en Europe, dans le Golfe et ailleurs. Un seul partenaire par pays exécute : c’est vous.</p>

<h2>Ce que Uback vous apporte</h2>
<ul>
<li><b>Des investisseurs que vous ne trouveriez pas seul.</b> Les intentions déclarées sur votre marché vous sont réservées : montants, secteurs, sociétés convoitées, avec l’identité des Backers qui ont consenti à être mis en relation.</li>
<li><b>De la visibilité.</b> Votre nom, votre statut réglementaire et votre numéro d’immatriculation apparaissent sur chaque classement du pays (« Mises en relation assurées par… »), et sur votre page partenaire.</li>
<li><b>Un tableau de bord.</b> Alertes quand les intentions sur une société ou un secteur franchissent le seuil, suivi des dossiers, trace de chaque contact.</li>
<li><b>Un kit de prospection trimestriel.</b> Une synthèse des intentions de votre marché, à envoyer à vos propres clients.</li>
<li><b>Une voix.</b> Vous pouvez publier des notes sous votre nom sur votre marché.</li>
</ul>

<h2>Ce que Uback ne vous apporte pas</h2>
<p>Un flux de deals garanti. Dans un marché comme le Maroc, avec quelques dizaines de tours par an tous acteurs confondus, Uback est un canal d’investisseurs et de notoriété supplémentaire, pas une source de revenus immédiate. Nous préférons le dire avant.</p>

<h2>Le cadre</h2>
<ul>
<li><b>Exclusivité par pays</b>, contrat annuel renouvelable et renégociable selon l’audience.</li>
<li><b>Vous restez seul maître des actes réglementés :</b> contact des sociétés, mandats, conseil, structuration, négociation, encaissement. Uback ne fait rien de tout cela.</li>
<li><b>Rémunération :</b> une redevance annuelle, avance sur les rétrocessions dues sur les deals conclus avec des Backers présentés par Uback.</li>
<li><b>Profil recherché :</b> conseiller en investissements financiers agréé par l’AMMC, banque d’affaires ou boutique M&amp;A, avec une pratique du non-coté et de l’anglais.</li>
</ul>

<h2 id="challengers">Pour les dirigeants : les Challengers</h2>
<p>Une société éligible qui ne figure pas dans le classement pourra, contre paiement, s’afficher dans une liste séparée et étiquetée « Challengers », pour une durée déterminée, avec un mémo accessible aux Backers vérifiés. Le référencement n’a aucun effet sur le classement. Ouverture après la signature du partenaire.</p>

<h2>Nous contacter</h2>
<p>Écrivez à <a href="mailto:partenaires@uback.com">partenaires@uback.com</a>. Nous vous enverrons le dossier partenaire (modèle économique, contrat type, calendrier) et conviendrons d’un échange.</p>
</div>
''' + FOOT

# ---------------------------------------------------------------- mentions légales
mentions = head("Mentions légales | Uback", "Mentions légales du site Uback.", "/mentions-legales.html") + '''
<div class="wrap prose">
<h1>Mentions légales</h1>
<h2>Éditeur</h2>
<p>DEALING-ROOM SARL, SARL au capital de 50 000 € enregistrée en France au RCS de Créteil sous le numéro 485313712. Directeur de la publication : Sebastien Blanchard. Contact : <a href="mailto:contact@uback.com">contact@uback.com</a>.</p>
<h2>Hébergement</h2>
<p>GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis. Site : <a href="https://github.com">github.com</a>.</p>
<h2>Nature du service</h2>
<p>Uback est un éditeur de contenu. Les classements publiés sont des opinions produites par des systèmes d’intelligence artificielle à partir d’informations publiques, selon une méthode publiée. Ils ne constituent ni un conseil en investissement, ni une recommandation personnalisée, ni une sollicitation ou une offre de titres. Uback ne reçoit aucun mandat, ne négocie aucune transaction et n’encaisse aucun fonds destiné à un investissement. Les mises en relation sont réalisées par un partenaire agréé, identifié sur chaque marché, sous sa seule responsabilité réglementaire.</p>
<h2>Droit de réponse</h2>
<p>Toute société citée peut demander la correction ou le retrait d’une information la concernant à <a href="mailto:corrections@uback.com">corrections@uback.com</a>.</p>
<h2>Données personnelles</h2>
<p>Les adresses e-mail collectées via le formulaire de suivi servent uniquement à l’envoi du classement mensuel et des informations sur l’ouverture du service. Elles ne sont ni vendues ni transmises à des tiers. Désinscription possible à tout moment. Responsable du traitement : DEALING-ROOM SARL. Droits d’accès, de rectification et d’effacement : <a href="mailto:privacy@uback.com">privacy@uback.com</a>.</p>
<h2>Propriété intellectuelle</h2>
<p>Les classements, textes et éléments graphiques du site sont la propriété de DEALING-ROOM SARL. La reproduction d’un classement est autorisée avec mention de la source et lien vers la page d’origine. Les noms de sociétés cités appartiennent à leurs propriétaires.</p>
</div>
''' + FOOT

merci = head("Merci | Uback Maroc", "Inscription confirmée.", "/merci.html") + '''
<div class="wrap prose" style="padding:60px 24px">
<h1>Merci, c’est noté.</h1>
<p class="lead">Si votre messagerie s’est ouverte, envoyez simplement le message préparé : vous recevrez le classement marocain chaque mois, et un mot dès l’ouverture des déclarations d’intention.</p>
<p>Sinon, écrivez-nous à <a href="mailto:@FORM_EMAIL@">@FORM_EMAIL@</a> avec pour objet « Suivre le classement Uback Maroc ».</p>
<p><a class="btn navy" href="/">Retour au classement</a></p>
</div>
''' + FOOT
merci = merci.replace('@FORM_EMAIL@', FORM_EMAIL)

def under_prefix(page):
    """Les gabarits écrivent des chemins absolus (/methode.html, /assets/…) : on les place sous /ma."""
    page = re.sub(r'((?:href|src|action)=")/(?!/)', rf'\1{PREFIX}/', page)
    page = page.replace('href="@HOME@"', 'href="/"')   # le logo Uback, lui, ramène à la homepage monde
    page = page.replace('href="@ROOT@', 'href="/')     # sélecteur de pays : liens vers les autres marchés
    return page.replace("location.href='/", f"location.href='{PREFIX}/")

# robots.txt, sitemap.xml, CNAME et netlify.toml sont à la racine et se maintiennent à la main.
for name, content in [('index.html', index), ('methode.html', methode), ('partenaire.html', partenaire), ('mentions-legales.html', mentions), ('merci.html', merci)]:
    open(f'{OUT}/{name}', 'w', encoding='utf-8', newline='\n').write(under_prefix(content))
