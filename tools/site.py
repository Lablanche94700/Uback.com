# -*- coding: utf-8 -*-
"""Gabarit unique des sites marchés (même structure pour tous les pays).
Ne pas lancer directement : tools/build_site.py l'exécute avec la configuration du marché dans M.
Les textes d'interface sont dans TXT (fr, en) ; tout ce qui est propre au pays vient de M ou des données.
Écrit uniquement dans le dossier du marché (ex. pl/), jamais à la racine."""
import json, html, os, re, shutil, datetime, copy
from urllib.parse import quote
import valuation
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
N = M['top_n']
RANKED = D['classement'][:N]
e = html.escape
cap = lambda s: s[:1].upper() + s[1:]

LOGO_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C8A052" stroke-width="2" aria-hidden="true">{}</svg>'
IC_AI = LOGO_SVG.format('<rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 20h8M12 18v2M7 9h4M7 13h10"/>')
IC_HUM = LOGO_SVG.format('<path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/><circle cx="12" cy="8" r="4"/>')
IC_MON = LOGO_SVG.format('<path d="M12 3v18M7 8h7a3 3 0 0 1 0 6H8a3 3 0 0 0 0 6h9"/>')

# ---------------------------------------------------------------- textes d'interface
# {name} Maroc · {in_} au Maroc · {In_} Au Maroc · {the} le Maroc · {adj_m} marocain · {adj_f} marocaine
# {adj_fp} marocaines · {N} places · {cities} Paris, Dubaï ou Montréal
TXT = {
'fr': dict(
  html_lang='fr', locale='fr_FR', skip='Aller au contenu', home_aria='Uback, accueil', nav_aria='Navigation principale',
  beta_b='Bêta · prototype', beta_t='Ce site est en construction : classements, textes et fonctionnalités évoluent chaque semaine.', beta_link='Nous écrire',
  p_method='methode.html', p_partner='partenaire.html', p_legal='mentions-legales.html', p_thanks='merci.html',
  id_rank='classement', id_sect='secteurs', id_follow='suivre', id_born='nees-ici', id_after='apres',
  nav_rank='Classement', nav_sect='Secteurs', nav_partner='Partenaire', nav_method='Méthode',
  soon='Bientôt disponible', follow='Suivre {the}', declare='Déclarer une intention',
  f_method='Méthode et règles du jeu', f_partner='Devenir partenaire', f_corr='Demander une correction', f_legal='Mentions légales',
  f_disc='Uback est un éditeur de contenu. Il ne fournit aucun conseil en investissement, ne reçoit aucun mandat et n’intervient dans aucune transaction. Les mises en relation sont réalisées par un partenaire agréé, en cours de sélection {in_}. Investir dans des sociétés non cotées comporte un risque de perte totale du capital investi.',
  conf3='Sources solides', conf2='Sources partielles', conf1='Sources faibles',
  founded='fondée en', l_sub='Sous-secteur', l_fund='Levées', l_conf='Confiance', raised=' cumulés',
  declare_cell='Déclarer une intention', b_levee='Levée en cours', b_suivie='Suivie par {{p}}', exit='Sortie', exit_by='Sortie – {{a}}',
  ld_name='Les {N} startups {adj_fp} les mieux valorisées – {date}',
  ld_desc="Classement trimestriel Uback des startups {adj_fp}, établi par IA à partir d'informations publiques. Uback ne valorise pas les sociétés : il les classe, et indique un ordre de grandeur estimé par IA.",
  title='Top {N} des startups {adj_fp} les mieux valorisées – {date} | Uback {name}',
  desc="Classement trimestriel des startups {adj_fp} non cotées ayant déjà levé des fonds, établi par IA à partir d'informations publiques. Uback ne valorise pas les sociétés : il les classe, et indique un ordre de grandeur estimé par IA.",
  h1='Les {N} startups {adj_fp} les mieux valorisées',
  lead='Un classement trimestriel des startups {adj_fp} non cotées ayant déjà levé des fonds, établi par intelligence artificielle à partir d’informations publiques. Uback ne valorise pas les sociétés : il les classe, et indique un ordre de grandeur estimé par IA.',
  th_val='Valorisation estimée (IA, ordre de grandeur)', l_val='Valorisation (IA)',
  vb_hundreds_k='Centaines de k$', vb_millions='Millions $', vb_tens_m='Dizaines de M$', vb_hundreds_m='Centaines de M$',
  vb_unicorn='Licorne', vb_decacorn='Décacorne', vb_not_estimated='Non estimé',
  vc_high='Confiance élevée', vc_medium='Confiance moyenne', vc_low='Confiance faible',
  report='Vous êtes cette société ? Signalez une erreur', report_subject='Signalement d’erreur – {{co}} – Uback {name}',
  val_disc='Les ordres de grandeur de valorisation sont des estimations éditoriales indicatives, produites par IA à partir d’informations publiques (montants levés, valorisations publiées, indicateurs cités). Ils ne constituent ni une évaluation financière, ni une offre, ni un conseil en investissement.',
  m_consensus='Claude · consensus multi-IA à partir de l’édition 1', m_method='Méthode publiée', m_order='Ordre jamais modifié par un humain',
  glance='Le marché en un coup d’œil', s_ranked='sociétés classées', s_radar='sociétés sur le radar', s_raised='levés en 2025', s_rounds='tours en 2025',
  sources='Sources : ', counters=' Les compteurs d’intentions s’afficheront au-delà d’un seuil de montant et de nombre de Backers.',
  listed='Repères cotés', listed_note='Hors classement : aucune intention possible sur une société cotée.',
  h2_rank='Classement national · tous secteurs', t_born='Nées ici, établies ailleurs', first_ed='Première édition : pas encore de mouvements.',
  th_co='Société', th_sub='Sous-secteur', th_fund='Levées connues', th_conf='Confiance', th_invest='Investir',
  disc_b='Ce classement est une opinion, pas une évaluation.',
  disc='Il est établi à partir d’informations publiques (presse, annonces de levées de fonds), selon une méthode publiée, sans intervention humaine sur l’ordre. L’indice de confiance reflète la qualité des sources. Toute société peut <a href="@ROOT@fr/methode.html#correction">demander une correction</a> ou contester sa position. Seuil d’éligibilité : au moins {seuil} levés, sociétés non cotées, opérations principales {in_}.',
  reg_h2='Trois regards, jamais un seul',
  reg_ai_h='Ce que pensent les IA', reg_ai='À chaque édition, la même question est posée à plusieurs IA. Les réponses sont fusionnées en un classement de consensus, avec un indice de confiance par position. L’édition 0 est établie par une seule IA ; le consensus arrive avec l’édition 1.',
  reg_hum_h='Ce que défendent les experts', reg_hum='Le partenaire agréé et des analystes contestent le classement : « pourquoi ce leader est absent », « pourquoi ce n° 3 est surévalué ». Les résumés sont gratuits.',
  reg_mon_h='Ce que veut l’argent', reg_mon='Les sociétés les plus convoitées : celles qui cumulent le plus d’intentions d’investissement payantes. Montants agrégés, jamais d’intention individuelle.',
  sect_h2='Classements par secteur', sect_sub='Quatre verticales au lancement, d’autres quand le test de faisabilité le permet.', sect_k='Bientôt · Top 10',
  inv_h2='Investir {in_}, à plusieurs, depuis {cities}',
  inv_lead='Uback agrège les intentions d’investissement des business angels, family offices, corporates et investisseurs de la diaspora. Vous entrez au capital aux côtés d’investisseurs professionnels déjà présents. Vous bénéficiez du même pacte d’associés.',
  steps_h='Le nombre fait la force', steps_sub='Seul, un petit ticket n’ouvre aucune porte. Regroupés, les Backers pèsent.',
  s1h='Déclarez une intention', s1='Sur une société ou sur un secteur, avec un ticket minimum et maximum. Payante, pour qualifier le sérieux&nbsp;; transférable tant qu’elle n’est pas transformée.',
  s2h='La masse critique est atteinte', s2='Quand le nombre de Backers et le cumul de leurs intentions franchissent un seuil, le partenaire agréé contacte la société et lui présente cette demande.',
  s3h='Le partenaire agréé structure', s3='Si les attentes de la société et celles des Backers convergent, il construit une opération et la présente directement aux Backers concernés.',
  s4h='Closing', s4='Levée ou cession de titres existants&nbsp;: les petits tickets sont regroupés dans un véhicule commun créé par le partenaire agréé. Chaque Backer décide d’y participer ou non.',
  steps_note='Uback ne conseille pas, ne négocie pas, n’encaisse rien. Chaque opération est menée par le partenaire agréé, sous le droit indiqué sur la fiche de la société.',
  cta_notify='Être prévenu à l’ouverture des intentions', cta_after='Que se passe-t-il après ma déclaration ?',
  cta_line='Ouverture des déclarations d’intention dès la signature du partenaire agréé · prix par tranche de ticket · validité 12 mois · crédit transférable',
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
  loc_elig='<b>Éligibilité.</b> Au moins {seuil} levés, sociétés non cotées, opérations principales {in_}.',
  loc_partner='<b>Partenaire recherché.</b> {partner_short}.', loc_src='<b>Sources.</b>',
  loc_more='Méthode et règles du jeu, communes à tous les pays →',
  fol_h='Recevoir chaque nouvelle édition', fol_p='Entrées, sorties et mouvements, chaque trimestre.',
  form_prefix='suivre-', email_lab='Votre e-mail', email_ph='votre@email.com', prof_aria='Votre profil',
  prof_inv='Investisseur', prof_ceo='Dirigeant de startup', prof_bank='Banque d’affaires / conseil', prof_other='Autre', fol_btn='Suivre',
  fol_fine='Un e-mail par édition. Désinscription en un clic. Aucune donnée transmise à des tiers.',
  fol_soon='Bientôt disponible : les inscriptions ouvriront prochainement.',
  cad='Trimestriel', next='Prochaine édition : {next}',
  js_body='Bonjour,\\n\\nJe souhaite recevoir chaque nouvelle édition du classement Uback {name}.\\n\\nE-mail : \'+em+\'\\nProfil : \'+pr+\'\\n',
  js_subject='Suivre le classement Uback {name}',),
'en': dict(
  html_lang='en', locale='en_US', skip='Skip to content', home_aria='Uback, home', nav_aria='Main navigation',
  beta_b='Beta · prototype', beta_t='This site is under construction: rankings, texts and features change every week.', beta_link='Contact us',
  p_method='method.html', p_partner='partner.html', p_legal='legal-notice.html', p_thanks='thank-you.html',
  id_rank='ranking', id_sect='sectors', id_follow='follow', id_born='born-here', id_after='after',
  nav_rank='Ranking', nav_sect='Sectors', nav_partner='Partner', nav_method='Method',
  soon='Coming soon', follow='Follow {the}', declare='Declare an intention',
  f_method='Method and rules', f_partner='Become a partner', f_corr='Request a correction', f_legal='Legal notice',
  f_disc='Uback is a content publisher. It provides no investment advice, receives no mandate and takes part in no transaction. Introductions are made by a licensed partner, currently being selected {in_}. Investing in non-listed companies carries a risk of losing all the capital invested.',
  conf3='Solid sources', conf2='Partial sources', conf1='Weak sources',
  founded='founded', l_sub='Sub-sector', l_fund='Funding', l_conf='Confidence', raised=' raised',
  declare_cell='Declare an intent', b_levee='Raise in progress', b_suivie='Followed by {{p}}', exit='Exit', exit_by='Exit – {{a}}',
  ld_name='{name}’s top {N} funded startups – {date}',
  ld_desc='Uback quarterly ranking of non-listed {adj_fp} startups, established by AI from public information. We don’t value companies. We rank them, and give an AI-estimated order of magnitude.',
  title='{name}’s top {N} funded startups – {date} | Uback {name}',
  desc='Quarterly ranking of non-listed {adj_fp} startups that have already raised funds, established by AI from public information. We don’t value companies. We rank them, and give an AI-estimated order of magnitude.',
  h1='{name}’s top {N} funded startups',
  lead='A quarterly ranking of non-listed {adj_fp} startups that have already raised funds, established by artificial intelligence from public information. We don’t value companies. We rank them, and give an AI-estimated order of magnitude.',
  th_val='Estimated valuation (AI, order of magnitude)', l_val='Valuation (AI)',
  vb_hundreds_k='Hundreds of k$', vb_millions='Millions $', vb_tens_m='Tens of M$', vb_hundreds_m='Hundreds of M$',
  vb_unicorn='Unicorn', vb_decacorn='Decacorn', vb_not_estimated='Not estimated',
  vc_high='High confidence', vc_medium='Medium confidence', vc_low='Low confidence',
  report='Is this your company? Report an error', report_subject='Error report – {{co}} – Uback {name}',
  val_disc='Valuation orders of magnitude are indicative editorial estimates, produced by AI from public information (amounts raised, published valuations, reported indicators). They are neither a financial valuation, nor an offer, nor investment advice.',
  m_consensus='Claude · multi-AI consensus from Edition 1', m_method='Published method', m_order='Order never changed by a human',
  glance='The market at a glance', s_ranked='companies ranked', s_radar='companies on the radar', s_raised='raised in 2025', s_rounds='rounds in 2025',
  sources='Sources: ', counters=' Intention counters will be shown above a threshold of amount and number of Backers.',
  listed='Listed benchmarks', listed_note='Not ranked: no intention is possible on a listed company.',
  h2_rank='National ranking · all sectors', t_born='Born here, based elsewhere', first_ed='First edition: no movements yet.',
  th_co='Company', th_sub='Sub-sector', th_fund='Known funding', th_conf='Confidence', th_invest='Invest',
  disc_b='This ranking is an opinion, not a valuation.',
  disc='It is based on public information (press, funding announcements), following a published method, with no human intervention on the order. The confidence index reflects the quality of the sources. Any company may <a href="@ROOT@method.html#correction">request a correction</a> or dispute its position. Eligibility threshold: at least {seuil} raised, non-listed companies, main operations {in_}.',
  reg_h2='Three perspectives, never just one',
  reg_ai_h='What the AIs think', reg_ai='For every edition, the same question is put to several AIs. The answers are merged into a consensus ranking, with a confidence index for each position. Edition 0 is established by a single AI; the consensus arrives with Edition 1.',
  reg_hum_h='What the experts argue', reg_hum='The licensed partner and analysts challenge the ranking: “why is this leader missing”, “why is number 3 overrated”. Summaries are free.',
  reg_mon_h='What the money wants', reg_mon='The most sought-after companies: those gathering the most paid investment intentions. Aggregated amounts, never an individual intention.',
  sect_h2='Rankings by sector', sect_sub='Four verticals at launch, more when the feasibility test allows.', sect_k='Coming soon · Top 10',
  inv_h2='Invest {in_}, together, from {cities}',
  inv_lead='Uback aggregates investment intentions from business angels, family offices, corporates and diaspora investors. You invest alongside professional investors already on the cap table. You benefit from the same shareholders’ agreement.',
  steps_h='Strength in numbers', steps_sub='Alone, a small ticket opens no doors. Together, Backers carry weight.',
  s1h='Declare an intention', s1='On a company or a sector, with a minimum and maximum ticket. Paid, to show you are serious; transferable as long as it has not been converted.',
  s2h='Critical mass is reached', s2='When the number of Backers and the total of their intentions cross a threshold, the licensed partner contacts the company and presents this demand.',
  s3h='The licensed partner structures', s3='If the company’s expectations and the Backers’ converge, the partner builds a transaction and presents it directly to the Backers concerned.',
  s4h='Closing', s4='Capital raise or sale of existing shares: small tickets are pooled in a common vehicle set up by the licensed partner. Each Backer decides whether to take part.',
  steps_note='Uback does not advise, does not negotiate, collects nothing. Each transaction is run by the licensed partner, under the law shown on the company’s profile.',
  cta_notify='Get notified when intentions open', cta_after='What happens after my declaration?',
  cta_line='Intention declarations open once the licensed partner signs · price per ticket band · valid 12 months · transferable credit',
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
  loc_elig='<b>Eligibility.</b> At least {seuil} raised, non-listed companies, main operations {in_}.',
  loc_partner='<b>Partner sought.</b> {partner_short}.', loc_src='<b>Sources.</b>',
  loc_more='Method and rules, common to all countries →',
  fol_h='Get every new edition', fol_p='New entries, exits and movements, every quarter.',
  form_prefix='follow-', email_lab='Your e-mail', email_ph='you@email.com', prof_aria='Your profile',
  prof_inv='Investor', prof_ceo='Startup manager', prof_bank='Investment bank / adviser', prof_other='Other', fol_btn='Follow',
  fol_fine='One e-mail per edition. One-click unsubscribe. No data passed on to third parties.',
  fol_soon='Coming soon: subscriptions will open shortly.',
  cad='Quarterly', next='Next edition: {next}',
  js_body='Hello,\\n\\nI would like to receive every new edition of the Uback {name} ranking.\\n\\nE-mail: \'+em+\'\\nProfile: \'+pr+\'\\n',
  js_subject='Follow the Uback {name} ranking',),
}
V = dict(name=M['name'], in_=M['in'], In_=cap(M['in']), the=M['the'], adj_m=M['adj_m'], adj_f=M['adj_f'], adj_fp=M['adj_fp'],
         N=N, next=M['next_edition'], months=M['months_txt'], cities=M['cities'], date=D['date_label'], seuil=e(D['seuil_levee']), partner_short=M['partner_short'])
