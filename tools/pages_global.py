# -*- coding: utf-8 -*-
"""Texte des pages globales (communes à tous les pays), rendues par tools/build_home.py :
/method.html et /fr/methode.html (méthode et règles du jeu, v2), /legal-notice.html et /mentions-legales.html.
Les pages pays n'ont pas de méthode propre : elles affichent un encadré « La méthode au Maroc… » qui renvoie ici.
Ancres utilisées par les pages pays : #estimation, #eligibilite / #eligibility, #avis-humains / #human-input,
#correction, #investir / #invest."""

METHOD = {
'fr': """<div class="wrap prose">
<h1>Méthode et règles du jeu</h1>
<p class="lead"><b>Uback classe les startups technologiques non cotées par ordre décroissant de valorisation estimée.</b> L’estimation est faite par des intelligences artificielles, à partir des informations disponibles : levées de fonds, valorisations publiées, indicateurs d’activité, investisseurs, comparables. Uback publie le rang et un ordre de grandeur, jamais un chiffre.</p>

<h2>Le marché décide, Uback estime</h2>
<p>La valeur d’une startup n’existe vraiment qu’au moment où elle est fixée par un accord : une levée de fonds, une cession, une entrée en bourse. Entre deux opérations, elle évolue en permanence, comme un cours de bourse, sans que personne ne l’observe.</p>
<p>Uback ne prétend pas fixer cette valeur. Il l’estime, avec les informations disponibles, dans un seul but : classer les sociétés entre elles. L’exercice est par nature imprécis. C’est pourquoi Uback publie des rangs et des tranches, jamais une valorisation chiffrée.</p>
<p>Le montant levé n’est pas le critère de classement. C’est un indice parmi d’autres. Une société qui a peu levé mais croît vite et rentablement peut valoir plus qu’une société qui a beaucoup levé.</p>

<h2>Deux familles de classements</h2>
<p><b>Par pays : tous secteurs confondus, puis par secteur.</b> Un classement pays réunit les startups dont les opérations principales (équipe, marché) sont dans le pays. Il est publié chaque trimestre, le 15 du mois. Chaque pays a son propre mois de départ : le Maroc, par exemple, est publié en février, mai, août et novembre. Les pays étant décalés les uns des autres, Uback publie chaque mois. La date de la prochaine édition figure sur la page d’accueil et sur la page de chaque pays.</p>
<p><b>Mondiaux, par segment.</b> Un classement mondial compare une startup à ses concurrents directs, où qu’ils soient : covoiturage, crypto exchanges, paie… Les segments s’inscrivent dans une arborescence publique à trois niveaux (famille &gt; secteur &gt; segment). Ces classements seront publiés deux fois par an, le 1er janvier et le 1er juillet. Les premiers sont en préparation.</p>
<p>Une même société peut donc figurer dans deux classements : celui de son pays et celui de son segment.</p>
<p><b>Pourquoi un rythme trimestriel et semestriel ?</b> Entre deux opérations, les informations disponibles sur une société non cotée changent peu. Un rythme espacé permet aux IA une analyse plus approfondie à chaque édition. Entre deux éditions, le Radar est mis à jour au fil des levées annoncées.</p>

<h2 id="estimation">Comment la valorisation est estimée</h2>
<p><b>Les mêmes données pour toutes les IA.</b> Pour chaque société éligible, Uback constitue un dossier de faits datés. Ce dossier comprend :</p>
<ul>
<li>les tours de financement : montant, date, nature, investisseurs ;</li>
<li>les valorisations publiées ;</li>
<li>les indicateurs d’activité connus : chiffre d’affaires, croissance, effectifs, clients, rentabilité, agréments ;</li>
<li>les rachats et introductions en bourse comparables dans le même segment.</li>
</ul>
<p>Chaque segment a ses indicateurs clés (par exemple, pour les néobanques : clients, chiffre d’affaires, résultat). Ils sont affichés sur la page du classement, tels que publiés et datés.</p>
<p><b>Plusieurs estimations indépendantes.</b> Chaque IA estime la valorisation de chaque société sans connaître les réponses des autres.</p>
<p><b>Le consensus.</b> L’estimation retenue est la médiane des estimations des IA. C’est elle qui détermine le rang : le n° 1 est la société dont la valorisation estimée est la plus élevée. L’ordre de grandeur affiché est la tranche qui contient cette médiane. Le rang et la tranche sont donc toujours cohérents.</p>
<p><b>L’indice de confiance.</b> Il est affiché pour chaque société et combine deux éléments : l’accord entre les IA et la qualité des données.</p>
<ul>
<li><b>Élevé</b> : les estimations convergent, et reposent sur une valorisation publiée ou un tour chiffré de moins de 24 mois.</li>
<li><b>Moyen</b> : les estimations divergent modérément, ou les données ont plus de 24 mois.</li>
<li><b>Faible</b> : les estimations divergent fortement, ou reposent sur une source unique.</li>
</ul>
<p>Quand les IA ne s’accordent pas, cette divergence est elle-même une information.</p>
<p><b>Des données de plus en plus riches.</b> Chaque édition intègre de nouvelles sources. La précision des estimations doit progresser d’une édition à l’autre.</p>
<p><b>Édition 0 (bêta).</b> Les premières éditions ont été établies par une seule IA (Claude, Anthropic), à partir d’une recherche documentaire. L’indice de confiance y reflète la seule qualité des sources. Le consensus de plusieurs IA s’appliquera prochainement, lors d’une future édition.</p>

<h2>L’ordre de grandeur</h2>
<p>Uback affiche une tranche, jamais un chiffre :</p>
<div class="table-wrap"><table>
<tr><th>Tranche</th><th>Valorisation estimée</th></tr>
<tr><td>Centaines de k$</td><td>100 k$ à 1 M$</td></tr>
<tr><td>Millions $</td><td>1 à 10 M$</td></tr>
<tr><td>Dizaines de M$</td><td>10 à 100 M$</td></tr>
<tr><td>Centaines de M$</td><td>100 M$ à 1 Md$</td></tr>
<tr><td>Licorne</td><td>1 à 10 Md$</td></tr>
<tr><td>Décacorne</td><td>plus de 10 Md$</td></tr>
</table></div>
<p>Au sein d’une tranche, les sociétés restent classées selon leur estimation. Quand les données ne permettent pas une estimation sérieuse, la société n’est pas classée. Elle figure au Radar.</p>
<p>Ces estimations sont éditoriales et indicatives. Elles ne constituent ni une évaluation financière, ni une offre, ni un conseil en investissement.</p>

<h2 id="eligibilite">Qui est éligible</h2>
<div class="table-wrap"><table>
<tr><th>Règle</th><th>Application</th></tr>
<tr><td>Startup technologique ou innovante</td><td>Le périmètre est défini par l’arborescence publique des secteurs, qui évolue.</td></tr>
<tr><td>A levé au moins 1 M$, dont un tour en fonds propres</td><td>Le seuil est cumulé, en fonds propres ou en dette, et au moins un tour doit avoir été réalisé en fonds propres. Des investisseurs sont donc déjà au capital et ont négocié leurs droits. Une subvention n’est pas une levée. Le même seuil s’applique dans tous les pays.</td></tr>
<tr><td>Non cotée</td><td>Les sociétés cotées sont affichées à part, comme repères, et ne sont jamais classées.</td></tr>
<tr><td>Active</td><td>Une société rachetée, fermée ou en procédure collective sort du classement. L’historique conserve ses positions.</td></tr>
<tr><td>Une activité principale</td><td>Chaque société est rattachée à un seul secteur et à un seul segment. Les conglomérats sont exclus.</td></tr>
<tr><td>Pays des opérations</td><td>Le pays retenu est celui des opérations, quel que soit le siège juridique. Le siège est indiqué sur la fiche. Les sociétés d’origine locale opérées depuis l’étranger figurent dans « Nées ici, établies ailleurs ».</td></tr>
</table></div>

<h2>Classement, Challengers, Radar</h2>
<ul>
<li><b>Le classement</b> : jusqu’à 20 sociétés par ordre de valorisation estimée. Il est plus court quand le marché compte moins de sociétés estimables. Rien ne s’y achète.</li>
<li><b>Les Challengers</b> : un espace de visibilité payant, réservé aux sociétés immatriculées en recherche de financement qui veulent se faire connaître des investisseurs. Il est affiché séparément, étiqueté comme sponsorisé, et n’a aucun effet sur le classement. Un Challenger qui devient éligible et estimable entre dans le classement dans les mêmes conditions que les autres sociétés.</li>
<li><b>Le Radar</b> : les autres sociétés éligibles connues, triées par date de dernière levée. Il est mis à jour en continu, sans estimation.</li>
</ul>

<h2 id="avis-humains">Règles de prise en compte des inputs des humains</h2>
<p>Uback ouvrira ses classements aux avis d’analystes. Un analyste pourra publier, sous son nom, une lecture critique d’un classement : pourquoi telle société lui paraît sous-estimée, pourquoi telle autre lui paraît surestimée. Ces textes lui permettront de faire connaître son expertise. Les lecteurs pourront les juger utiles ou non.</p>
<p>Les IA pourront tenir compte de ces avis, sans y être tenues. <b>Seules les IA décident du classement, et elles n’ont pas à justifier la prise en compte ou non d’un avis.</b> Aucun avis, aucun vote, aucun paiement ne s’impose à elles.</p>
<p>Les règles selon lesquelles les IA considèrent ces avis figurent dans les instructions qui leur sont données, et ces instructions sont publiques.</p>
<p>Les corrections de faits sont traitées différemment (voir « Corrections ») : un montant, une date ou un statut erroné est corrigé dans les données dès qu’il est vérifié.</p>

<h2>Les règles du jeu</h2>
<ol>
<li><b>Le classement n’est jamais à vendre.</b> Aucun paiement, d’une société, d’un partenaire ou d’un investisseur, n’influence un rang ni une tranche.</li>
<li><b>Aucun humain ne modifie l’ordre.</b> Un humain peut exclure une société pour un motif d’éligibilité, de façon tracée, ou relancer le calcul. Il ne réordonne jamais.</li>
<li><b>La méthode est publique.</b> Cette page et les instructions données aux IA pour chaque type de classement (pays, segment) sont publiques. Les données de travail et les estimations chiffrées ne le sont pas.</li>
<li><b>Uback n’est pas un intermédiaire financier.</b> Uback ne détient aucun mandat, ne négocie pas, ne donne pas de conseil et n’encaisse aucun fonds destiné à un investissement. Toute opération est proposée par le partenaire agréé du pays, sous sa propre responsabilité.</li>
<li><b>Les données ne sortent pas.</b> Les intentions d’investissement sont confidentielles. Aucune donnée n’est vendue. Elles ne sont transmises qu’au partenaire agréé du pays, avec le consentement de l’investisseur.</li>
</ol>
<div class="callout" id="investir"><p><b>Investir.</b> Uback permet aux investisseurs de déclarer une intention d’investissement sur un secteur, un pays, ou une société ouverte aux Backers. La mécanique est décrite sur la page « <a href="/fr/investir.html">Investir avec Uback</a> ».</p></div>

<h2 id="correction">Corrections</h2>
<p>Toute société citée peut signaler une information inexacte (montant, date, secteur, statut) ou contester son rang, via le <a href="/fr/correction.html">formulaire de correction</a>. Chaque demande reçoit une réponse motivée, et chaque correction de fait est tracée.</p>
<p>Une société ne peut pas demander à ne pas figurer dans un classement. Uback traite d’informations publiques sur des acteurs de la vie économique. Seul un motif d’éligibilité peut entraîner une sortie.</p>

<h2>Sources et limites</h2>
<p>Uback s’appuie sur la presse économique et technologique de chaque pays, la presse internationale, les rapports de place, les registres publics et des services de données. Chaque page pays cite les médias et services utilisés.</p>
<p>Uback n’exclut ni les erreurs d’interprétation ni la reprise involontaire d’informations inexactes publiées ailleurs. Nous faisons de notre mieux pour les écarter, et nous corrigeons dès qu’une erreur est signalée.</p>
</div>
""",
'en': """<div class="wrap prose">
<h1>Method and rules of the game</h1>
<p class="lead"><b>Uback ranks non-listed tech startups in descending order of estimated valuation.</b> The estimate is produced by artificial intelligence models, using the information available: funding rounds, published valuations, business metrics, investors, comparables. Uback publishes the rank and an order of magnitude, never a figure.</p>

<h2>The market decides, Uback estimates</h2>
<p>A startup’s value only truly exists when an agreement sets it: a funding round, a sale, an IPO. Between two transactions, it keeps moving, like a share price, without anyone observing it.</p>
<p>Uback does not claim to set that value. It estimates it, with the information available, for one purpose only: to rank companies against each other. The exercise is imprecise by nature. That is why Uback publishes ranks and ranges, never a valuation figure.</p>
<p>The amount raised is not the ranking criterion. It is one signal among others. A company that has raised little but grows fast and profitably may be worth more than one that has raised a lot.</p>

<h2>Two families of rankings</h2>
<p><b>By country: all sectors, then by sector.</b> A country ranking covers startups whose main operations (team, market) are in that country. It is published every quarter, on the 15th of the month. Each country has its own starting month: Morocco, for example, is published in February, May, August and November. Because countries are staggered, Uback publishes every month. The date of the next edition is shown on the homepage and on each country page.</p>
<p><b>Global, by segment.</b> A global ranking compares a startup with its direct competitors, wherever they are: carpooling, crypto exchanges, payroll… Segments sit in a public three-level taxonomy (family &gt; sector &gt; segment). These rankings will be published twice a year, on January 1 and July 1. The first ones are in preparation.</p>
<p>The same company can therefore appear in two rankings: its country’s and its segment’s.</p>
<p><b>Why quarterly and twice-yearly?</b> Between two transactions, the information available on a non-listed company changes little. A slower pace gives the AI models room for deeper analysis at each edition. Between editions, the Radar is updated as funding rounds are announced.</p>

<h2 id="estimation">How valuation is estimated</h2>
<p><b>The same data for every AI.</b> For each eligible company, Uback builds a file of dated facts. It includes:</p>
<ul>
<li>funding rounds: amount, date, type, investors;</li>
<li>published valuations;</li>
<li>known business metrics: revenue, growth, headcount, customers, profitability, licences;</li>
<li>comparable acquisitions and IPOs in the same segment.</li>
</ul>
<p>Each segment has its own key metrics (for consumer neobanks: customers, revenue, profit). They are shown on the ranking page, as published and dated.</p>
<p><b>Several independent estimates.</b> Each AI estimates the valuation of each company without knowing the others’ answers.</p>
<p><b>The consensus.</b> The estimate used is the median of the AI estimates. It determines the rank: number 1 is the company with the highest estimated valuation. The order of magnitude shown is the range containing that median. Rank and range are therefore always consistent.</p>
<p><b>The confidence index.</b> It is shown for each company and combines two things: agreement between the AI models, and data quality.</p>
<ul>
<li><b>High</b>: estimates converge, and rest on a published valuation or a disclosed round less than 24 months old.</li>
<li><b>Medium</b>: estimates diverge moderately, or the data is more than 24 months old.</li>
<li><b>Low</b>: estimates diverge sharply, or rest on a single source.</li>
</ul>
<p>When the AI models disagree, the disagreement is information in itself.</p>
<p><b>Richer data over time.</b> Each edition adds new sources. Estimates should become more precise from one edition to the next.</p>
<p><b>Edition 0 (beta).</b> The first editions were produced by a single AI (Claude, Anthropic), from desk research. The confidence index reflects source quality only. A consensus of several AI models will apply soon, in a future edition.</p>

<h2>Order of magnitude</h2>
<p>Uback shows a range, never a figure:</p>
<div class="table-wrap"><table>
<tr><th>Range</th><th>Estimated valuation</th></tr>
<tr><td>Hundreds of k$</td><td>$100k to $1M</td></tr>
<tr><td>Millions</td><td>$1M to $10M</td></tr>
<tr><td>Tens of millions</td><td>$10M to $100M</td></tr>
<tr><td>Hundreds of millions</td><td>$100M to $1B</td></tr>
<tr><td>Unicorn</td><td>$1B to $10B</td></tr>
<tr><td>Decacorn</td><td>over $10B</td></tr>
</table></div>
<p>Within a range, companies remain ranked by their estimate. When the data does not allow a serious estimate, the company is not ranked. It appears in the Radar.</p>
<p>These estimates are editorial and indicative. They are neither a financial valuation, nor an offer, nor investment advice.</p>

<h2 id="eligibility">Who is eligible</h2>
<div class="table-wrap"><table>
<tr><th>Rule</th><th>How it applies</th></tr>
<tr><td>Tech or innovative startup</td><td>The scope is defined by the public sector taxonomy, which evolves.</td></tr>
<tr><td>Has raised at least $1M, including one equity round</td><td>The threshold is cumulative, equity or debt, and at least one round must have been an equity round. Investors are therefore already on the cap table and have negotiated their rights. A grant is not a funding round. The same threshold applies in every country.</td></tr>
<tr><td>Non-listed</td><td>Listed companies are shown separately, as benchmarks, and are never ranked.</td></tr>
<tr><td>Active</td><td>A company that has been acquired, has closed or is in insolvency proceedings leaves the ranking. Its past positions remain in the history.</td></tr>
<tr><td>One main activity</td><td>Each company belongs to one sector and one segment only. Conglomerates are excluded.</td></tr>
<tr><td>Country of operations</td><td>The country used is the country of operations, whatever the legal seat. The seat is shown on the company profile. Locally founded companies run from abroad appear in “Born here, based elsewhere”.</td></tr>
</table></div>

<h2>Ranking, Challengers, Radar</h2>
<ul>
<li><b>The ranking</b>: up to 20 companies in order of estimated valuation. It is shorter when a market has fewer companies that can be estimated. Nothing in it can be bought.</li>
<li><b>Challengers</b>: a paid visibility space, reserved for registered companies raising funds that want to be seen by investors. It is displayed separately, labelled as sponsored, and has no effect on the ranking. A Challenger that becomes eligible and can be estimated enters the ranking on the same terms as any other company.</li>
<li><b>The Radar</b>: the other known eligible companies, sorted by date of last funding round. Updated continuously, without estimates.</li>
</ul>

<h2 id="human-input">How human input is taken into account</h2>
<p>Uback will open its rankings to analysts’ views. An analyst will be able to publish, under their own name, a critical reading of a ranking: why one company seems underestimated, why another seems overestimated. These pieces will let them showcase their expertise. Readers will be able to rate them as useful or not.</p>
<p>The AI models may take these views into account, but are not bound to. <b>Only the AI models decide the ranking, and they do not have to justify whether or not they took a view into account.</b> No view, vote or payment is binding on them.</p>
<p>The rules by which the AI models consider these views are part of the instructions given to them, and those instructions are public.</p>
<p>Factual corrections are handled differently (see “Corrections”): a wrong amount, date or status is corrected in the data as soon as it is verified.</p>

<h2>Rules of the game</h2>
<ol>
<li><b>The ranking is never for sale.</b> No payment, from a company, a partner or an investor, influences a rank or a range.</li>
<li><b>No human changes the order.</b> A human may exclude a company on eligibility grounds, with a record kept, or re-run the calculation. Never reorder it.</li>
<li><b>The method is public.</b> This page and the instructions given to the AI models for each type of ranking (country, segment) are public. Working data and estimate figures are not.</li>
<li><b>Uback is not a financial intermediary.</b> Uback holds no mandate, does not negotiate, gives no advice and collects no funds intended for investment. Any transaction is offered by the country’s licensed partner, under its own responsibility.</li>
<li><b>Data stays in.</b> Investment intentions are confidential. No data is sold. It is passed only to the country’s licensed partner, with the investor’s consent.</li>
</ol>
<div class="callout" id="invest"><p><b>Invest.</b> Uback lets investors declare an investment intention on a sector, a country, or a company open to Backers. How it works is described on the “<a href="/invest.html">Invest with Uback</a>” page.</p></div>

<h2 id="correction">Corrections</h2>
<p>Any company mentioned may report inaccurate information (amount, date, sector, status) or dispute its rank, using the <a href="/correction.html">correction form</a>. Every request receives a reasoned reply, and every factual correction is recorded.</p>
<p>A company cannot ask not to appear in a ranking. Uback deals with public information about economic actors. Only an eligibility reason can lead to removal.</p>

<h2>Sources and limits</h2>
<p>Uback relies on each country’s business and tech press, international press, industry reports, public registers and data services. Each country page lists the media and services used.</p>
<p>Uback does not rule out errors of interpretation, or the inadvertent use of inaccurate information published elsewhere. We do our best to keep them out, and we correct them as soon as an error is reported.</p>
</div>
""",
}

