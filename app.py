# -*- coding: utf-8 -*-
import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import datetime

# --- CONFIGURATIE ---
# Haal de API key op uit de geheime instellingen van Streamlit
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    # Fallback voor als je lokaal test zonder secrets file, of als de key mist
    client = None

# --- JURIDISCHE TEKSTBLOKKEN (DE MUNITIE - REVISIE 2) ---
TEXT_BLOCKS = {
    1: """
    **Strijdigheid met Verkeersstructuur (Sluipverkeer via 'De Knip')**
    Het plan leidt het verkeer van 'Blok A' via de interne wegenstructuur (Bruysterbosch/Bunderbosch/Ravensbosch/Jansbosch/Savelsbosch). Dit is in strijd met het principe van 'Duurzaam Veilig'. Deze straten zijn ingericht als Erftoegangsweg (30km/h) en niet berekend op de toevoeging van extra ontsluitingsverkeer voor 43 appartementen plus bezoekers. De voorgestelde verkeersafwikkeling tast de leefbaarheid onevenredig aan en leidt tot ongewenst sluipverkeer door de wijk.
    """,
    2: """
    **Aantasting Verblijfsfunctie en Veiligheid Kinderen**
    De meeste straten in Vroendaal functioneren feitelijk als 'woonerf' (verblijfsgebied) waar kinderen op straat spelen. De toename van verkeersintensiteit door het plan doorbreekt dit karakter. De gemeente faciliteert hier een situatie waarin de auto domineert boven de spelende bezoeker, wat haaks staat op de gemeentelijke ambities voor veilige, kindvriendelijke wijken. De objectieve verkeersveiligheid komt in het geding.
    """,
    3: """
    **Risico Schoolroute (Kruising Savelsbosch/Rijksweg)**
    De verkeersgeneratie van het plan interfereert met de langzaam-verkeersroute richting basisscholen en Porta Mosana (route Savelsbosch). Het plan voorziet niet in adequate veiligheidsmaatregelen voor overstekende fietsers en voetgangers op de kruispunten die zwaarder belast gaan worden. Zonder fysieke aanpassing van de infrastructuur is de veiligheid van schoolgaande kinderen niet gewaarborgd.
    """,
    4: """
    **Verkeersveiligheid Rijksweg N278 (Inkorten Uitvoegstrook)**
    De ontsluiting van 'Blok B' op de Rijksweg (N278) is verkeerstechnisch onaanvaardbaar. Het plan voorziet in het opsplitsen/inkorten van de bestaande opstelstrook/uitvoegstrook. Dit creëert een 'weefvak' dat te kort is volgens CROW-richtlijnen. Dit leidt tot reëel gevaar van terugslag van wachtend verkeer op de hoofdrijbaan (50 km/u), wat de doorstroming (van hulpdiensten) op deze cruciale route naar het MUMC+ blokkeert.
    """,
    5: """
    **Parkeerproblematiek (Waterbedeffect door Slagboom)**
    De parkeeroplossing is niet realistisch. Bezoekersparkeren wordt deels op eigen terrein achter een slagboom of poort gesitueerd. De praktijk wijst uit dat bezoekers en bezorgdiensten deze drempel mijden en kiezen voor de openbare weg. Hierdoor ontstaat een 'waterbedeffect': de parkeerdruk verschuift naar de reeds drukke en smalle omliggende straten in Vroendaal. De parkeerbalans voldoet daarmee enkel op papier, maar niet in de praktijk. Ook voldoen de afmetingen van de bezoekersparkeerplaatsen niet allemaal aan de CROW normen.
    """,
    6: """
    **Ruimtelijke Insluiting**
    Voor de bewoners aan de omringende straten die grenzen aan het plangebied, leidt het plan tot ernstige ruimtelijke insluiting. Het hoogteverschil tussen de bestaande laagbouw en de geplande 11 meter hoge bebouwing (3 lagen op een halfverdiepte parkeerkelder) is te groot. Er is sprake van een abrupte schaalsprong die het woongenot en de privacy onevenredig aantast ('inclusie-effect').
    """,
    7: """
    **Privacyinbreuk door Balkons (Art. 5:50 BW)**
    De positionering van de balkons en raampartijen in de nieuwe blokken zorgt voor directe, onbelemmerde inkijk in de privédomeinen (tuinen en woonkamers) van omwonenden. Gezien de korte afstand en de hoogte is er sprake van onrechtmatige hinder ex artikel 5:50 BW. Het plan voorziet onvoldoende in maatregelen (zoals ondoorzichtig glas of groene buffers) om deze privacyinbreuk te voorkomen.
    """,
    8: """
    **Verlies van Bezonning en Daglicht**
    Door de massa en hoogte van de bebouwing (blokken A en B) wordt de bezonning in de tuinen en woningen van omwonenden beperkt, met name in de wintermaanden en het voorjaar. Indiener betwist dat de effecten 'aanvaardbaar' zijn en stelt dat de vermindering van daglichttoetreding leidt tot een significante verslechtering van het woonklimaat die niet is gerechtvaardigd door het bouwbelang.
    """,
    9: """
    **Stedenbouwkundige Dissonantie (De 'UFO' in de wijk)**
    Het plan sluit niet aan bij de bestaande morfologie van Vroendaal/Heugem (grondgebonden, dorpse sfeer). De gekozen typologie ('stedelijke blokken', massief, strakke facades) vormt een trendbreuk en detoneert met de omgeving. Het plan voldoet niet aan de redelijke eisen van welstand omdat het geen relatie aangaat met de omliggende bebouwing, maar zich er juist van afkeert.
    """,
    10: """
    **Funderingsrisico's en Trillingen (Bodemgesteldheid)**
    Gezien de specifieke bodemopbouw (Löss/Leem en mogelijke geroerde grond) zijn de risico's op zettingsschade aan omliggende woningen bij hei- of trilwerkzaamheden groot. Veel omliggende woningen zijn op beton gefundeerd. Indiener eist een nulmeting en een trillingsmonitoringsplan conform SBR-A (schade) en SBR-B (hinder) als harde vergunningsvoorwaarde.
    """,
    11: """
    **Bodemverontreiniging (Risico Verspreiding)**
    De locatie is een voormalige autosloperij. Hoewel sanering is toegezegd, maakt indiener zich zorgen over de verspreiding van restvervuiling (zware metalen, asbest, PAK's) tijdens de graafwerkzaamheden (verwaaiing van stof). Het 'roeren' in deze historisch belaste grond vormt een direct gezondheidsrisico voor de direct omwonenden. De saneringsplannen ontbreken en bieden derhalve geen garantie tegen blootstellingsrisico's.
    """,
    12: """
    **Bouwlogistiek: Geen Bouwverkeer door de Wijk**
    Het bouwlogistieke plan is onvoldoende uitgewerkt. De infrastructuur van Vroendaal is fysiek ongeschikt voor zwaar bouwverkeer (draaicirkels, aslast). Indiener eist dat in de vergunning wordt vastgelegd dat al het bouwverkeer (aan- en afvoer) uitsluitend direct via de Rijksweg (N278) wordt afgewikkeld en onder geen beding door de woonwijk mag rijden.
    """,
    13: """
    **Hittestress en 'Verstening' (Klimaatadaptatie)**
    Het plan voorziet in massale verstening van het perceel. Uit de 'Hittekaart Maastricht' blijkt dat dit gebied nu al risicovol is voor hittestress. Het vervangen van halfverharding/groen door beton en asfalt verergert het 'Urban Heat Island' effect. Dit is in strijd met de gemeentelijke Omgevingsvisie 2040 waarin vergroening en klimaatadaptatie centraal staan.
    """,
    14: """
    **Ecologie: Bomen versus 'Struweel'**
    In de plantoelichting worden bestaande, waardevolle bomen ten onrechte gekwalificeerd als 'struweel' of 'opschot'. Dit lijkt een administratieve truc om de herplantplicht en kapvergunningvereisten te omzeilen. Indiener verzet zich tegen deze kwalificatie en stelt dat de groene buffer een essentiële ecologische en visuele functie vervult die behouden moet blijven.
    """,
    15: """
    **Onvolledige Stikstofberekening (Aerius)**
    De stikstofberekening (Aerius) rammelt. De verkeersgeneratie in de Aerius-modelinvoer lijkt niet overeen te komen met de werkelijke verkeersprognoses (inclusief bezorgdiensten/bezoekers). Tevens is onduidelijk of cumulatie met andere projecten in de regio (o.a. Porta Mosana) correct is meegenomen. Significant negatieve effecten op Natura 2000 (Savelsbos) zijn derhalve niet met zekerheid uitgesloten.
    """,
    16: """
    **Onzorgvuldige Participatie (Draagvlak ontbreekt)**
    De gemeente stelt dat er geparticipeerd is, maar het participatieverslag geeft een vertekend beeld. Een petitie met 421 handtekeningen ('Huizen Oké, massa NEE') wordt terzijde geschoven. Er is sprake van 'vinkjes-participatie': de plannen zijn ondanks massaal verzet nauwelijks aangepast op essentiële punten (hoogte, ontsluiting, massa). Van een zorgvuldig proces is geen sprake.
    """,
    17: """
    **Vooringenomenheid (De 'Gratis Munitie' Kwestie)**
    Er is sprake van schending van het beginsel van onpartijdigheid (art. 2:4 Awb). Uit openbaar geworden interne correspondentie blijkt dat ambtenaren de instructie kregen om bewoners geen informatie te geven om hen geen 'gratis munitie' te verschaffen. Deze houding diskwalificeert de gemeente als objectieve belangenafweger en maakt het besluitvormingsproces onrechtmatig.
    """,
    18: """
    **Gebrekkige Informatievoorziening (Woo-verzoeken)**
    Belanghebbenden zijn stelselmatig benadeeld in hun informatiepositie. Essentiële rapporten waren niet tijdig beschikbaar of moesten via Woo-verzoeken worden afgedwongen. Hierdoor hebben omwonenden niet de eerlijke kans gehad om hun zienswijze ten volle voor te bereiden binnen de termijn, wat in strijd is met het zorgvuldigheidsbeginsel (art. 3:2 Awb).
    """,
    19: """
    **Uitvoerbaarheid: Netcongestie**
    In de toelichting wordt te makkelijk voorbijgegaan aan de netcongestie in Limburg. Een bouwplan is pas ruimtelijk aanvaardbaar als de uitvoerbaarheid (stroomaansluiting voor 60+ woningen en warmtepompen) gegarandeerd is. Zonder harde toezegging van Enexis is vergunningverlening voorbarig en in strijd met de eisen van goede ruimtelijke ordening.
    """,
    20: """
    **Alternatievenonderzoek (Burgerplan)**
    De Werkgroep heeft een realistisch alternatief gepresenteerd: grondgebonden woningen die passen in de wijkstructuur. De gemeente heeft dit alternatief zonder deugdelijke motivering terzijde geschoven. Volgens jurisprudentie dient het bevoegd gezag serieuze alternatieven volwaardig mee te wegen; door vast te houden aan het projectontwikkelaars-plan wordt het algemeen belang van de buurt miskend.
    """
}