L = {k: v.format(**V) for k, v in TXT[M['lang']].items()}
PP, PT = L['p_partner'], L['p_thanks']
# méthode et mentions légales : pages globales, communes à tous les pays (générées par tools/build_home.py)
GM = '@ROOT@fr/methode.html' if M['lang'] == 'fr' else '@ROOT@method.html'
GL = '@ROOT@mentions-legales.html' if M['lang'] == 'fr' else '@ROOT@legal-notice.html'

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
</head>
<body>
<a class="skip" href="#main">{L['skip']}</a>
<div class="beta"><div class="wrap"><b>{L['beta_b']}</b><span class="beta-t">— {L['beta_t']}</span><a href="mailto:contact@uback.com">{L['beta_link']}</a></div></div>
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
      <a href="/#backers">Backers</a>
      <a href="/{PP}">{L['nav_partner']}</a>
      <a href="{GM}">{L['nav_method']}</a>
    </nav>
    <span class="spacer"></span>
    <span class="langs">{langs}</span>
    <a class="btn" href="/#{L['id_follow']}">{L['follow']}</a>
    <a class="btn gold" href="/#backers">{L['declare']}</a>
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
      <span>·</span><a href="{GM}">{L['f_method']}</a>
      <span>·</span><a href="/{PP}">{L['f_partner']}</a>
      <span>·</span><a href="{GM}#correction">{L['f_corr']}</a>
      <span>·</span><a href="{GL}">{L['f_legal']}</a>
      <span class="spacer"></span>
      <span>Uback.com · {datetime.date.today().year}</span>
    </div>
    <p>{L['f_disc']}</p>
  </div>
