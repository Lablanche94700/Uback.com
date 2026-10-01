# -*- coding: utf-8 -*-
"""Gabarit unique des sites marchés (même structure pour tous les pays).
Ne pas lancer directement : tools/build_site.py l'exécute avec la configuration du marché dans M.
Les textes d'interface sont dans TXT (fr, en) ; tout ce qui est propre au pays vient de M ou des données.
Écrit uniquement dans le dossier du marché (ex. pl/), jamais à la racine."""
import json, html, os, re, shutil, datetime, copy
from urllib.parse import quote
import valuation
from footer import footer
from analytics import HEAD as GA_HEAD
from build_site import format_date_short
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # racine du dépôt = dossier publié
PREFIX = M['path']                  # chemin de cette version sur uback.com : /ma (anglais), /ma/fr (français)…
ASSETS = '/' + M['code'] + '/assets'   # feuille de style et images : partagées par les langues d'un marché
OUT = ROOT + PREFIX                 # seul dossier écrit par ce gabarit (ou ses sous-dossiers de langue)
DATA = f"{ROOT}/{M['code']}/data"
D = json.load(open(f"{DATA}/{M['data']}", encoding='utf-8'))
if M.get('overlay'):
    # couche de traduction : les textes dans la langue de la page, les chiffres restent ceux du fichier de référence
    T_ = json.load(open(f"{DATA}/{M['overlay']}", encoding='utf-8'))
    for k in ('edition', 'date_label', 'methode', 'seuil_levee', 'radar', 'nees_ici', 'nees_ailleurs', 'hors_classement', 'reperes_cotes'):
        if k in T_:
            D[k] = T_[k]
    D['marche'].update({k: v for k, v in T_.get('marche', {}).items()})
    for c in D['classement']:
        t = T_['classement'][c['nom']]
        vi = c.get('valuation_input')
        for k in ('sous_secteur', 'ville', 'leve_cumule', 'derniere_levee', 'juridiction', 'note'):
            c[k] = t[k]
        if vi:
            vi = c['valuation_input'] = copy.deepcopy(vi)
            vi['round_label'], vi['adjust_reason'] = t.get('round_label'), t.get('adjust_reason', '')
_MONTH = {'janv': 1, 'janvier': 1, 'jan': 1, 'january': 1, 'févr': 2, 'février': 2, 'feb': 2, 'february': 2,
          'mars': 3, 'mar': 3, 'march': 3, 'avr': 4, 'avril': 4, 'apr': 4, 'april': 4, 'mai': 5, 'may': 5,
          'juin': 6, 'jun': 6, 'june': 6, 'juil': 7, 'juillet': 7, 'jul': 7, 'july': 7, 'août': 8, 'aug': 8, 'august': 8,
          'sept': 9, 'septembre': 9, 'sep': 9, 'september': 9, 'oct': 10, 'octobre': 10, 'october': 10,
          'nov': 11, 'novembre': 11, 'november': 11, 'déc': 12, 'décembre': 12, 'dec': 12, 'december': 12}

def last_round_date(txt):
    """Date la plus récente citée dans « dernière levée » : (année, mois), mois = 0 si seule l'année est connue ; None sinon."""
    best = None
    for m in re.finditer(r'(?:([A-Za-zÀ-ÿ]+)\.?\s+)?~?((?:19|20)\d\d)\b', txt):
        d = (int(m.group(2)), _MONTH.get((m.group(1) or '').lower(), 0))
        best = d if best is None or d > best else best
    return best

# Radar : trié par date de dernière levée décroissante, pour toutes les éditions (méthode publiée)
D['radar'] = sorted(D['radar'], key=lambda r: (0, tuple(-x for x in last_round_date(r['derniere_levee'])))
                    if last_round_date(r['derniere_levee']) else (1,))

for c in D['classement']:
    # justification de la valorisation dans la langue de la page (même règle, mêmes chiffres)
    if c.get('valuation_input'):
        c.update(valuation.estimate(c['valuation_input'], D['date'], M['lang']))
BASE = 'https://uback.com' + PREFIX
# libellé d'édition : celui des données s'il existe (« Édition 0 – bêta »), sinon le trimestre de publication (« T4 2026 »)
_y, _mo = D['date'].split('-')
EDITION = D.get('edition') or f"{'T' if M['lang'] == 'fr' else 'Q'}{(int(_mo) - 1) // 3 + 1} {_y}"
FORM_MODE = 'soon'                  # 'soon' (inscriptions pas encore ouvertes : « Bientôt disponible » au clic),
                                    # 'mailto' (message prérempli vers FORM_EMAIL) ou 'netlify' (Netlify Forms)
FORM_EMAIL = 'contact@uback.com'
# nombre de places affiché = sociétés réellement classées (le classement peut être plus court que top_n)
N = min(M['top_n'], len(D['classement']))
RANKED = D['classement'][:N]
e = html.escape
cap = lambda s: s[:1].upper() + s[1:]


