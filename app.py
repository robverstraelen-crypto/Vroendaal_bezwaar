# -*- coding: utf-8 -*-
import datetime
import re
import textwrap

import streamlit as st
from openai import OpenAI
from fpdf import FPDF

# =========================================================
# 0) CONFIG
# =========================================================

APP_TITLE = "⚖️ Zienswijze Generator Vroendaal"
PAGE_TITLE = "Verzet Vroendaal"
PAGE_ICON = "⚖️"

MODEL_NAME = "gpt-4o"
TEMPERATURE = 0.4

UI_INSTRUCTIE_MD = """
**Instructie**
Met deze tool genereert u een juridisch onderbouwde zienswijze tegen het nieuwbouwplan.
Vul uw gegevens in, vink uw bezwaren aan en klik op **'Genereer'**.
"""

SYSTEM_PROMPT = """
Je bent een senior procesadvocaat bestuursrecht, gespecialiseerd in de Omgevingswet en de gemeente Maastricht.
Je schrijft een formele Zienswijze namens een bewoner tegen het plan 'Woningbouw Vroendaal'.

STIJL:
- Formeel, dwingend, juridisch correct, maar begrijpelijk.
- Gebruik termen als: 'strijd met goede ruimtelijke ordening', 'onzorgvuldige voorbereiding', 'aantasting woon- en leefklimaat'.
- Wees scherp op de inhoud, maar beleefd in de vorm.

HARD CONSTRAINTS (ZEER BELANGRIJK):
- Gebruik uitsluitend de GESELECTEERDE TEKSTBLOKKEN (letterlijk) en eventuele 'Eigen bezwaren' van de gebruiker.
- Voeg geen nieuwe feiten, argumenten of juridische grondslagen toe.
- Je mag alleen korte verbindende zinnen toevoegen voor leesbaarheid, zonder nieuwe inhoud.

STRUCTUUR:
1) Formele aanhef aan de Gemeente Maastricht (bevoegd gezag).
2) Inleiding met gegevens indiener en belanghebbendheid (verwerk 'Persoonlijke situatie' professioneel als die is ingevuld).
3) Werk de geselecteerde punten uit onder tussenkopjes volgens de categorieën.
   - Neem per punt de titel op als kop en zet de tekstblok letterlijk daaronder.
4) Voeg 'Eigen bezwaren' als apart hoofdstuk toe aan het einde indien aanwezig.
5) Afsluiting met verzoek om aanpassing/afwijzing, verzoek om ontvangstbevestiging.
6) Onderteken met Naam en Adres.
""".strip()

# =========================================================
# 1) DATA: Tekstblokken (letterlijk uit jouw docx)
#    Structuur: Category (H1) -> Section (H2) -> Blocks (H3+tekst)
# =========================================================

