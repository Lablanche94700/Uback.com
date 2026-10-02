# -*- coding: utf-8 -*-
"""Texte des pages globales (communes à tous les pays), rendues par tools/build_home.py :
/method.html et /fr/methode.html (méthode et règles du jeu, v2), /legal-notice.html et /mentions-legales.html.
Les pages pays n'ont pas de méthode propre : elles affichent un encadré « La méthode au Maroc… » qui renvoie ici.
Ancres utilisées par les pages pays : #estimation, #eligibilite / #eligibility, #avis-humains / #human-input,
#correction, #investir / #invest."""

METHOD = {
'fr': """<div class="wrap prose">
<h1>Méthode et règles du jeu</h1>
<p class="lead"><b>Uback classe les startups technologiques non cotées par ordre décroissant de valorisation estimée.</b> L’estimation est faite par des intelligences artificielles, à partir des informations disponibles : levées de fonds, valorisations publiées, indicateurs d’activité, investisseurs, comparables. Uback publie le rang, une valorisation estimée et sa fourchette d’incertitude, ainsi que l’ordre de grandeur.</p>

<h2>Le marché décide, Uback estime</h2>
<p>La valeur d’une startup n’existe vraiment qu’au moment où elle est fixée par un accord : une levée de fonds, une cession, une entrée en bourse. Entre deux opérations, elle évolue en permanence, comme un cours de bourse, sans que personne ne l’observe.</p>
<p>Uback ne prétend pas fixer cette valeur. Il l’estime, avec les informations disponibles, dans un seul but : classer les sociétés entre elles. L’exercice est par nature imprécis. C’est pourquoi Uback publie des rangs et des tranches, jamais une valorisation chiffrée.</p>
<p>Le montant levé n’est pas le critère de classement. C’est un indice parmi d’autres. Une société qui a peu levé mais croît vite et rentablement peut valoir plus qu’une société qui a beaucoup levé.</p>

<h2>Deux familles de classements</h2>
<p><b>Par pays : tous secteurs confondus, puis par secteur.</b> Un classement pays réunit les startups dont les opérations principales (équipe, marché) sont dans le pays. Il est publié chaque trimestre, le 15 du mois. Chaque pays a son propre mois de départ : le Maroc, par exemple, est publié en février, mai, août et novembre. Les pays étant décalés les uns des autres, Uback publie chaque mois. La date de la prochaine édition figure sur la page d’accueil et sur la page de chaque pays.</p>
<p><b>Mondiaux, par segment.</b> Un classement mondial compare une startup à ses concurrents directs, où qu’ils soient : covoiturage, crypto exchanges, paie… Les segments s’inscrivent dans une arborescence publique à trois niveaux (famille &gt; secteur &gt; segment). Ces classements seront publiés deux fois par an, le 1er janvier et le 1er juillet. Les premiers sont en préparation.</p>
<p>Une même société peut donc figurer dans deux classements : celui de son pays et celui de son segment.</p>
<p><b>Pourquoi un rythme trimestriel et semestriel ?</b> Entre deux opérations, les informations disponibles sur une société non cotée changent peu. Un rythme espacé permet aux IA une analyse plus approfondie à chaque édition. Entre deux éditions, le Radar est mis à jour au fil des levées annoncées.</p>

<h2 id="consensus">Cinq IA, un verdict</h2>
<p>Dès la première édition en mode live, chaque classement sera le consensus de cinq IA issues de trois continents : Claude (Anthropic), GPT (OpenAI), Gemini (Google), Mistral (Mistral AI) et DeepSeek.</p>
<ol>
<li><b>Un dossier par société.</b> Une chaîne de collecte unique rassemble les faits publics (levées, investisseurs, valorisations publiées), chacun avec sa source.</li>
<li><b>Même dossier, même prompt.</b> Les cinq IA reçoivent exactement le même dossier et le même prompt. Aucune ne cherche sur le web de son côté.</li>
<li><b>La médiane tranche.</b> Chaque IA donne une tranche de valorisation et sa justification. Le classement suit la médiane ; l’écart entre les IA fixe l’indice de confiance.</li>
</ol>
<p>Chaque édition indiquera la version exacte de chaque IA utilisée, et le prompt sera public. DeepSeek est exécuté sur des serveurs situés hors de Chine.</p>
<p><b>Aujourd’hui (Édition 0 – bêta) :</b> les classements sont produits par Claude seul. Le consensus des cinq IA s’appliquera dès la première édition en mode live.</p>

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
<p><b>Le consensus.</b> L’estimation retenue est la médiane des estimations des IA. C’est elle qui détermine le rang : le n° 1 est la société dont la valorisation estimée est la plus élevée. L’ordre de grandeur affiché est la tranche qui contient cette médiane. Le rang et la tranche sont donc toujours cohérents. La fourchette reflète l’écart entre les estimations des IA.</p>
<p><b>L’indice de confiance.</b> Il est affiché pour chaque société et combine deux éléments : l’accord entre les IA et la qualité des données.</p>
<ul>
<li><b>Élevé</b> : les estimations convergent, et reposent sur une valorisation publiée ou un tour chiffré de moins de 24 mois.</li>
<li><b>Moyen</b> : les estimations divergent modérément, ou les données ont plus de 24 mois.</li>
<li><b>Faible</b> : les estimations divergent fortement, ou reposent sur une source unique.</li>
</ul>
<p>Quand les IA ne s’accordent pas, cette divergence est elle-même une information.</p>
<p><b>Des données de plus en plus riches.</b> Chaque édition intègre de nouvelles sources. La précision des estimations doit progresser d’une édition à l’autre.</p>
<p><b>Édition 0 (bêta).</b> Les premières éditions ont été établies par une seule IA (Claude, Anthropic), à partir d’une recherche documentaire. L’indice de confiance y reflète la seule qualité des sources.</p>

<h2 id="ordre-de-grandeur">L’estimation, la fourchette et l’ordre de grandeur</h2>
<p>Pour chaque société classée, Uback affiche trois éléments :</p>
<ul>
<li><b>Une estimation centrale</b> (par exemple « ≈ 1,5 Md$ »), arrondie à deux chiffres significatifs. C’est elle qui fixe le rang.</li>
<li><b>Une fourchette d’incertitude</b> autour de cette estimation, d’autant plus large que les données sont anciennes, uniques ou fragiles.</li>
<li><b>L’ordre de grandeur</b>, c’est-à-dire la tranche qui contient l’estimation :</li>
</ul>
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
<p><b>Édition 0 (bêta), en attendant le consensus des cinq IA.</b> L’estimation centrale part de la dernière valorisation publiée si elle date de moins de 24 mois ; sinon du dernier tour en fonds propres, en supposant qu’il représente 15 à 25 % du capital (soit environ 5 fois son montant) ; jamais d’une dette ni d’une subvention. L’IA peut l’ajuster d’un facteur 3 au plus, dans un sens ou dans l’autre, en citant les faits publics qui le justifient. La fourchette dépend de l’indice de confiance : de −20 % à +25 % s’il est élevé, de deux tiers à une fois et demie s’il est moyen, de la moitié au double s’il est faible.</p>
<p>Ces estimations sont éditoriales, purement indicatives et par nature imparfaites : seul le marché fixe la valeur d’une société, lors d’une levée ou d’une cession. Elles ne constituent ni une évaluation financière, ni une offre, ni un conseil en investissement. Une société qui estime un chiffre inexact peut <a href="/fr/correction.html">demander une correction</a>.</p>

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
<li><b>Le classement</b> : toutes les sociétés que les IA savent valoriser avec un accord suffisant (au moins 3 des 5 IA dans la même tranche ou dans des tranches voisines), par ordre de valorisation estimée, dans la limite de 20 noms (50 sur les plus grands marchés). Une société sur laquelle elles ne s’accordent pas va au Radar. Rien ne s’y achète.</li>
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
<p class="lead"><b>Uback ranks non-listed tech startups in descending order of estimated valuation.</b> The estimate is produced by artificial intelligence models, using the information available: funding rounds, published valuations, business metrics, investors, comparables. Uback publishes the rank, an estimated valuation and its uncertainty range, along with the order of magnitude.</p>

<h2>The market decides, Uback estimates</h2>
<p>A startup’s value only truly exists when an agreement sets it: a funding round, a sale, an IPO. Between two transactions, it keeps moving, like a share price, without anyone observing it.</p>
<p>Uback does not claim to set that value. It estimates it, with the information available, for one purpose only: to rank companies against each other. The exercise is imprecise by nature. That is why Uback publishes ranks and ranges, never a valuation figure.</p>
<p>The amount raised is not the ranking criterion. It is one signal among others. A company that has raised little but grows fast and profitably may be worth more than one that has raised a lot.</p>

<h2>Two families of rankings</h2>
<p><b>By country: all sectors, then by sector.</b> A country ranking covers startups whose main operations (team, market) are in that country. It is published every quarter, on the 15th of the month. Each country has its own starting month: Morocco, for example, is published in February, May, August and November. Because countries are staggered, Uback publishes every month. The date of the next edition is shown on the homepage and on each country page.</p>
<p><b>Global, by segment.</b> A global ranking compares a startup with its direct competitors, wherever they are: carpooling, crypto exchanges, payroll… Segments sit in a public three-level taxonomy (family &gt; sector &gt; segment). These rankings will be published twice a year, on January 1 and July 1. The first ones are in preparation.</p>
<p>The same company can therefore appear in two rankings: its country’s and its segment’s.</p>
<p><b>Why quarterly and twice-yearly?</b> Between two transactions, the information available on a non-listed company changes little. A slower pace gives the AI models room for deeper analysis at each edition. Between editions, the Radar is updated as funding rounds are announced.</p>

<h2 id="consensus">Five AI models, one verdict</h2>
<p>From the first live edition, every ranking will be the consensus of five AI models from three continents: Claude (Anthropic), GPT (OpenAI), Gemini (Google), Mistral (Mistral AI) and DeepSeek.</p>
<ol>
<li><b>One file per company.</b> A single collection pipeline gathers the public facts (funding rounds, investors, published valuations), each with its source.</li>
<li><b>Same file, same prompt.</b> The five models receive exactly the same file and the same prompt. None of them searches the web on its own.</li>
<li><b>The median decides.</b> Each model gives a valuation range and its reasoning. The ranking follows the median; the spread between the models sets the confidence index.</li>
</ol>
<p>Each edition will show the exact version of each model used, and the prompt will be public. DeepSeek is run on servers outside China.</p>
<p><b>Today (Edition 0 – beta):</b> rankings are produced by Claude alone. The five-model consensus will apply from the first live edition.</p>

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
<p><b>The consensus.</b> The estimate used is the median of the AI estimates. It determines the rank: number 1 is the company with the highest estimated valuation. The order of magnitude shown is the bracket containing that median. Rank and bracket are therefore always consistent. The range reflects the spread between the AI estimates.</p>
<p><b>The confidence index.</b> It is shown for each company and combines two things: agreement between the AI models, and data quality.</p>
<ul>
<li><b>High</b>: estimates converge, and rest on a published valuation or a disclosed round less than 24 months old.</li>
<li><b>Medium</b>: estimates diverge moderately, or the data is more than 24 months old.</li>
<li><b>Low</b>: estimates diverge sharply, or rest on a single source.</li>
</ul>
<p>When the AI models disagree, the disagreement is information in itself.</p>
<p><b>Richer data over time.</b> Each edition adds new sources. Estimates should become more precise from one edition to the next.</p>
<p><b>Edition 0 (beta).</b> The first editions were produced by a single AI (Claude, Anthropic), from desk research. The confidence index reflects source quality only.</p>

<h2 id="order-of-magnitude">Estimate, range and order of magnitude</h2>
<p>For each ranked company, Uback shows three things:</p>
<ul>
<li><b>A central estimate</b> (for example “≈ USD 1.5bn”), rounded to two significant figures. It sets the rank.</li>
<li><b>An uncertainty range</b> around that estimate, wider when the data is old, single-sourced or fragile.</li>
<li><b>The order of magnitude</b>, that is the bracket containing the estimate:</li>
</ul>
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
<p><b>Edition 0 (beta), pending the five-model consensus.</b> The central estimate starts from the latest published valuation if it is less than 24 months old; otherwise from the latest equity round, assuming it represents 15 to 25% of the capital (about 5 times its amount); never from debt or a grant. The AI may adjust it by a factor of 3 at most, either way, citing the public facts that justify it. The range depends on the confidence index: −20% to +25% when it is high, two-thirds to one and a half times when it is medium, half to double when it is low.</p>
<p>These estimates are editorial, purely indicative and imperfect by nature: only the market sets a company’s value, through a funding round or a sale. They are neither a financial valuation, nor an offer, nor investment advice. A company that considers a figure inaccurate can <a href="/correction.html">request a correction</a>.</p>

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
<li><b>The ranking</b>: every company the AI models can value with enough agreement (at least 3 of the 5 models in the same or adjacent valuation ranges), in order of estimated valuation, up to 20 names (50 in the largest markets). A company they cannot value with enough agreement goes to the Radar. Nothing in it can be bought.</li>
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
<li><b>Uback is not a financial intermediary.</b> Uback holds no mandate, does not negotiate, gives no advice and collects no funds intended for investment. Any transaction is offered by the country’s local partner, under its own responsibility.</li>
<li><b>Data stays in.</b> Investment intentions are confidential. No data is sold. It is passed only to the country’s local partner, with the investor’s consent.</li>
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
<p>Les adresses e-mail collectées via le formulaire de suivi servent uniquement à l’envoi de chaque nouvelle édition du classement et des informations sur l’ouverture du service. Elles ne sont ni vendues ni transmises à des tiers. Désinscription possible à tout moment. Responsable du traitement : DEALING-ROOM SARL. Les messages envoyés avec les formulaires de contact et de correction sont acheminés par le service Web3Forms (web3forms.com), qui les transmet par e-mail à <a href="mailto:contact@uback.com">contact@uback.com</a> ; ils servent uniquement à répondre à votre demande. Droits d’accès, de rectification et d’effacement : <a href="mailto:privacy@uback.com">privacy@uback.com</a>.</p>
<h2 id="cookies">Cookies et mesure d’audience</h2>
<p>Uback mesure son audience avec Google Analytics (Google Ireland Limited), uniquement si vous l’acceptez dans le bandeau affiché à votre première visite. Tant que vous n’avez pas accepté, aucun cookie de mesure n’est déposé et aucune donnée n’est envoyée à Google. Ignorer le bandeau vaut refus.</p>
<p>Si vous acceptez, Google Analytics dépose les cookies <code>_ga</code> et <code>_ga_*</code> (durée maximale : 13 mois) pour compter les visites et les pages vues, de façon statistique. Ces données ne servent ni à la publicité ni au profilage, et ne sont pas vendues. Elles peuvent être transférées aux États-Unis, dans le cadre du Data Privacy Framework UE–États-Unis.</p>
<p>Votre choix est conservé 6 mois sur votre appareil, puis vous est redemandé. Vous pouvez le modifier à tout moment avec le lien « Cookies » en bas de chaque page ; un refus efface les cookies de mesure déjà déposés. Questions : <a href="mailto:privacy@uback.com">privacy@uback.com</a>.</p>
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
<p>Uback is a content publisher. The rankings published are opinions produced by artificial intelligence systems from public information, following a published method. They constitute neither investment advice, nor a personal recommendation, nor a solicitation or an offer of securities. Uback receives no mandate, negotiates no transaction and collects no funds intended for an investment. Introductions are made by a local partner identified in each market, under its sole regulatory responsibility.</p>
<h2>Right of reply</h2>
<p>Any company mentioned may report inaccurate information about it or dispute its rank, using the <a href="/correction.html">correction form</a>.</p>
<h2>Personal data</h2>
<p>E-mail addresses collected through the follow form are used only to send every new edition of the ranking and information about the opening of the service. They are neither sold nor passed on to third parties. You may unsubscribe at any time. Data controller: DEALING-ROOM SARL. Messages sent with the contact and correction forms are routed by the Web3Forms service (web3forms.com), which forwards them by e-mail to <a href="mailto:contact@uback.com">contact@uback.com</a>; they are used only to answer your request. Rights of access, rectification and erasure: <a href="mailto:privacy@uback.com">privacy@uback.com</a>.</p>
<h2 id="cookies">Cookies and audience measurement</h2>
<p>Uback measures its audience with Google Analytics (Google Ireland Limited), only if you accept it in the banner shown on your first visit. Until you accept, no measurement cookie is set and no data is sent to Google. Ignoring the banner counts as a refusal.</p>
<p>If you accept, Google Analytics sets the <code>_ga</code> and <code>_ga_*</code> cookies (maximum lifetime: 13 months) to count visits and page views, statistically. This data is used neither for advertising nor for profiling, and is not sold. It may be transferred to the United States, under the EU–US Data Privacy Framework.</p>
<p>Your choice is kept for 6 months on your device, then asked again. You can change it at any time with the “Cookies” link at the bottom of every page; a refusal deletes any measurement cookies already set. Questions: <a href="mailto:privacy@uback.com">privacy@uback.com</a>.</p>
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
<p>Uback fonctionne comme un achat groupé. Vous déclarez votre intention d’investir dans un secteur (classement mondial) ou dans un pays. Votre intention rejoint le pool correspondant. Quand une société classée est ouverte aux Backers, parce qu’un actionnaire envisage de céder ou qu’elle prévoit de lever, vous pouvez aussi rejoindre le pool de cette société. Quand le montant cumulé du pool atteint sa masse critique, un montant plancher estimé par l’IA pour chaque pool, le pool est transmis au partenaire agréé, qui présente cette demande à la société.</p>
<p>Uback ne vend pas de titres et ne collecte aucun fonds. Il rassemble des intentions. L’investissement lui-même, s’il a lieu, est proposé par le partenaire agréé, sous sa responsabilité.</p>

<h2 id="etapes">En quatre étapes</h2>
<ol class="steps4">
<li><b>Vous déclarez une intention.</b> Sur un secteur ou un pays, avec une tranche de ticket, et si vous le souhaitez une société préférée dans ce périmètre (votre intention reste dans le pool du secteur ou du pays : la préférence est un signal transmis avec le pool). Sur une société précise, quand elle est ouverte aux Backers.</li>
<li><b>La masse critique est atteinte.</b> Les intentions s’additionnent dans le pool. Quand son montant cumulé atteint la masse critique, un montant plancher estimé par l’IA pour chaque pool, le pool est transmis au partenaire agréé. Les intentions qu’il contient sont alors engagées.</li>
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
<li><b>Une intention, pas un engagement.</b> Déclarer ne vous oblige pas à investir. La décision finale vous appartient toujours. Une fois le pool transmis, l’intention ne peut plus être déplacée, mais vous restez libre de ne pas investir.</li>
</ul>

<h2 id="prix">Pourquoi une intention est payante</h2>
<p>Une intention gratuite ne vaut rien aux yeux d’une startup. Le paiement prouve que la demande est sérieuse, et c’est ce qui donne du poids au partenaire quand il contacte la société.</p>
<p>Le prix dépend du pays et de la tranche de ticket. Il sera affiché à l’ouverture des déclarations dans chaque pays. Le montant payé rémunère la déclaration : ce n’est ni un acompte, ni un investissement, et il n’est pas remboursable.</p>

<h2 id="ouverte">Sociétés ouvertes aux Backers</h2>
<p>Uback n’affiche une intention sur une société que lorsqu’une opération est envisageable : un actionnaire, souvent minoritaire, nous a informés qu’il envisage de céder tout ou partie de ses titres, ou la société nous a informés qu’elle prévoit de lever des fonds prochainement. La ligne de la société porte alors un badge. Les autres sociétés restent classées, et l’intérêt qu’elles suscitent s’exprime à travers le pool de leur secteur ou de leur pays.</p>
<p><a href="mailto:contact@uback.com?subject=Open%20to%20Backers">Actionnaire ou dirigeant ? Contactez-nous</a></p>

<h2 id="duree">Une intention valable à vie, déplaçable jusqu’à la transmission</h2>
<p><b>Votre intention est valable à vie</b>, sans date limite, tant que son pool n’a pas été transmis au partenaire.</p>
<p>Jusque-là, vous pouvez la déplacer à tout moment vers un autre secteur, un autre pays ou une autre société ouverte aux Backers. Elle quitte alors son pool et rejoint le nouveau. Le partenaire peut vous suggérer un déplacement ; la décision reste la vôtre.</p>
<p><b>Dès que son pool est transmis, votre intention est engagée.</b> Elle a rempli son rôle : porter la demande des Backers auprès de la société. Elle n’est plus déplaçable, quelle que soit l’issue, accord ou non. Si vous souhaitez rejoindre un autre pool ensuite, vous déclarez une nouvelle intention.</p>

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
<p>Uback works like group buying. You declare your intention to invest in a sector (worldwide ranking) or in a country. Your intention joins the matching pool. When a ranked company is open to Backers, because a shareholder is considering a sale or the company plans to raise, you can also join that company’s pool. When the pool’s combined amount reaches its critical mass, a floor amount estimated by the AI for each pool, the pool is passed to the local partner, who presents this demand to the company.</p>
<p>Uback does not sell securities and does not collect any funds. It brings intentions together. The investment itself, if it happens, is offered by the local partner, under its own responsibility.</p>

<h2 id="steps">Four steps</h2>
<ol class="steps4">
<li><b>You declare an intention.</b> On a sector or a country, with a ticket range, and if you wish a preferred company within it (your intention stays in the sector or country pool: the preference is a signal passed on with the pool). On a specific company, when it is open to Backers.</li>
<li><b>Critical mass is reached.</b> Intentions add up in the pool. When its combined amount reaches critical mass, a floor amount estimated by the AI for each pool, the pool is passed to the local partner. The intentions it holds are then committed.</li>
<li><b>The local partner structures.</b> It contacts the company, presents the Backers’ demand and checks whether expectations match: amount, valuation, rights.</li>
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
<li><b>An intention, not a commitment.</b> Declaring does not oblige you to invest. The final decision is always yours. Once the pool is passed on, the intention can no longer be moved, but you remain free not to invest.</li>
</ul>

<h2 id="price">Why an intention is paid</h2>
<p>A free intention means nothing to a startup. Payment proves the demand is serious, and that is what gives the partner weight when it approaches the company.</p>
<p>The price depends on the country and the ticket range. It will be shown when declarations open in each country. The amount paid covers the declaration: it is neither a deposit nor an investment, and it is non-refundable.</p>

<h2 id="open">Companies open to Backers</h2>
<p>Uback only shows an intention on a company when a transaction is possible: a shareholder, often a minority one, has told us they are considering selling some or all of their shares, or the company has told us it plans to raise funds soon. The company’s row then carries a badge. Other companies remain ranked, and the interest they attract is expressed through the pool of their sector or country.</p>
<p><a href="mailto:contact@uback.com?subject=Open%20to%20Backers">Shareholder or founder? Contact us</a></p>

<h2 id="duration">An intention valid for life, movable until it is passed on</h2>
<p><b>Your intention is valid for life</b>, with no expiry date, as long as its pool has not been passed to the partner.</p>
<p>Until then, you can move it at any time to another sector, another country or another company open to Backers. It then leaves its pool and joins the new one. The partner may suggest a move; the decision remains yours.</p>
<p><b>Once its pool is passed on, your intention is committed.</b> It has done its job: carrying the Backers’ demand to the company. It can no longer be moved, whatever the outcome, agreement or not. To join another pool afterwards, you declare a new intention.</p>

<h2>Counters</h2>
<p>Each company, sector and country shows the number of Backers and the combined amount of its pool. To protect confidentiality, these figures are rounded into ranges.</p>

<h2>Why only companies that have already raised funds</h2>
<p><a href="/method.html#eligibility">Uback only ranks companies that have raised at least $1M, including one equity round.</a> Professional investors are therefore already on the cap table and have negotiated a shareholders’ agreement. Backers who come in after them do not start from a blank page.</p>

<h2>The local partner</h2>
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
<p>Uback is in public beta. In each country, investment intentions will open as soon as the local partner is signed. @OPENING@</p>
</div>
""",
}

