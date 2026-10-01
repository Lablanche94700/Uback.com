# Uback – site public

**Funded startups, ranked by AI.**

Site statique de Uback, publié par GitHub Pages sur https://uback.com. La racine porte la homepage monde (en anglais) ; chaque marché vit dans son dossier, en commençant par le Maroc dans `/ma`.

Contenu du Maroc : classement « Édition 0 – bêta » des 20 startups marocaines les mieux valorisées, radar, repères, méthode et règles du jeu, page partenaire, mentions légales.

## Structure

```
index.html              ← homepage monde (anglais), générée par tools/build_home.py : ne pas modifier à la main
data/sectors.json       ← arborescence des classements mondiaux (famille > secteur > segment), source unique
data/geo.json           ← géographie, source unique : pays (statut, tier, densité), 7 régions et 14 sous-régions, collections
                          (UE, UEMOA) ; ne jamais modifier une donnée à la main, toute règle d'affichage s'en calcule
data/calendar.json      ← calendrier annuel théorique (sortie de tools/build_calendar.py : ne pas modifier à la main)
regions/<slug>/         ← pages de zone (7 régions, 14 sous-régions), générées par tools/build_regions.py
collections/<slug>/     ← pages de collection (european-union, uemoa), générées par tools/build_regions.py
calendar/               ← calendrier des publications (anglais) + export calendar/uback-calendar.ics, par tools/build_home.py
faq/, fr/faq/           ← FAQ (anglais / français, balisage FAQPage), texte dans tools/pages_global.py
method.html, fr/methode.html      ← méthode et règles du jeu GLOBALES (anglais / français), communes à tous les pays
legal-notice.html, mentions-legales.html ← mentions légales globales (anglais / français)
correction.html, fr/correction.html ← formulaire de correction global (CORRECTION_MODE dans tools/build_home.py :
                          'mailto' → message structuré « Champ : valeur » vers contact@uback.com ; 'netlify' → formulaire
                          natif « correction ») ; préremplissable : ?company=…&country=ma
thank-you.html, fr/merci.html ← confirmation du formulaire de correction (noindex)
partner.html, fr/partenaire.html ← page partenaire UNIQUE (règle n° 1 : partenaires locaux, un par pays, chacun avec un ou
                          plusieurs secteurs ; success fee partagé sur les opérations transfrontalières) ; le pays s'adapte à
                          la page d'appel (?country=ma, sinon la page d'origine) ; blocs pays calculés depuis MARKETS
contact.html, fr/contact.html ← formulaire de contact (« Contact us » du pied de page), même envoi que la correction
                          (message structuré « Champ : valeur » vers contact@uback.com, puis page de remerciement)
                        (ces pages sont générées par tools/build_home.py, texte de la méthode dans tools/pages_global.py)
methode.html, partenaire.html, merci.html
                        ← redirections (anciennes adresses, à garder) vers /fr/methode.html et /ma/fr/…
assets/                 ← favicons et ancienne image de partage, pour la racine
data/classement-ma-2026-09.json   ← copie à l'ancien chemin, pour ne casser aucun lien
sitemap.xml, robots.txt ← maintenus à la main (racine, pays, segments, zones, collections, calendrier, FAQ)
CNAME                   ← domaine servi par GitHub Pages
netlify.toml            ← prêt pour une migration vers Netlify (formulaire natif)

ma/                     ← site Maroc, entièrement généré : anglais à la racine (/ma/, version principale),
                          français dans /ma/fr/ ; textes anglais des données dans data/classement-ma-*.en.json
                          (couche de traduction : les chiffres restent dans le fichier français de référence) ;
                          les anciennes pages françaises de /ma/ redirigent vers /ma/fr/
  index.html            ← accueil : classement, radar, Backers, partenaire, encadré « La méthode au Maroc »
                          (calendrier, seuil, partenaire recherché, sources) qui renvoie à la méthode globale
  partner.html / fr/partenaire.html ← redirections vers la page partenaire unique, ouverte sur le pays (?country=ma)
  thank-you.html / fr/merci.html    ← confirmation du formulaire de suivi (noindex)
  method.html, legal-notice.html, fr/methode.html, fr/mentions-legales.html
                        ← redirections vers les pages globales (anciennes adresses)
  assets/               ← style.css (marine #1E3A5F, or #C8A052, Inter), favicons, image de partage
  data/classement-ma-2026-09.json ← la donnée du classement (une entrée par société, source par montant)

pl/, vn/, fr/           ← sites Pologne, Vietnam et France (anglais), même structure que le Maroc, entièrement générés :
  index.html, thank-you.html, assets/ (copies depuis ma/), data/ ; partner.html redirige vers la page partenaire unique ;
  method.html et legal-notice.html redirigent vers les pages globales
fr/ est PARTAGÉ : le site France (build_site.py : index.html, thank-you.html, assets/, data/, et les redirections
  partner.html, method.html, legal-notice.html) y côtoie les pages globales en français de build_home.py (methode.html,
  investir.html, correction.html, merci.html, contact.html, partenaire.html, faq/). Aucun nom commun, aucun générateur ne
  supprime de fichier. /fr/ est le classement France (anglais), jamais « l'accueil en français » ; toute nouvelle page globale
  française doit éviter les noms du gabarit pays (index.html, partner.html, thank-you.html, method.html, legal-notice.html).

tools/build_site.py     ← réglages de chaque marché (langue, pays, diaspora, secteurs, partenaire, presse…)
tools/site.py           ← gabarit unique de tous les marchés ; textes d'interface en français et en anglais (TXT)
tools/og-image-<code>.html ← source de <code>/assets/og-image.png (image de partage 1200×630)
tools/pages_global.py   ← texte de la méthode et des mentions légales globales (français / anglais)
tools/build_segments.py ← classements mondiaux par segment (/segments/<slug>/, depuis data/segments/<slug>.json)
tools/build_home.py     ← génère index.html et les pages globales ; homepage : classements mondiaux par secteur (depuis data/sectors.json)
                          et classements par pays, en accordéon par région (depuis data/geo.json)
tools/build_calendar.py ← calcule data/calendar.json depuis data/geo.json et data/sectors.json
tools/build_regions.py  ← pages de zone et de collection (depuis data/geo.json et data/calendar.json)
tools/footer.py         ← pied de page unique de tout le site (HTML + CSS ; la CSS est recopiée dans ma/assets/style.css
                          entre les marqueurs « footer:start / footer:end » par build_site.py : ne pas la modifier là)
tools/geo.py            ← lecture commune de data/geo.json et data/calendar.json (zones, pays, prochaine date d'un classement)
```