# ---------------------------------------------------------------- textes d'interface
# {name} Maroc · {in_} au Maroc · {In_} Au Maroc · {the} le Maroc · {adj_m} marocain · {adj_f} marocaine
# {adj_fp} marocaines · {N} places · {cities} Paris, Dubaï ou Montréal
TXT = {
'fr': dict(
  html_lang='fr', locale='fr_FR', skip='Aller au contenu', home_aria='Uback, accueil', nav_aria='Navigation principale',
  beta_b='Bêta · prototype', beta_t='Ce site est en construction : classements, textes et fonctionnalités évoluent chaque semaine.',
  p_method='methode.html', p_partner='partenaire.html', p_legal='mentions-legales.html', p_thanks='merci.html',
  id_rank='classement', id_sect='secteurs', id_follow='suivre', id_born='nees-ici', id_after='apres',
  nav_rank='Classement', nav_sect='Secteurs', nav_partner='Partenaire', nav_invest='Investir', nav_method='Méthode',
  soon='Bientôt disponible', follow='Suivre {the}', declare='Déclarer un intérêt', hero_cta='Déclarer un intérêt pour {startups}',
  f_method='Méthode et règles du jeu', f_partner='Devenir partenaire', f_corr='Demander une correction', f_legal='Mentions légales',
  f_disc='Uback est un éditeur de contenu. Il ne fournit aucun conseil en investissement, ne reçoit aucun mandat et n’intervient dans aucune transaction. Les mises en relation sont réalisées par un partenaire agréé, en cours de sélection {in_}. Investir dans des sociétés non cotées comporte un risque de perte totale du capital investi.',
  conf3='Sources solides', conf2='Sources partielles', conf1='Sources faibles',
  founded='fondée en', l_sub='Sous-secteur', l_fund='Levées', l_conf='Confiance', raised=' cumulés',
  declare_cell='Déclarer une intention', b_levee='Levée prévue', b_cession='Cession d’actionnaire',
  n_levee='La société a informé Uback qu’elle prévoit de lever prochainement.', n_cession='Un actionnaire a informé Uback qu’il envisage de céder.', b_suivie='Suivie par {{p}}', exit='Sortie', exit_by='Sortie – {{a}}',
  ld_name='Les {N} startups {adj_fp} les mieux valorisées – {date}',
  ld_desc="Classement trimestriel Uback des startups {adj_fp}, établi par IA à partir d'informations publiques. Le marché fixe la valeur ; notre IA l’estime.",
  title='Top {N} des startups {adj_fp} les mieux valorisées – {date} | Uback {name}',
  desc="Classement trimestriel des startups {adj_fp} non cotées ayant déjà levé des fonds, établi par IA à partir d'informations publiques. Le marché fixe la valeur ; notre IA l’estime.",
  h1='Les {N} startups {adj_fp} les mieux valorisées',
  lead='Un classement trimestriel des startups {adj_fp} non cotées ayant déjà levé des fonds, établi par intelligence artificielle à partir d’informations publiques. Le marché fixe la valeur ; notre IA l’estime.',
  th_val='Valorisation estimée (IA, ordre de grandeur)', l_val='Valorisation (IA)',
  vb_hundreds_k='Centaines de k$', vb_millions='Millions $', vb_tens_m='Dizaines de M$', vb_hundreds_m='Centaines de M$',
  vb_unicorn='Licorne', vb_decacorn='Décacorne', vb_not_estimated='Non estimé',
  vc_high='Confiance élevée', vc_medium='Confiance moyenne', vc_low='Confiance faible',
  report='Vous êtes cette société ? Signalez une erreur', report_subject='Signalement d’erreur – {{co}} – Uback {name}',
  val_disc='Les ordres de grandeur de valorisation sont des estimations éditoriales indicatives, produites par IA à partir d’informations publiques (montants levés, valorisations publiées, indicateurs cités). Ils ne constituent ni une évaluation financière, ni une offre, ni un conseil en investissement.',
  m_consensus='Claude · consensus multi-IA lors d’une prochaine édition', m_method='Méthode publiée', m_order='Ordre jamais modifié par un humain',
  glance='Le marché en un coup d’œil', s_ranked='sociétés classées', s_radar='sociétés sur le radar', s_raised='levés en 2025', s_rounds='tours en 2025',
  sources='Sources : ', counters=' Les compteurs d’intentions s’afficheront au-delà d’un seuil de montant et de nombre de Backers.',
  listed='Repères cotés', listed_note='Hors classement : aucune intention possible sur une société cotée.',
  h2_rank='Classement national · tous secteurs', t_born='Nées ici, établies ailleurs', first_ed='Première édition : pas encore de mouvements.',
  th_co='Société', th_sub='Sous-secteur', th_fund='Levées connues', th_conf='Confiance', th_invest='Ouverte aux Backers',
  disc_b='Ce classement est une opinion, pas une évaluation.',
  disc='Il est établi à partir d’informations publiques (presse, annonces de levées de fonds), selon une méthode publiée, sans intervention humaine sur l’ordre. L’indice de confiance reflète la qualité des sources. Toute société peut <a href="@ROOT@fr/methode.html#correction">demander une correction</a> ou contester sa position. Seuil d’éligibilité : au moins {seuil} levés, sociétés non cotées, opérations principales {in_}.',
  read_h2='Comment lire ce classement',
  read_rank_h='Rang', read_rank='Les sociétés sont classées par valorisation estimée par IA, la plus élevée en tête. Le marché fixe la valeur ; notre IA l’estime.',
  read_range_h='Tranche', read_range='Un ordre de grandeur, jamais un chiffre.',
  read_conf_h='Confiance', read_high='<b>Élevé :</b> valorisation ou tour publié de moins de 24 mois.', read_med='<b>Moyen :</b> données plus anciennes.',
  read_low='<b>Faible :</b> source unique ou non confirmée.', read_more='Méthode complète →',
  sect_h2='Classements par secteur', sect_sub='Quatre verticales au lancement, d’autres quand le test de faisabilité le permet.', sect_k='Bientôt · Top 10',
  inv_h2='Investir {in_}, à plusieurs, depuis {cities}',
  inv_lead='Uback agrège les intentions d’investissement des business angels, family offices, corporates et investisseurs de la diaspora. Vous investissez aux côtés d’investisseurs professionnels déjà au capital, qui ont négocié un pacte d’associés : vous ne partez pas d’une page blanche.',
  steps_h='Le nombre fait la force', steps_sub='Seul, un petit ticket n’ouvre aucune porte. Regroupés, les Backers pèsent.',
  s1h='Déclarez un intérêt', s1='Sur le pays ou l’un de ses secteurs, avec une fourchette de ticket, et si vous le souhaitez une société préférée. Payante, pour qualifier le sérieux&nbsp;; valable à vie et déplaçable vers un autre pool tant que son pool n’est pas transmis au partenaire.',
  s2h='La masse critique est atteinte', s2='Quand le montant cumulé du pool atteint sa masse critique, un montant plancher estimé par l’IA, le pool est transmis au partenaire agréé, qui présente cette demande à la société.',
  s3h='Le partenaire agréé structure', s3='Si les attentes de la société et celles des Backers convergent, il construit une opération et la présente directement aux Backers concernés.',
  s4h='Closing', s4='Levée ou cession de titres existants&nbsp;: les petits tickets sont regroupés dans un véhicule commun créé par le partenaire agréé. Chaque Backer décide d’y participer ou non.',
  steps_note='Uback ne conseille pas, ne négocie pas, n’encaisse rien. Chaque opération est menée par le partenaire agréé, sous le droit indiqué sur la fiche de la société.',
  cta_notify='Être prévenu à l’ouverture des intentions', cta_after='Que se passe-t-il après ma déclaration ?',
  cta_line='Ouverture des déclarations d’intention dès la signature du partenaire agréé · prix par tranche de ticket · valable à vie · déplaçable jusqu’à la transmission du pool',
  ph_k='Le partenaire Uback {in_}', ph_h2='Mises en relation assurées par un partenaire agréé, en cours de sélection',
  ph_p='{partner_short}, seul habilité à contacter les sociétés et à structurer les deals. Uback reste un média : il classe et agrège les intentions, il n’intervient dans aucune transaction.',
  ph_s1='dossiers travaillés', ph_s2='deals conclus', ph_s3='délai moyen de réponse',
  of_k='Banques d’affaires, boutiques M&amp;A, conseils agréés', of_h3='Devenez le partenaire exclusif Uback {in_}',
  of_l1='Des investisseurs étrangers que vous ne trouveriez pas seul', of_l2='Votre nom sur chaque classement du pays',
  of_l3='Un tableau des intentions par secteur et par société, réservé à vous', of_l4='Un kit de prospection trimestriel pour vos propres clients',
  of_btn='Découvrir le partenariat', of_fine='Contrat annuel, exclusivité par pays. Uback apporte des investisseurs et de la visibilité, pas un flux de deals garanti.',
  rad_h='Radar · sociétés éligibles connues, non classées', rad_p='Triées par date de dernière levée, sans jugement ni appel d’IA. Montant non divulgué : la levée est confirmée par la presse, pas son montant.',
  born_h='Nées {in_}, établies ailleurs', born_p='Sociétés d’origine {adj_f} dont les opérations principales sont désormais à l’étranger : hors classement, avec le droit qui régit leurs titres.',
  based_h='Nées ailleurs, établies {in_}', based_p='Sociétés fondées à l’étranger dont les opérations principales sont {in_}.',
  out_h='Hors classement',
  id_local='methode-locale', loc_h='La méthode {in_}',
  loc_cal='<b>Calendrier.</b> Classement trimestriel, publié le 15 {months}. Prochaine édition : {next}.',
  elig_h='Éligibilité.', elig='Éligibilité : au moins 1 M$ levés dont un tour en fonds propres, société non cotée, opérations principales {in_}.',
  disc2='Classement établi par ordre décroissant de valorisation estimée par IA, à partir d’informations publiques, selon une méthode publiée, sans intervention humaine sur l’ordre. Les tranches de valorisation sont des estimations éditoriales indicatives : ni une évaluation financière, ni une offre, ni un conseil en investissement. Le marché seul fixe la valeur d’une société, lors d’une levée ou d’une cession.',
  ed0='Édition 0 : établie par Claude (Anthropic) ; consensus de plusieurs IA lors d’une prochaine édition. ',
  tip_round='Dernier tour en fonds propres connu : ', tip_pub='Valorisation publiée : ', tip_conf='Indice de confiance : ',
  tc_high='Élevé', tc_medium='Moyen', tc_low='Faible', tip_none='Aucun tour en fonds propres au montant publié.', tip_more='Méthode',
  id_invest='investir', id_steps='etapes', id_opening='ouverture', f_invest='Investir',
  loc_partner='<b>Partenaire recherché.</b> {partner_short}.', loc_src='<b>Sources.</b>',
  loc_more='Méthode et règles du jeu, communes à tous les pays →',
  fol_h='Recevoir chaque nouvelle édition', fol_p='Entrées, sorties et mouvements, chaque trimestre.',
  form_prefix='suivre-', email_lab='Votre e-mail', email_ph='votre@email.com', prof_aria='Votre profil',
  prof_inv='Investisseur', prof_ceo='Dirigeant de startup', prof_bank='Banque d’affaires / conseil', prof_other='Autre', fol_btn='Suivre',
  fol_fine='Un e-mail par édition. Désinscription en un clic. Aucune donnée transmise à des tiers.',
  fol_soon='Bientôt disponible : les inscriptions ouvriront prochainement.',
  cad='Trimestriel', next='Prochaine édition : {next}',
  snap_day='Publié le {snap}', snap_month='Publié en {snap}', next_on='Prochaine mise à jour prévue le {next_short}',
  ooc='Mise à jour hors calendrier', f_cal='Calendrier', f_faq='FAQ',
  js_body='Bonjour,\\n\\nJe souhaite recevoir chaque nouvelle édition du classement Uback {name}.\\n\\nE-mail : \'+em+\'\\nProfil : \'+pr+\'\\n',
  js_subject='Suivre le classement Uback {name}',),
'en': dict(
  html_lang='en', locale='en_US', skip='Skip to content', home_aria='Uback, home', nav_aria='Main navigation',
  beta_b='Beta · prototype', beta_t='This site is under construction: rankings, texts and features change every week.',
  p_method='method.html', p_partner='partner.html', p_legal='legal-notice.html', p_thanks='thank-you.html',
  id_rank='ranking', id_sect='sectors', id_follow='follow', id_born='born-here', id_after='after',
  nav_rank='Ranking', nav_sect='Sectors', nav_partner='Partner', nav_invest='Invest', nav_method='Method',
  soon='Coming soon', follow='Follow {the}', declare='Declare an interest', hero_cta='Declare an interest in {startups}',
  f_method='Method and rules', f_partner='Become a partner', f_corr='Request a correction', f_legal='Legal notice',
  f_disc='Uback is a content publisher. It provides no investment advice, receives no mandate and takes part in no transaction. Introductions are made by a licensed partner, currently being selected {in_}. Investing in non-listed companies carries a risk of losing all the capital invested.',
  conf3='Solid sources', conf2='Partial sources', conf1='Weak sources',
  founded='founded', l_sub='Sub-sector', l_fund='Funding', l_conf='Confidence', raised=' raised',
  declare_cell='Declare an intent', b_levee='Raising soon', b_cession='Shareholder selling',
  n_levee='The company has told Uback it plans to raise funds soon.', n_cession='A shareholder has told Uback they are considering a sale.', b_suivie='Followed by {{p}}', exit='Exit', exit_by='Exit – {{a}}',
  ld_name='{name}’s top {N} funded startups – {date}',
  ld_desc='Uback quarterly ranking of non-listed {adj_fp} startups, established by AI from public information. The market sets the value; our AI estimates it.',
  title='{name}’s top {N} funded startups – {date} | Uback {name}',
  desc='Quarterly ranking of non-listed {adj_fp} startups that have already raised funds, established by AI from public information. The market sets the value; our AI estimates it.',
  h1='{name}’s top {N} funded startups',
  lead='A quarterly ranking of non-listed {adj_fp} startups that have already raised funds, established by artificial intelligence from public information. The market sets the value; our AI estimates it.',
  th_val='Estimated valuation (AI, order of magnitude)', l_val='Valuation (AI)',
  vb_hundreds_k='Hundreds of k$', vb_millions='Millions $', vb_tens_m='Tens of M$', vb_hundreds_m='Hundreds of M$',
  vb_unicorn='Unicorn', vb_decacorn='Decacorn', vb_not_estimated='Not estimated',
  vc_high='High confidence', vc_medium='Medium confidence', vc_low='Low confidence',
  report='Is this your company? Report an error', report_subject='Error report – {{co}} – Uback {name}',
  val_disc='Valuation orders of magnitude are indicative editorial estimates, produced by AI from public information (amounts raised, published valuations, reported indicators). They are neither a financial valuation, nor an offer, nor investment advice.',
  m_consensus='Claude · multi-AI consensus in a future edition', m_method='Published method', m_order='Order never changed by a human',
  glance='The market at a glance', s_ranked='companies ranked', s_radar='companies on the radar', s_raised='raised in 2025', s_rounds='rounds in 2025',
  sources='Sources: ', counters=' Intention counters will be shown above a threshold of amount and number of Backers.',
  listed='Listed benchmarks', listed_note='Not ranked: no intention is possible on a listed company.',
  h2_rank='National ranking · all sectors', t_born='Born here, based elsewhere', first_ed='First edition: no movements yet.',
  th_co='Company', th_sub='Sub-sector', th_fund='Known funding', th_conf='Confidence', th_invest='Open to Backers',
  disc_b='This ranking is an opinion, not a valuation.',
  disc='It is based on public information (press, funding announcements), following a published method, with no human intervention on the order. The confidence index reflects the quality of the sources. Any company may <a href="@ROOT@method.html#correction">request a correction</a> or dispute its position. Eligibility threshold: at least {seuil} raised, non-listed companies, main operations {in_}.',
  read_h2='How to read this ranking',
  read_rank_h='Rank', read_rank='Companies are ranked by AI-estimated valuation, highest first. The market sets the value; our AI estimates it.',
  read_range_h='Range', read_range='An order of magnitude, never a figure.',
  read_conf_h='Confidence', read_high='<b>High:</b> recent published valuation or round (under 24 months).', read_med='<b>Medium:</b> older data.',
  read_low='<b>Low:</b> single or unconfirmed source.', read_more='Full method →',
  sect_h2='Rankings by sector', sect_sub='Four verticals at launch, more when the feasibility test allows.', sect_k='Coming soon · Top 10',
  inv_h2='Invest {in_}, together, from {cities}',
  inv_lead='Uback aggregates investment intentions from business angels, family offices, corporates and diaspora investors. You invest alongside professional investors already on the cap table, who have negotiated a shareholders’ agreement: you don’t start from a blank page.',
  steps_h='Strength in numbers', steps_sub='Alone, a small ticket opens no doors. Together, Backers carry weight.',
  s1h='Declare an interest', s1='In the country or one of its sectors, with a ticket range, and if you wish a preferred company. Paid, to show you are serious; valid for life, and movable to another pool until its pool is passed to the partner.',
  s2h='Critical mass is reached', s2='When the pool’s combined amount reaches its critical mass, a floor amount estimated by the AI, the pool is passed to the licensed partner, who presents this demand to the company.',
  s3h='The licensed partner structures', s3='If the company’s expectations and the Backers’ converge, the partner builds a transaction and presents it directly to the Backers concerned.',
  s4h='Closing', s4='Capital raise or sale of existing shares: small tickets are pooled in a common vehicle set up by the licensed partner. Each Backer decides whether to take part.',
  steps_note='Uback does not advise, does not negotiate, collects nothing. Each transaction is run by the licensed partner, under the law shown on the company’s profile.',
  cta_notify='Get notified when intentions open', cta_after='What happens after my declaration?',
  cta_line='Intention declarations open once the licensed partner signs · price per ticket band · valid for life · movable until the pool is passed on',
  ph_k='The Uback partner {in_}', ph_h2='Introductions made by a licensed partner, currently being selected',
  ph_p='{partner_short}, the only party entitled to contact companies and structure deals. Uback remains a media: it ranks and aggregates intentions, it takes part in no transaction.',
  ph_s1='deals worked on', ph_s2='deals closed', ph_s3='average response time',
  of_k='Investment banks, M&amp;A boutiques, licensed advisers', of_h3='Become Uback’s exclusive partner {in_}',
  of_l1='Foreign investors you would not find on your own', of_l2='Your name on every ranking of the country',
  of_l3='A dashboard of intentions by sector and by company, reserved for you', of_l4='A quarterly prospecting kit for your own clients',
  of_btn='Discover the partnership', of_fine='Annual contract, exclusive per country. Uback brings investors and visibility, not a guaranteed deal flow.',
  rad_h='Radar · known eligible companies, not ranked', rad_p='Sorted by date of last round, with no judgement and no AI call. Undisclosed amount: the round is confirmed by the press, not its amount.',
  born_h='Born {in_}, based elsewhere', born_p='Companies of {adj_f} origin whose main operations are now abroad: not ranked, shown with the law governing their shares.',
  based_h='Born elsewhere, based {in_}', based_p='Companies founded abroad whose main operations are {in_}.',
  out_h='Not ranked',
  id_local='local-method', loc_h='The method {in_}',
  loc_cal='<b>Calendar.</b> Quarterly ranking, published on the 15th {months}. Next edition: {next}.',
  elig_h='Eligibility.', elig='Eligibility: at least $1M raised including one equity round, non-listed company, main operations {in_}.',
  disc2='Ranking in descending order of AI-estimated valuation, based on public information, following a published method, with no human intervention on the order. Valuation ranges are indicative editorial estimates: neither a financial valuation, nor an offer, nor investment advice. Only the market sets a company’s value, through a funding round or a sale.',
  ed0='Edition 0: produced by Claude (Anthropic); a consensus of several AI models will apply in a future edition. ',
  tip_round='Last known equity round: ', tip_pub='Published valuation: ', tip_conf='Confidence index: ',
  tc_high='High', tc_medium='Medium', tc_low='Low', tip_none='No equity round with a disclosed amount.', tip_more='Method',
  id_invest='invest', id_steps='steps', id_opening='opening', f_invest='Invest',
  loc_partner='<b>Partner sought.</b> {partner_short}.', loc_src='<b>Sources.</b>',
  loc_more='Method and rules, common to all countries →',
  fol_h='Get every new edition', fol_p='New entries, exits and movements, every quarter.',
  form_prefix='follow-', email_lab='Your e-mail', email_ph='you@email.com', prof_aria='Your profile',
  prof_inv='Investor', prof_ceo='Startup manager', prof_bank='Investment bank / adviser', prof_other='Other', fol_btn='Follow',
  fol_fine='One e-mail per edition. One-click unsubscribe. No data passed on to third parties.',
  fol_soon='Coming soon: subscriptions will open shortly.',
  cad='Quarterly', next='Next edition: {next}',
  snap_day='Published {snap}', snap_month='Published {snap}', next_on='Next scheduled update {next_short}',
  ooc='Out-of-cycle update', f_cal='Calendar', f_faq='FAQ',
  js_body='Hello,\\n\\nI would like to receive every new edition of the Uback {name} ranking.\\n\\nE-mail: \'+em+\'\\nProfile: \'+pr+\'\\n',
  js_subject='Follow the Uback {name} ranking',),
}
# « Published » : date du dernier verdict de l'IA, arrêt des données de l'édition (« AAAA-MM-JJ » ou « AAAA-MM ») ; vide : non affichée
SNAP = D.get('snapshot_date') or ''
V = dict(name=M['name'], in_=M['in'], In_=cap(M['in']), the=M['the'], adj_m=M['adj_m'], adj_f=M['adj_f'], adj_fp=M['adj_fp'],
         N=N, next=M['next_edition'], months=M['months_txt'], cities=M['cities'], date=D['date_label'], seuil=e(D['seuil_levee']), partner_short=M['partner_short'],
         startups=M['startups_label'], snap=format_date_short(SNAP, M['lang']) if SNAP else '', next_short=M['next_edition_short'])
