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

# --- JURIDISCHE TEKSTBLOKKEN (DE MUNITIE) ---
TEXT_BLOCKS = {
    1: """
    **Strijdigheid met Verkeersstructuur en Leefbaarheid (Ravensbosch/Bruysterbosch)**
    Het plan is in strijd met de vereiste van 'een goede ruimtelijke ordening' (art. 5.2 Omgevingswet) doordat het een verkeersintensiteit van circa 400 mvt/etmaal genereert die wordt afgewikkeld via smalle woonstraten (erftoegangswegen, 30km-zone). De interne wegenstructuur van Vroendaal is morfologisch en profiel-technisch niet berekend op deze toename, zeker niet in combinatie met zwaar bouwverkeer en logistieke diensten. Dit leidt tot een onaanvaardbare aantasting van het verblijfsklimaat en de verkeersveiligheid in de wijk.
    """,
    2: """
    **Aantasting Veiligheid Spelende Kinderen (Woonerf-karakter)**
    De straten in Vroendaal functioneren feitelijk als woonerf waar de auto te gast is en kinderen op straat spelen. De voorgenomen verkeerstoename doorbreekt dit karakter en creëert objectieve onveiligheid voor kwetsbare verkeersdeelnemers. Het plan staat hiermee haaks op de gemeentelijke beleidsambities inzake 'Kindvriendelijk Maastricht' en de verkeersveiligheidsvisie 'Duurzaam Veilig'.
    """,
    3: """
    **Onveilige Schoolroute (Savelsbosch)**
    De ontsluitingsroute doorkruist of interfereert met een primaire fiets- en looproute voor schoolgaande kinderen (o.a. richting basisschool/opvang). Gezien het ontbreken van vrijliggende fietspaden of veilige oversteekvoorzieningen op de kruisingen rondom de Savelsbosch, introduceert het plan onaanvaardbare risico's voor deze kwetsbare groep. Dit getuigt niet van een zorgvuldige belangenafweging.
    """,
    4: """
    **Verkeersinfarct en Blokkade Hulpdiensten (N278/Rijksweg)**
    De aansluiting van 'Blok B' op de Rijksweg (N278) via een opsplitsing/inkorting van de opstelstrook is verkeerskundig onverantwoord. De N278 is een cruciale calamiteitenroute voor ambulances en brandweer richting het MUMC+ en het Heuvelland. De kans op terugslag (filevorming) tot op de hoofdrijbaan is reëel, waardoor de aanrijtijden van hulpdiensten in het geding komen. Het algemeen belang van openbare veiligheid wordt hier ten onrechte ondergeschikt gemaakt aan het bouwplan.
    """,
    5: """
    **Parkeeroverlast en 'Waterbedeffect'**
    De parkeerbalans in het plan is gebaseerd op te optimistische aannames en normen die niet aansluiten bij de feitelijke autobezit-graad in dit segment. Doordat bezoekersparkeren deels achter een slagboom of op afstand wordt georganiseerd, zal een 'waterbedeffect' optreden: parkeerdruk verschuift naar de omliggende openbare straten in Vroendaal. Dit leidt tot overlast en onveilige situaties door foutparkeren.
    """,
    6: """
    **Ruimtelijke Insluiting en Aantasting Woongenot**
    De situering van de bouwmassa's direct grenzend aan de bestaande achtertuinen leidt tot een gevoel van insluiting en een onevenredige inbreuk op het woongenot. Er is geen sprake van een zorgvuldige landschappelijke inpassing of een respectvolle overgangszone tussen de bestaande laagbouw en de nieuwe hoogbouw, wat in strijd is met goede stedenbouwkundige principes.
    """,
    7: """
    **Privacyinbreuk en Directe Inkijk (Art. 5:50 BW)**
    Het plan voorziet in hoogbouw met balkons/buitenruimtes die direct uitzicht bieden op de privéterreinen van omwonenden. Gezien de beperkte afstand en de hoogte van de bebouwing (tot 4 bouwlagen), is er sprake van een onrechtmatige hinder in de zin van artikel 5:50 BW en een ernstige aantasting van de privacysfeer die in een stedelijke omgeving niet zonder meer geduld hoeft te worden.
    """,
    8: """
    **Verlies van Bezonning (Schaduwhinder)**
    De hoogbouw zorgt voor significante schaduwwerking op de naastgelegen percelen. Met name in het voor- en najaar en de winter zal de bezonning in tuinen en woonkamers drastisch afnemen. Het ontbreekt aan een onafhankelijke bezonningsstudie die onomstotelijk aantoont dat wordt voldaan aan de 'lichte' TNO-norm voor bezonning. Zonder dit bewijs is het besluit onzorgvuldig.
    """,
    9: """
    **Stedenbouwkundige Dissonantie (Schaalgrootte)**
    Het plan sluit qua maat, schaal en korrelgrootte niet aan bij de bestaande morfologie van de wijk Vroendaal. De wijk kenmerkt zich door grondgebonden woningen en een open structuur. De massieve, aaneengesloten bouwblokken ('stedelijke wand') vormen een trendbreuk die afbreuk doet aan de ruimtelijke kwaliteit en identiteit van de omgeving (strijd met Welstandsnota/Omgevingsvisie).
    """,
    10: """
    **Risico op Trillingsschade en Zettingen (SBR-Richtlijnen)**
    Gezien de bodemgesteldheid en de noodzaak tot zwaar hei- of boorwerk, bestaat er een groot risico op schade aan de funderingen en muren van omliggende woningen. Indiener eist dat voorafgaand aan vergunningverlening een nulmeting wordt verricht en een trillingsprognose conform SBR-richtlijnen A (schade) en B (hinder) wordt opgesteld. De gemeente dient aansprakelijkheid voor schade expliciet te borgen.
    """,
    11: """
    **Gezondheidsrisico's Bodemverontreiniging (Voormalige Autosloperij)**
    De locatie betreft een voormalige autosloperij met een historie van bodemverontreiniging. De garanties dat sanering plaatsvindt zonder risico op verspreiding van gevaarlijke stoffen (o.a. asbest, zware metalen) of explosieven naar de woonomgeving zijn onvoldoende. Het voorzorgsbeginsel vereist dat onomstotelijk vaststaat dat de volksgezondheid tijdens de graafwerkzaamheden niet in gevaar komt.
    """,
    12: """
    **Onacceptabele Bouwroute door Woonwijk**
    Het bouwlogistieke plan is vaag of ontbreekt. Het leiden van zwaar bouwverkeer door de smalle woonstraten van Vroendaal gedurende een periode van ca. 1,5 tot 2 jaar is onacceptabel vanwege geluidsoverlast, trillingen, onveiligheid en schade aan het wegdek. Indiener eist dat de bouwroute uitsluitend direct via de Rijksweg/N278 wordt gefaciliteerd.
    """,
    13: """
    **Hittestress en Verstening (Strijd met Klimaatadaptatie)**
    Het plan voorziet in massale verstening van een thans groene locatie. Dit draagt bij aan het 'Urban Heat Island' effect, waarbij temperaturen (zoals erkend in gemeentelijke hittekaarten) kunnen oplopen tot 47°C. Dit is in directe strijd met de gemeentelijke ambities uit de Omgevingsvisie 2040 en de 'Klimaatadaptatiestrategie Maastricht' om hittestress tegen te gaan.
    """,
    14: """
    **Onterechte Kwalificatie Groen en Bomenkap**
    In de plannen worden bestaande, volwassen bomen en groenstructuren ten onrechte afgedaan als laagwaardig 'struweel' om kap te legitimeren zonder herplantplicht. Dit is misleidend. Indiener maakt bezwaar tegen de kap en beroept zich op het belang van behoud van biodiversiteit en de regels uit de Bomenverordening/APV. De ecologische waarde wordt onderschat.
    """,
    15: """
    **Ontbrekende Cumulatie Stikstof (Natuurtoets)**
    De uitgevoerde stikstofberekening (AERIUS) is onvolledig en daarmee juridisch onhoudbaar. Er is geen rekening gehouden met de cumulatieve effecten van andere projecten in de directe omgeving (o.a. Porta Mosana). Hierdoor kunnen significant negatieve effecten op het nabijgelegen Natura 2000-gebied (Savelsbos) niet met de vereiste zekerheid worden uitgesloten (strijd met Wet natuurbescherming).
    """,
    16: """
    **Schijnparticipatie en Negeren Draagvlak**
    Het participatieproces voldoet niet aan de eisen van de Maastrichtse Participatieverordening. Uit het verslag blijkt dat 421 bewoners een petitie hebben getekend ('NEE tegen dit plan'), maar dit massale gebrek aan draagvlak wordt in de besluitvorming genegeerd. De participatie was een formaliteit ('afvinklijstje') zonder dat er wezenlijk iets met de inbreng van de buurt is gedaan.
    """,
    17: """
    **Vooringenomenheid en Schending Art. 2:4 Awb**
    Er zijn sterke aanwijzingen dat de gemeente niet onpartijdig heeft gehandeld. Uit interne correspondentie ('Gratis Munitie' mail) blijkt dat ambtenaren is opgedragen bewoners actief informatie te onthouden om juridische posities niet te versterken. Dit is een flagrante schending van het verbod op vooringenomenheid (artikel 2:4 Awb) en het fair-play beginsel, wat het hele besluit vernietigbaar maakt.
    """,
    18: """
    **Strijd met Informatieplicht (Art. 3:11 Awb)**
    Essentiële stukken (waaronder volledige onderzoeksrapporten naar bodem en stikstof) waren ten tijde van de terinzagelegging niet compleet of niet toegankelijk. Hierdoor zijn belanghebbenden geschaad in hun vermogen om tijdig en adequaat een zienswijze in te dienen. Dit is in strijd met de zorgvuldigheid en de informatieplicht ex artikel 3:11 Awb.
    """,
    19: """
    **Onzekerheid Nutsvoorzieningen (Netcongestie)**
    De uitvoerbaarheid van het plan is niet gewaarborgd. Gezien de huidige netcongestieproblematiek in Limburg is er geen garantie dat de nieuwe woningen tijdig op het elektriciteitsnet kunnen worden aangesloten. Het verlenen van een vergunning voor een plan waarvan de feitelijke uitvoerbaarheid onzeker is, is in strijd met de eisen van een goede ruimtelijke ordening.
    """,
    20: """
    **Negeren van het Burgeralternatief**
    De werkgroep heeft een concreet en haalbaar alternatief plan ingediend (grondgebonden woningen, passend in de wijk). De gemeente heeft nagelaten dit alternatief serieus te onderzoeken en te vergelijken met het voorliggende plan. Volgens vaste jurisprudentie dient het bevoegd gezag serieuze alternatieven in de belangenafweging te betrekken; dat is hier ten onrechte niet gebeurd.
    """
}

CHECKBOX_LABELS = {
    1: "Verkeer door de Wijk (Ravensbosch)",
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
    if not client:
        return "⚠️ Er is geen API key ingesteld. Ik kan geen brief genereren. Controleer je 'Secrets' in Streamlit."

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Er ging iets mis bij de AI connectie: {str(e)}"

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
                
                if "⚠️" in brief_tekst or "Er ging iets mis" in brief_tekst:
                    st.error(brief_tekst)
                else:
                    st.success("Uw zienswijze is gereed!")
                    
                    # Toon tekst op scherm
                    st.text_area("Concept Zienswijze:", value=brief_tekst, height=400)
                    
                    # Download knop PDF
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
