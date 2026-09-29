# Uback – site public

**Funded startups, ranked by AI.**

Site statique de Uback, publié par GitHub Pages sur https://uback.com. La racine porte la homepage monde (en anglais) ; chaque marché vit dans son dossier, en commençant par le Maroc dans `/ma`.

Contenu du Maroc : classement « Édition 0 – bêta » des 20 startups marocaines les mieux valorisées, radar, repères, méthode et règles du jeu, page partenaire, mentions légales.

## Structure

```
index.html              ← homepage monde (anglais), générée par tools/build_home.py : ne pas modifier à la main
data/sectors.json       ← arborescence des classements mondiaux (famille > secteur > segment), source unique
method.html, fr/methode.html      ← méthode et règles du jeu GLOBALES (anglais / français), communes à tous les pays
legal-notice.html, mentions-legales.html ← mentions légales globales (anglais / français)
correction.html, fr/correction.html ← formulaire de correction global (CORRECTION_MODE dans tools/build_home.py :
                          'mailto' → message structuré « Champ : valeur » vers contact@uback.com ; 'netlify' → formulaire
                          natif « correction ») ; préremplissable : ?company=…&country=ma
thank-you.html, fr/merci.html ← confirmation du formulaire de correction (noindex)
                        (ces pages sont générées par tools/build_home.py, texte de la méthode dans tools/pages_global.py)
methode.html, partenaire.html, merci.html
                        ← redirections (anciennes adresses, à garder) vers /fr/methode.html et /ma/fr/…
assets/                 ← favicons et ancienne image de partage, pour la racine
data/classement-ma-2026-09.json   ← copie à l'ancien chemin, pour ne casser aucun lien
sitemap.xml, robots.txt ← maintenus à la main (racine + pages /ma)
CNAME                   ← domaine servi par GitHub Pages
netlify.toml            ← prêt pour une migration vers Netlify (formulaire natif)

ma/                     ← site Maroc, entièrement généré : anglais à la racine (/ma/, version principale),
                          français dans /ma/fr/ ; textes anglais des données dans data/classement-ma-*.en.json
                          (couche de traduction : les chiffres restent dans le fichier français de référence) ;
                          les anciennes pages françaises de /ma/ redirigent vers /ma/fr/
  index.html            ← accueil : classement, radar, Backers, partenaire, encadré « La méthode au Maroc »
                          (calendrier, seuil, partenaire recherché, sources) qui renvoie à la méthode globale
  partner.html / fr/partenaire.html ← pitch pour le futur partenaire exclusif (propre à chaque pays)
  thank-you.html / fr/merci.html    ← confirmation du formulaire de suivi (noindex)
  method.html, legal-notice.html, fr/methode.html, fr/mentions-legales.html
                        ← redirections vers les pages globales (anciennes adresses)
  assets/               ← style.css (marine #1E3A5F, or #C8A052, Inter), favicons, image de partage
  data/classement-ma-2026-09.json ← la donnée du classement (une entrée par société, source par montant)

pl/, vn/                ← sites Pologne et Vietnam (anglais), même structure que le Maroc, entièrement générés :
  index.html, partner.html, thank-you.html, assets/ (copies depuis ma/), data/ ;
  method.html et legal-notice.html redirigent vers les pages globales

tools/build_site.py     ← réglages de chaque marché (langue, top_n, pays, diaspora, secteurs, partenaire, presse…)
tools/site.py           ← gabarit unique de tous les marchés ; textes d'interface en français et en anglais (TXT)
tools/og-image-<code>.html ← source de <code>/assets/og-image.png (image de partage 1200×630)
tools/pages_global.py   ← texte de la méthode et des mentions légales globales (français / anglais)
tools/build_segments.py ← classements mondiaux par segment (/segments/<slug>/, depuis data/segments/<slug>.json)
tools/build_home.py     ← génère index.html et les pages globales ; homepage : classements mondiaux par secteur (depuis data/sectors.json)
                          et classements par pays / régionaux (liste REGIONS en tête du script)
```

Ajouter un marché : créer `<code>/data/classement-<code>-AAAA-MM.json` (mêmes clés que le Maroc), l'ajouter à
`MARKETS` dans `tools/build_site.py`, lancer `python3 tools/build_site.py <code>`, puis le passer en « live » dans
`REGIONS` de `tools/build_home.py`, lancer `python3 tools/build_home.py`, et ajouter ses pages dans `sitemap.xml`.
`ma/assets/style.css` reste la seule feuille de style des marchés.

## Homepage et classements mondiaux par secteur

`python3 tools/build_home.py` réécrit `index.html` (HTML statique, tous les noms de familles, secteurs et segments
présents pour le référencement ; le JavaScript ne sert qu'à la recherche, aux onglets mobiles et au formulaire).
Arborescence : `data/sectors.json`, trois niveaux fixes (famille > secteur > segment) ; seul le segment est classé ;
identifiant `FAMILLE-nn-nn`, slug anglais stable. Un segment est publié automatiquement (lien vers
`/segments/<slug>/`) dès qu'un fichier `data/segments/<slug>.json` existe.

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

Classements pays : **trimestriels**, publiés le 15, un pays par mois pour que Uback publie chaque mois
(Vietnam : janv., avr., juil., oct. ; Maroc : févr., mai, août, nov. ; Pologne : mars, juin, sept., déc.).
Réglages `cadence`, `publish_day`, `publish_months` dans `MARKETS` (`tools/build_site.py`) ; la fonction
`next_edition()` calcule la prochaine date, affichée sur les pages marchés et sur la homepage. La date affichée
est celle du jour de la génération : relancer les deux scripts après chaque édition.
Classements mondiaux par secteur : **semestriels** (1er janvier, 1er juillet).

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

- Créer les adresses `contact@`, `corrections@`, `partner@`, `privacy@uback.com` (redirections suffisent).
- Édition 1 : consensus multi-IA (Claude, Gemini, ChatGPT), indice de confiance, pages société et secteur, EN puis AR.