# FAQ (/faq/ et /fr/faq/) : (ancre, question, réponse). D'autres questions suivront ; le balisage FAQPage (schema.org)
# est calculé depuis cette liste par tools/build_home.py.
FAQ = {
'en': [
 ('china', 'Why doesn’t China have its own ranking?',
  'Uback ranks startups that investors can actually back. Non-Chinese investors have practically no access to Chinese startups: capital controls, offshore VIE structures and foreign-investment restrictions keep them out. Publishing a Chinese ranking would be a false promise, and our rule 8 forbids false promises. We still analyse Chinese companies: they serve as valuation comparables and as competitors that can affect the value of the startups we rank. Hong Kong-registered companies operating mainly in mainland China follow the same rule.'),
 ('countries', 'How does Uback choose the countries it ranks?',
  'Uback doesn’t choose them: an algorithm does. A country gets a national ranking when at least 15 distinct companies operating there raised at least USD 1M in equity over the last 36 months, with at least two independent public sources. The size of that pool sets the format of the ranking. Below 15, companies still appear in their zone’s regional ranking. Countries under broad EU or US sanctions are excluded. The list is recomputed every year and published on 31 December. A country enters at 15 and leaves only below 10.'),
 ('out-of-cycle', 'Can a ranking be updated before its scheduled date?',
  'Yes. When a major event occurs (a large round, an acquisition, a shutdown), Uback may publish an out-of-cycle update. The scheduled edition is still published on its official date.'),
],
'fr': [
 ('china', 'Pourquoi la Chine n’a-t-elle pas son classement ?',
  'Uback classe des startups dans lesquelles un investisseur peut réellement investir. Les investisseurs non chinois n’ont pratiquement aucun accès aux startups chinoises : contrôle des capitaux, structures offshore (VIE), restrictions aux investissements étrangers. Publier un classement chinois serait une fausse promesse, ce que notre règle n° 8 interdit. Nous analysons pourtant les sociétés chinoises : elles servent de comparables de valorisation et de concurrents susceptibles de peser sur la valeur des startups que nous classons. Les sociétés immatriculées à Hong Kong mais opérant principalement en Chine continentale suivent la même règle.'),
 ('countries', 'Comment Uback choisit-il les pays classés ?',
  'Uback ne les choisit pas : c’est l’algorithme qui le fait. Un pays a son classement national dès qu’au moins 15 sociétés distinctes, opérant dans ce pays, ont levé au moins 1 M$ en equity sur les 36 derniers mois, avec au moins deux sources publiques indépendantes. La taille de ce vivier fixe le format du classement. En dessous de 15, les sociétés figurent quand même dans le classement régional de leur zone. Les pays sous sanctions larges de l’UE ou des États-Unis sont exclus. La liste est recalculée chaque année et publiée le 31 décembre. Un pays entre à 15 et ne sort que sous 10.'),
 ('out-of-cycle', 'Un classement peut-il être mis à jour avant sa date prévue ?',
  'Oui. En cas d’événement majeur (grosse levée, rachat, fermeture), Uback peut publier une mise à jour hors calendrier. L’édition prévue est quand même publiée à sa date officielle.'),
],
}

