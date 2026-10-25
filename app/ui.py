"""Webinterface voor de Vacature Matcher (Streamlit).

Dit bestand doet alleen presentatie: invoer ophalen,
de matcher aanroepen, en het resultaat tonen.
Alle logica zit in app/matcher.py en app/rag.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.matcher import match_vacature
from app.rag import maak_chunks, bouw_cv_store


# ---------- Pagina-instelling ----------

st.set_page_config(page_title="Vacature Matcher", page_icon="🔍", layout="wide")
st.title("Vacature Matcher 🔍")
st.caption("Plak een vacature, upload je CV, en zie of jullie bij elkaar passen.")


# ---------- Invoer ----------

cv_bestand = st.file_uploader("Upload je CV (.txt)", type=["txt"])
vacature_tekst = st.text_area(
    "Vacature",
    height=250,
    placeholder="Plak hier de volledige vacature-tekst...",
)

analyse_knop = st.button("Analyseer match", type="primary", use_container_width=True)


# ---------- Verwerking ----------

if analyse_knop and cv_bestand and vacature_tekst:
    cv_tekst = cv_bestand.getvalue().decode("utf-8")

    voortgang = st.progress(0, text="CV verwerken...")
    bouw_cv_store(maak_chunks(cv_tekst))
    voortgang.progress(40, text="Vacature analyseren en matchen...")

    analyse = match_vacature(vacature_tekst)

    voortgang.progress(100, text="Klaar!")
    voortgang.empty()

    # ---------- Resultaten ----------

    st.header(analyse.functietitel)

    kolom1, kolom2 = st.columns([1, 3])
    with kolom1:
        st.metric("Match", f"{analyse.match_percentage}%")
    with kolom2:
        st.progress(analyse.match_percentage / 100)

    st.subheader("Beoordeling per eis")
    for e in analyse.eisen:
        icoon = "✅" if e.gevonden_in_cv else "❌"
        with st.expander(f"{icoon} {e.eis}"):
            st.write(f"**Onderbouwing:** {e.onderbouwing}")
            st.caption(f"Toelichting: {e.toelichting}")

    links, rechts = st.columns(2)
    with links:
        st.subheader("💪 Sterke punten")
        for p in analyse.sterke_punten:
            st.markdown(f"- {p}")
    with rechts:
        st.subheader("🎯 Verbeterpunten")
        for v in analyse.verbeterpunten:
            st.markdown(f"- {v}")

    st.info(analyse.samenvatting)

elif analyse_knop and not cv_bestand:
    st.warning("Upload eerst je CV (een .txt-bestand).")

elif analyse_knop and not vacature_tekst:
    st.warning("Plak eerst de vacature-tekst.")