BLOCKS = [
    # Procedurele gebreken -> Misleiding Contracten
    {
        "id": 1,
        "category": "Procedurele gebreken",
        "section": "Misleiding Contracten",
        "title": "Fantoomcontract ondermijnt rechtmatigheid besluitvorming",
        "text": "De anterieure overeenkomst is gepresenteerd als gesloten, terwijl deze juridisch nog niet bestond. Op 26 november 2025 meldde het College aan de gemeenteraad dat de overeenkomst was aangegaan, terwijl alleen de ontwikkelaar had getekend en de gemeentelijke handtekening ontbrak. De overeenkomst is pas op 22 december 2025 rechtsgeldig tot stand gekomen. Hierdoor is de raad feitelijk onjuist geïnformeerd en is de actieve inlichtingenplicht geschonden. Desondanks is het ontwerpplan al op 4 december 2025 ter inzage gelegd, in strijd met de Omgevingswet die vereist dat het kostenverhaal vooraf is verzekerd. Gedurende 18 dagen lag het plan zonder juridische en financiële basis ter inzage. Deze misleiding staat niet op zichzelf: essentiële contractbijlagen ontbreken, basisgegevens van de contractpartij zijn onjuist en contractuele afspraken beperken de beleidsvrijheid van de raad. Dit wijst op een onzorgvuldig en onrechtmatig proces."
    },
    {
        "id": 2,
        "category": "Procedurele gebreken",
        "section": "Misleiding Contracten",
        "title": "Structurele misleiding van de gemeenteraad",
        "text": "De gemeenteraad is structureel onjuist en onvolledig geïnformeerd over zowel de juridische status, de inhoud als de gevolgen van het plan. Het College heeft op 26 november 2025 gemeld dat de anterieure overeenkomst was aangegaan, terwijl deze pas op 22 december 2025 rechtsgeldig is ondertekend. Hierdoor is de raad misleid over het verzekerd zijn van het kostenverhaal en is het ontwerpplan vanaf 4 december 18 dagen onrechtmatig ter inzage gelegd. Daarnaast zijn essentiële contractbijlagen met financiële risico’s achtergehouden en bevat de overeenkomst basale fouten, zoals een niet-bestaand KvK-nummer. Ook is ten onrechte gecommuniceerd dat het plan is verkleind, terwijl de bouwmassa feitelijk gelijk bleef. Door contractuele koppeling van grondverkoop aan dit bouwvolume heeft de gemeente een financieel belang gekregen, waardoor de beleidsvrijheid van de raad ernstig is beperkt."
    },
    {
        "id": 3,
        "category": "Procedurele gebreken",
        "section": "Misleiding Contracten",
        "title": "Slordige contractvorming ondermijnt besluitvorming",
        "text": "Het foutieve KvK-nummer in de anterieure overeenkomst toont de ernstige onzorgvuldigheid waarmee het contract tot stand is gekomen. In het contract is een niet-bestaand KvK-nummer opgenomen, terwijl de gemeente heeft nagelaten de identiteit van de contractpartij correct te verifiëren. Dit is geen onschuldige typefout, maar symptomatisch voor een geforceerd proces. Deze slordigheid staat niet op zichzelf: de overeenkomst werd aan de raad gepresenteerd als gesloten, terwijl zij juridisch pas op 22 december 2025 tot stand kwam. Daardoor lag het plan 18 dagen onrechtmatig ter inzage zonder verzekerd kostenverhaal. Bovendien ontbreken essentiële contractbijlagen, waaronder kostenramingen, overdrachtstekeningen en het bodemrapport. Hierdoor heeft de raad geen inzicht gehad in financiële en milieutechnische risico’s. Dit geheel wijst op structurele misleiding en een ondeugdelijke juridische basis van het plan."
    },

    # Procedurele gebreken -> Onrechtmatige Inzage
    {
        "id": 4,
        "category": "Procedurele gebreken",
        "section": "Onrechtmatige Inzage",
        "title": "Onrechtmatige terinzagelegging door ontbrekend kostenverhaal",
        "text": "De terinzagelegging van het plan is gestart zonder te voldoen aan een fundamentele wettelijke voorwaarde. Op 4 december 2025 is het ontwerpplan ter inzage gelegd, terwijl de anterieure overeenkomst pas op 22 december 2025 door de gemeente is ondertekend. Daarmee was het kostenverhaal gedurende 18 dagen niet verzekerd, in strijd met artikel 13.6 van de Omgevingswet. De mededeling in het ontwerpplan dat het kostenverhaal was verzekerd, was in deze periode feitelijk onjuist. Daarnaast zijn raad en burgers voorafgaand aan de inzage misleid door de mededeling dat de overeenkomst reeds was aangegaan. Ook was het dossier inhoudelijk onvolledig, doordat essentiële bijlagen zoals kostenramingen, overdrachtstekeningen en het bodemrapport ontbraken. Hierdoor konden burgers hun zienswijze niet baseren op volledige informatie. De inzageprocedure is daarmee niet rechtsgeldig aangevangen."
    },
    {
        "id": 5,
        "category": "Procedurele gebreken",
        "section": "Onrechtmatige Inzage",
        "title": "Incompleet dossier schendt rechtsbescherming burgers",
        "text": "Het ter inzage gelegde dossier was fundamenteel incompleet en heeft de rechtsbescherming van burgers en de controlerende taak van de gemeenteraad ernstig geschaad. Essentiële bijlagen bij de anterieure overeenkomst ontbraken, waaronder de kostenraming voor de aanpassing van de Rijksweg, de overdrachtstekening van gemeentegrond en het bodemrapport over ernstige vervuiling. Hierdoor ontbrak inzicht in financiële, juridische en milieutechnische risico’s. Daarnaast zijn cruciale veiligheidsstukken niet ter inzage gelegd, zoals de vereiste provinciale ontheffing in een grondwaterbeschermingsgebied, het veiligheids- en saneringsplan, een bezonningsstudie en relevante ecologische informatie. Ook bestonden er verschillende openbare dossiers en zijn documenten pas na ingebrekestelling laat vrijgegeven. Door deze informatie-asymmetrie is de inzageprocedure niet rechtsgeldig aangevangen en zijn burgers feitelijk belemmerd in het indienen van een volwaardige zienswijze."
    },
    {
        "id": 6,
        "category": "Procedurele gebreken",
        "section": "Onrechtmatige Inzage",
        "title": "Schending fair play en obstructie openbaarheid",
        "text": "De gemeente heeft het beginsel van fair play en het recht op een gelijk speelveld ernstig geschonden door doelbewust informatie achter te houden en openbaarmaking te traineren. Interne communicatie laat zien dat ambtenaren zijn geïnstrueerd om geen overleg te voeren met omwonenden om te voorkomen dat zij “gratis munitie” zouden krijgen voor hun zienswijze. Hiermee heeft de gemeente zich niet neutraal opgesteld, maar als tegenpartij van burgers. Daarnaast zijn Woo-verzoeken naar cruciale beslisinformatie bewust vertraagd en pas na ingebrekestelling op 29 januari 2026 mondjesmaat vrijgegeven, slechts twee weken voor het einde van de zienswijzetermijn. Burgers werden hierdoor geconfronteerd met een onwerkbare hoeveelheid complexe stukken. Bovendien is de Woo misbruikt om documenten achter te houden die op grond van de Awb verplicht ter inzage hadden moeten liggen. Hierdoor is sprake van informatie-asymmetrie en een niet-rechtsgeldige inspraakprocedure."
    },

    # Procedurele gebreken -> Integriteit en Vooringenomenheid
    {
        "id": 7,
        "category": "Procedurele gebreken",
        "section": "Integriteit en Vooringenomenheid",
        "title": "Bestuurlijke collusie ondermijnt onafhankelijkheid gemeente",
        "text": "De gemeente heeft haar rol als onafhankelijk en neutraal bevoegd gezag verlaten en zich structureel opgesteld als bondgenoot van de projectontwikkelaar. Interne communicatie toont aan dat de gemeente zichzelf positioneerde als één front met de ontwikkelaar tegenover bewoners en bewust overleg vermeed om hun rechtspositie te verzwakken. Daarnaast is sprake van financiële verstrengeling: de gemeente fungeerde als betaald projectbureau en koppelde grondverkoop contractueel aan dit specifieke bouwvolume, waardoor een direct financieel belang ontstond bij goedkeuring van het plan. Ook zijn ambtelijke processen aangepast aan wensen van de ontwikkelaar, waaronder het cosmetisch herschrijven van negatieve deskundigenadviezen, gezamenlijke persregie en procedurele versnelling op verzoek van de ontwikkelaar. Bewoners werden structureel uitgesloten, terwijl de ontwikkelaar ongehinderde toegang tot bestuur en besluitvorming had. Dit alles vormt een ernstige schending van het verbod op vooringenomenheid en tast de integriteit van de besluitvorming fundamenteel aan."
    },
    {
        "id": 8,
        "category": "Procedurele gebreken",
        "section": "Integriteit en Vooringenomenheid",
        "title": "Bewuste boycot van burgerdialoog",
        "text": "De gemeente heeft de dialoog met de Werkgroep doelbewust geboycot als onderdeel van een ambtelijke en bestuurlijke strategie. Interne e-mails tonen aan dat overleg met bewoners expliciet is verboden om te voorkomen dat informatie “tegen ons en de ontwikkelaar” zou worden gebruikt. Wettelijke informatievoorziening werd daarmee gezien als het verschaffen van “gratis munitie” aan een tegenpartij, wat duidt op vooringenomenheid en een schending van artikel 2:4 Awb. De gemeente identificeerde zich openlijk met de ontwikkelaar en verloor haar neutraliteit als bevoegd gezag. Bewoners werden operationeel uitgesloten van gesprekken, informatieavonden en bestuurlijk overleg, terwijl de ontwikkelaar onbeperkte toegang tot het stadhuis behield. Tegelijk werd intern gezocht naar manieren om inhoudelijke discussie in de raad te vermijden. Deze systematische uitsluiting bewijst dat geen sprake was van participatie, maar van een gecoördineerde verdediging van het bouwplan."
    },
    {
        "id": 9,
        "category": "Procedurele gebreken",
        "section": "Integriteit en Vooringenomenheid",
        "title": "Betaalplanologie ondermijnt bestuurlijke onafhankelijkheid",
        "text": "De besluitvorming is gestuurd door perverse financiële prikkels die de onafhankelijkheid van de gemeente ernstig aantasten. Via de plankostenscan brengt de gemeente €152.702 in rekening bij de ontwikkelaar voor circa 1.000 ambtelijke uren, waardoor zij feitelijk als betaald projectbureau opereert en een direct financieel belang krijgt bij het doorgaan van het plan. Daarnaast is de verkoop van 266 m² gemeentelijk openbaar groen contractueel gekoppeld aan dit specifieke bouwvolume. Hierdoor ontstaat een situatie van financiële gijzeling: aanpassing van het plan leidt tot contractbreuk of verlies van inkomsten. De democratische afweging wordt zo vooraf financieel vastgezet. Door deze constructies functioneert de gemeente niet langer als onpartijdige belangenafweger, maar als financiële partner van de ontwikkelaar. Dit verklaart de vooringenomen houding tegenover bewoners en vormt een ernstige schending van bestuurlijke integriteit."
    },

    # Fysieke Leefomgeving -> Maat en Schaal
    {
        "id": 10,
        "category": "Fysieke Leefomgeving",
        "section": "Maat en Schaal",
        "title": "Overschrijding bouwhoogte schaadt maat en schaal",
        "text": "Het bouwplan overschrijdt bewust de toegestane bouwhoogte en past niet binnen de maat en schaal van de wijk Vroendaal. Voor dit gebied geldt volgens de Omgevingsvisie een maximale bouwhoogte van 10 meter, terwijl het ontwerp een totale hoogte van 11,63 meter bereikt, een overschrijding van meer dan 16%. Deze afwijking is gemaskeerd door te rekenen met een kunstmatig peil, waardoor het gebouw op papier lager lijkt dan het in werkelijkheid is. Feitelijk ervaren omwonenden een gevelhoogte van ruim 10,8 meter exclusief opbouw. Daarnaast is de massaliteit verhuld door een onjuiste footprint te presenteren: de werkelijke verstening is circa 50% groter dan aangegeven. In een laagbouwwijk leidt dit tot een ernstige schaalbreuk, verlies van winterzon en forse privacy-aantasting door directe inkijk. Dit plan negeert de menselijke maat en berust op rekenkundige trucs."
    },
    {
        "id": 11,
        "category": "Fysieke Leefomgeving",
        "section": "Maat en Schaal",
        "title": "Footprint-misleiding verhult buitensporig bouwvolume",
        "text": "Het plan misleidt over de werkelijke footprint en maskeert daarmee een buitensporig bouwvolume. In de toelichting wordt een footprint van 1.475 m² gepresenteerd, terwijl de feitelijke verstening 2.230 m² bedraagt. Dit verschil van ruim 50% ontstaat doordat de halfverdiepte parkeerkelder niet wordt meegerekend. Hierdoor wordt de fysieke impact van het gebouw structureel onderschat. Een footprint van deze omvang veroorzaakt een ernstige schaalbreuk in de fijnmazige stadsrandwijk Vroendaal en staat haaks op de menselijke maat. Daarnaast leidt de maximale verstening tot verhoogde hittestress, wateroverlast en het onmogelijk maken van wadi’s en een parkachtige inrichting. Het overmaatse volume past bovendien niet op het eigen perceel en wordt alleen mogelijk gemaakt door de verkoop van 266 m² openbaar groen. Deze cijfermatige manipulatie verhult een plan dat de omgeving blijvend aantast."
    },
    {
        "id": 12,
        "category": "Fysieke Leefomgeving",
        "section": "Maat en Schaal",
        "title": "Schaalbreuk met laagbouwwijk Vroendaal",
        "text": "Het bouwplan veroorzaakt een fundamentele schaalbreuk met de bestaande laagbouwwijk Vroendaal. De wijk bestaat overwegend uit grondgebonden woningen met een fijnmazige, dorpse structuur, terwijl het plan voorziet in twee massieve, gestapelde bouwblokken van drie lagen op een halfverdiepte parkeerkelder. Deze typologie en massa sluiten niet aan op het bestaande stedenbouwkundige weefsel en vormen een vreemd lichaam in de wijk. Daarnaast wordt het beleidsmatige uitgangspunt voor stadsrandwijken van maximaal 10 meter bouwhoogte overschreden met een feitelijke hoogte van 11,63 meter. Ook de werkelijke footprint van 2.230 m² is aanzienlijk groter dan gepresenteerd en disproportioneel voor de locatie. De visuele dominantie leidt tot ernstige privacy-aantasting door directe inkijk vanuit zestien appartementen op vier bestaande woningen. Van zorgvuldige inpassing is geen sprake."
    },

    # Fysieke Leefomgeving -> Milieu en gezondheid
    {
        "id": 13,
        "category": "Fysieke Leefomgeving",
        "section": "Milieu en gezondheid",
        "title": "Onverantwoorde woningbouw op vervuilde locatie",
        "text": "De bouwlocatie betreft een zwaar vervuilde voormalige autosloperij en vormt een acuut risico voor volksgezondheid en milieu. Er is sprake van extreme loodverontreiniging ver boven de interventiewaarde, mogelijke asbest- en PAK-vervuiling en onvolledig bodemonderzoek, terwijl de bestemming wijzigt naar wonen. Bodemrapporten zijn ondanks interne bezwaren toch gebruikt, wat wijst op manipulatie om het plan door te zetten. Tijdens de bouw bestaat een onopgelost veiligheidsconflict tussen asbest- en explosievenprotocollen, zonder integraal veiligheidsplan voor omwonenden op korte afstand. De locatie ligt bovendien in een grondwaterbeschermingsgebied; diepe heipalen kunnen leiden tot verspreiding van vervuiling richting drinkwater, terwijl een vereiste provinciale ontheffing ontbreekt. Sanering is financieel en procedureel niet geborgd: er is geen goedgekeurd saneringsplan en geen budget gereserveerd. Woningbouw onder deze omstandigheden is onverantwoord en strijdig met de zorgplicht."
    },
    {
        "id": 14,
        "category": "Fysieke Leefomgeving",
        "section": "Milieu en gezondheid",
        "title": "Genegeerde gezondheidsrisico’s door locatiekeuze",
        "text": "De locatiekeuze brengt ernstige en onvoldoende onderzochte gezondheidsrisico’s met zich mee. Het plan ligt direct aan de Rijksweg, een drukke verkeersader die fungeert als aanzienlijke bron van fijnstof. De gevolgen voor luchtkwaliteit en gezondheid zijn onvoldoende meegewogen, terwijl het project zelf extra verkeer genereert. Daarnaast wordt het risico van landbouwgif genegeerd: op circa 200 meter afstand vinden bespuitingen plaats, zonder dat onderzoek is gedaan naar spuitzones en blootstelling. Deze risico’s stapelen zich op bij de bestaande bodemvervuiling van de voormalige autosloperij. Desondanks voorziet het plan in sociale huurwoningen, bedoeld voor kwetsbare groepen, die juist extra bescherming verdienen. Zonder harde garanties over schone lucht en een veilige leefomgeving worden toekomstige bewoners blootgesteld aan een cumulatie van milieubelasting. Vanuit het oogpunt van volksgezondheid is deze locatiekeuze onverantwoord."
    },
    {
        "id": 15,
        "category": "Fysieke Leefomgeving",
        "section": "Milieu en gezondheid",
        "title": "Hittestress door verstening bedreigt leefbaarheid",
        "text": "Het bouwplan verergert hittestress en creëert een onleefbaar microklimaat, in strijd met de zorgplicht voor een gezonde leefomgeving. In de planstukken wordt erkend dat de gevoelstemperatuur ter plaatse richting 2050 kan oplopen tot 47°C. Het ontwerp versterkt dit risico door maximale verstening: twee massieve gebouwen met halfverdiepte parkeerkelders resulteren in een werkelijke footprint van circa 2.230 m² en veroorzaken een sterk hitte-eilandeffect. Natuurlijke bodemkoelte gaat verloren en de voorgestelde wadi’s zijn onvoldoende om dit te compenseren. Daarnaast wordt bestaand volwassen groen gekapt, waardoor schaduw en verkoeling verdwijnen. Herplant biedt pas na decennia effect. De gemeente accepteert deze ingreep ten gunste van bouwlogistiek en financieel gemak. Daarmee wordt een erkend gezondheidsrisico vergroot in plaats van beperkt, wat strijdig is met beleid en zorgplicht."
    },
    {
        "id": 16,
        "category": "Fysieke Leefomgeving",
        "section": "Milieu en gezondheid",
        "title": "Gemanipuleerde geluidsrapporten ondermijnen woonklimaat",
        "text": "De geluidsrapportages vormen geen betrouwbare basis voor besluitvorming en brengen de gezondheid van bewoners in gevaar. Interne gemeentelijke adviseurs hebben de onderzoeken herhaaldelijk als “niet akkoord” en oncontroleerbaar bestempeld, omdat essentiële invoergegevens ontbraken of afgekeurde rapporten opnieuw zijn ingediend. Desondanks zijn deze stukken gebruikt in het ontwerpbesluit. Daarnaast zijn rekenkundige trucs toegepast om de geluidsbelasting kunstmatig te verlagen, zoals het meenemen van blinde gevels, het weglaten van de A2 uit de berekeningen en het toepassen van een onjuiste meetmethode voor nieuwbouw. Ook is geen rekening gehouden met extra rolgeluid van grasbetontegels, waardoor geluidshinder structureel wordt onderschat. Toetsing aan geldende milieuzonering ontbrak. Hierdoor ontstaat een schijnveiligheid die het daadwerkelijke woon- en leefklimaat niet beschermt."
    },

    # Fysieke Leefomgeving -> Waterhuishouding
    {
        "id": 17,
        "category": "Fysieke Leefomgeving",
        "section": "Waterhuishouding",
        "title": "Grondwaterbescherming maakt plan onuitvoerbaar",
        "text": "De bouwlocatie ligt in het Grondwaterbeschermingsgebied Mergelland en vormt een onaanvaardbaar risico voor de drinkwatervoorziening. Het plan voorziet in diepe heipalen en een parkeerkelder die de beschermende kleilaag doorboren. Hierdoor ontstaat hydrologische kortsluiting, waarbij ernstige bodemvervuiling kan doorsijpelen naar het diepe grondwaterreservoir. Dit risico wordt gebagatelliseerd, terwijl vergelijkingen met omliggende bebouwing feitelijk onjuist zijn. Daarnaast is het plan in strijd met de Provinciale Omgevingsverordening, die grondroering dieper dan 3 meter verbiedt zonder ontheffing. Deze ontheffing ontbreekt, waardoor het plan juridisch onuitvoerbaar is. Ook de waterhuishouding is onoplosbaar: infiltratie is verboden, waterberging schiet tekort en het risico op wateroverlast wordt afgewenteld op omwonenden. De veiligheid van het grondwater is niet geborgd."
    },
    {
        "id": 18,
        "category": "Fysieke Leefomgeving",
        "section": "Waterhuishouding",
        "title": "Onopgelost waterbergingstekort ondermijnt plan",
        "text": "Het plan kent een structureel waterbergingstekort van 185 m³ dat niet is opgelost. Interne stukken tonen aan dat dit tekort door de gemeente is aangemerkt als “huiswerk voor de ontwikkelaar”, terwijl een omgevingsplan niet kan worden vastgesteld zonder een sluitende wateroplossing. Infiltratie is juridisch verboden vanwege de ligging in het grondwaterbeschermingsgebied en technisch onmogelijk door de slechte doorlatendheid van de bodem. Desondanks wordt in de planstukken ten onrechte uitgegaan van voldoende infiltratiecapaciteit. De voorgestelde wadi’s zijn fysiek niet realiseerbaar door ruimtegebrek naast de kelderwanden, waardoor een badkuip-effect en wateroverlast ontstaan. Het Waterschap waarschuwt voor waterstanden tot 100 cm. De ontwikkelaar voorkomt dit voor zichzelf door ophoging, waarmee de overlast wordt afgewenteld op omwonenden. De waterhuishouding is daarmee technisch en juridisch ondeugdelijk."
    },
    {
        "id": 19,
        "category": "Fysieke Leefomgeving",
        "section": "Waterhuishouding",
        "title": "Rioolverlegging maakt plan juridisch onuitvoerbaar",
        "text": "De noodzakelijke rioolverlegging vormt een onoplosbare technische en juridische klem. Door de omvang van het gebouw en de parkeerkelder moet het riool worden verlegd naar circa 4 meter diepte, terwijl in het grondwaterbeschermingsgebied grondroering dieper dan 3 meter strikt is verboden zonder provinciale ontheffing. Deze ontheffing ontbreekt, waardoor het plan juridisch niet uitvoerbaar is. Daarnaast is de voorgestelde oplossing civieltechnisch afgekeurd door gemeentelijke specialisten vanwege knikken in een hoofdleiding en ernstige beheer- en onderhoudsrisico’s. Ondanks deze afwijzingen schuift de gemeente de uitvoerbaarheid door naar de toekomst door te suggereren dat proefsleuven later uitkomst moeten bieden. Daarmee wordt een omgevingsplan vastgesteld zonder zekerheid over de technische haalbaarheid. Dit bevestigt dat het bouwvolume te groot is voor de locatie en dat vitale infrastructuur en milieuregels worden opgeofferd aan commerciële belangen."
    },

    # Mobiliteit en parkeren -> Verkeersveiligheid
    {
        "id": 20,
        "category": "Mobiliteit en parkeren",
        "section": "Verkeersveiligheid",
        "title": "Onveilige wijkontsluiting door willekeurige verkeerskeuze",
        "text": "De ontsluiting van het plan via smalle woonstraten is onveilig, onnodig en fysiek onuitvoerbaar. Het grootste deel van het verkeer wordt door een rustige 30-km-woonwijk geleid, terwijl volledige ontsluiting via de Rijksweg niet is onderzocht. Hiermee wordt verkeer van een gebiedsontsluitingsweg verplaatst naar erftoegangswegen, in strijd met verkeersveiligheidsprincipes. De rijbaanbreedte van circa 3,6 meter voldoet niet aan de eis van 4,5 meter vrije doorgang voor hulpdiensten, waardoor bereikbaarheid bij calamiteiten niet is gegarandeerd. Blokkades door pakketbezorgers of foutparkeren maken de situatie extra risicovol. Interne waarschuwingen van deskundigen zijn genegeerd en vervangen door cosmetische teksten om het besluit te rechtvaardigen. Een technisch haalbaar alternatief dat de wijk ontlast, is niet serieus onderzocht. Hiermee wordt een aantoonbaar onveilige ontsluiting afgedwongen."
    },
    {
        "id": 21,
        "category": "Mobiliteit en parkeren",
        "section": "Verkeersveiligheid",
        "title": "Manipulatie verkeersrapporten schaadt veiligheid",
        "text": "De verkeersrapportages zijn systematisch gemanipuleerd om een politiek gewenste ontsluiting te legitimeren, ten koste van de verkeersveiligheid. Interne e-mails tonen aan dat deskundigen zijn gevraagd om “mooie zinnen” te formuleren om een technisch onwenselijke route door de woonwijk goed te praten. Fysieke onmogelijkheden zijn genegeerd, zoals een rijbaanbreedte van 3,6 meter die niet voldoet aan de vereiste 4,5 meter voor hulpdiensten. Daarnaast zijn negatieve interne adviezen, waaronder expliciete “niet akkoord”-oordelen over de inrit en verkeerscapaciteit, buiten het besluit gehouden. Ook is technische onkunde gemaskeerd door relevante verkeersbronnen buiten beschouwing te laten. Veiliger alternatieven zijn niet serieus onderzocht of actief gefrustreerd. Hierdoor berust de besluitvorming op een papieren werkelijkheid die de veiligheid van bewoners en hulpdiensten niet waarborgt."
    },
    {
        "id": 22,
        "category": "Mobiliteit en parkeren",
        "section": "Verkeersveiligheid",
        "title": "Hulpdiensten fysiek onbereikbaar",
        "text": "De bereikbaarheid voor hulpdiensten is fysiek en wiskundig onmogelijk en vormt een ernstig veiligheidsrisico. De brandweer vereist een vrije doorrijbreedte van 4,5 meter, terwijl de betrokken woonstraat slechts 3,6 meter breed is. Dit tekort van 0,9 meter maakt het onmogelijk om aan de wettelijke veiligheidseisen te voldoen. De situatie wordt verder verslechterd door pakketbezorgers en foutparkeren, waardoor de weg regelmatig volledig wordt geblokkeerd. De bereikbaarheid van hulpdiensten wordt daarmee afhankelijk van toeval. Interne waarschuwingen dat ontsluiting via deze woonstraat onwenselijk is, zijn genegeerd en vervangen door cosmetische teksten om de situatie veilig te laten lijken. Een veiliger alternatief via de hoofdweg is niet onderzocht. Hiermee wordt een aantoonbaar onveilige ontsluiting afgedwongen, waarbij de veiligheid van bewoners ondergeschikt is gemaakt aan andere belangen."
    },

    # Mobiliteit en parkeren -> Parkeerproblematiek
    {
        "id": 23,
        "category": "Mobiliteit en parkeren",
        "section": "Parkeerproblematiek",
        "title": "Structureel parkeertekort veroorzaakt wijkoverlast",
        "text": "Het plan voldoet niet aan de geldende parkeernormen en leidt tot directe afwenteling van parkeerdruk op de omgeving. Voor Gebouw A zijn minimaal 44 bewonersplaatsen vereist, terwijl er na toewijzing aan bezoekers slechts 28 beschikbaar blijven. Dit resulteert in een structureel tekort van ten minste 15 bewonersplaatsen. Daarnaast zijn diverse parkeerplaatsen te smal en voldoen zij niet aan de CROW-richtlijnen, waardoor zij feitelijk onbruikbaar zijn voor bezoekers. Ook worden bezoekersplaatsen achter slagbomen meegeteld, terwijl deze juridisch niet openbaar toegankelijk zijn. Hierdoor ontstaat een papieren parkeerbalans die in de praktijk niet functioneert. De voorgenomen verkoop van bezoekersplaatsen ondermijnt het principe van gedeeld gebruik verder. Bezoekers en bewoners zullen daardoor uitwijken naar omliggende woonstraten, in strijd met het uitgangspunt dat nieuwbouw haar parkeerbehoefte volledig op eigen terrein moet oplossen."
    },
    {
        "id": 24,
        "category": "Mobiliteit en parkeren",
        "section": "Parkeerproblematiek",
        "title": "Fictieve bezoekersplaatsen achter slagboom",
        "text": "De parkeerbalans is ondeugdelijk doordat bezoekersplaatsen achter slagbomen worden meegeteld. Deze plaatsen zijn juridisch niet openbaar toegankelijk en mogen volgens vaste jurisprudentie niet gelden als bezoekersparkeerplaatsen. Door de fysieke afsluiting functioneren zij feitelijk als privaat terrein voor bewoners. Daarnaast vormt een slagboom een praktische en psychologische drempel: bezoekers en bezorgdiensten zullen niet wachten of aanbellen, maar uitwijken naar de openbare straat. Hierdoor blijft de theoretische capaciteit in de garages onbenut en neemt de parkeerdruk in de omliggende woonstraten toe. Dit leidt tot afwenteling van parkeerproblemen op de wijk, in strijd met het uitgangspunt dat nieuwbouw zijn parkeerbehoefte op eigen terrein moet oplossen. De voorgenomen verkoop van bezoekersplaatsen versterkt dit probleem en ondermijnt de collectieve norm. Zonder vrij toegankelijke bezoekersplaatsen is de parkeerbalans feitelijk onhoudbaar."
    },
    {
        "id": 25,
        "category": "Mobiliteit en parkeren",
        "section": "Parkeerproblematiek",
        "title": "Te smalle parkeervakken veroorzaken papiertekort",
        "text": "De ingetekende parkeervakken voldoen niet aan de geldende CROW-richtlijnen en zijn daardoor functioneel onbruikbaar. Bezoekersplaatsen zijn uitgevoerd met een breedte van 2,50 meter, terwijl voor wisselende gebruikers een minimale breedte van 2,65 tot 2,70 meter vereist is. Deze normschending leidt tot zogenoemd schuwgedrag: bezoekers mijden de te krappe vakken of parkeren over de belijning, waardoor aangrenzende plaatsen eveneens onbruikbaar worden. Hierdoor ontstaat een papieren parkeerbalans die in de praktijk niet functioneert. Omdat deze vakken technisch niet geschikt zijn voor bezoekers, mogen zij niet worden meegeteld, wat resulteert in een feitelijk parkeertekort. Bezoekers zullen uitwijken naar de openbare ruimte, waardoor parkeerdruk wordt afgewenteld op omliggende woonstraten. Dit is in strijd met het uitgangspunt dat nieuwbouw haar parkeerbehoefte volledig en deugdelijk op eigen terrein moet oplossen."
    },

    # Participatie -> Schijnparticipatie
    {
        "id": 26,
        "category": "Participatie",
        "section": "Schijnparticipatie",
        "title": "Misleidend participatieverslag ondergraaft inspraak",
        "text": "Het participatieverslag van 16 juni 2025 geeft een onjuist en gekleurd beeld van het participatieproces en misleidt de gemeenteraad. Het verslag schetst een constructieve en positieve sfeer, terwijl de bijeenkomsten feitelijk werden gekenmerkt door brede weerstand, frustratie en een unaniem afwijzen van het bouwvolume, ondersteund door 421 handtekeningen. Kritische vragen, toezeggingen en inhoudelijke bezwaren zijn selectief weggelaten of herschreven tot algemene opmerkingen, waarna standaardantwoorden zijn toegevoegd die niet zijn gegeven. Participatie had bovendien geen invloed op kernkeuzes zoals bouwhoogte en massa, die al vastlagen. Alternatieven zijn niet serieus onderzocht en bewoners zijn onder druk gezet. De gemeente heeft dit door de ontwikkelaar opgestelde verslag zonder verificatie overgenomen en daarmee haar vergewisplicht verzaakt. Hierdoor is sprake van schijnparticipatie en besluitvorming op basis van een onjuiste voorstelling van zaken."
    },
    {
        "id": 27,
        "category": "Participatie",
        "section": "Schijnparticipatie",
        "title": "Kernbezwaren structureel genegeerd",
        "text": "De participatieprocedure heeft niet geleid tot daadwerkelijke invloed van bewoners en is verworden tot schijnparticipatie. Gedurende het hele traject zijn drie kernbezwaren consequent genegeerd: het te grote bouwvolume, de excessieve bouwhoogte en de onveilige verkeersafwikkeling. De gepresenteerde “verkleining” van het plan betreft slechts een administratieve wijziging; de fysieke massa en impact zijn ongewijzigd gebleven. Ook de bouwhoogte is niet substantieel aangepast en verkeersbezwaren zijn afgedaan met beloften van nader onderzoek. Inbreng van bewoners werd structureel afgewezen zodra deze de businesscase van de ontwikkelaar raakte. Het Burgeralternatief is zonder inhoudelijke toets verworpen en zelfs ter beoordeling voorgelegd aan de ontwikkelaar zelf. De gemeente heeft weerstand gebagatelliseerd en de dialoog actief geblokkeerd. Daarmee is sprake van informeren en negeren, niet van echte participatie."
    }
]

