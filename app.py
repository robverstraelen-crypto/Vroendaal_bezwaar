# -*- coding: utf-8 -*-
import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import datetime

# --- CONFIGURATIE ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    client = None

# De bijgewerkte teksten (20 stuks)
TEXT_BLOCKS = {
    1: "Misleiding van de Raad over Contractdatum\nIk maak ernstig bezwaar tegen de onrechtmatige start van deze procedure. Het College heeft de Gemeenteraad in de Raadsinformatiebrief (RIB) van 26 november 2025 geïnformeerd dat de anterieure overeenkomst "is aangegaan". Uit het dossier blijkt echter dat deze pas op 22 december is getekend. De Raad – en daarmee de burger – is bewust op het verkeerde been gezet over de juridische status van het project. Een besluit dat rust op feitelijk onjuiste informatie aan het hoogste bestuursorgaan is in strijd met het zorgvuldigheidsbeginsel (art. 3:2 Awb) en de actieve inlichtingenplicht. Ik verzoek u de procedure te staken wegens onbehoorlijk bestuur.",
    2: "Ongeldige Contractpartij (KvK-kwestie)\nUit onderzoek blijkt dat de gemeente een Anterieure Overeenkomst heeft gesloten met een entiteit die op het moment van tekenen (22 december 2025) juridisch niet bestond of handelde onder een niet-geregistreerd KvK-nummer. Een overheidsorgaan kan geen rechtsgeldige privaatrechtelijke overeenkomsten sluiten met niet-bestaande partijen. Hierdoor ontbreekt de wettelijke basis voor het kostenverhaal en de planschadeafwenteling, wat een dwingende voorwaarde is voor het vaststellen van een omgevingsplan. Omdat de contractuele basis onder het plan ontbreekt, is het besluit tot vaststelling van het TAM-omgevingsplan juridisch onhoudbaar en vernietigbaar.",
    3: "Strijd met Didam-arrest (Onderhandse gunning)\nDe gronduitgifte en de planologische medewerking zijn één-op-één gegund aan de ontwikkelaar zonder openbare selectieprocedure. Dit is in strijd met het Didam-arrest, dat gelijke kansen eist voor marktpartijen. De gemeente heeft verzuimd vooraf kenbaar te maken waarom deze specifieke ontwikkelaar als enige in aanmerking zou komen. Doordat in de anterieure overeenkomst (art. 20) de Didam-publicatie als opschortende voorwaarde is opgenomen, en deze termijn nog liep tijdens de start van de procedure, is het besluit prematuur. Ik maak bezwaar tegen deze onrechtmatige bevoordeling die de transparantie van het openbaar bestuur schaadt",
    4: "Stikstofberekening en Intern Salderen (Jurisprudentie 2026)\nDe conclusie in het besluit dat er geen negatieve effecten zijn op Natura 2000-gebieden, is gebaseerd op een stikstofberekening die uitgaat van 'intern salderen' met oude bedrijfsrechten. Gezien de recente jurisprudentie (o.a. uitspraak 14 januari 2026) is het inzetten van latente ruimte ('slapende vergunningen') juridisch uiterst wankel. De gemeente verzuimt aan te tonen dat de voormalige bedrijfsactiviteiten daadwerkelijk en recentelijk plaatsvonden. Zonder een ecologische toets die voldoet aan de allerlaatste stand van de rechtspraak, is het vaststellen van dit plan in strijd met de Wet natuurbescherming en riskeert de gemeente directe vernietiging bij de Raad van State.",
    5: "Achterhouden van Cruciale Veiligheidsstukken\nDe terinzagelegging van het plan is onvolledig en daarmee onwettig. In de Anterieure Overeenkomst wordt verwezen naar essentiële bijlagen zoals het 'Veiligheidsplan Sanering', de 'Civieltechnische tekening Rijksweg' en diverse bodemonderzoeken. Deze stukken ontbreken in het publieke dossier op Omgevingswet.overheid.nl. Burgers kunnen hierdoor geen volwaardige zienswijze indienen over hun eigen veiligheid en gezondheid. Het argument van de gemeente dat deze stukken "niet cruciaal" zijn, is een schending van het recht op informatie. Ik eis dat de termijn wordt heropend zodra het dossier compleet is, conform de eisen van de Algemene wet bestuursrecht.",
    6: "Onjuiste Footprint (1.475 m² vs 2.230 m²)\nDe ruimtelijke onderbouwing is gebaseerd op een feitelijke onjuistheid. De toelichting stelt dat de footprint van het gebouw ca. 1.475 m² bedraagt. Dit is misleidend. Het plan voorziet in een halfverdiepte parkeerkelder die bouwkundig deel uitmaakt van de constructie en tot aan de perceelsgrenzen reikt. De daadwerkelijke footprint – en daarmee de verstening van het perceel – bedraagt circa 2.230 m². De impact op de bodem en de waterhuishouding is hierdoor ruim 50% groter dan aan de Raad wordt voorgespiegeld. Een bestemmingsplan waarvan de toelichting (tekst) zo ernstig afwijkt van de feitelijke situatie (kaart), kan niet worden vastgesteld.",
    7: "Strijd met Gebiedsprofiel Stadsrand (11 meter)\nHet plangebied valt binnen het profiel 'Stadsrand' van de Omgevingsvisie. Hier geldt als expliciet uitgangspunt dat de bouwhoogte beperkt blijft tot maximaal 10 meter en dat de bebouwing een 'dorpse maat' moet hebben. Het voorliggende plan voorziet in massieve blokken van 11 meter hoog (exclusief opbouw). Hiermee wijkt de gemeente zonder noodzaak af van haar eigen beleidskaders. De financiële optimalisatie van het bouwprogramma (meer lagen = meer winst) is geen ruimtelijke rechtvaardiging om de overgang naar het landschap te verstoren met stedelijke hoogbouw die niet past in de korrelgrootte van Vroendaal.",
    8: "Afstand tot voorzieningen groter dan 500 meter\nDe gemeente rechtvaardigt de hoogbouw met de stelling dat de locatie op "circa 500 meter" van winkelcentrum De Roserije ligt, wat verdichting zou toestaan. Dit is feitelijk onjuist. De werkelijke loopafstand via de openbare weg bedraagt circa 750 meter (50% verder). Solitaire winkels dichterbij (zoals een AH of bloemist) kwalificeren volgens de Omgevingsvisie niet als 'centrumvoorziening' die hoogstedelijke verdichting legitimeert. Doordat niet wordt voldaan aan het nabijheidscriterium, geldt de hoofdregel van de Stadsrand: terughoudendheid en 'per saldo nul woningen toevoegen'. Het plan voldoet dus niet aan een Evenwichtige Toedeling van Functies aan Locaties (EFTAL).",
    9: "Stedenbouwkundige Schaalbreuk\nHet plan wordt gepresenteerd als een "stedenbouwkundige afronding" van de wijk. Dit is een onbegrijpelijke kwalificatie. De bestaande omgeving (Vroendaal/Heugem) kenmerkt zich door grondgebonden woningen, patio's en een fijnmazige structuur. Het plaatsen van twee massieve, aaneengesloten appartementenblokken op een sokkel creëert geen aansluiting, maar een abrupte schaalbreuk. Het gebouw landt als een autonoom, gebiedsvreemd object ('UFO') in de wijk. De Commissie Ruimtelijke Kwaliteit heeft verzuimd te toetsen of deze typologie wel past bij de identiteit van de plek, zoals artikel 1.3 van de Omgevingswet vereist.",
    10: "Technische Onuitvoerbaarheid Wateropgave (Wadi vs. Kelder)\nDe waterparagraaf stelt dat hemelwater wordt opgevangen in wadi's op eigen terrein. Dit is technisch onhoudbaar. Gezien de enorme footprint van de parkeerkelder (2.230 m²) is er nauwelijks 'volle grond' beschikbaar. Het aanleggen van wadi's in de smalle reststroken naast de kelderwanden leidt tot grote risico's op vochtdoorslag en instabiliteit. Indien de ontwikkelaar kiest voor ondergrondse infiltratiekratten, is de toelichting (die spreekt over zichtbaar groen/wadi's) misleidend. Bovendien is de Limburgse lössbodem slecht doorlatend, wat bij dit enorme verharde oppervlak onherroepelijk leidt tot wateroverlast voor de buren.",
    11: "'The Fishbowl Effect' (Privacy-inbreuk)\nDHet plan tast mijn privacy op onaanvaardbare wijze aan. Waar ik nu grens aan een rustig perceel, kijken straks vanuit vele appartementenbewoners vanaf balkons rechtstreeks mijn tuin en/of woon- en slaapkamer in. De verhouding (vele kijkers op enkele tuinen/huizen) creëert een 'viskom-effect': ik voel mij permanent bekeken. Doordat de bestaande groene buffer (bomen) fysiek grotendeels wordt geruimd en niet zal worden vervangen met bomen van de huidige omvang ontbreekt een gedegen vorm van afscherming.  De gemeente weegt de belangen van de ontwikkelaar zwaarder dan mijn fundamentele recht op een ongestoorde leefomgeving en huisvrede.",
    12: "Bezonning: De 'Winterdip'\n De gemeente heeft verzuimd een formele bezonningsstudie ter inzage te leggen, waardoor ik niet kan controleren wat de impact is op mijn woning. Uit eigen simulaties blijkt dat het gebouw (11 meter hoog) in de wintermaanden (november-februari) mijn woning grotendeels in de schaduw zet. Dat het plan wellicht voldoet aan de 'lichte' TNO-norm (die pas telt vanaf 19 februari), is voor mij onacceptabel. Juist in de donkere maanden is zonlicht essentieel voor mijn woongenot en energierekening. Het plan ontneemt mij dit licht op onevenredige wijze.",
    13: "Ambtelijke Manipulatie Verkeersadvies\nIk maak bezwaar tegen de verkeerskundige onderbouwing omdat deze tot stand is gekomen door ambtelijke manipulatie. Uit Woo-stukken blijkt dat ambtenaren de opdracht gaven om voor de ontsluiting "mooie zinnen te formuleren" omdat wethouders niet naar alternatieven wilden luisteren. Dit bewijst dat het verkeersadvies niet objectief is, maar een politiek besteld resultaat. Een bestemmingsplan dat rust op een gemanipuleerd advies is in strijd met het zorgvuldigheidsbeginsel en kan geen standhouden bij de rechter. Ik eis een onafhankelijk nieuw verkeersonderzoek.",
    14: "Onveilige Ontsluiting \nHet plan knipt de ontsluiting op: 43 woningen worden via de rustige woonstraten (Bruysterbosch/Bunderbosch/Jansbosch/Ravensbosch) geleid in plaats van via de rechtstreekse ontsluiting op de Rijksweg. Hiervoor ontbreekt elke noodzaak. De smalle woonstraten, waar veel kinderen spelen, zijn niet berekend op deze toename van verkeer en bezorgdiensten. Het creëert onveilige situaties en sluipverkeer door de wijk. De gemeente heeft nagelaten serieus te onderzoeken of een volledige ontsluiting op de Rijksweg (of via een ventweg) mogelijk is , of hiervan de resultaten hiervan toe publiceren. De keuze voor Bunderbosch is willekeur en tast de verkeersveiligheid in mijn wijk aan.",
    15: "'Blanco Cheque' Rijksweg (Ontbrekende Tekeningen)\nDe aansluiting van Plandeel B op de N278 (Rijksweg) is verkeerskundig onverantwoord. In de stukken ontbreken gedetailleerde inrichtingstekeningen met zichtlijnen, draaicirkels en opstelstroken. Hierdoor kan niemand controleren of de inrit veilig is in combinatie met het drukke fietspad en het 50 km/u-verkeer. De gemeente vraagt de Raad in te stemmen met een 'blanco cheque', waarbij de veiligheid pas later wordt bekeken. Dit is in strijd met de rechtszekerheid. Ik eis dat de vergunning wordt geweigerd zolang de civieltechnische veiligheid niet onomstotelijk vaststaat.",
    16: "Cumulatie Milieuperron en Parkeren\nDe verkeersmodellen negeren de realiteit van het naastgelegen milieuperron. Op piekmomenten staan hier wachtrijen met auto's. De cumulatie van dit verkeer met de bewoners en bezoekers van 66 nieuwe woningen leidt tot een verkeersinfarct en gevaarlijke manoeuvres. Daarnaast is de parkeerbalans in het plan te krap en zijn bezoekersplaatsen niet vrij-toegankelijk. Dit leidt onvermijdelijk tot parkeeroverlast rondom de hoofdingang van gebouw B en daarmee de bereikbaarheid van het milieuperron. Ook zal, indien het milieuperron op deze plaats wordt gehandhaafd, de combinatie van bezoeker aan dit perron en het onvermijdelijke parkeren op straat tot serieuze verkeerscongestie zorgen.",
    17: "Het Negeren van de Rotonde\nBewoners en zelfs de wethouder hebben geopperd om een rotonde aan te leggen als structurele oplossing voor de onveilige Rijksweg. Dit alternatief is zonder goede motivering terzijde geschoven ("past niet in richtlijnen"). De gemeente weigert uit te leggen waarom verkeersveiligheid geen reden is om van richtlijnen af te wijken. Het frustreren van een veilige oplossing (rotonde) ten gunste van een goedkope, onveilige uitrit getuigt van onbehoorlijk bestuur. Ik eis dat de besluitvorming wordt opgeschort tot de rotonde-variant serieus is doorgerekend.",
    18: "Mismatch Woonbehoefte\nHet plan voorziet overwegend in kleine appartementen. Dit sluit niet aan bij de demografische behoefte van Vroendaal. De vergrijzende wijk vraagt om ruime, levensloopbestendige appartementen voor senioren die willen doorstromen vanuit hun gezinswoning. Door te kiezen voor maximale aantallen (kleine units) in plaats van kwaliteit, bouwt de gemeente voor de leegstand van de toekomst. Deze 'schoenendozen' op een locatie ver van het centrum hebben een slechte marktpositie. Het plan voldoet daarmee niet aan de kwalitatieve eisen van de Woonvisie Maastricht.",
    19: "Negeren Burgeralternatief (Participatie)\nDe gemeente stelt dat er geparticipeerd is, maar heeft het constructieve 'Burgeralternatief' (grondgebonden woningen, passend in de maat) zonder serieus onderzoek terzijde geschoven. De participatie is gereduceerd tot een informatieavond zonder invloed. In het verslag wordt de massale weerstand van de buurt gebagatelliseerd. Dit is in strijd met de geest van de Omgevingswet, die vroegtijdige en volwaardige participatie eist. Ik voel mij als burger niet gehoord en eis dat het Burgeralternatief alsnog als volwaardig scenario wordt getoetst.",
    20: "**Bodemverontreiniging en Volksgezondheid**\nHet plangebied is historisch belast en uit bodemonderzoeken blijkt ernstige verontreiniging. De gemeente kiest ervoor om het bestemmingsplan vast te stellen voordat er een goedgekeurd saneringsplan ligt. Hiermee worden de risico's voor de volksgezondheid (verspreiding van lood/asbeststof tijdens de bouw) doorgeschoven naar de uitvoering. Gezien de nabijheid van woningen is dit onverantwoord. Ik eis dat de procedure wordt gestopt totdat de veiligheid van omwonenden tijdens de sanering onomstotelijk is geborgd in een goedgekeurd en openbaar plan."
}