</footer>
</body>
</html>
'''

def conf(n):
    dots = ''.join('<i class="f"></i>' if i < n else '<i></i>' for i in range(3))
    return f'<span class="conf" aria-hidden="true">{dots}</span><span class="conf-l">{L["conf" + str(n)]}</span>'

def val(c):
    """Tranche de valorisation estimée par IA + confiance ; la justification s'affiche au survol ou au tap (bouton + infobulle)."""
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
            f'<span class="val-tip" role="tooltip" id="{tid}">{e(c.get("valuation_basis", ""))}</span></span>')

def invest(c):
    """Colonne « Investir » : bouton d'intention, précédé d'un badge d'état s'il y a lieu.
    acces : defaut | levee (levée en cours) | travaillee (suivie par le partenaire du marché) | sortie (rachat, sans bouton).
    L'état par défaut n'affiche aucun libellé ; « travaillee » n'est jamais affiché sans partenaire signé."""
    a = c.get('acces') or 'defaut'
    btn = f'<a class="btn" href="/#backers">{L["declare_cell"]}</a>'
    if a == 'sortie':
        who = (c.get('acquereur') or '').strip()
        return f'<span class="exit">{L["exit_by"].format(a=e(who)) if who else L["exit"]}</span>'
    if a == 'levee':
        return f'<span class="inv-badge gold">{L["b_levee"]}</span>{btn}'
    if a == 'travaillee' and M.get('partner_name'):
        return f'<span class="inv-badge line">{L["b_suivie"].format(p=e(M["partner_name"]))}</span>{btn}'
    return btn

def row(c):
    top = ' class="top"' if c['rang'] == 1 else ''
    jur = ''
    if c.get('juridiction') and (not c['juridiction'].startswith(M['name']) or ';' in c['juridiction']):
        jur = f'<span class="jur">{e(c["juridiction"])}</span>'
    note = f'<div class="src">{e(c["note"])}</div>' if c.get('note') else ''
    subject = quote(L['report_subject'].format(co=c['nom']))
    report = f'<a class="report" href="mailto:contact@uback.com?subject={subject}">{L["report"]}</a>'
    return f'''<tr{top}>