Ordre de génération complet : `build_calendar.py`, `build_site.py`, `build_segments.py`, `build_regions.py`, puis
`build_home.py` (tous dans `tools/`, Python 3 standard).

**Ajouter un pays = passer son statut à `live` dans `data/geo.json`** (et renseigner son `url`), une fois sa première
édition prête : créer `<code>/data/classement-<code>-AAAA-MM.json` (mêmes clés que le Maroc), l'ajouter à `MARKETS` dans
`tools/build_site.py` (mois de publication = ceux du calendrier ; le script échoue sinon), relancer la génération complète
et ajouter ses pages dans `sitemap.xml`. Homepage, menu Rankings, pages de zone et calendrier suivent sans autre code.
Aucune page pays n'existe avant sa première édition : un pays `planned` reste une pastille « Coming soon ».
`ma/assets/style.css` reste la seule feuille de style des marchés.

## Homepage et classements mondiaux par secteur

`python3 tools/build_home.py` réécrit `index.html` (HTML statique, tous les noms de familles, secteurs et segments
présents pour le référencement ; le JavaScript ne sert qu'à la recherche, aux onglets mobiles et au formulaire).
Arborescence : `data/sectors.json`, trois niveaux fixes (famille > secteur > segment) ; seul le segment est classé ;
identifiant `FAMILLE-nn-nn`, slug anglais stable. Un segment est publié automatiquement (lien vers
`/segments/<slug>/`) dès qu'un fichier `data/segments/<slug>.json` existe.

En-tête de la homepage et des pages globales : menu « Rankings » / « Classements » (familles publiées → `/sectors/<famille>/`,
pays en ligne → leur page, plus « All sectors » / « All countries » vers la homepage, la Méthode mise en avant en bas
du menu, puis la FAQ) ; l'en-tête compte trois entrées, Rankings, Calendar et Invest. Calculé à chaque génération
(`rankings_menu()` dans `tools/build_home.py`).

Colonne « Country rankings » : accordéon par région (`data/geo.json`), sur le modèle des familles ; dans une région, les
pays rattachés directement, puis un intertitre cliquable par sous-région (→ `/regions/<slug>/`), les pays `live` en carte
et les pays `planned` en pastilles « Coming soon » ; les pays `radar`, la Chine et les pays exclus n'y figurent pas.
Ouverte par défaut : la région qui compte le plus de pays `live` (à égalité, celle du Maroc). Ligne « Collections » en bas.

## Pages de zone et de collection

`python3 tools/build_regions.py` génère `/regions/<slug>/` (régions et sous-régions) et `/collections/<slug>/`, même charte
que les pages famille : fil d'Ariane, chapô calculé, sous-régions, pays classés (live : lien et dates ; planned : « Coming
soon »), classement régional à venir et ses dates théoriques, radar de la zone, ligne Chine (East Asia, Asia), formulaire
de suivi prérempli sur la zone. Chaque page pays renvoie à sa zone (menu des pays) ; chaque page segment renvoie aux
zones de ses sociétés quand elles existent dans `data/geo.json`.