L = {k: v.format(**V) for k, v in TXT[M['lang']].items()}
# mise à jour hors calendrier (facultative) : out_of_cycle {date, reason}, sous « Published » ; l'édition prévue reste due
_o = D.get('out_of_cycle')
OOC = ('\n      <div class="meta" style="margin:-8px 0 16px">'
       f'<span>{L["ooc"]}</span><span>·</span><span>{format_date_short(_o["date"], M["lang"])}</span><span>·</span>'
       f'<span>{e(_o["reason"])}</span></div>') if _o else ''
PP, PT = L['p_partner'], L['p_thanks']
# page partenaire unique (générée par tools/build_home.py), ouverte sur ce pays ; l'ancienne page du pays y redirige
PARTNER = f"@ROOT@{'fr/partenaire.html' if M['lang'] == 'fr' else 'partner.html'}?country={M['code']}"
# méthode et mentions légales : pages globales, communes à tous les pays (générées par tools/build_home.py)
GM = '@ROOT@fr/methode.html' if M['lang'] == 'fr' else '@ROOT@method.html'
GL = '@ROOT@mentions-legales.html' if M['lang'] == 'fr' else '@ROOT@legal-notice.html'
GC = '@ROOT@fr/correction.html' if M['lang'] == 'fr' else '@ROOT@correction.html'   # formulaire de correction (global)
GI = '@ROOT@fr/investir.html' if M['lang'] == 'fr' else '@ROOT@invest.html'         # page « Investir avec Uback » (globale)
POOL = f"{GI}?pool=country&amp;country={M['code']}#{L['id_opening']}"              # intérêt pour le pool du pays