# =========================================================
# 2) Helpers
# =========================================================

def get_client() -> OpenAI | None:
    try:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        return None

def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def create_pdf_bytes(text: str) -> bytes:
    """
    FPDF supports latin-1 well; we keep a safe encoding conversion.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_font("Arial", size=11)

    clean_text = text.encode("latin-1", "replace").decode("latin-1")

    for line in clean_text.split("\n"):
        # wrap long lines softly
        wrapped = textwrap.wrap(line, width=110) or [""]
        for w in wrapped:
            pdf.multi_cell(0, 6, w)

    return pdf.output(dest="S").encode("latin-1")

def build_block_index():
    by_id = {b["id"]: b for b in BLOCKS}
    categories = sorted(set(b["category"] for b in BLOCKS), key=lambda x: x.lower())

    # category -> sections -> list(ids)
    cat_map = {}
    for cat in categories:
        cat_map[cat] = {}
        sections = sorted(set(b["section"] for b in BLOCKS if b["category"] == cat), key=lambda x: x.lower())
        for sec in sections:
            ids = [b["id"] for b in BLOCKS if b["category"] == cat and b["section"] == sec]
            cat_map[cat][sec] = ids

    return by_id, categories, cat_map

BY_ID, CATEGORIES, CAT_MAP = build_block_index()

def format_selected_blocks(selected_ids: list[int]) -> str:
    """
    We pass blocks as structured bullet list so the model can keep them literal.
    """
    lines = []
    for i in selected_ids:
        b = BY_ID[i]
        lines.append(f"## {b['category']} → {b['section']}\n")
        lines.append(f"### {b['title']}\n{b['text']}\n")
    return "\n".join(lines).strip()

def generate_zienswijze(
    client: OpenAI,
    naam: str,
    adres: str,
    woonplaats: str,
    datum_str: str,
    personal_note: str,
    selected_ids: list[int],
    custom_items: list[str],
) -> str:
    selected_ids = sorted(set(selected_ids))

    blocks_payload = format_selected_blocks(selected_ids)

    custom_items_clean = [normalize_ws(x) for x in custom_items if normalize_ws(x)]
    custom_block = ""
    if custom_items_clean:
        custom_block = "## Eigen bezwaren (door indiener)\n" + "\n".join([f"- {x}" for x in custom_items_clean])

    user_prompt = f"""
