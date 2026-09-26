# Uback – site public

**Funded startups, ranked by AI.**

Site statique de Uback, publié par GitHub Pages sur https://uback.com. La racine porte la homepage monde (en anglais) ; chaque marché vit dans son dossier, en commençant par le Maroc dans `/ma`.

Contenu du Maroc : classement « Édition 0 – bêta » des 20 startups marocaines les mieux valorisées, radar, repères, méthode et règles du jeu, page partenaire, mentions légales.

## Structure

```
index.html              ← homepage monde (anglais), générée par tools/build_home.py : ne pas modifier à la main
data/sectors.json       ← arborescence des classements mondiaux (famille > secteur > segment), source unique
methode.html, partenaire.html, mentions-legales.html, merci.html
                        ← redirections vers /ma/… (anciennes adresses, à garder)
assets/                 ← favicons et ancienne image de partage, pour la racine
data/classement-ma-2026-09.json   ← copie à l'ancien chemin, pour ne casser aucun lien
sitemap.xml, robots.txt ← maintenus à la main (racine + pages /ma)
CNAME                   ← domaine servi par GitHub Pages
netlify.toml            ← prêt pour une migration vers Netlify (formulaire natif)

ma/                     ← site Maroc, entièrement généré
  index.html            ← accueil Maroc : classement, radar, Backers, partenaire
  methode.html          ← méthode, règles du jeu, éligibilité, droit de réponse
  partenaire.html       ← pitch pour le futur partenaire exclusif
  mentions-legales.html ← éditeur (sans adresse, volontairement) et hébergeur
  merci.html            ← confirmation du formulaire de suivi
  assets/               ← style.css (marine #1E3A5F, or #C8A052, Inter), favicons, image de partage
  data/classement-ma-2026-09.json ← la donnée du classement (une entrée par société, source par montant)

pl/, vn/                ← sites Pologne et Vietnam (anglais), même structure que le Maroc, entièrement générés :
  index.html, method.html, partner.html, legal-notice.html, thank-you.html, assets/ (copies depuis ma/), data/

tools/build_site.py     ← réglages de chaque marché (langue, top_n, pays, diaspora, secteurs, partenaire, presse…)
tools/site.py           ← gabarit unique de tous les marchés ; textes d'interface en français et en anglais (TXT)
tools/og-image-<code>.html ← source de <code>/assets/og-image.png (image de partage 1200×630)
tools/build_home.py     ← génère index.html : classements mondiaux par secteur (depuis data/sectors.json)
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
identifiant `FAMILLE-nn-nn`, slug anglais stable. Chaque segment a `"status": "soon"` ; pour publier un classement,
passer à `"status": "published"` et ajouter `"url"`, puis relancer le script (le segment devient un lien).

Image de partage : modifier `tools/og-image-ma.html` (édition, mois), la capturer en 1200×630
(`msedge --headless=new --window-size=1200,630 --screenshot=og.png tools/og-image-ma.html`),
la copier dans `ma/assets/og-image.png`, puis incrémenter `?v=` de `og:image` dans le générateur
pour que les réseaux sociaux rafraîchissent leur cache.

Les pages de `ma/` ne se modifient pas à la main : on modifie le JSON ou le générateur, puis on relance `python3 tools/build_site.py` (Python 3 standard, aucune dépendance). Les gabarits écrivent des liens absolus (`/methode.html`) ; le générateur les place sous `/ma`.

## Mettre à jour le classement

1. Modifier `ma/data/classement-ma-2026-09.json` (ou créer le fichier du mois suivant et changer son nom dans `tools/build_site.py`).
2. Lancer `python3 tools/build_site.py`.
3. Committer et pousser sur `main` : GitHub Pages republie en une à deux minutes.

Règle du jeu n° 3 : l'ordre n'est jamais modifié à la main. Une société peut être exclue pour un motif d'éligibilité (tracé dans le JSON via `note`), jamais réordonnée.

## Formulaire « Recevoir le classement chaque mois »

GitHub Pages ne traite pas les formulaires. En attendant Netlify, le formulaire ouvre la messagerie du visiteur avec un message prérempli vers `contact@uback.com` (`FORM_MODE = 'mailto'` dans le générateur). Sur Netlify, passer `FORM_MODE = 'netlify'` : le formulaire `suivre-maroc` est alors détecté automatiquement.

## Reste à faire

- Créer les adresses `contact@`, `corrections@`, `partenaires@`, `privacy@uback.com` (redirections suffisent).
- Édition 1 : consensus multi-IA (Claude, Gemini, ChatGPT), indice de confiance, pages société et secteur, EN puis AR.
