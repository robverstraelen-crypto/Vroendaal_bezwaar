# -*- coding: utf-8 -*-
import datetime
import io
import re
from typing import List, Dict, Any

import streamlit as st
from openai import OpenAI
from fpdf import FPDF

from docx import Document
from docx.shared import Pt

# =========================================================
# CONFIG
# =========================================================

APP_TITLE = "📝 Zienswijze Generator Vroendaal"
PAGE_TITLE = "Verzet Vroendaal"
PAGE_ICON = "⚖️"

DEADLINE_TEXT = "📅 DEADLINE: 12 FEBRUARI 2026"
DOSSIER_ZAAKNUMMER = "Z2025-00004367"

MODEL_NAME = "gpt-4o"
TEMPERATURE = 0.4

INTRO_MD = """
Gebruik deze tool om uw bezwaar te genereren.  
Alle teksten zijn juridisch gecheckt en bevatten de laatste bewijzen uit de Woo-stukken.
"""

INSTRUCTIES_KORT = """
**Instructie (kort)**  
1) Vul uw gegevens in.  
2) Kies of dit een **aanvulling op een pro-forma** is.  
3) (Optioneel) dien in **onder protest** bij late/ontbrekende stukken.  
4) Selecteer uw bezwaren en download het document.
"""

# Dit prompt bewaakt: géén nieuwe argumenten toevoegen.
SYSTEM_PROMPT = f"""
Je bent een senior procesadvocaat bestuursrecht, gespecialiseerd in de Omgevingswet en de gemeente Maastricht.
Je schrijft een formele zienswijze namens een bewoner tegen het ontwerp TAM-Omgevingsplan Vroendaal.

STIJL:
- Formeel, dwingend, juridisch correct, maar begrijpelijk.
- Geen agressie; wel scherp en precies.

HARD CONSTRAINTS:
- Gebruik uitsluitend de GESELECTEERDE TEKSTBLOKKEN (letterlijk) en eventuele 'Eigen bezwaren' van de gebruiker.
- Voeg geen nieuwe feiten, argumenten of juridische grondslagen toe.
- Je mag alleen korte verbindende zinnen toevoegen voor leesbaarheid, zonder nieuwe inhoud.
- Neem geen bronnen/citaten op die niet in de tekstblokken staan.

STRUCTUUR:
- Aanhef + onderwerpregel (met zaaknummer {DOSSIER_ZAAKNUMMER})
- Inleiding: afhankelijk van 'pro-forma aanvulling' en 'onder protest'
- Bezwaren: genummerd, per punt titel + tekstblok letterlijk
- Eigen bezwaren: als apart hoofdstuk, genummerd doorlopend
- Conclusie + verzoek ontvangstbevestiging
- Ondertekening
""".strip()

# =========================================================
# DATA: Tekstblokken (letterlijk) — VERVANG/COMPLETEER HIER
# =========================================================

BLOCKS: List[Dict[str, Any]] = [
    # --- (voorbeelden; laat hier jouw volledige set in staan) ---
    {"id": 1, "category": "Procedurele gebreken", "section": "Misleiding Contracten",
     "title": "Fantoomcontract ondermijnt rechtmatigheid besluitvorming",
     "text": "De anterieure overeenkomst is gepresenteerd als gesloten, terwijl deze juridisch nog niet bestond. ..."},
    {"id": 2, "category": "Procedurele gebreken", "section": "Misleiding Contracten",
     "title": "Structurele misleiding van de gemeenteraad",
     "text": "De gemeenteraad is structureel onjuist en onvolledig geïnformeerd ..."},
    # ...
    {"id": 27, "category": "Participatie", "section": "Schijnparticipatie",
     "title": "Kernbezwaren structureel genegeerd",
     "text": "De participatieprocedure heeft niet geleid tot daadwerkelijke invloed ..."},
]

# =========================================================
# HELPERS
# =========================================================

def get_client() -> OpenAI | None:
    try:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        return None