## Classements mondiaux par segment

`python3 tools/build_segments.py` génère `/segments/<slug>/index.html` pour chaque `data/segments/<slug>.json`
(exemple : `consumer-neobanks.json`). Un nouveau segment = un nouveau JSON, sans nouveau code. Même charte que les pages
pays (feuille `ma/assets/style.css`, copiée dans `segments/assets/`) ; filtres par zone (`#region=europe`…), rangs mondiaux
conservés. Le script échoue si le rang ne suit pas l'estimation interne (`estimate_usd`, décroissante) ou si une tranche
ne correspond pas à l'estimation ; `estimate_usd` et `note_internal` ne sont jamais affichés (vérifié à chaque génération).
Pages famille : le même script génère `/sectors/<famille>/` (ex. `/sectors/fintech/`) pour toute famille ayant au
moins un segment publié : segments par secteur (publiés ou à venir), licornes et décacornes par ordre alphabétique
(jamais de classement entre segments). Le menu « Fintech » des pages segment y renvoie. Ajouter la page au sitemap.
Intentions : par défaut, l'intérêt porte sur le pool du segment (bouton or de l'en-tête et du hero, lien
`/invest.html?pool=segment&segment=<slug>#opening`). Une intention sur une société n'apparaît que si elle est ouverte aux
Backers : champ facultatif `"open_to_backers": {"type": "secondary" | "raise", "since": "AAAA-MM"}` (actionnaire qui envisage
de céder, ou levée prévue ; vérifié par `check()`). La colonne « Open to Backers » n'est affichée que si au moins une société l'a.
Règle affichée partout (page Invest, sections Backers) : un intérêt sur un secteur ou un pays peut indiquer une société
préférée (signal transmis avec le pool, pas de pool société) ; une intention est valable à vie tant que son pool n'est pas
transmis au partenaire (masse critique = montant plancher estimé par l'IA pour chaque pool), puis engagée et non déplaçable.
Drapeaux : `tools/flags.py` (ajouter un pays si besoin). Image de partage rendue automatiquement (Edge) quand son
contenu change ; empreinte dans `tools/og-segments.json`. Après génération : relancer `tools/build_home.py`
et ajouter la page dans `sitemap.xml`.

Image de partage : modifier `tools/og-image-ma.html` (édition, mois), la capturer en 1200×630
(`msedge --headless=new --window-size=1200,630 --screenshot=og.png tools/og-image-ma.html`),
la copier dans `ma/assets/og-image.png`, puis incrémenter `?v=` de `og:image` dans le générateur
pour que les réseaux sociaux rafraîchissent leur cache.

Les pages de `ma/` ne se modifient pas à la main : on modifie le JSON ou le générateur, puis on relance `python3 tools/build_site.py` (Python 3 standard, aucune dépendance). Les gabarits écrivent des liens absolus (`/methode.html`) ; le générateur les place sous `/ma`.

## Calendrier des éditions

`python3 tools/build_calendar.py` calcule `data/calendar.json` (à relancer à chaque changement de la liste des pays ou des
segments) ; il doit afficher « 68 countries ×4 · 21 regional ×2 · 157 segments ×2 ». Dates fixes d'une année sur l'autre ;
calendrier **théorique**, appliqué à la sortie de bêta ; page `/calendar/` et export `.ics` générés par `tools/build_home.py`.
Classements pays : **trimestriels** ; ancres conservées (Vietnam le 15 janv./avr./juil./oct., Maroc le 15 févr./mai/août/nov.,
Pologne le 15 mars/juin/sept./déc.). `build_site.py` vérifie que `publish_months` (`MARKETS`) donne la même date que le
calendrier. Classements régionaux et mondiaux par segment : **semestriels**, aux dates du calendrier.

Sur chaque classement (pays, segment, famille), une ligne sous le titre : édition · « Published » (dernier verdict de l'IA :
`snapshot_date` des données pays, `published` des données segment ; famille : le plus récent de ses segments) ·
« Next scheduled update » (prochaine date du calendrier ; famille : la plus proche de ses segments). Le champ
`next_edition` des JSON segment n'est plus lu. Mise à jour hors calendrier : champ facultatif
`"out_of_cycle": {"date": "AAAA-MM-JJ", "reason": "…"}` dans la donnée d'un classement, affiché sous la ligne ;
l'édition prévue reste due. La date affichée est celle du jour de la génération : relancer la génération après chaque édition.

Libellé d'édition : celui du champ `edition` des données s'il existe (les éditions 0 gardent « Édition 0 – bêta »),
sinon le trimestre de publication, « Q4 2026 » / « T4 2026 ».

## Mettre à jour le classement

1. Créer le fichier de l'édition (ex. `ma/data/classement-ma-2026-11.json`, sans champ `edition` pour obtenir « T4 2026 »)
   et changer son nom dans `MARKETS` ; pour le Maroc, mettre aussi à jour la couche anglaise `*.en.json`.
2. Lancer `python3 tools/build_site.py` puis `python3 tools/build_home.py`.
3. Committer et pousser sur `main` : GitHub Pages republie en une à deux minutes.
Entre deux éditions, le Radar peut être mis à jour au fil des levées annoncées.

Colonne « Ouverte aux Backers » des pages pays, champ `acces` de chaque société : `defaut` (rien : l'intérêt porte sur le
pool du pays, `startups_label` dans `MARKETS`), `travaillee` (badge « Suivie par » si partenaire signé), `levee` (la société
prévoit de lever) et `cession` (un actionnaire envisage de céder) : badge, phrase et bouton d'intention sur la société ;
`sortie` (rachat, sans bouton). La colonne est masquée si aucune société n'a de contenu.

Règle du jeu n° 3 : l'ordre n'est jamais modifié à la main. Une société peut être exclue pour un motif d'éligibilité (tracé dans le JSON via `note`), jamais réordonnée.

## Formulaire « Recevoir chaque nouvelle édition »

**Inscriptions pas encore ouvertes** : `FORM_MODE = 'soon'` dans `tools/site.py` et `tools/build_home.py`. Le formulaire
reste affiché, mais un clic sur « Suivre / Follow » affiche « Bientôt disponible / Coming soon » ; rien n'est envoyé.
Pour ouvrir les inscriptions (futur branchement Mailchimp, par pays et par secteur), changer ce réglage puis régénérer.

GitHub Pages ne traite pas les formulaires. En attendant Netlify, le formulaire ouvre la messagerie du visiteur avec un message prérempli vers `contact@uback.com` (`FORM_MODE = 'mailto'` dans le générateur). Sur Netlify, passer `FORM_MODE = 'netlify'` : le formulaire `suivre-maroc` est alors détecté automatiquement.

## Reste à faire

Adresses e-mail (OVH MXPlan) : `contact@uback.com` (boîte, reçoit les formulaires de contact et de correction) et
`privacy@uback.com` (redirection vers contact@). Toute nouvelle adresse : une redirection ou un alias vers contact@,
pas un nouveau compte (l'offre en compte 5). Le site n'utilise aucune autre adresse.


- Édition 1 : consensus multi-IA (Claude, Gemini, ChatGPT), indice de confiance, pages société et secteur, EN puis AR.