# Page /calendar/ (anglais) : encadré et règles ; la vue par mois est calculée depuis data/calendar.json par tools/build_home.py.
CALENDAR_INTRO = """<div class="callout"><p><b>Theoretical calendar.</b> Uback is in beta. This is the calendar Uback will follow once it leaves beta. Dates are fixed and repeat every year.</p></div>
<ul>
<li>Country rankings: quarterly</li>
<li>Global segment rankings: twice a year</li>
<li>Regional rankings: twice a year</li>
<li>Days 29–31: no scheduled publication (reserved for out-of-cycle updates)</li>
</ul>"""

# Page partenaire unique (/partner.html, /fr/partenaire.html) : le pays s'adapte à la page d'appel (?country=ma, sinon la page
# d'où vient le visiteur). @COUNTRIES@ : sélecteur et un bloc par pays en ligne, calculés depuis MARKETS par tools/build_home.py.
PARTNER = {
'en': """<div class="wrap prose">
<h1>Become a Uback partner</h1>
<p class="lead">Uback ranks startups country by country and segment by segment, and aggregates investment intentions from business angels, family offices, corporates and diaspora investors worldwide. Deals are run by local partners.</p>

<h2 id="rules">Rule no. 1: local partners</h2>
<ul>
<li><b>One local partner per country.</b> Each country is served by a single local partner, exclusive. It alone contacts the country’s companies and structures deals, under local law.</li>
<li><b>Each local partner also leads one or more sectors.</b> On top of its country, each local partner is assigned one or more sectors (fintech, healthtech…), which it follows in every country Uback covers.</li>
<li><b>Cross-border deals are run together.</b> When a sector lead wants to bring a deal to a startup in another country, it runs the approach with that country’s local partner. The two partners share the success fee.</li>
</ul>

@COUNTRIES@

<h2>What Uback brings you</h2>
<ul>
<li><b>Investors you would not find on your own.</b> The intentions declared on your country and on your sectors are passed to you: amounts, sectors, sought-after companies, with the identity of the Backers who agreed to be introduced.</li>
<li><b>Visibility.</b> Your name, regulatory status and registration number appear on every ranking of your country and of your sectors (“Introductions made by…”).</li>
<li><b>A dashboard.</b> Alerts when a pool (country, sector or company open to Backers) reaches its critical mass, deal tracking, a record of every contact.</li>
<li><b>A quarterly prospecting kit.</b> A summary of the intentions on your market and your sectors, to send to your own clients.</li>
<li><b>A voice.</b> You can publish notes under your name on your market and your sectors.</li>
</ul>

<h2>What Uback does not bring you</h2>
<p>A guaranteed deal flow. Uback is an additional channel for investors and visibility, not a source of immediate revenue. We would rather say so upfront.</p>

<h2>The framework</h2>
<ul>
<li><b>Exclusive per country</b>, annual contract, renewable and renegotiable according to the audience; one or more sectors assigned on top.</li>
<li><b>You alone remain in charge of regulated activities</b> in your country: contacting companies, mandates, advice, structuring, negotiation, collection of funds. Uback does none of this.</li>
<li><b>Remuneration:</b> an annual fee, as an advance on the retrocessions due on deals closed with Backers introduced by Uback. On a cross-border deal, the success fee is shared between the sector lead and the local partner.</li>
</ul>

<h2 id="challengers">For managers: the Challengers</h2>
<p>A registered company raising funds that is not in the ranking will be able, for a fee, to appear in a separate list labelled “Challengers”, for a set period, with a memo available to verified Backers. The listing has no effect on the ranking. Opens once the local partner signs.</p>

<h2>Contact us</h2>
<p><a class="ptn-contact" href="/contact.html?subject=partnership">Write to us</a> (subject: Partnership). We will send you the partner pack (business model, standard contract, timeline) and arrange a call.</p>
</div>
""",
'fr': """<div class="wrap prose">
<h1>Devenir partenaire Uback</h1>
<p class="lead">Uback classe les startups pays par pays et segment par segment, et agrège les intentions d’investissement des business angels, family offices, corporates et investisseurs de la diaspora, partout dans le monde. Les opérations sont menées par des partenaires locaux agréés.</p>

<h2 id="regles">Règle n° 1 : des partenaires locaux</h2>
<ul>
<li><b>Un partenaire local par pays.</b> Chaque pays est servi par un seul partenaire local agréé, en exclusivité. Lui seul contacte les sociétés du pays et structure les opérations, sous le droit local.</li>
<li><b>Chaque partenaire local pilote aussi un ou plusieurs secteurs.</b> En plus de son pays, chaque partenaire local se voit attribuer un ou plusieurs secteurs (fintech, healthtech…), qu’il suit dans tous les pays couverts par Uback.</li>
<li><b>Les opérations transfrontalières se mènent à deux.</b> Quand un responsable secteur veut proposer une opération à une startup d’un autre pays, il pilote l’action avec le partenaire local de ce pays. Les deux partenaires se partagent le success fee.</li>
</ul>

@COUNTRIES@

<h2>Ce que Uback vous apporte</h2>
<ul>
<li><b>Des investisseurs que vous ne trouveriez pas seul.</b> Les intentions déclarées sur votre pays et sur vos secteurs vous sont transmises : montants, secteurs, sociétés convoitées, avec l’identité des Backers qui ont consenti à être mis en relation.</li>
<li><b>De la visibilité.</b> Votre nom, votre statut réglementaire et votre numéro d’immatriculation apparaissent sur chaque classement de votre pays et de vos secteurs (« Mises en relation assurées par… »).</li>
<li><b>Un tableau de bord.</b> Alertes quand un pool (pays, secteur ou société ouverte aux Backers) atteint sa masse critique, suivi des dossiers, trace de chaque contact.</li>
<li><b>Un kit de prospection trimestriel.</b> Une synthèse des intentions de votre marché et de vos secteurs, à envoyer à vos propres clients.</li>
<li><b>Une voix.</b> Vous pouvez publier des notes sous votre nom sur votre marché et vos secteurs.</li>
</ul>

<h2>Ce que Uback ne vous apporte pas</h2>
<p>Un flux de deals garanti. Uback est un canal d’investisseurs et de notoriété supplémentaire, pas une source de revenus immédiate. Nous préférons le dire avant.</p>

<h2>Le cadre</h2>
<ul>
<li><b>Exclusivité par pays</b>, contrat annuel renouvelable et renégociable selon l’audience ; un ou plusieurs secteurs attribués en plus.</li>
<li><b>Vous restez seul maître des actes réglementés</b> dans votre pays : contact des sociétés, mandats, conseil, structuration, négociation, encaissement. Uback ne fait rien de tout cela.</li>
<li><b>Rémunération :</b> une redevance annuelle, avance sur les rétrocessions dues sur les deals conclus avec des Backers présentés par Uback. Sur une opération transfrontalière, le success fee est partagé entre le responsable secteur et le partenaire local.</li>
</ul>

<h2 id="challengers">Pour les dirigeants : les Challengers</h2>
<p>Une société immatriculée, en cours de levée de fonds, qui ne figure pas dans le classement pourra, contre paiement, s’afficher dans une liste séparée et étiquetée « Challengers », pour une durée déterminée, avec un mémo accessible aux Backers vérifiés. Le référencement n’a aucun effet sur le classement. Ouverture après la signature du partenaire local.</p>

<h2>Nous contacter</h2>
<p><a class="ptn-contact" href="/fr/contact.html?subject=partnership">Écrivez-nous</a> (objet : Partenariat). Nous vous enverrons le dossier partenaire (modèle économique, contrat type, calendrier) et conviendrons d’un échange.</p>
</div>
""",
}