<td class="rank">{c['rang']}</td>
<td><span class="co">{e(c['nom'])}<small>{e(c['ville'])} · {L['founded']} {c['creation']}</small></span>{jur}{note}{report}</td>
<td data-l="{L['l_sub']}">{e(c['sous_secteur'])}</td>
<td data-l="{L['l_fund']}">{e(c['leve_cumule'])}{L['raised']}<br><span class="src">{e(c['derniere_levee'])} · {src(c['source'])}</span></td>
<td data-l="{L['l_val']}">{val(c)}</td>
<td data-l="{L['l_conf']}">{conf(c['confiance'])}</td>
<td class="act">{invest(c)}</td>
</tr>'''

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
      <p class="lead">{L['lead']}</p>
      <div class="meta">
        <span class="tag beta">{e(EDITION)} · {e(D['date_label'])}</span>
        <span class="tag cad">{L['cad']}</span><span>{L['next']}</span><span>·</span>
        <span>{L['m_consensus']}</span><span>·</span>
        <a href="{GM}">{L['m_method']}</a><span>·</span>
        <span>{L['m_order']}</span>
      </div>
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
      <div class="tabs"><a class="on" href="#{L['id_rank']}">Top {N}</a><a href="#radar">Radar</a><a href="#{L['id_born']}">{L['t_born']}</a><a href="/{PP}#challengers">Challengers</a></div>
      <span class="spacer"></span>
      <span class="sub">{L['first_ed']}</span>
    </div>
    <table class="tbl">
      <thead><tr><th>#</th><th>{L['th_co']}</th><th>{L['th_sub']}</th><th>{L['th_fund']}</th><th>{L['th_val']}</th><th>{L['th_conf']}</th><th class="th-inv">{L['th_invest']}</th></tr></thead>
      <tbody>
      {''.join(row(c) for c in RANKED)}
      </tbody>
    </table>
    <div class="disclaimer"><b>{L['disc_b']}</b> {L['val_disc']} {e(D['methode'])} {L['disc']}</div>

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

<section class="soft" id="regards">
  <div class="wrap">
    <div class="sec-head"><h2>{L['reg_h2']}</h2></div>
    <div class="grid3">
      <div class="card"><div class="ic">{IC_AI}</div><h3>{L['reg_ai_h']}</h3><p>{L['reg_ai']}</p></div>
      <div class="card"><div class="ic">{IC_HUM}</div><h3>{L['reg_hum_h']}</h3><p>{L['reg_hum']}</p></div>
      <div class="card"><div class="ic">{IC_MON}</div><h3>{L['reg_mon_h']}</h3><p>{L['reg_mon']}</p></div>
    </div>
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
      <a class="btn ghost" href="{GM}#{L['id_after']}">{L['cta_after']}</a>
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
        <a class="btn navy" href="/{PP}">{L['of_btn']}</a>
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
      <p>{L['loc_elig']}</p>
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
    PAGES[PP] = head(f"Devenir le partenaire exclusif Uback {M['in']} | Uback", "Banques d'affaires, boutiques M&A, conseils agréés : Uback vous apporte des investisseurs étrangers et de la visibilité, en exclusivité par pays.", f"/{PP}") + f'''