CHECKBOX_LABELS = {
    1: "Verkeer door de Wijk",
    2: "Veiligheid Spelende Kinderen",
    3: "Onveilige Schoolroute",
    4: "Verkeersinfarct Rijksweg & Hulpdiensten",
    5: "Parkeeroverlast",
    6: "Insluiting Achtertuinen",
    7: "Privacy & Inkijk (Balkons)",
    8: "Verlies van Zonlicht",
    9: "Massale Hoogbouw (Niet passend)",
    10: "Trillingsschade & Fundering",
    11: "Gevaarlijke Bodem (Asbest)",
    12: "Bouwverkeer door de Wijk",
    13: "Hittestress & Verstening",
    14: "Kap van Bomen",
}





import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import datetime

# --- CONFIGURATIE ---
# Haal de API key op uit de geheime instellingen van Streamlit
# Als je lokaal test, maak dan een mapje .streamlit met daarin secrets.toml
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Geen API Key gevonden. Voer deze in bij de 'Secrets' instellingen van Streamlit.")
    st.stop()

# --- JURIDISCHE DATABASE (ONZE TEXT BLOCKS) ---
TEXT_BLOCKS = {
    1: "Strijdigheid met Verkeersstructuur en Leefbaarheid: Het plan is in strijd met de vereiste van 'een goede ruimtelijke ordening' (art. 5.2 Omgevingswet) doordat het een verkeersintensiteit van circa 300 mvt/etmaal genereert die wordt afgewikkeld via smalle woonstraten (erftoegangswegen, 30km-zone). De interne wegenstructuur van Vroendaal is morfologisch en profiel-technisch niet berekend op deze toename. Dit leidt tot een onaanvaardbare aantasting van het verblijfsklimaat.",
    2: "Aantasting Veiligheid Spelende Kinderen: De straten in Vroendaal functioneren feitelijk als woonerf. De voorgenomen verkeerstoename doorbreekt dit karakter en creëert objectieve onveiligheid voor kwetsbare verkeersdeelnemers. Het plan staat hiermee haaks op de gemeentelijke beleidsambities inzake 'Kindvriendelijk Maastricht' en 'Duurzaam Veilig'.",
    3: "Onveilige Schoolroute (Savelsbosch): De ontsluitingsroute interfereert met een primaire fiets- en looproute voor schoolgaande kinderen. Gezien het ontbreken van vrijliggende fietspaden of veilige oversteekvoorzieningen, introduceert het plan onaanvaardbare risico's. Dit getuigt niet van een zorgvuldige belangenafweging.",
    4: "Verkeersinfarct en Blokkade Hulpdiensten (N278): De aansluiting op de Rijksweg (N278) via een inkorting van de opstelstrook is onverantwoord. De N278 is een cruciale calamiteitenroute richting het MUMC+. De kans op terugslag (file) tot op de hoofdrijbaan is reëel, waardoor aanrijtijden van hulpdiensten in het geding komen.",
    5: "Parkeeroverlast: De parkeerbalans is gebaseerd op te optimistische aannames. Doordat bezoekersparkeren deels achter een slagboom zit, zal een 'waterbedeffect' optreden: parkeerdruk verschuift naar de omliggende straten in Vroendaal.",
    6: "Ruimtelijke Insluiting: De situering van de bouwmassa's direct grenzend aan de bestaande achtertuinen leidt tot een gevoel van insluiting en een onevenredige inbreuk op het woongenot. Er is geen sprake van een zorgvuldige landschappelijke inpassing.",
    7: "Privacyinbreuk (Art. 5:50 BW): Het plan voorziet in hoogbouw met balkons die direct uitzicht bieden op privéterreinen. Gezien de beperkte afstand is er sprake van onrechtmatige hinder in de zin van artikel 5:50 BW en een ernstige aantasting van de privacy.",
    8: "Verlies van Bezonning: De hoogbouw zorgt voor significante schaduwwerking. Het ontbreekt aan een onafhankelijke bezonningsstudie die aantoont dat wordt voldaan aan de TNO-normen. Zonder dit bewijs is het besluit onzorgvuldig.",
    9: "Stedenbouwkundige Dissonantie: Het plan sluit qua maat en schaal niet aan bij de bestaande morfologie van Vroendaal (grondgebonden). De massieve bouwblokken vormen een trendbreuk die afbreuk doet aan de ruimtelijke kwaliteit (strijd met Welstand).",
    10: "Trillingsschade & Fundering: Gezien de bodemgesteldheid bestaat groot risico op schade aan funderingen. Indiener eist een nulmeting en trillingsprognose conform SBR-richtlijnen A en B als harde voorwaarde in de vergunning.",
    11: "Gevaarlijke Bodem (Voormalige Autosloperij): De garanties dat sanering plaatsvindt zonder risico op verspreiding van gevaarlijke stoffen (asbest, metalen) naar de woonomgeving zijn onvoldoende. Het voorzorgsbeginsel vereist dat de volksgezondheid niet in gevaar komt.",
    12: "Onacceptabele Bouwroute: Het leiden van zwaar bouwverkeer door de smalle woonstraten is onacceptabel. Indiener eist dat de bouwroute uitsluitend direct via de Rijksweg/N278 wordt gefaciliteerd.",
    13: "Hittestress (Klimaatadaptatie): De massale verstening draagt bij aan het 'Urban Heat Island' effect (hittekaart: risico 47°C). Dit is in strijd met de 'Klimaatadaptatiestrategie Maastricht'.",
    14: "Bomenkap: Volwassen bomen worden ten onrechte als 'struweel' gekwalificeerd om kap te legitimeren zonder herplantplicht. Indiener maakt bezwaar tegen het verlies van biodiversiteit.",
    15: "Stikstof (Natuurtoets): De AERIUS-berekening is onvolledig (geen cumulatie met andere projecten zoals Porta Mosana). Negatieve effecten op Natura 2000-gebied Savelsbos zijn niet uitgesloten.",
    16: "Schijnparticipatie: Het participatieproces negeert dat 421 bewoners 'NEE' hebben gezegd. De participatie was een formaliteit zonder dat wezenlijk iets met de inbreng is gedaan (strijd met Participatieverordening).",
    17: "Vooringenomenheid (Art 2:4 Awb): Uit interne stukken ('Gratis Munitie') blijkt dat ambtenaren informatie achterhielden doordat ambtenaren niet in gesprek mochten gaan met leden van de werkgroep. Dit is een schending van het verbod op vooringenomenheid en het fair-play beginsel.",
    18: "Ontbrekende Informatie (Art 3:11 Awb): Essentiële stukken (bodem, stikstof, groenstrook, provincie, zakelijke overeenkomst) waren niet tijdig compleet ter inzage. Belanghebbenden zijn geschaad in hun reactiemogelijkheid.",
    19: "Netcongestie: Er is geen garantie dat de woningen op het stroomnet kunnen worden aangesloten. Een vergunning voor een onuitvoerbaar plan is in strijd met een goede ruimtelijke ordening.",
    20: "Negeren Burgeralternatief: De gemeente heeft het haalbare alternatief van de bewoners (grondgebonden) ten onrechte niet serieus meegewogen in de besluitvorming."
}