def src(url, label='source', style=''):
    return f'<a href="{e(url)}"{style} rel="nofollow noopener" target="_blank">{label}</a>'

PAGE_KEY = {'/': 'index'}
for _l in TXT:
    for _k in ('method', 'partner', 'legal', 'thanks'):
        PAGE_KEY['/' + TXT[_l]['p_' + _k]] = _k

def page_in(lang, key):
    """Chemin d'une page dans une langue donnée (ex. ('fr', 'method') → methode.html)."""
    return '' if key == 'index' else TXT[lang]['p_' + key]

def head(title, desc, path, extra=''):
    url = BASE + path
    key = PAGE_KEY[path]
    # sélecteur de langue : lien vers la même page dans l'autre langue ; langues à venir grisées
    items = [f'<span class="on">{v["lang"].upper()}</span>' if v['path'] == PREFIX else
             f'<a class="lang-link" href="@ROOT@{v["path"][1:]}/{page_in(v["lang"], key)}" hreflang="{v["lang"]}">{v["lang"].upper()}</a>'
             for v in M['variants']]
    items += [f'<span class="soon" title="{L["soon"]}">{c}</span>' for c in M['langs_soon']]
    langs = '<span>·</span>'.join(items)
    alt = ''
    if len(M['variants']) > 1:
        alt = ''.join(f'\n<link rel="alternate" hreflang="{v["lang"]}" href="https://uback.com{v["path"]}/{page_in(v["lang"], key)}">'
                      for v in M['variants'])
        dv = next(v for v in M['variants'] if v['default'])
        alt += f'\n<link rel="alternate" hreflang="x-default" href="https://uback.com{dv["path"]}/{page_in(dv["lang"], key)}">'
    return f'''<!doctype html>
<html lang="{L['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">{'<meta name="robots" content="noindex">' if key == 'thanks' else ''}
<link rel="canonical" href="{url}">{alt}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Uback">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://uback.com{ASSETS}/{M['og']}?v={M['og_v']}">
<meta property="og:locale" content="{L['locale']}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v={M['css_v']}">
{extra}
{GA_HEAD}
</head>
<body>
<a class="skip" href="#main">{L['skip']}</a>
<div class="beta"><div class="wrap"><b>{L['beta_b']}</b><span class="beta-t">— {L['beta_t']}</span></div></div>
<header class="hdr">
  <div class="wrap">
    <a class="brand" href="@ROOT@" aria-label="{L['home_aria']}"><span class="u">U</span>Uback</a>
    {M['switcher']}
    <button class="menu-toggle" aria-label="Menu" aria-expanded="false" onclick="var n=document.getElementById('nav');var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1E3A5F" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <nav class="main" id="nav" aria-label="{L['nav_aria']}">
      <a href="/#{L['id_rank']}">{L['nav_rank']}</a>
      <a href="/#{L['id_sect']}">{L['nav_sect']}</a>
      <a href="{GM}">{L['nav_method']}</a>
      <a href="/#backers">Backers</a>
      <a href="{GI}">{L['nav_invest']}</a>
      <a href="{PARTNER}">{L['nav_partner']}</a>
    </nav>
    <span class="spacer"></span>
    <span class="langs">{langs}</span>
    <a class="btn" href="/#{L['id_follow']}">{L['follow']}</a>
    <a class="btn gold" href="{POOL}">{L['declare']}</a>
  </div>
</header>
<main id="main">
'''

