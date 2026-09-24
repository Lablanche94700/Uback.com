# Uback – site public

**AI rankings, challenged by humans.**

Site statique de Uback, publié par GitHub Pages sur https://uback.com (provisoirement : le site du marché marocain occupe la racine ; il migrera vers `ma.uback.com` quand le sous-domaine sera créé).

Contenu : classement « Édition 0 – bêta » des 20 startups marocaines les mieux valorisées, radar, repères, méthode et règles du jeu, page partenaire, mentions légales.

## Structure

```
index.html              ← accueil Maroc : classement, radar, Backers, partenaire
methode.html            ← méthode, règles du jeu, éligibilité, droit de réponse
partenaire.html         ← pitch pour le futur partenaire exclusif
mentions-legales.html   ← à compléter (adresse, RCS, hébergeur)
merci.html              ← confirmation du formulaire de suivi
assets/                 ← style.css (marine #1E3A5F, or #C8A052, Inter), favicons, image de partage
data/classement-ma-2026-09.json   ← la donnée du classement (une entrée par société, source par montant)
tools/build_site.py     ← génère les pages HTML à partir du JSON
CNAME                   ← domaine servi par GitHub Pages
netlify.toml            ← prêt pour une migration vers Netlify (formulaire natif)
```

Les pages HTML ne se modifient pas à la main : on modifie le JSON ou le générateur, puis on relance `python3 tools/build_site.py` (Python 3 standard, aucune dépendance).

## Mettre à jour le classement

1. Modifier `data/classement-ma-2026-09.json` (ou créer le fichier du mois suivant et changer son nom dans `tools/build_site.py`).
2. Lancer `python3 tools/build_site.py`.
3. Committer et pousser sur `main` : GitHub Pages republie en une à deux minutes.

Règle du jeu n° 3 : l'ordre n'est jamais modifié à la main. Une société peut être exclue pour un motif d'éligibilité (tracé dans le JSON via `note`), jamais réordonnée.

## Formulaire « Recevoir le classement chaque mois »

GitHub Pages ne traite pas les formulaires. En attendant Netlify, le formulaire ouvre la messagerie du visiteur avec un message prérempli vers `contact@uback.com` (`FORM_MODE = 'mailto'` dans le générateur). Sur Netlify, passer `FORM_MODE = 'netlify'` : le formulaire `suivre-maroc` est alors détecté automatiquement.

## Reste à faire

- Créer les adresses `contact@`, `corrections@`, `partenaires@`, `privacy@uback.com` (redirections suffisent).
- Remplir `mentions-legales.html` (crochets).
- Sous-domaine `ma.uback.com` puis `uback.com` comme page monde.
- Édition 1 : consensus multi-IA (Claude, Gemini, ChatGPT), indice de confiance, pages société et secteur, EN puis AR.