def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def build_indexes(blocks):
    by_id = {b["id"]: b for b in blocks}
    categories = sorted({b["category"] for b in blocks}, key=lambda x: x.lower())
    cat_map = {}
    for cat in categories:
        cat_map[cat] = {}
        sections = sorted({b["section"] for b in blocks if b["category"] == cat}, key=lambda x: x.lower())
        for sec in sections:
            ids = [b["id"] for b in blocks if b["category"] == cat and b["section"] == sec]
            cat_map[cat][sec] = ids
    return by_id, categories, cat_map

BY_ID, CATEGORIES, CAT_MAP = build_indexes(BLOCKS)

def matches_search(block, q: str) -> bool:
    q = (q or "").strip().lower()
    if not q:
        return True
    return (q in block["title"].lower()) or (q in block["text"].lower()) or (q in block["section"].lower())

def create_pdf_bytes(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_font("Arial", size=11)

    clean_text = (text or "").encode("latin-1", "replace").decode("latin-1")
    for line in clean_text.split("\n"):
        pdf.multi_cell(0, 6, line)
    return pdf.output(dest="S").encode("latin-1")

# =========================================================
# DOCX GENERATOR (zoals je vorige versie)
# =========================================================

def create_zienswijze_doc(data: Dict[str, str],
                         selected_points: List[Dict[str, str]],
                         is_pro_forma: bool,
                         is_protest: bool,
                         eigen_bezwaren: List[str]) -> Document:
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    # 1. Header (afzender)
    p_sender = doc.add_paragraph()
    p_sender.add_run(f"{data['naam']}\n").bold = True
    p_sender.add_run(f"{data['adres']}\n{data['postcode']} {data['woonplaats']}\n{data['email']}")

    doc.add_paragraph("\n")
    # Ontvanger
    p_receiver = doc.add_paragraph()
    p_receiver.add_run("Aan de Gemeenteraad van Maastricht\nPostbus 1992\n6201 BZ Maastricht")

    datum_str = datetime.date.today().strftime("%d-%m-%Y")
    doc.add_paragraph(f"\nMaastricht, {datum_str}")

    # 2. Betreft
    p_subject = doc.add_paragraph()
    p_subject.add_run("Betreft: ").bold = True
    subject_text = f"ZIENSWIJZE TAM-OMGEVINGSPLAN 'VROENDAAL' ({DOSSIER_ZAAKNUMMER})"
    if is_pro_forma:
        subject_text = f"AANVULLING OP PRO-FORMA ZIENSWIJZE ({DOSSIER_ZAAKNUMMER})"
    p_subject.add_run(subject_text)

    # 3. Inleiding (dynamisch)
    doc.add_paragraph("Geachte leden van de Raad,\n")

    intro_text = ""
    if is_pro_forma:
        intro_text += "Hierbij dien ik, ondergetekende, mijn inhoudelijke aanvulling in op de eerder door mij ingediende pro-forma zienswijze. "
    else:
        intro_text += "Hierbij dien ik, ondergetekende, mijn zienswijze in tegen het ontwerp TAM-Omgevingsplan Vroendaal. "

    if is_protest:
        intro_text += (
            "Ik dien deze zienswijze in ONDER PROTEST.\n\n"
            "Omdat het dossier incompleet is en (cruciale) stukken laat of gefaseerd beschikbaar zijn gesteld, "
            "maak ik een formeel voorbehoud om deze zienswijze later nog aan te vullen zodra alle stukken volledig ter inzage zijn gelegd.\n"
        )

    intro_text += "\nIk breng de volgende bezwaren naar voren:"
    doc.add_paragraph(intro_text)

    # 4. Punten (doorlopende nummering)
    n = 0
    if not selected_points:
        doc.add_paragraph("[LET OP: Selecteer minimaal één bezwaarpunt in de app.]")
    else:
        for b in selected_points:
            n += 1
            p = doc.add_paragraph()
            runner = p.add_run(f"\n{n}. {b['title']}")
            runner.bold = True
            doc.add_paragraph(b["text"])

    # Eigen bezwaren (optioneel; doorlopende nummering)
    eigen_clean = [normalize_ws(x) for x in (eigen_bezwaren or []) if normalize_ws(x)]
    if eigen_clean:
        doc.add_paragraph("\nEigen bezwaren (door indiener)\n")
        for item in eigen_clean:
            n += 1
            p = doc.add_paragraph()
            runner = p.add_run(f"\n{n}. {item}")
            runner.bold = True

    # 5. Slot
    slot_text = (
        "\nConclusie & Vordering\n"
        "Ik verzoek u deze zienswijze te betrekken bij de besluitvorming en het plan niet in deze vorm vast te stellen. "
        "Ik verzoek u tevens de ontvangst van deze zienswijze schriftelijk te bevestigen.\n"
    )
    doc.add_paragraph(slot_text)

    doc.add_paragraph("\n\nHoogachtend,\n\n(Handtekening)\n\n")
    doc.add_paragraph(f"{data['naam']}")

    return doc

# =========================================================
# STREAMLIT UI
# =========================================================

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
st.title(APP_TITLE)
st.markdown(INTRO_MD)
st.warning(DEADLINE_TEXT)
st.markdown(INSTRUCTIES_KORT)

client = get_client()
if client is None:
    st.warning("⚠️ Geen OpenAI API key gevonden. Voeg `OPENAI_API_KEY` toe in Streamlit Secrets.")
    st.stop()

# Sidebar: zoek & reset
with st.sidebar:
    st.header("Selectie & hulp")
    search_q = st.text_input("Zoek in titels/tekst", value="", placeholder="bijv. waterberging, parkeertekort, Woo…")
    st.divider()
    if st.button("Selectie wissen", use_container_width=True):
        for b in BLOCKS:
            st.session_state[f"cb_{b['id']}"] = False
        st.rerun()

# STAP 1: Gegevens
st.header("1. Uw Gegevens")
col1, col2 = st.columns(2)
with col1:
    naam = st.text_input("Naam & Voorletters")
    adres = st.text_input("Straat & Huisnummer")
with col2:
    postcode = st.text_input("Postcode")
    woonplaats = st.text_input("Woonplaats", value="Maastricht")
email = st.text_input("E-mailadres")

# STAP 2: Type indiening
st.header("2. Type Indiening")
is_pro_forma = st.checkbox("Dit is een AANVULLING op een eerdere pro-forma zienswijze", value=False)
is_protest = st.checkbox("Ik dien dit in ONDER PROTEST (vanwege late/ontbrekende stukken)", value=True)

# STAP 3: Bezwaren kiezen (mindmap-structuur: categorie -> sectie -> punten)
st.header("3. Kies uw Bezwaren")
st.info("Vink aan wat op u van toepassing is. Gebruik de zoekfunctie links om sneller te filteren.")

tabs = st.tabs(CATEGORIES)
for tab, cat in zip(tabs, CATEGORIES):
    with tab:
        sections = list(CAT_MAP[cat].keys())
        for sec in sections:
            ids = CAT_MAP[cat][sec]
            ids_filtered = [i for i in ids if matches_search(BY_ID[i], search_q)]
            if not ids_filtered:
                continue
            with st.expander(f"{sec} ({len(ids_filtered)} punten)", expanded=("Integriteit" in sec)):
                for bid in ids_filtered:
                    b = BY_ID[bid]
                    checked = st.checkbox(b["title"], key=f"cb_{bid}", value=st.session_state.get(f"cb_{bid}", False))
                    if checked:
                        st.caption(f"{b['text'][:160]}...")

# Eigen bezwaren
st.subheader("Eigen bezwaren / argumenten (optioneel)")
st.caption("U kunt tot 5 eigen punten toevoegen.")

if "custom_items" not in st.session_state:
    st.session_state.custom_items = [""]

cbtn1, cbtn2, cbtn3 = st.columns([1, 1, 2])
with cbtn1:
    if st.button("➕ Voeg punt toe"):
        if len(st.session_state.custom_items) < 5:
            st.session_state.custom_items.append("")
        st.rerun()
with cbtn2:
    if st.button("➖ Verwijder laatste"):
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

# STAP 4: Genereren & Download + instructies
st.header("4. Download & Indieninstructies")

selected_ids = [b["id"] for b in BLOCKS if st.session_state.get(f"cb_{b['id']}", False)]
selected_points = [{"title": BY_ID[i]["title"], "text": BY_ID[i]["text"]} for i in selected_ids]

generate_docx = st.button("🚀 Genereer Zienswijze (.docx)", type="primary", use_container_width=True)

if generate_docx:
    if not naam or not adres:
        st.error("Vul naam en adres in.")
        st.stop()
    if len(selected_points) == 0 and not any(normalize_ws(x) for x in st.session_state.custom_items):
        st.error("Kies minimaal één punt (of voeg een eigen bezwaar toe).")
        st.stop()

    user_data = {
        "naam": naam,
        "adres": adres,
        "postcode": postcode,
        "woonplaats": woonplaats,
        "email": email
    }

    # DOCX (zoals je oude generator)
    doc = create_zienswijze_doc(
        data=user_data,
        selected_points=selected_points,
        is_pro_forma=is_pro_forma,
        is_protest=is_protest,
        eigen_bezwaren=st.session_state.custom_items
    )

    bio = io.BytesIO()
    doc.save(bio)

    st.success("Uw document is klaar!")
    st.download_button(
        label="⬇️ Download Word-bestand",
        data=bio.getvalue(),
        file_name=f"Zienswijze_{naam.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # Optioneel: PDF van dezelfde inhoud (handig als upload)
    try:
        # We renderen een eenvoudige tekstvariant; Word blijft leidend.
        # (PDF is optioneel en 'best effort' zonder perfecte opmaak.)
        txt_preview = f"{naam}\n{adres}\n{postcode} {woonplaats}\n{email}\n\n"
        txt_preview += f"Aan de Gemeenteraad van Maastricht\nPostbus 1992\n6201 BZ Maastricht\n\n"
        txt_preview += f"Maastricht, {datetime.date.today().strftime('%d-%m-%Y')}\n\n"
        if is_pro_forma:
            txt_preview += f"Betreft: AANVULLING OP PRO-FORMA ZIENSWIJZE ({DOSSIER_ZAAKNUMMER})\n\n"
        else:
            txt_preview += f"Betreft: ZIENSWIJZE TAM-OMGEVINGSPLAN 'VROENDAAL' ({DOSSIER_ZAAKNUMMER})\n\n"
        txt_preview += "Geachte leden van de Raad,\n\n"
        # korte intro in tekst
        txt_preview += "Ik breng de volgende bezwaren naar voren:\n\n"
        for idx, b in enumerate(selected_points, 1):
            txt_preview += f"{idx}. {b['title']}\n{b['text']}\n\n"

        pdf_bytes = create_pdf_bytes(txt_preview)
        st.download_button(
            label="📄 Download (eenvoudige) PDF",
            data=pdf_bytes,
            file_name=f"Zienswijze_{naam.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    except Exception:
        pass

st.markdown("---")
st.subheader("📮 Hoe dien ik dit in?")
st.markdown(f"""
U heeft 3 opties om uw zienswijze in te dienen. **Doe dit uiterlijk 12 februari 2026.**

**Optie 1: Digitaal (Snelst)**
- Ga naar de website van de gemeente Maastricht en zoek op 'Zienswijze indienen'.
- Log in met uw DigiD.
- Upload het Word-bestand (of sla het eerst op als PDF).

**Optie 2: Per Post (Aangetekend aanbevolen)**
- Print het document uit.
- **Zet uw handtekening** onderaan de brief.
- Stuur het naar:  
  > Gemeenteraad van Maastricht  
  > Postbus 1992  
  > 6201 BZ Maastricht  

**Optie 3: Per E-mail (alleen als dit passend is in uw situatie)**
- Mail naar `post@maastricht.nl` o.v.v. "Zienswijze zaak {DOSSIER_ZAAKNUMMER}" en vraag om een ontvangstbevestiging.

*Tip: Stuur ook een kopie naar de griffie (`griffie@maastricht.nl`) zodat raadsleden weten dat u gereageerd heeft.*
""")