FOOT = '\n</main>\n' + footer(M['lang'], root='@ROOT@', country=M['code'], disc=L['f_disc']) + '\n</body>\n</html>\n'

def conf(n):
    dots = ''.join('<i class="f"></i>' if i < n else '<i></i>' for i in range(3))
    return f'<span class="conf" aria-hidden="true">{dots}</span><span class="conf-l">{L["conf" + str(n)]}</span>'

def tip_facts(c):
    """Infobulle de la tranche : uniquement des faits publics (dernier tour en fonds propres connu, valorisation publiée,
    indice de confiance). Le raisonnement de l'IA (ajustements, multiples, fourchette) reste dans les données, non affiché."""
    vi, lang, lines = c.get('valuation_input') or {}, M['lang'], []
    if vi.get('round_usd') and vi.get('round_date'):
        when = valuation.month(vi['round_date'], lang)
        parts = [p for p in (vi.get('round_label'), valuation.money(vi['round_usd'], lang), when) if p]
        txt = ' · '.join(parts)
        inv = re.search(re.escape(when) + r'\s*\(([^()]*)\)', c.get('derniere_levee', ''))
        if inv:                                               # investisseurs cités juste après la date de ce même tour
            txt += f' ({inv.group(1)})'
        lines.append(L['tip_round'] + txt)
    else:
        lines.append(L['tip_none'])
    if vi.get('published_usd') and vi.get('published_date'):
        lines.append(L['tip_pub'] + f"{valuation.money(vi['published_usd'], lang)} ({valuation.month(vi['published_date'], lang)})")
    if c.get('valuation_bracket', 'not_estimated') != 'not_estimated':
        lines.append(L['tip_conf'] + L['tc_' + c.get('valuation_confidence', 'low')])
    return '<br>'.join(e(x) for x in lines)