LEGAL = {
'fr': """<div class="wrap prose">
<h1>Mentions légales</h1>
<h2>Éditeur</h2>
<p>DEALING-ROOM SARL, SARL au capital de 50 000 € enregistrée en France au RCS de Créteil sous le numéro 485313712. Directeur de la publication : Sebastien Blanchard. Contact : <a href="mailto:contact@uback.com">contact@uback.com</a>.</p>
<h2>Hébergement</h2>
<p>GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis. Site : <a href="https://github.com">github.com</a>.</p>
<h2>Nature du service</h2>
<p>Uback est un éditeur de contenu. Les classements publiés sont des opinions produites par des systèmes d’intelligence artificielle à partir d’informations publiques, selon une méthode publiée. Ils ne constituent ni un conseil en investissement, ni une recommandation personnalisée, ni une sollicitation ou une offre de titres. Uback ne reçoit aucun mandat, ne négocie aucune transaction et n’encaisse aucun fonds destiné à un investissement. Les mises en relation sont réalisées par un partenaire agréé, identifié sur chaque marché, sous sa seule responsabilité réglementaire.</p>
<h2>Droit de réponse</h2>
<p>Toute société citée peut signaler une information inexacte la concernant ou contester son rang, via le <a href="/fr/correction.html">formulaire de correction</a>.</p>
<h2>Données personnelles</h2>
<p>Les adresses e-mail collectées via le formulaire de suivi servent uniquement à l’envoi de chaque nouvelle édition du classement et des informations sur l’ouverture du service. Elles ne sont ni vendues ni transmises à des tiers. Désinscription possible à tout moment. Responsable du traitement : DEALING-ROOM SARL. Droits d’accès, de rectification et d’effacement : <a href="mailto:privacy@uback.com">privacy@uback.com</a>.</p>
<h2>Propriété intellectuelle</h2>
<p>Les classements, textes et éléments graphiques du site sont la propriété de DEALING-ROOM SARL. La reproduction d’un classement est autorisée avec mention de la source et lien vers la page d’origine. Les noms de sociétés cités appartiennent à leurs propriétaires.</p>
</div>
""",
'en': """<div class="wrap prose">
<h1>Legal notice</h1>
<h2>Publisher</h2>
<p>DEALING-ROOM SARL, a French limited liability company (SARL) with a share capital of EUR 50,000, registered with the Créteil Trade and Companies Register under number 485313712. Publication director: Sebastien Blanchard. Contact: <a href="mailto:contact@uback.com">contact@uback.com</a>.</p>
<h2>Hosting</h2>
<p>GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, United States. Website: <a href="https://github.com">github.com</a>.</p>
<h2>Nature of the service</h2>
<p>Uback is a content publisher. The rankings published are opinions produced by artificial intelligence systems from public information, following a published method. They constitute neither investment advice, nor a personal recommendation, nor a solicitation or an offer of securities. Uback receives no mandate, negotiates no transaction and collects no funds intended for an investment. Introductions are made by a licensed partner identified in each market, under its sole regulatory responsibility.</p>
<h2>Right of reply</h2>
<p>Any company mentioned may report inaccurate information about it or dispute its rank, using the <a href="/correction.html">correction form</a>.</p>
<h2>Personal data</h2>
<p>E-mail addresses collected through the follow form are used only to send every new edition of the ranking and information about the opening of the service. They are neither sold nor passed on to third parties. You may unsubscribe at any time. Data controller: DEALING-ROOM SARL. Rights of access, rectification and erasure: <a href="mailto:privacy@uback.com">privacy@uback.com</a>.</p>
<h2>Intellectual property</h2>
<p>The rankings, texts and graphic elements of the website are the property of DEALING-ROOM SARL. Reproducing a ranking is allowed with credit to the source and a link to the original page. Company names belong to their owners.</p>
</div>
""",
}

