# -*- coding: utf-8 -*-
"""Texte des pages globales (communes à tous les pays), rendues par tools/build_home.py :
/method.html et /fr/methode.html (méthode et règles du jeu), /legal-notice.html et /mentions-legales.html.
« @CAL@ » est remplacé par le calendrier des éditions de chaque pays. Les pages pays n'ont plus de méthode propre :
elles affichent un encadré « Dans ce pays » (calendrier, seuil, partenaire recherché, sources) qui renvoie ici."""

METHOD = {
'fr': """<div class="wrap prose">
<h1>Méthode et règles du jeu</h1>
<p class="lead">Uback est un algorithme avant d’être un site. Sa crédibilité repose sur des règles simples, publiques, identiques dans tous les pays et appliquées sans exception.</p>

<h2>Les règles du jeu</h2>
<ol>
<li><b>Uback ne valorise pas les sociétés : il les classe, et indique un ordre de grandeur estimé par IA.</b> Cet ordre de grandeur est une tranche indicative, jamais un chiffre, calculée selon une règle publiée ; seules des valeurs publiques, datées et sourcées servent de point de départ (montants levés, valorisations publiées).</li>
<li><b>Un classement n’est jamais à vendre.</b> Aucun paiement, d’une société, d’un partenaire ou d’un analyste, n’influence une position. Le référencement payant (« Challengers ») est affiché à part, étiqueté comme tel, et n’entre jamais dans le classement.</li>
<li><b>Aucun humain ne modifie l’ordre.</b> Un validateur peut exclure une société pour un motif d’éligibilité, tracé, ou relancer le calcul ; jamais réordonner.</li>
<li><b>Uback ne démarche jamais.</b> Tout contact sortant vers une société, un dirigeant ou un actionnaire passe par le partenaire agréé du pays.</li>
<li><b>Uback n’est pas un intermédiaire financier.</b> Aucun mandat, aucune négociation, aucun conseil, aucun encaissement de fonds destinés à un investissement.</li>
<li><b>Les données ne sortent pas.</b> Les intentions de cession sont confidentielles ; aucune donnée n’est vendue ni transmise à des tiers, hors le partenaire local avec le consentement du déclarant.</li>
<li><b>Tout est publié, tout est tracé.</b> IA interrogées, date, règle de consensus, critères d’éligibilité sont publics ; chaque société dispose d’un droit de réponse.</li>
<li><b>Aucune fausse promesse.</b> La colonne « Investir » n’affiche un état que lorsqu’il est avéré (levée en cours, dossier suivi, sortie). Une intention non transformée est un crédit transférable.</li>
</ol>

<h2>Comment le classement est établi</h2>
<p>À chaque édition, la même question est posée à plusieurs intelligences artificielles pour chaque pays et chaque secteur : quelles sont les sociétés éligibles les mieux valorisées, dans l’ordre ? Les réponses sont fusionnées en un classement de consensus (par points : 1er = 20 points, 2e = 19, etc.). Un indice de confiance est affiché pour chaque position : quand les IA sont d’accord, le classement est solide ; quand elles divergent, la divergence devient elle-même une information.</p>
<p><b>Un rythme trimestriel.</b> La valorisation d’une société non cotée ne bouge qu’à ses levées de fonds et à sa sortie : un classement trimestriel suffit à suivre le marché, et laisse aux IA le temps d’une analyse plus approfondie. Chaque pays est publié un mois sur trois, le 15, en décalé : Uback publie ainsi chaque mois. Le calendrier de chaque pays figure ci-dessous. Entre deux éditions, le Radar est mis à jour au fil des levées annoncées.</p>
@CAL@
<p><b>Édition 0 (bêta).</b> Cette première édition a été établie par une seule IA (Claude, Anthropic), à partir d’une recherche documentaire sur la presse et les annonces de levées de fonds, chaque montant étant sourcé. L’indice de confiance y reflète la qualité des sources disponibles. Le consensus multi-IA s’applique à partir de l’édition 1.</p>

<h2 id="valorisation">Ordre de grandeur de valorisation</h2>
<p>À côté de chaque société, Uback indique une tranche de valorisation estimée par IA : centaines de milliers de dollars, millions, dizaines de millions, centaines de millions, licorne (plus d’un milliard) ou décacorne (plus de dix milliards). C’est un ordre de grandeur indicatif, jamais un chiffre, et il n’intervient pas dans l’ordre du classement. Survolez ou touchez la tranche pour voir sur quoi repose l’estimation.</p>
<ul>
<li><b>Le point de départ.</b> Si une valorisation a été publiée depuis moins de 24 mois, elle sert d’ancrage. Sinon, Uback part du dernier tour en fonds propres dont le montant est connu : les investisseurs prennent en général 15 à 25 % du capital, la valorisation après le tour est donc estimée entre 4 et 6,7 fois le montant levé. La dette et les subventions ne servent jamais d’ancrage.</li>
<li><b>Un ajustement limité.</b> L’IA peut décaler l’estimation d’une tranche au plus, vers le haut ou vers le bas, à partir de faits publics : tour ultérieur au montant non publié, chiffre d’affaires, rentabilité, agrément, restructuration… Chaque ajustement est justifié et affiché.</li>
<li><b>La règle de la borne basse.</b> La tranche affichée est celle qui contient le bas de la fourchette estimée : entre deux tranches, Uback retient la plus prudente.</li>
<li><b>L’indice de confiance.</b> Élevée : valorisation publiée, ou tour chiffré et recoupé, de moins de 24 mois. Moyenne : tour de plus de 24 mois, ou seul le cumul levé est connu. Faible : source unique ou sources divergentes.</li>
<li><b>« Non estimé ».</b> Quand aucun tour en fonds propres n’a de montant publié, quand il n’y a que de la dette ou des subventions, ou quand l’ancrage repose sur une source incertaine, Uback n’affiche aucune tranche plutôt qu’un chiffre fragile.</li>
<li><b>Signaler une erreur.</b> Chaque ligne du classement permet à la société concernée de signaler une erreur à <a href="mailto:contact@uback.com">contact@uback.com</a>. La correction est tracée.</li>
</ul>
<p>Ces ordres de grandeur sont des estimations éditoriales indicatives : ils ne constituent ni une évaluation financière, ni une offre, ni un conseil en investissement.</p>

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

<h2>La colonne « Investir »</h2>
<p>Chaque société classée propose le bouton « Déclarer une intention ». Un badge discret s’y ajoute seulement quand un fait est avéré : « Levée en cours » quand la société lève des fonds, « Suivie par… » quand le partenaire agréé du pays a un dossier ouvert. Une société rachetée affiche « Sortie », avec le nom de l’acquéreur quand il est connu, et n’accepte plus d’intention. Les sociétés cotées ne sont pas classées : elles figurent parmi les repères cotés.</p>

<h2 id="apres">Que se passe-t-il après ma déclaration ?</h2>
<p>Une déclaration d’intention est payante (prix par pays et par tranche de ticket), valable douze mois, et transférable : tant qu’elle n’a pas été transformée, vous pouvez la supprimer et reporter son crédit sur une autre société ou un secteur. Uback ne promet pas un deal. Il promet que votre intention, agrégée à celles des autres Backers, compte dans la masse critique&nbsp;: quand le nombre de Backers et le cumul de leurs intentions franchissent un seuil, le partenaire agréé du pays contacte la société et lui présente cette demande. Si les attentes de la société et celles des Backers convergent, il structure une opération et la présente directement aux Backers concernés, sous son nom et sous sa responsabilité réglementaire. Les petits tickets sont regroupés dans un véhicule commun créé par le partenaire agréé&nbsp;; chaque Backer décide d’y participer ou non. Dans chaque pays, les déclarations d’intention ouvriront dès la signature du partenaire agréé.</p>

<h2 id="correction">Droit de réponse et corrections</h2>
<p>Toute société citée peut demander la correction d’une information (montant, date, secteur, statut), contester sa position ou demander son retrait, en écrivant à <a href="mailto:corrections@uback.com">corrections@uback.com</a>. Chaque demande reçoit une réponse motivée. Les dirigeants peuvent revendiquer la fiche de leur société pour y publier leurs indicateurs et déclarer une intention de lever des fonds.</p>

<h2>Sources</h2>
<p>Presse économique et technologique de chaque pays et presse internationale, rapports de place et communiqués des investisseurs : chaque page pays détaille ses sources. Chaque montant du classement renvoie à sa source.</p>
</div>
""",
'en': """<div class="wrap prose">
<h1>Method and rules</h1>
<p class="lead">Uback is an algorithm before it is a website. Its credibility rests on simple, public rules, identical in every country and applied without exception.</p>

<h2>The rules</h2>
<ol>
<li><b>We don’t value companies. We rank them, and give an AI-estimated order of magnitude.</b> This order of magnitude is an indicative bracket, never a figure, computed with a published rule; only public, dated and sourced figures are used as a starting point (amounts raised, published valuations).</li>
<li><b>A ranking is never for sale.</b> No payment, from a company, a partner or an analyst, influences a position. Paid listing (“Challengers”) is shown separately, labelled as such, and never enters the ranking.</li>
<li><b>No human changes the order.</b> A reviewer may exclude a company on a traced eligibility ground, or rerun the calculation; never reorder.</li>
<li><b>Uback never solicits.</b> Any outgoing contact with a company, a manager or a shareholder goes through the country’s licensed partner.</li>
<li><b>Uback is not a financial intermediary.</b> No mandate, no negotiation, no advice, no collection of funds intended for an investment.</li>
<li><b>Data stays in.</b> Intentions to sell are confidential; no data is sold or passed on to third parties, except to the local partner with the declarant’s consent.</li>
<li><b>Everything is published, everything is traced.</b> AIs queried, date, consensus rule and eligibility criteria are public; every company has a right of reply.</li>
<li><b>No false promises.</b> The “Invest” column only shows a status when it is established (raise in progress, deal followed, exit). An intention that has not been converted is a transferable credit.</li>
</ol>

<h2>How the ranking is built</h2>
<p>For every edition, the same question is put to several artificial intelligences for each country and each sector: which eligible companies are the most highly valued, in order? The answers are merged into a consensus ranking (by points: 1st = 20 points, 2nd = 19, and so on). A confidence index is shown for each position: when the AIs agree, the ranking is solid; when they diverge, the divergence itself becomes information.</p>
<p><b>A quarterly rhythm.</b> The valuation of a non-listed company only moves when it raises funds or exits: a quarterly ranking is enough to follow the market, and gives the AIs time for a deeper analysis. Each country is published every third month, on the 15th, on a staggered calendar, so that Uback publishes every month. Each country’s calendar is shown below. Between two editions, the Radar is updated as new rounds are announced.</p>
@CAL@
<p><b>Edition 0 (beta).</b> This first edition was established by a single AI (Claude, Anthropic), from desk research on the press and funding announcements, each amount being sourced. The confidence index reflects the quality of the available sources. The multi-AI consensus applies from Edition 1.</p>

<h2 id="valuation">Valuation order of magnitude</h2>
<p>Next to each company, Uback shows an AI-estimated valuation bracket: hundreds of thousands of dollars, millions, tens of millions, hundreds of millions, unicorn (over one billion) or decacorn (over ten billion). It is an indicative order of magnitude, never a figure, and it plays no part in the order of the ranking. Hover over or tap the bracket to see what the estimate is based on.</p>
<ul>
<li><b>The starting point.</b> If a valuation was published less than 24 months ago, it is the anchor. Otherwise, Uback starts from the last equity round with a disclosed amount: investors usually take 15 to 25% of the capital, so the post-money valuation is estimated at 4 to 6.7 times the amount raised. Debt and grants are never used as an anchor.</li>
<li><b>A limited adjustment.</b> The AI may shift the estimate by one bracket at most, up or down, based on public facts: a later round of undisclosed size, revenue, profitability, a licence, a restructuring… Every adjustment is justified and shown.</li>
<li><b>The lower-bound rule.</b> The bracket shown is the one containing the bottom of the estimated range: between two brackets, Uback keeps the more cautious one.</li>
<li><b>The confidence index.</b> High: a published valuation, or a disclosed and confirmed round, less than 24 months old. Medium: a round over 24 months old, or only the total raised is known. Low: a single source or conflicting sources.</li>
<li><b>“Not estimated”.</b> When no equity round has a disclosed amount, when there is only debt or grants, or when the anchor rests on an uncertain source, Uback shows no bracket rather than a fragile figure.</li>
<li><b>Report an error.</b> Each line of the ranking lets the company concerned report an error to <a href="mailto:contact@uback.com">contact@uback.com</a>. Every correction is traced.</li>
</ul>
<p>These orders of magnitude are indicative editorial estimates: they are neither a financial valuation, nor an offer, nor investment advice.</p>

<h2>Eligibility</h2>
<table>
<tr><th>Rule</th><th>Application</th></tr>
<tr><td>Technology or innovative company</td><td>Starting scope; the sector tree is public and evolving.</td></tr>
<tr><td>One main activity, one sector</td><td>Conglomerates and multi-activity companies are excluded. A company appears in one ranking only.</td></tr>
<tr><td>Has raised funds</td><td>At least USD 500k (or equivalent) in equity or debt, verifiable (public announcement, register, or partner attestation). A grant is not a funding round. Debt is distinguished from equity.</td></tr>
<tr><td>Non-listed</td><td>Listed companies are benchmarks, shown separately, never ranked.</td></tr>
<tr><td>Active</td><td>A company acquired, closed or in insolvency proceedings leaves the ranking; history keeps its positions.</td></tr>
<tr><td>Main operations in the country</td><td>A ranking’s country is the country of operations (team, market), whatever the legal seat. The legal seat and the law governing the shares are shown on each profile. Companies of local origin operated abroad appear in “Born here, based elsewhere”.</td></tr>
</table>

<h2>The “Invest” column</h2>
<p>Every ranked company offers the “Declare an intent” button. A discreet badge is added only when a fact is established: “Raise in progress” when the company is raising funds, “Followed by…” when the country’s licensed partner has an open deal. An acquired company shows “Exit”, with the acquirer’s name when known, and no longer accepts intentions. Listed companies are not ranked: they appear among the listed benchmarks.</p>

<h2 id="after">What happens after my declaration?</h2>
<p>An intention declaration is paid (price per country and per ticket band), valid for twelve months, and transferable: as long as it has not been converted, you can delete it and move its credit to another company or a sector. Uback does not promise a deal. It promises that your intention, aggregated with those of other Backers, counts towards critical mass: when the number of Backers and the total of their intentions cross a threshold, the country’s licensed partner contacts the company and presents this demand. If the company’s expectations and the Backers’ converge, the partner structures a transaction and presents it directly to the Backers concerned, under its own name and regulatory responsibility. Small tickets are pooled in a common vehicle set up by the licensed partner; each Backer decides whether to take part. In each country, intention declarations will open once the licensed partner signs.</p>

<h2 id="correction">Right of reply and corrections</h2>
<p>Any company mentioned may request the correction of an information (amount, date, sector, status), dispute its position or ask to be removed, by writing to <a href="mailto:corrections@uback.com">corrections@uback.com</a>. Every request receives a reasoned answer. Managers can claim their company’s profile to publish their indicators and declare an intention to raise funds.</p>

<h2>Sources</h2>
<p>Local and international business and technology press, market reports and investor announcements: each country page lists its sources. Every amount in the ranking links to its source.</p>
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
<p>Toute société citée peut demander la correction ou le retrait d’une information la concernant à <a href="mailto:corrections@uback.com">corrections@uback.com</a>.</p>
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
<p>Any company mentioned may request the correction or removal of information about it at <a href="mailto:corrections@uback.com">corrections@uback.com</a>.</p>
<h2>Personal data</h2>
<p>E-mail addresses collected through the follow form are used only to send every new edition of the ranking and information about the opening of the service. They are neither sold nor passed on to third parties. You may unsubscribe at any time. Data controller: DEALING-ROOM SARL. Rights of access, rectification and erasure: <a href="mailto:privacy@uback.com">privacy@uback.com</a>.</p>
<h2>Intellectual property</h2>
<p>The rankings, texts and graphic elements of the website are the property of DEALING-ROOM SARL. Reproducing a ranking is allowed with credit to the source and a link to the original page. Company names belong to their owners.</p>
</div>
""",
}