def val(c):
    """Tranche de valorisation estimée par IA + confiance ; les faits publics s'affichent au survol ou au tap (bouton + infobulle)."""
    b, vc = c.get('valuation_bracket', 'not_estimated'), c.get('valuation_confidence', 'low')
    n = {'high': 3, 'medium': 2, 'low': 1}[vc]
    dots = '' if b == 'not_estimated' else '<span class="conf" aria-hidden="true">' + ''.join(
        '<i class="f"></i>' if i < n else '<i></i>' for i in range(3)) + '</span>'
    conf_txt = '' if b == 'not_estimated' else f'<span class="sr"> · {L["vc_" + vc]}</span>'
    tid = f"vb-{c['rang']}"
    ne = ' ne' if b == 'not_estimated' else ''
    toggle = "var p=this.parentNode;this.setAttribute('aria-expanded',p.classList.toggle('open'))"   # tap sur mobile (iOS ne donne pas le focus)
    return (f'<span class="val{ne}"><button type="button" class="val-b" aria-describedby="{tid}" aria-expanded="false" onclick="{toggle}">'
            f'<span class="vl">{L["vb_" + b]}</span>{dots}{conf_txt}</button>'
            f'<span class="val-tip"><span id="{tid}">{tip_facts(c)}</span>'
            f'<a class="tip-more" href="{GM}#estimation">{L["tip_more"]}</a></span></span>')

def invest(c):
    """Colonne « Ouverte aux Backers ». Par défaut, l'intérêt porte sur le pool du pays (bouton de l'en-tête et du hero) :
    une intention sur une société n'apparaît que si elle est ouverte aux Backers.
    acces : defaut (rien) | travaillee (badge « Suivie par » si partenaire signé, sans bouton)
            | levee (la société prévoit de lever) | cession (un actionnaire envisage de céder) : badge, phrase, bouton
            | sortie (rachat : mention, sans bouton).
    La colonne n'est affichée que si au moins une société a un contenu (SHOW_INV)."""
    a = c.get('acces') or 'defaut'
    if a == 'sortie':
        who = (c.get('acquereur') or '').strip()
        return f'<span class="exit">{L["exit_by"].format(a=e(who)) if who else L["exit"]}</span>'
    if a in ('levee', 'cession'):
        href = f"{GI}?pool=company&amp;company={quote(c['nom'])}&amp;country={M['code']}#{L['id_opening']}"
        return (f'<span class="inv-badge gold">{L["b_" + a]}</span><span class="inv-note">{L["n_" + a]}</span>'
                f'<a class="btn" href="{href}">{L["declare_cell"]}</a>')
    if a == 'travaillee' and M.get('partner_name'):
        return f'<span class="inv-badge line">{L["b_suivie"].format(p=e(M["partner_name"]))}</span>'
    return ''

def row(c):
    top = ' class="top"' if c['rang'] == 1 else ''
    jur = ''
    if c.get('juridiction') and (not c['juridiction'].startswith(M['name']) or ';' in c['juridiction']):
        jur = f'<span class="jur">{e(c["juridiction"])}</span>'
    note = f'<div class="src">{e(c["note"])}</div>' if c.get('note') else ''
    # « Signalez une erreur » : formulaire de correction prérempli (société, pays)
    report = f'<a class="report" href="{GC}?company={quote(c["nom"])}&amp;country={M["code"]}">{L["report"]}</a>'
    return f'''<tr{top}>
<td class="rank">{c['rang']}</td>
<td><span class="co">{e(c['nom'])}<small>{e(c['ville'])} · {L['founded']} {c['creation']}</small></span>{jur}{note}{report}</td>
<td data-l="{L['l_sub']}">{e(c['sous_secteur'])}</td>
<td data-l="{L['l_fund']}">{e(c['leve_cumule'])}{L['raised']}<br><span class="src">{e(c['derniere_levee'])} · {src(c['source'])}</span></td>
<td data-l="{L['l_val']}">{val(c)}</td>
<td data-l="{L['l_conf']}">{conf(c['confiance'])}</td>
{f'<td class="act">{invest(c)}</td>' if SHOW_INV else ''}
</tr>'''

SHOW_INV = any(invest(c) for c in RANKED)

def li(r, sub=None):
    extra = f'<br><span class="src">{e(r[sub])}</span>' if sub else ''
    return f'<li><span><b>{e(r["nom"])}</b> · {e(r["sous_secteur"])}{extra}</span><span>{e(r["derniere_levee"])} · {src(r["source"])}</span></li>'

jsonld = {
  "@context": "https://schema.org", "@type": "ItemList",
  "name": L['ld_name'],
  "description": L['ld_desc'],
  "itemListOrder": "https://schema.org/ItemListOrderDescending",
  "itemListElement": [{"@type": "ListItem", "position": c['rang'], "name": c['nom'], "url": f"https://{c['site']}"} for c in RANKED]
}
MK = D['marche']
SRC = ', '.join(src(s['url'], e(s['label']), ' style="color:#c7d0dc"') for s in MK['sources'])
BASED = f'''
        <h3 style="margin-top:22px">{L['based_h']}</h3>
        <p>{L['based_p']}</p>
        <ul class="list">
        {''.join(li(r, 'lieu') for r in D['nees_ailleurs'])}
        </ul>''' if D.get('nees_ailleurs') else ''