<div class="wrap prose">
<h1>Devenir le partenaire exclusif Uback {M['in']}</h1>
<p class="lead">Uback classe les startups d’un pays et agrège les intentions d’investissement des business angels, family offices, corporates et investisseurs de la diaspora, en Europe, dans le Golfe et ailleurs. Un seul partenaire par pays exécute : c’est vous.</p>

<h2>Ce que Uback vous apporte</h2>
<ul>
<li><b>Des investisseurs que vous ne trouveriez pas seul.</b> Les intentions déclarées sur votre marché vous sont réservées : montants, secteurs, sociétés convoitées, avec l’identité des Backers qui ont consenti à être mis en relation.</li>
<li><b>De la visibilité.</b> Votre nom, votre statut réglementaire et votre numéro d’immatriculation apparaissent sur chaque classement du pays (« Mises en relation assurées par… »), et sur votre page partenaire.</li>
<li><b>Un tableau de bord.</b> Alertes quand les intentions sur une société ou un secteur franchissent le seuil, suivi des dossiers, trace de chaque contact.</li>
<li><b>Un kit de prospection trimestriel.</b> Une synthèse des intentions de votre marché, à envoyer à vos propres clients.</li>
<li><b>Une voix.</b> Vous pouvez publier des notes sous votre nom sur votre marché.</li>
</ul>