# Page « Investir avec Uback » : « @OPENING@ » est remplacé selon l'état des inscriptions (FORM_MODE de build_home.py).
INVEST = {
'fr': """<div class="wrap prose">
<h1>Investir avec Uback</h1>
<p class="lead"><b>Le nombre fait la force.</b> Seul, un investisseur n’a pas accès au capital des meilleures startups d’un pays. Ensemble, les Backers d’Uback forment un pool d’investisseurs que ces sociétés ne peuvent pas ignorer.</p>

<h2 id="principe">Le principe</h2>
<p>Uback fonctionne comme un achat groupé. Vous déclarez votre intention d’investir dans un secteur (classement mondial) ou dans un pays. Votre intention rejoint le pool correspondant. Quand une société classée est ouverte aux Backers, parce qu’un actionnaire envisage de céder ou qu’elle prévoit de lever, vous pouvez aussi rejoindre le pool de cette société. Quand leur nombre et leur montant cumulé atteignent un seuil, le partenaire agréé du pays présente cette demande à la société.</p>
<p>Uback ne vend pas de titres et ne collecte aucun fonds. Il rassemble des intentions. L’investissement lui-même, s’il a lieu, est proposé par le partenaire agréé, sous sa responsabilité.</p>

<h2 id="etapes">En quatre étapes</h2>
<ol class="steps4">
<li><b>Vous déclarez une intention.</b> Sur un secteur ou un pays, avec une tranche de ticket, et si vous le souhaitez les sociétés que vous aimeriez voir en priorité. Sur une société précise, quand elle est ouverte aux Backers.</li>
<li><b>La masse critique est atteinte.</b> Les intentions s’additionnent dans le pool. Quand le seuil est franchi, le pool est transmis au partenaire agréé du pays.</li>
<li><b>Le partenaire agréé structure.</b> Il contacte la société, lui présente la demande des Backers et vérifie si les attentes convergent : montant, valorisation, droits.</li>
<li><b>Closing.</b> Si un accord est possible, le partenaire présente l’opération directement aux Backers concernés. Chacun décide librement d’y participer ou non. Les petits tickets sont regroupés dans un véhicule commun créé par le partenaire.</li>
</ol>

<h2 id="qui">Qui peut déclarer une intention</h2>
<p>Les déclarations sont réservées :</p>
<ul>
<li>aux <b>investisseurs qui se déclarent avertis</b> : business angels, family offices, investisseurs de la diaspora, qui connaissent les risques de l’investissement dans des sociétés non cotées ;</li>
<li>aux <b>entreprises</b> qui investissent pour leur propre compte (corporate venture, groupes industriels).</li>
</ul>

<h2>Ce que vous déclarez</h2>
<ul>
<li><b>Une cible.</b> Un secteur ou un pays ; ou une société précise, quand elle est ouverte aux Backers. Sur un secteur ou un pays, le partenaire peut vous présenter plusieurs sociétés.</li>
<li><b>Une tranche de ticket</b>, de 25 k$ à 10 M$.</li>
<li><b>Une intention, pas un engagement.</b> Déclarer ne vous oblige pas à investir. La décision finale vous appartient toujours.</li>
</ul>

<h2 id="prix">Pourquoi une intention est payante</h2>
<p>Une intention gratuite ne vaut rien aux yeux d’une startup. Le paiement prouve que la demande est sérieuse, et c’est ce qui donne du poids au partenaire quand il contacte la société.</p>
<p>Le prix dépend du pays et de la tranche de ticket. Il sera affiché à l’ouverture des déclarations dans chaque pays. Le montant payé rémunère la déclaration : ce n’est ni un acompte, ni un investissement, et il n’est pas remboursable.</p>

<h2 id="ouverte">Sociétés ouvertes aux Backers</h2>
<p>Uback n’affiche une intention sur une société que lorsqu’une opération est envisageable : un actionnaire, souvent minoritaire, nous a informés qu’il envisage de céder tout ou partie de ses titres, ou la société nous a informés qu’elle prévoit de lever des fonds prochainement. La ligne de la société porte alors un badge. Les autres sociétés restent classées, et l’intérêt qu’elles suscitent s’exprime à travers le pool de leur secteur ou de leur pays.</p>
<p><a href="mailto:contact@uback.com?subject=Open%20to%20Backers">Actionnaire ou dirigeant ? Contactez-nous</a></p>

<h2 id="duree">Une intention sans date limite, et déplaçable</h2>
<p><b>Votre intention reste valable tant qu’elle n’a pas abouti</b>, sans limite de durée.</p>
<p>Vous pouvez la déplacer à tout moment vers une autre société ou un autre secteur. Elle quitte alors son pool et rejoint le nouveau. Le partenaire peut aussi vous suggérer un déplacement, quand une autre société correspond mieux à votre intention. La décision reste la vôtre.</p>
<p>Si le partenaire présente le pool à une société et qu’aucun accord n’est trouvé, votre intention ne se perd pas. Vous la conservez et pouvez la déplacer.</p>

<h2>Les compteurs</h2>
<p>Chaque société, chaque secteur et chaque pays affiche le nombre de Backers et le montant cumulé de son pool. Pour préserver la confidentialité, ces chiffres sont arrondis par tranches.</p>

<h2>Pourquoi seulement des sociétés déjà financées</h2>
<p><a href="/fr/methode.html#eligibilite">Uback ne classe que des sociétés qui ont levé au moins 1 M$, dont au moins un tour en fonds propres.</a> Des investisseurs professionnels sont donc déjà au capital et ont négocié un pacte d’associés. Les Backers qui entrent à leur tour ne partent pas d’une page blanche.</p>

<h2>Le partenaire agréé</h2>
<p>Dans chaque pays, Uback confie les pools à un seul partenaire : une boutique de fusions-acquisitions ou une société spécialisée en levée de fonds, agréée par le régulateur local. Il est présenté sur la page du pays.</p>
<p>Le partenaire ne reçoit vos coordonnées qu’avec votre consentement, et seulement quand votre pool lui est transmis.</p>

<div class="callout warn" id="risques">
<h2>Les risques</h2>
<p>Investir dans une société non cotée comporte un risque de perte totale du capital investi. Les titres sont peu liquides : il peut être impossible de les revendre pendant plusieurs années. N’investissez que des sommes dont vous pouvez supporter la perte.</p>
</div>

<h2>Ce qu’Uback ne fait pas</h2>
<ul>
<li>Uback ne garantit pas qu’une opération aura lieu.</li>
<li>Uback ne négocie pas, ne conseille pas et ne détient aucun mandat.</li>
<li>Uback n’encaisse aucun fonds destiné à un investissement.</li>
<li>Uback ne vend et ne transmet vos données à personne d’autre que le partenaire du pays.</li>
</ul>

@POOLCTX@
<h2 id="ouverture">Où en est-on ?</h2>
<p>Uback est en bêta publique. Dans chaque pays, les déclarations d’intention ouvriront dès la signature du partenaire agréé. @OPENING@</p>
</div>
""",
'en': """<div class="wrap prose">
<h1>Invest with Uback</h1>
<p class="lead"><b>Strength in numbers.</b> On their own, investors rarely get access to the best startups in a country. Together, Uback’s Backers form an investor pool these companies cannot ignore.</p>

<h2 id="principle">The principle</h2>
<p>Uback works like group buying. You declare your intention to invest in a sector (worldwide ranking) or in a country. Your intention joins the matching pool. When a ranked company is open to Backers, because a shareholder is considering a sale or the company plans to raise, you can also join that company’s pool. When their number and combined amount reach a threshold, the country’s licensed partner presents this demand to the company.</p>
<p>Uback does not sell securities and does not collect any funds. It brings intentions together. The investment itself, if it happens, is offered by the licensed partner, under its own responsibility.</p>

<h2 id="steps">Four steps</h2>
<ol class="steps4">
<li><b>You declare an intention.</b> On a sector or a country, with a ticket range, and if you wish the companies you would like in priority. On a specific company, when it is open to Backers.</li>
<li><b>Critical mass is reached.</b> Intentions add up in the pool. Once the threshold is crossed, the pool is passed to the country’s licensed partner.</li>
<li><b>The licensed partner structures.</b> It contacts the company, presents the Backers’ demand and checks whether expectations match: amount, valuation, rights.</li>
<li><b>Closing.</b> If an agreement is possible, the partner presents the transaction directly to the Backers concerned. Each one freely decides whether to take part. Small tickets are pooled in a common vehicle set up by the partner.</li>
</ol>

<h2 id="who">Who can declare an intention</h2>
<p>Declarations are reserved for:</p>
<ul>
<li><b>investors who declare themselves experienced</b>: business angels, family offices, diaspora investors, who understand the risks of investing in non-listed companies;</li>
<li><b>companies</b> investing on their own account (corporate venture, industrial groups).</li>
</ul>

<h2>What you declare</h2>
<ul>
<li><b>A target.</b> A sector or a country; or a specific company, when it is open to Backers. For a sector or a country, the partner may present several companies to you.</li>
<li><b>A ticket range</b>, from $25k to $10M.</li>
<li><b>An intention, not a commitment.</b> Declaring does not oblige you to invest. The final decision is always yours.</li>
</ul>

<h2 id="price">Why an intention is paid</h2>
<p>A free intention means nothing to a startup. Payment proves the demand is serious, and that is what gives the partner weight when it approaches the company.</p>
<p>The price depends on the country and the ticket range. It will be shown when declarations open in each country. The amount paid covers the declaration: it is neither a deposit nor an investment, and it is non-refundable.</p>

<h2 id="open">Companies open to Backers</h2>
<p>Uback only shows an intention on a company when a transaction is possible: a shareholder, often a minority one, has told us they are considering selling some or all of their shares, or the company has told us it plans to raise funds soon. The company’s row then carries a badge. Other companies remain ranked, and the interest they attract is expressed through the pool of their sector or country.</p>
<p><a href="mailto:contact@uback.com?subject=Open%20to%20Backers">Shareholder or founder? Contact us</a></p>

<h2 id="duration">An intention with no expiry date, that you can move</h2>
<p><b>Your intention remains valid until it succeeds</b>, with no time limit.</p>
<p>You can move it at any time to another company or another sector. It then leaves its pool and joins the new one. The partner may also suggest a move, when another company better matches your intention. The decision remains yours.</p>
<p>If the partner presents the pool to a company and no agreement is reached, your intention is not lost. You keep it and can move it.</p>

<h2>Counters</h2>
<p>Each company, sector and country shows the number of Backers and the combined amount of its pool. To protect confidentiality, these figures are rounded into ranges.</p>

<h2>Why only companies that have already raised funds</h2>
<p><a href="/method.html#eligibility">Uback only ranks companies that have raised at least $1M, including one equity round.</a> Professional investors are therefore already on the cap table and have negotiated a shareholders’ agreement. Backers who come in after them do not start from a blank page.</p>

<h2>The licensed partner</h2>
<p>In each country, Uback entrusts pools to a single partner: an M&amp;A boutique or a fundraising firm, licensed by the local regulator. It is introduced on the country page.</p>
<p>The partner only receives your contact details with your consent, and only when your pool is passed on to it.</p>

<div class="callout warn" id="risks">
<h2>Risks</h2>
<p>Investing in a non-listed company carries a risk of losing all the capital invested. The shares are illiquid: it may be impossible to sell them for several years. Only invest money you can afford to lose.</p>
</div>

<h2>What Uback does not do</h2>
<ul>
<li>Uback does not guarantee that a transaction will take place.</li>
<li>Uback does not negotiate, advise or hold any mandate.</li>
<li>Uback does not collect any funds intended for investment.</li>
<li>Uback does not sell or pass your data to anyone other than the country’s partner.</li>
</ul>

@POOLCTX@
<h2 id="opening">Where are we?</h2>
<p>Uback is in public beta. In each country, investment intentions will open as soon as the licensed partner is signed. @OPENING@</p>
</div>
""",
}