CHECKBOX_LABELS = {
    1: "1. Misleiding over Contractdatum",
    2: "2. Ongeldige Contractpartij (KvK)",
    3: "3. Didam-arrest (Gunning)",
    4: "4. Stikstof (Jurisprudentie 2026)",
    5: "5. Ontbrekende Veiligheidsstukken",
    6: "6. Onjuiste Footprint (1.475 vs 2.230)",
    7: "7. Bouwhoogte (11m vs 10m)",
    8: "8. Misleidende Afstand (750m vs 500m)",
    9: "9. Stedenbouwkundige Schaalbreuk",
    10: "10. Water/Wadi Onuitvoerbaar",
    11: "11. Privacy/Inkijk (Fishbowl)",
    12: "12. Bezonning (Winterdip)",
    13: "13. Gemanipuleerd Verkeersadvies",
    14: "14. Onveilige Ontsluiting",
    15: "15. Ontbrekende Tekeningen N278",
    16: "16. Milieuperron & Parkeren",
    17: "17. Negeren Rotonde-oplossing",
    18: "18. Verkeerde Woningtypes",
    19: "19. Negeren Burgeralternatief",
    20: "20. Bodem & Volksgezondheid"
}

# --- AI FUNCTIE ---
def generate_zienswijze(naam, adres, datum, selected_ids, personal_note):
    if not client:
        return "⚠️ Geen API key gevonden."

    juridische_argumenten = ""
    for i in selected_ids:
        juridische_argumenten += f"- {TEXT_BLOCKS[i]}\n"

    system_prompt = """
    Je bent een senior procesadvocaat bestuursrecht. Je schrijft de INHOUDELIJKE ONDERBOUWING van een Zienswijze (ter aanvulling op een eerder pro-forma ingediend bezwaar).
    
    FOCUS:
    - Gebruik de verstrekte argumenten integraal. 
    - De toon is strijdvaardig, juridisch technisch en uiterst kritisch richting het College van B&W van Maastricht.
    - Termen: 'onbehoorlijk bestuur', 'schending van het vertrouwensbeginsel', 'prematuur besluit', 'gebrekkige motivering'.
    - De brief moet aan de Gemeenteraad gericht zijn.
    """

    user_prompt = f"""
    INDIENER: {naam}, {adres}. DATUM: {datum}.
    PERSOONLIJK BELANG: {personal_note}
    GESELECTEERDE JURIDISCHE PUNTEN: {juridische_argumenten}
    
    Schrijf een volledige, formele brief.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, clean_text)
    return pdf.output(dest="S").encode("latin-1")

# --- UI ---
st.set_page_config(page_title="Zienswijze Vroendaal 2.0", layout="wide")
st.title("⚖️ Zienswijze Generator Vroendaal 2.0")
st.warning("Deze versie bevat de geüpdatete juridische bezwaren (versie januari 2026).")

with st.form("zienswijze_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        naam = st.text_input("Naam")
        adres = st.text_input("Adres")
    with c2:
        woonplaats = st.text_input("Postcode/Plaats", value="Maastricht")
    with c3:
        datum = st.text_input("Datum", value=datetime.date.today().strftime("%d-%m-%Y"))

    st.subheader("Selecteer uw inhoudelijke bezwaarpunten")
    
    selected_ids = []
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("### 🏛️ Procedure & Juridisch")
        for i in range(1, 6):
            if st.checkbox(CHECKBOX_LABELS[i], key=i): selected_ids.append(i)
        st.markdown("### 📐 Maat & Schaal")
        for i in range(6, 9):
            if st.checkbox(CHECKBOX_LABELS[i], key=i): selected_ids.append(i)

    with col_b:
        st.markdown("### 🌿 Groen & Leefklimaat")
        for i in range(9, 13):
            if st.checkbox(CHECKBOX_LABELS[i], key=i): selected_ids.append(i)
        st.markdown("### 🚗 Verkeer & Veiligheid")
        for i in range(13, 17):
            if st.checkbox(CHECKBOX_LABELS[i], key=i): selected_ids.append(i)

    with col_c:
        st.markdown("### 📋 Overig & Beleid")
        for i in range(18, 21):
            if st.checkbox(CHECKBOX_LABELS[i], key=i): selected_ids.append(i)

    personal_note = st.text_area("Persoonlijke toevoeging (bijv. impact op uw specifieke woning/gezin):")
    submitted = st.form_submit_button("Genereer Volledige Zienswijze")

if submitted:
    if not naam or not selected_ids:
        st.error("Vul uw naam in en selecteer minimaal één punt.")
    else:
        with st.spinner("Brief wordt opgesteld..."):
            brief = generate_zienswijze(naam, f"{adres}, {woonplaats}", datum, selected_ids, personal_note)
            st.text_area("Uw Brief:", brief, height=400)
            st.download_button("Download PDF", create_pdf(brief), "Zienswijze_Vroendaal_Update.pdf", "application/pdf")