<h2>Ce que Uback ne vous apporte pas</h2>
<p>Un flux de deals garanti. Dans un marché comme {M['the']}, avec {M['deals_phrase']}, Uback est un canal d’investisseurs et de notoriété supplémentaire, pas une source de revenus immédiate. Nous préférons le dire avant.</p>

<h2>Le cadre</h2>
<ul>
<li><b>Exclusivité par pays</b>, contrat annuel renouvelable et renégociable selon l’audience.</li>
<li><b>Vous restez seul maître des actes réglementés :</b> contact des sociétés, mandats, conseil, structuration, négociation, encaissement. Uback ne fait rien de tout cela.</li>
<li><b>Rémunération :</b> une redevance annuelle, avance sur les rétrocessions dues sur les deals conclus avec des Backers présentés par Uback.</li>
<li><b>Profil recherché :</b> {M['partner_long']}.</li>
</ul>

<h2 id="challengers">Pour les dirigeants : les Challengers</h2>
<p>Une société éligible qui ne figure pas dans le classement pourra, contre paiement, s’afficher dans une liste séparée et étiquetée « Challengers », pour une durée déterminée, avec un mémo accessible aux Backers vérifiés. Le référencement n’a aucun effet sur le classement. Ouverture après la signature du partenaire.</p>