CHECKBOX_LABELS = {
    1: "Verkeer door de Wijk",
    2: "Veiligheid Spelende Kinderen",
    3: "Onveilige Schoolroute",
    4: "Verkeersinfarct Rijksweg & Hulpdiensten",
    5: "Parkeeroverlast",
    6: "Insluiting Achtertuinen",
    7: "Privacy & Inkijk (Balkons)",
    8: "Verlies van Zonlicht",
    9: "Massale Hoogbouw (Niet passend)",
    10: "Trillingsschade & Fundering",
    11: "Gevaarlijke Bodem (Asbest)",
    12: "Bouwverkeer door de Wijk",
    13: "Hittestress & Verstening",
    14: "Kap van Bomen",
    15: "Stikstof & Natuur",
    16: "Schijnparticipatie",
    17: "Vooringenomenheid Gemeente",
    18: "Geheime/Ontbrekende Stukken",
    19: "Netcongestie (Stroom)",
    20: "Steun Burgeralternatief"
}

# --- FUNCTIES ---

def generate_zienswijze(naam, adres, datum, selected_ids, personal_note):
    # Bouw de juridische argumentatie op
    juridische_argumenten = ""
    for i in selected_ids:
        juridische_argumenten += f"- PUNT {i}: {TEXT_BLOCKS[i]}\n"

    # De System Prompt (De Senior Advocaat Persona)
    system_prompt = """
    Je bent een senior procesadvocaat bestuursrecht, gespecialiseerd in de Omgevingswet en de gemeente Maastricht.
    Je schrijft een formele Zienswijze namens een bewoner tegen het plan 'Woningbouw Vroendaal'.
    
    STIJL:
    - Formeel, dwingend, juridisch correct, maar begrijpelijk.
    - Gebruik termen als: 'strijd met goede ruimtelijke ordening', 'onzorgvuldige voorbereiding', 'aantasting woon- en leefklimaat'.
    - Wees scherp op de inhoud, maar beleefd in de vorm.
    
    INSTRUCTIE:
    1. Begin met de formele aanhef aan de Gemeenteraad van Maastricht.
    2. Integreer de 'Persoonlijke Toevoeging' van de gebruiker in de inleiding om specifiek belang aan te tonen. Herschrijf dit zodat het professioneel klinkt.
    3. Werk de aangeleverde JURIDISCHE PUNTEN uit tot een lopend, logisch betoog. Gebruik tussenkopjes.
    4. Sluit af met de eis tot afwijzing van het plan en verzoek om bevestiging.
    5. Onderteken met Naam en Adres.
    """

    user_prompt = f"""
    GEGEVENS INDIENER:
    Naam: {naam}
    Adres: {adres}
    Datum: {datum}
    
    PERSOONLIJKE TOEVOEGING (Integreer dit als belang):
    "{personal_note}"
    
    JURIDISCHE PUNTEN (Verwerk deze argumenten in de brief):
    {juridische_argumenten}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Simpele encoding fix voor PDF (vervangt niet-ondersteunde karakters)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, clean_text)
    return pdf.output(dest="S").encode("latin-1")

# --- DE WEBSITE (UI) ---

st.set_page_config(page_title="Verzet Vroendaal", page_icon="⚖️")

st.title("⚖️ Zienswijze Generator Vroendaal")
st.markdown("""
**Instructie:**
Met deze tool genereert u een juridisch onderbouwde zienswijze tegen het nieuwbouwplan.
Vul uw gegevens in, vink uw bezwaren aan en klik op 'Genereer'.
""")

with st.form("zienswijze_form"):
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("Uw Naam")
        adres = st.text_input("Uw Adres + Huisnummer")
    with col2:
        woonplaats = st.text_input("Postcode + Woonplaats", value="Maastricht")
        datum = st.text_input("Datum", value=datetime.date.today().strftime("%d-%m-%Y"))

    st.subheader("Selecteer uw bezwaren")
    st.info("Kies de punten die op u van toepassing zijn. De tool voegt de juridische onderbouwing automatisch toe.")
    
    selected_ids = []
    
    # Maak 2 kolommen voor de checkboxes
    c1, c2 = st.columns(2)
    
    # Eerste 10 in kolom 1
    with c1:
        st.markdown("**Leefbaarheid & Woning**")
        for i in range(1, 11):
            if st.checkbox(CHECKBOX_LABELS[i], key=i):
                selected_ids.append(i)
                
    # Volgende 10 in kolom 2
    with c2:
        st.markdown("**Milieu, Natuur & Procedure**")
        for i in range(11, 21):
            if st.checkbox(CHECKBOX_LABELS[i], key=i):
                selected_ids.append(i)

    st.subheader("Persoonlijke Situatie (Optioneel)")
    personal_note = st.text_area("Wat is uw specifieke zorg? (Bijv: 'Mijn tuin grenst aan de inrit', 'Mijn kind fietst hier')", height=100)

    submitted = st.form_submit_button("🚀 Genereer Mijn Zienswijze")

# --- LOGICA NA INDIENEN ---

if submitted:
    if not naam or not adres:
        st.error("Vul alstublieft uw naam en adres in.")
    elif len(selected_ids) == 0:
        st.error("Selecteer minimaal één bezwaarpunt.")
    else:
        with st.spinner("De jurist schrijft uw brief... (dit duurt ca. 10 seconden)"):
            try:
                # Roep AI aan
                brief_tekst = generate_zienswijze(naam, f"{adres}, {woonplaats}", datum, selected_ids, personal_note)
                
                st.success("Uw zienswijze is gereed!")
                
                # Toon tekst op scherm
                st.text_area("Concept Zienswijze:", value=brief_tekst, height=400)
                
                # Download knop PDF
                # Let op: FPDF ondersteunt standaard beperkte tekensets, dus we houden het simpel
                pdf_bytes = create_pdf(brief_tekst)
                st.download_button(
                    label="📄 Download als PDF",
                    data=pdf_bytes,
                    file_name="Zienswijze_Vroendaal.pdf",
                    mime="application/pdf"
                )
                
                st.warning("⚠️ DISCLAIMER: Lees de brief goed door voordat u deze verstuurt. U blijft zelf verantwoordelijk voor de inhoud.")
                
            except Exception as e:
                st.error(f"Er ging iets mis: {e}")