GEGEVENS INDIENER:
Naam: {naam}
Adres: {adres}, {woonplaats}
Datum: {datum_str}

PERSOONLIJKE SITUATIE (optioneel; verwerk professioneel als belanghebbendheid):
{personal_note.strip() if personal_note.strip() else "(niet ingevuld)"}

GESELECTEERDE TEKSTBLOKKEN (letterlijk opnemen, alleen verbindende zinnen toegestaan):
{blocks_payload}

{custom_block}
""".strip()

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=TEMPERATURE,
    )
    return resp.choices[0].message.content

# =========================================================
# 3) STREAMLIT UI
# =========================================================

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
st.title(APP_TITLE)
st.markdown(UI_INSTRUCTIE_MD)

client = get_client()
if client is None:
    st.warning("⚠️ Geen OpenAI API key gevonden. Voeg `OPENAI_API_KEY` toe in Streamlit Secrets.")
    st.stop()

# Sidebar: quick tools
with st.sidebar:
    st.header("Selectie & hulp")
    st.caption("Tip: begin met 3–7 sterke punten en voeg daarna aan waar relevant.")
    search_q = st.text_input("Zoek in titels/tekst", value="", placeholder="bijv. waterberging, parkeertekort, Woo…")
    st.divider()
    if st.button("Selectie wissen", use_container_width=True):
        for b in BLOCKS:
            st.session_state[f"cb_{b['id']}"] = False
        st.rerun()

# Form
with st.form("zienswijze_form", clear_on_submit=False):
    colA, colB, colC = st.columns([1.2, 1.2, 1.0])
    with colA:
        naam = st.text_input("Uw Naam", value="")
        adres = st.text_input("Uw Adres + Huisnummer", value="")
    with colB:
        woonplaats = st.text_input("Postcode + Woonplaats", value="Maastricht")
        datum_default = datetime.date.today().strftime("%d-%m-%Y")
        datum = st.text_input("Datum", value=datum_default)
    with colC:
        st.markdown("**Output**")
        include_pdf = st.checkbox("PDF download tonen", value=True)
        show_preview = st.checkbox("Tekst-preview tonen", value=True)

    st.subheader("Selecteer uw bezwaren")
    st.info("Kies de punten die op u van toepassing zijn. De tool verwerkt de geselecteerde tekstblokken in een formele zienswijze.")

    # Tabs per categorie
    tabs = st.tabs(CATEGORIES)

    def matches_search(block: dict, q: str) -> bool:
        if not q.strip():
            return True
        qn = q.strip().lower()
        return (qn in block["title"].lower()) or (qn in block["text"].lower()) or (qn in block["section"].lower())

    for tab, cat in zip(tabs, CATEGORIES):
        with tab:
            st.markdown(f"### {cat}")
            sections = list(CAT_MAP[cat].keys())

            # Category-level buttons
            bcol1, bcol2, bcol3 = st.columns([1, 1, 2])
            with bcol1:
                if st.button("Alles selecteren", key=f"sel_all_{cat}"):
                    for sec in sections:
                        for bid in CAT_MAP[cat][sec]:
                            st.session_state[f"cb_{bid}"] = True
                    st.rerun()
            with bcol2:
                if st.button("Alles deselecteren", key=f"desel_all_{cat}"):
                    for sec in sections:
                        for bid in CAT_MAP[cat][sec]:
                            st.session_state[f"cb_{bid}"] = False
                    st.rerun()
            with bcol3:
                st.caption("Gebruik de expander per sectie om overzicht te houden.")

            for sec in sections:
                ids = CAT_MAP[cat][sec]
                # Filter by search
                ids_filtered = [i for i in ids if matches_search(BY_ID[i], search_q)]
                if not ids_filtered:
                    continue

                with st.expander(f"{sec} ({len(ids_filtered)} punten)", expanded=False):
                    scol1, scol2 = st.columns([1, 3])
                    with scol1:
                        if st.button("Selecteer sectie", key=f"sel_sec_{cat}_{sec}"):
                            for bid in ids_filtered:
                                st.session_state[f"cb_{bid}"] = True
                            st.rerun()
                        if st.button("Deselecteer sectie", key=f"desel_sec_{cat}_{sec}"):
                            for bid in ids_filtered:
                                st.session_state[f"cb_{bid}"] = False
                            st.rerun()

                    with scol2:
                        for bid in ids_filtered:
                            b = BY_ID[bid]
                            checked = st.checkbox(
                                f"{b['title']}",
                                key=f"cb_{bid}",
                                value=st.session_state.get(f"cb_{bid}", False),
                            )
                            if checked:
                                st.caption(b["text"])

    st.subheader("Persoonlijke situatie (optioneel)")
    personal_note = st.text_area(
        "Beschrijf kort uw specifieke belang (feitelijk).",
        height=110,
        placeholder="Bijv: mijn tuin grenst aan het plangebied / mijn kind fietst hier / zichtlijn / geluid / parkeerdruk…"
    )

    st.subheader("Eigen bezwaren / argumenten (optioneel)")
    st.caption("U kunt tot 5 eigen punten toevoegen. Deze worden als apart hoofdstuk opgenomen (zonder nieuwe feiten te verzinnen).")

    if "custom_items" not in st.session_state:
        st.session_state.custom_items = [""]

    # Buttons to add/remove
    cbtn1, cbtn2, cbtn3 = st.columns([1, 1, 2])
    with cbtn1:
        if st.button("➕ Voeg punt toe", type="secondary"):
            if len(st.session_state.custom_items) < 5:
                st.session_state.custom_items.append("")
            st.rerun()
    with cbtn2:
        if st.button("➖ Verwijder laatste", type="secondary"):
            if len(st.session_state.custom_items) > 1:
                st.session_state.custom_items.pop()
            st.rerun()
    with cbtn3:
        st.caption(f"Aantal eigen punten: {len(st.session_state.custom_items)}/5")

    custom_inputs = []
    for idx in range(len(st.session_state.custom_items)):
        val = st.text_area(
            f"Eigen bezwaar {idx+1}",
            value=st.session_state.custom_items[idx],
            height=80,
            key=f"custom_{idx}",
            placeholder="Schrijf hier uw eigen bezwaar (liefst concreet en feitelijk)."
        )
        custom_inputs.append(val)

    st.session_state.custom_items = custom_inputs

    submitted = st.form_submit_button("🚀 Genereer mijn zienswijze", type="primary")

# =========================================================
# 4) Generate & Output
# =========================================================

if submitted:
    # Collect selected ids
    selected_ids = []
    for b in BLOCKS:
        if st.session_state.get(f"cb_{b['id']}", False):
            selected_ids.append(b["id"])

    if not naam.strip() or not adres.strip():
        st.error("Vul alstublieft uw naam en adres in.")
        st.stop()

    if len(selected_ids) == 0 and not any(normalize_ws(x) for x in st.session_state.custom_items):
        st.error("Selecteer minimaal één bezwaarpunt of voeg minimaal één eigen bezwaar toe.")
        st.stop()

    with st.spinner("De jurist schrijft uw zienswijze..."):
        try:
            brief_tekst = generate_zienswijze(
                client=client,
                naam=naam.strip(),
                adres=adres.strip(),
                woonplaats=woonplaats.strip(),
                datum_str=datum.strip(),
                personal_note=personal_note,
                selected_ids=selected_ids,
                custom_items=st.session_state.custom_items,
            )
        except Exception as e:
            st.error(f"Er ging iets mis: {e}")
            st.stop()

    st.success("Uw zienswijze is gereed.")

    if show_preview:
        st.text_area("Concept Zienswijze (preview)", value=brief_tekst, height=520)

    if include_pdf:
        pdf_bytes = create_pdf_bytes(brief_tekst)
        safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", naam.strip())[:40] or "Zienswijze"
        filename = f"Zienswijze_Vroendaal_{safe_name}.pdf"
        st.download_button(
            label="📄 Download als PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf"
        )

    st.warning("⚠️ DISCLAIMER: Lees de zienswijze goed door vóór verzending. U blijft zelf verantwoordelijk voor de inhoud.")