<h2>Nous contacter</h2>
<p>Écrivez à <a href="mailto:partenaires@uback.com">partenaires@uback.com</a>. Nous vous enverrons le dossier partenaire (modèle économique, contrat type, calendrier) et conviendrons d’un échange.</p>
</div>
''' + FOOT

    PAGES[PT] = head(f"Merci | Uback {M['name']}", "Inscription confirmée.", f"/{PT}") + f'''
<div class="wrap prose" style="padding:60px 24px">
<h1>Merci, c’est noté.</h1>
<p class="lead">Si votre messagerie s’est ouverte, envoyez simplement le message préparé : vous recevrez chaque nouvelle édition du classement {M['adj_m']}, et un mot dès l’ouverture des déclarations d’intention.</p>
<p>Sinon, écrivez-nous à <a href="mailto:{FORM_EMAIL}">{FORM_EMAIL}</a> avec pour objet « Suivre le classement Uback {M['name']} ».</p>
<p><a class="btn navy" href="/">Retour au classement</a></p>
</div>
''' + FOOT

else:
    PAGES[PP] = head(f"Become Uback’s exclusive partner {M['in']} | Uback", "Investment banks, M&A boutiques, licensed advisers: Uback brings you foreign investors and visibility, exclusively per country.", f"/{PP}") + f'''