# Page partenaire en français : taille du marché et profil recherché des pays qui n'ont pas de version française (MARKETS)
PARTNER_FR = {
 'fr': dict(deals='environ 600 tours de table par an tous acteurs confondus',
            profile='prestataire de services d’investissement ou conseiller en investissements financiers (CIF) régulé par l’AMF (Autorité des marchés financiers), banque d’affaires ou boutique M&amp;A, avec une pratique du non-coté et de l’anglais'),
 'pl': dict(deals='environ 180 tours de table par an tous acteurs confondus',
            profile='entreprise d’investissement agréée par la KNF (autorité polonaise de surveillance financière), banque d’affaires ou boutique M&amp;A, avec une pratique du non-coté et de l’anglais'),
 'vn': dict(deals='environ 100 tours de table par an tous acteurs confondus',
            profile='société de bourse ou de gestion agréée par la SSC (autorité des marchés du Vietnam), banque d’affaires ou boutique M&amp;A, avec une pratique du non-coté et de l’anglais'), 'in': dict(deals='environ 900 tours de table par an tous acteurs confondus',
            profile='merchant banker ou conseiller en investissement enregistré auprès du SEBI (autorité des marchés indienne), banque d’affaires ou boutique M&amp;A, avec une pratique du non-coté et de l’investissement transfrontalier'),
 'kr': dict(deals='plus de 8 000 investissements en capital-risque par an tous acteurs confondus',
            profile='société de bourse ou conseiller en investissement agréé par la FSC (autorité financière coréenne), banque d’affaires ou boutique M&amp;A, avec une pratique du non-coté et de l’investissement transfrontalier'),
 'ng': dict(deals='environ 90 startups levant au moins 100 000 USD par an',
            profile='issuing house ou broker-dealer enregistré auprès de la SEC Nigeria (autorité des marchés nigériane), banque d’affaires ou boutique M&amp;A, avec une pratique du non-coté et de l’investissement transfrontalier'),
}