index = head(L['title'], L['desc'], "/", f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>')

index += f'''
<div class="wrap">
  <div class="hero">
    <div>
      <div class="kicker">Funded startups, ranked by AI</div>
      <h1>{L['h1']}</h1>
      <div class="meta" style="margin-bottom:16px"><span>{e(EDITION)}</span><span>·</span>{'<span>' + (L['snap_day'] if len(SNAP) == 10 else L['snap_month']) + '</span><span>·</span>' if SNAP else ''}<span>{L['next_on']}</span></div>{OOC}
      <p class="lead">{L['lead']}</p>
      <div class="meta">
        <span class="tag cad">{L['cad']}</span>
        <span>{L['m_consensus']}</span><span>·</span>
        <a href="{GM}">{L['m_method']}</a><span>·</span>
        <span>{L['m_order']}</span>
      </div>
      <p class="hero-cta"><a class="btn gold" href="{POOL}">{L['hero_cta']}</a></p>
    </div>
    <div class="panel">
      <div class="k">{L['glance']}</div>
      <div class="stats">
        <div><b>{len(RANKED)}</b><span>{L['s_ranked']}</span></div>
        <div><b>{len(D['radar'])}</b><span>{L['s_radar']}</span></div>
        <div><b>{e(MK['total_2025'])}</b><span>{L['s_raised']}</span></div>
        <div><b>{e(MK['deals_2025'])}</b><span>{L['s_rounds']}</span></div>
      </div>
      <div class="fine">{e(MK['commentaire'])} {L['sources']}{SRC}.{L['counters']}</div>
    </div>
  </div>

  <div class="reperes">
    <span class="lab">{L['listed']}</span>
    {''.join(f'<span class="pill">{e(r["nom"])} · {e(r["info"])} · {src(r["source"])}</span>' for r in D['reperes_cotes'])}
    <span class="fine">{L['listed_note']}</span>
  </div>
</div>

<section id="{L['id_rank']}" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head">
      <h2>{L['h2_rank']}</h2>
      <div class="tabs"><a class="on" href="#{L['id_rank']}">Top {N}</a><a href="#radar">Radar</a><a href="#{L['id_born']}">{L['t_born']}</a><a href="{PARTNER}#challengers">Challengers</a></div>
      <span class="spacer"></span>
      <span class="sub">{L['first_ed']}</span>
    </div>
    <table class="tbl">
      <thead><tr><th>#</th><th>{L['th_co']}</th><th>{L['th_sub']}</th><th>{L['th_fund']}</th><th>{L['th_val']}</th><th>{L['th_conf']}</th>{f'<th class="th-inv">' + L['th_invest'] + '</th>' if SHOW_INV else ''}</tr></thead>
      <tbody>
      {''.join(row(c) for c in RANKED)}
      </tbody>
    </table>
    <div class="disclaimer">{L['disc2']} {L['ed0'] if EDITION.lower().startswith(('édition 0', 'edition 0')) else ''}{L['elig']} <a href="{GC}">{L['f_corr']}</a></div>

    <div class="follow-band" id="{L['id_follow']}">
      <div class="fb-text">
        <h3>{L['fol_h']}</h3>
        <p>{L['fol_p']}</p>
      </div>
      <div class="fb-form">
        <form class="follow" name="{L['form_prefix']}{M['slug']}" method="POST" action="/{PT}" data-netlify="true" netlify-honeypot="bot-field"{' data-mailto="' + FORM_EMAIL + '"' if FORM_MODE == 'mailto' else ''}{' data-soon="1" novalidate' if FORM_MODE == 'soon' else ''}>
          <input type="hidden" name="form-name" value="{L['form_prefix']}{M['slug']}">
          <input type="hidden" name="marche" value="{M['code']}">
          <p class="skip"><label>Ne pas remplir : <input name="bot-field"></label></p>
          <label class="skip" for="email">{L['email_lab']}</label>
          <input id="email" name="email" type="email" required placeholder="{L['email_ph']}" autocomplete="email">
          <select name="profil" aria-label="{L['prof_aria']}">
            <option value="investisseur">{L['prof_inv']}</option>
            <option value="dirigeant">{L['prof_ceo']}</option>
            <option value="banque">{L['prof_bank']}</option>
            <option value="autre">{L['prof_other']}</option>
          </select>
          <button class="btn navy" type="submit">{L['fol_btn']}</button>
        </form>
        <p class="src">{L['fol_fine']}</p>
        <p class="soon-msg" role="status" hidden>{L['fol_soon']}</p>
      </div>
      <script>
      (function(){{var s=document.querySelector('form[data-soon]');if(s){{s.addEventListener('submit',function(ev){{ev.preventDefault();
        var m=s.parentNode.querySelector('.soon-msg');m.hidden=false;}});}}}})();
      (function(){{var f=document.querySelector('form[data-mailto]');if(!f)return;
      f.addEventListener('submit',function(ev){{ev.preventDefault();
        var em=f.email.value,pr=f.profil.options[f.profil.selectedIndex].text;
        var body='{L['js_body']}';
        window.location.href='mailto:'+f.dataset.mailto+'?subject='+encodeURIComponent('{L['js_subject']}')+'&body='+encodeURIComponent(body);
        setTimeout(function(){{window.location.href='/{PT}';}},1500);}});}})();
      </script>
    </div>
  </div>
</section>

<section class="soft" id="read">
  <div class="wrap">
    <div class="sec-head"><h2>{L['read_h2']}</h2></div>
    <div class="grid3">
      <div class="card"><h3>{L['read_rank_h']}</h3><p>{L['read_rank']}</p></div>
      <div class="card"><h3>{L['read_range_h']}</h3><p>{L['read_range']}</p>
        <ol class="scale">{''.join(f'<li>{L["vb_" + b]}</li>' for b in valuation.BRACKETS)}</ol></div>
      <div class="card"><h3>{L['read_conf_h']}</h3><ul class="read-list"><li>{L['read_high']}</li><li>{L['read_med']}</li><li>{L['read_low']}</li></ul></div>
    </div>
    <p class="read-more"><a href="{GM}#estimation">{L['read_more']}</a></p>
  </div>
</section>

<section id="{L['id_sect']}">
  <div class="wrap">
    <div class="sec-head"><h2>{L['sect_h2']}</h2><span class="sub">{L['sect_sub']}</span></div>
    <div class="grid4">
{chr(10).join(f'      <div class="card"><span class="k">{L["sect_k"]}</span><h3>{t}</h3><p>{d}</p></div>' for t, d in M['sectors'])}
    </div>
    <div class="soon-list">{''.join(f'<span>{s}</span>' for s in M['sectors_soon'])}</div>
  </div>
</section>

<section class="navy" id="backers">
  <div class="wrap">
    <div class="sec-head"><h2>{L['inv_h2']}</h2></div>
    <p class="lead">{L['inv_lead']}</p>
    <div class="steps-head">
      <h3>{L['steps_h']}</h3>
      <p>{L['steps_sub']}</p>
    </div>
    <div class="grid4">
      <div class="card dark"><span class="num">1</span><h3>{L['s1h']}</h3><p>{L['s1']}</p></div>
      <div class="card dark"><span class="num">2</span><h3>{L['s2h']}</h3><p>{L['s2']}</p></div>
      <div class="card dark"><span class="num">3</span><h3>{L['s3h']}</h3><p>{L['s3']}</p></div>
      <div class="card dark"><span class="num">4</span><h3>{L['s4h']}</h3><p>{L['s4']}</p></div>
    </div>
    <p class="steps-note">{L['steps_note']}</p>
    <div class="cta-row">
      <a class="btn gold" href="#{L['id_follow']}">{L['cta_notify']}</a>
      <a class="btn ghost" href="{GI}#{L['id_steps']}">{L['cta_after']}</a>
      <span>{L['cta_line']}</span>
    </div>
  </div>
</section>

<section id="partenaire-home">
  <div class="wrap">
    <div class="partner">
      <div>
        <span class="k">{L['ph_k']}</span>
        <h2>{L['ph_h2']}</h2>
        <p>{L['ph_p']}</p>
        <div class="pstats"><div><b>—</b>{L['ph_s1']}</div><div><b>—</b>{L['ph_s2']}</div><div><b>—</b>{L['ph_s3']}</div></div>
      </div>
      <div class="offer">
        <span class="k">{L['of_k']}</span>
        <h3>{L['of_h3']}</h3>
        <ul>
          <li>{L['of_l1']}</li>
          <li>{L['of_l2']}</li>
          <li>{L['of_l3']}</li>
          <li>{L['of_l4']}</li>
        </ul>
        <a class="btn navy" href="{PARTNER}">{L['of_btn']}</a>
        <span class="fine">{L['of_fine']}</span>
      </div>
    </div>
  </div>
</section>

<section class="soft" id="radar">
  <div class="wrap">
    <div class="box line">
      <h3>{L['rad_h']}</h3>
      <p>{L['rad_p']}</p>
      <ul class="list">
      {''.join(li(r) for r in D['radar'])}
      </ul>
      <h3 id="{L['id_born']}" style="margin-top:22px">{L['born_h']}</h3>
      <p>{L['born_p']}</p>
      <ul class="list">
      {''.join(li(r, 'lieu') for r in D['nees_ici'])}
      </ul>{BASED}
      <h3 style="margin-top:22px">{L['out_h']}</h3>
      <ul class="list">
      {''.join(f'<li><span><b>{e(r["nom"])}</b> · {e(r["motif"])}</span><span>{src(r["source"])}</span></li>' for r in D['hors_classement'])}
      </ul>
    </div>
    <div class="box local" id="{L['id_local']}">
      <h3>{L['loc_h']}</h3>
      <p>{L['loc_cal']}</p>
      <p>{L['elig']}</p>
      <p>{L['loc_partner']}</p>
      <p>{L['loc_src']} {M['press']}</p>
      <p><a href="{GM}">{L['loc_more']}</a></p>
    </div>
  </div>
</section>
''' + FOOT

# ---------------------------------------------------------------- pages de contenu (texte long par langue)
PAGES = {}
if M['lang'] == 'fr':
    PAGES[PT] = head(f"Merci | Uback {M['name']}", "Inscription confirmée.", f"/{PT}") + f'''
<div class="wrap prose" style="padding:60px 24px">
<h1>Merci, c’est noté.</h1>
<p class="lead">Si votre messagerie s’est ouverte, envoyez simplement le message préparé : vous recevrez chaque nouvelle édition du classement {M['adj_m']}, et un mot dès l’ouverture des déclarations d’intention.</p>
<p>Sinon, écrivez-nous à <a href="mailto:{FORM_EMAIL}">{FORM_EMAIL}</a> avec pour objet « Suivre le classement Uback {M['name']} ».</p>
<p><a class="btn navy" href="/">Retour au classement</a></p>
</div>
''' + FOOT

else:
    PAGES[PT] = head(f"Thank you | Uback {M['name']}", "Subscription confirmed.", f"/{PT}") + f'''
<div class="wrap prose" style="padding:60px 24px">
<h1>Thank you, it’s noted.</h1>
<p class="lead">If your e-mail app opened, simply send the prepared message: you will receive every new edition of the {M['adj_m']} ranking, and a word as soon as intention declarations open.</p>
<p>Otherwise, write to us at <a href="mailto:{FORM_EMAIL}">{FORM_EMAIL}</a> with the subject “Follow the Uback {M['name']} ranking”.</p>
<p><a class="btn navy" href="/">Back to the ranking</a></p>
</div>
''' + FOOT

def under_prefix(page):
    """Les gabarits écrivent des chemins absolus (/methode.html, /assets/…) : on les place sous le dossier de la version.
    /assets/ va vers les fichiers partagés du marché ; « @ROOT@ » marque les liens vers la racine du site."""
    page = re.sub(r'((?:href|src)=")/assets/', r'\1@ROOT@' + ASSETS[1:] + '/', page)
    page = re.sub(r'((?:href|src|action)=")/(?!/)', rf'\1{PREFIX}/', page)
    page = page.replace('href="@ROOT@', 'href="/').replace('src="@ROOT@', 'src="/')
    return page.replace("location.href='/", f"location.href='{PREFIX}/")

# feuille de style et icônes : une seule source (ma/assets/), chaque autre marché en reçoit une copie
if M['code'] != 'ma':
    os.makedirs(f"{ROOT}{ASSETS}", exist_ok=True)
    for f in ('style.css', 'favicon.svg', 'favicon-192.png'):
        shutil.copyfile(f'{ROOT}/ma/assets/{f}', f'{ROOT}{ASSETS}/{f}')

os.makedirs(OUT, exist_ok=True)
for name, content in [('index.html', index)] + list(PAGES.items()):
    open(f'{OUT}/{name}', 'w', encoding='utf-8', newline='\n').write(under_prefix(content))

def redirect(path, target):
    """Page de redirection (anciennes adresses) : aucune adresse publiée ne doit casser."""
    open(path, 'w', encoding='utf-8', newline='\n').write(f'''<!doctype html>
<html lang="{L['html_lang']}">
<head>
<meta charset="utf-8">
<title>Page déplacée | Uback</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="https://uback.com{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace('{target}' + (location.search ? '{'&' if '?' in target else '?'}' + location.search.slice(1) : '') + location.hash);</script>
</head>
<body>
<p><a href="{target}">uback.com{target}</a></p>
</body>
</html>
''')

# méthode et mentions légales : anciennes pages du marché → pages globales
G_METHOD, G_LEGAL = GM.replace('@ROOT@', '/'), GL.replace('@ROOT@', '/')
redirect(f"{OUT}/{L['p_method']}", G_METHOD)
redirect(f"{OUT}/{L['p_legal']}", G_LEGAL)
redirect(f"{OUT}/{PP}", PARTNER.replace('@ROOT@', '/'))     # ancienne page partenaire du pays → page unique

# version secondaire (ex. /ma/fr) : les anciennes adresses de ses pages à la racine du marché redirigent
if not M['default']:
    root_dir = f"{ROOT}/{M['code']}"
    dv = next(v for v in M['variants'] if v['default'])
    taken = {TXT[dv['lang']]['p_' + k] for k in ('method', 'partner', 'legal', 'thanks')}   # pages de la version principale
    for name in PAGES:
        if name not in taken:
            redirect(f'{root_dir}/{name}', f'{PREFIX}/{name}')
    for name, target in ((L['p_method'], G_METHOD), (L['p_legal'], G_LEGAL), (PP, PARTNER.replace('@ROOT@', '/'))):
        if name not in taken:
            redirect(f'{root_dir}/{name}', target)