<div class="wrap prose">
<h1>Become Uback’s exclusive partner {M['in']}</h1>
<p class="lead">Uback ranks a country’s startups and aggregates investment intentions from business angels, family offices, corporates and diaspora investors, in Europe, the Gulf and elsewhere. A single partner per country executes: you.</p>

<h2>What Uback brings you</h2>
<ul>
<li><b>Investors you would not find on your own.</b> The intentions declared on your market are reserved for you: amounts, sectors, sought-after companies, with the identity of the Backers who agreed to be introduced.</li>
<li><b>Visibility.</b> Your name, regulatory status and registration number appear on every ranking of the country (“Introductions made by…”), and on your partner page.</li>
<li><b>A dashboard.</b> Alerts when intentions on a company or a sector cross the threshold, deal tracking, a record of every contact.</li>
<li><b>A quarterly prospecting kit.</b> A summary of the intentions on your market, to send to your own clients.</li>
<li><b>A voice.</b> You can publish notes under your name on your market.</li>
</ul>

<h2>What Uback does not bring you</h2>
<p>A guaranteed deal flow. In a market like {M['the']}, with {M['deals_phrase']}, Uback is an additional channel for investors and visibility, not a source of immediate revenue. We would rather say so upfront.</p>

<h2>The framework</h2>
<ul>
<li><b>Exclusive per country</b>, annual contract, renewable and renegotiable according to the audience.</li>
<li><b>You alone remain in charge of regulated activities:</b> contacting companies, mandates, advice, structuring, negotiation, collection of funds. Uback does none of this.</li>
<li><b>Remuneration:</b> an annual fee, as an advance on the retrocessions due on deals closed with Backers introduced by Uback.</li>
<li><b>Profile sought:</b> {M['partner_long']}.</li>
</ul>

<h2 id="challengers">For managers: the Challengers</h2>
<p>An eligible company that is not in the ranking will be able, for a fee, to appear in a separate list labelled “Challengers”, for a set period, with a memo available to verified Backers. The listing has no effect on the ranking. Opens once the partner signs.</p>

<h2>Contact us</h2>
<p>Write to <a href="mailto:partenaires@uback.com">partenaires@uback.com</a>. We will send you the partner pack (business model, standard contract, timeline) and arrange a call.</p>
</div>
''' + FOOT

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
<script>location.replace('{target}' + location.search + location.hash);</script>
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

# version secondaire (ex. /ma/fr) : les anciennes adresses de ses pages à la racine du marché redirigent
if not M['default']:
    root_dir = f"{ROOT}/{M['code']}"
    dv = next(v for v in M['variants'] if v['default'])
    taken = {TXT[dv['lang']]['p_' + k] for k in ('method', 'partner', 'legal', 'thanks')}   # pages de la version principale
    for name in PAGES:
        if name not in taken:
            redirect(f'{root_dir}/{name}', f'{PREFIX}/{name}')
    for name, target in ((L['p_method'], G_METHOD), (L['p_legal'], G_LEGAL)):
        if name not in taken:
            redirect(f'{root_dir}/{name}', target)
