"""
app.py
──────
Interface Streamlit — Observatoire Économique France
Connectée au workflow n8n (Agent 1 → MCP SIRENE → Agent 2)

Lancement :
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Observatoire Économique — France",
    page_icon="🏛",
    layout="wide",
    initial_sidebar_state="expanded"
)

WEBHOOK_URL = "http://localhost:5678/webhook/sirene-mcp-agent"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.stApp { background: #0f1117; color: #e8eaf0; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

section[data-testid="stSidebar"] {
    background: #161822 !important;
    border-right: 1px solid #1e2130;
}
section[data-testid="stSidebar"] * { color: #c5c9d8 !important; }

.hero {
    background: linear-gradient(135deg, #161c2d 0%, #0f1117 60%, #0d1520 100%);
    border: 1px solid #1e2845;
    border-radius: 24px;
    padding: 36px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: #3b82f6; margin-bottom: 12px;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem; color: #f0f2f8;
    line-height: 1.15; margin-bottom: 10px;
}
.hero-sub { font-size: 1rem; color: #7a8099; margin-bottom: 18px; }
.hero-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.tag {
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.25);
    color: #93c5fd; border-radius: 999px;
    padding: 5px 12px; font-size: 0.75rem; font-weight: 500;
}
.section-label {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #4b5380;
    margin-bottom: 14px; margin-top: 6px;
}
.kpi-card {
    background: #161822; border: 1px solid #1e2130;
    border-radius: 20px; padding: 22px 24px;
}
.kpi-icon { font-size: 1.4rem; margin-bottom: 12px; }
.kpi-label { font-size: 0.78rem; color: #555c7a; margin-bottom: 6px; }
.kpi-val { font-size: 2.1rem; font-weight: 700; color: #f0f2f8; line-height: 1; }
.kpi-sub { font-size: 0.8rem; color: #3b82f6; margin-top: 8px; font-weight: 500; }
.insight-box {
    background: #111827; border: 1px solid #1e2845;
    border-left: 5px solid #3b82f6; border-radius: 16px;
    padding: 24px 28px; margin-bottom: 28px; line-height: 1.75;
}
.insight-header {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #3b82f6; margin-bottom: 12px;
}
.insight-text { color: #c5c9d8; font-size: 0.97rem; }
.params-box {
    background: #0d1520; border: 1px solid #1e2845;
    border-left: 5px solid #6366f1; border-radius: 12px;
    padding: 16px 20px; margin-bottom: 20px;
    font-size: 0.85rem; color: #818cf8;
}
.chart-wrap {
    background: #161822; border: 1px solid #1e2130;
    border-radius: 20px; padding: 20px 20px 10px; margin-bottom: 18px;
}
.stButton > button {
    background: #2563eb !important; color: #fff !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.65rem 1.1rem !important; font-weight: 600 !important;
    width: 100% !important;
}
.stButton > button:hover { background: #1d4ed8 !important; }
.stTextInput > div > div > input {
    background: #161822 !important; border: 1px solid #1e2130 !important;
    border-radius: 12px !important; color: #e8eaf0 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
.stTabs [data-baseweb="tab"] {
    background: #161822 !important; border-radius: 10px 10px 0 0 !important;
    color: #7a8099 !important; border: 1px solid #1e2130 !important;
}
.stTabs [aria-selected="true"] {
    background: #1a2540 !important; color: #93c5fd !important;
    font-weight: 600 !important;
}
.pill-ok {
    display: inline-block; background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.3); color: #34d399;
    border-radius: 999px; padding: 4px 12px;
    font-size: 0.75rem; font-weight: 600;
}
.pill-ia {
    display: inline-block; background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3); color: #818cf8;
    border-radius: 999px; padding: 4px 12px;
    font-size: 0.75rem; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers graphiques ─────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c5c9d8", family="DM Sans"),
    margin=dict(l=10, r=10, t=30, b=20)
)
BLUE_SCALE = [[0.0,"#0d1a3a"],[0.33,"#1d4ed8"],[0.66,"#3b82f6"],[1.0,"#93c5fd"]]

def chart_bar(data, titre=""):
    if not data: return go.Figure()
    df = pd.DataFrame(data).sort_values("value", ascending=True)
    fig = px.bar(df, x="value", y="label", orientation="h",
                 text="value", color="value",
                 color_continuous_scale=BLUE_SCALE, title=titre)
    fig.update_traces(textposition="outside", textfont_color="#c5c9d8")
    fig.update_layout(**PLOTLY_LAYOUT, height=420, coloraxis_showscale=False,
                      xaxis_title="Nombre d'entreprises", yaxis_title="")
    fig.update_xaxes(showgrid=True, gridcolor="#1e2130")
    return fig

def chart_treemap(data, titre=""):
    if not data: return go.Figure()
    df = pd.DataFrame(data)
    fig = px.treemap(df, path=["label"], values="value",
                     color="value", color_continuous_scale=BLUE_SCALE, title=titre)
    fig.update_layout(**PLOTLY_LAYOUT, height=440, coloraxis_showscale=False)
    return fig

def chart_pie(data, titre=""):
    if not data: return go.Figure()
    df = pd.DataFrame(data)
    fig = px.pie(df, names="label", values="value", hole=0.52, title=titre,
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_layout(**PLOTLY_LAYOUT, height=420)
    return fig

def call_webhook(question: str) -> dict:
    r = requests.post(WEBHOOK_URL, json={"question": question}, timeout=120)
    r.raise_for_status()
    return r.json()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏛 Observatoire")
    st.markdown("<span class='pill-ok'>n8n actif</span> &nbsp; <span class='pill-ia'>Ollama llama3.1</span>",
                unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Architecture**")
    st.caption("🌐 Streamlit → n8n Webhook")
    st.caption("🤖 Agent 1 → Extraction JSON")
    st.caption("🔌 MCP → API SIRENE")
    st.caption("🤖 Agent 2 → Analyse textuelle")
    st.markdown("---")
    st.markdown("**Exemples de questions**")
    suggestions = [
        "Combien d'entreprises de transport en France ?",
        "Top secteurs tech à Paris ?",
        "Répartition des entreprises de santé par département",
        "Entreprises de conseil en Île-de-France",
        "Startups numériques en Gironde (33) ?",
        "Part des restaurants en France ?",
        "Top communes avec des entreprises de finance ?",
        "Entreprises de construction en Rhône (69) ?",
    ]
    for i, s in enumerate(suggestions):
        if st.button(s, key=f"sug_{i}"):
            st.session_state["question_input"] = s
    st.markdown("---")
    webhook_url = st.text_input("Webhook URL", value=WEBHOOK_URL)
    st.caption("Modifie si ton port n8n est différent")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">Open Data SIRENE · IA Agentique · MCP · Ollama</div>
  <div class="hero-title">Observatoire Économique<br>de la France</div>
  <div class="hero-sub">
    Posez une question en langage naturel. L'Agent 1 extrait les paramètres,
    le MCP interroge la base SIRENE, l'Agent 2 analyse les résultats.
  </div>
  <div class="hero-tags">
    <span class="tag">🤖 2 Agents IA</span>
    <span class="tag">🔌 Protocole MCP</span>
    <span class="tag">📊 Visualisation adaptative</span>
    <span class="tag">🗺 Toute la France</span>
    <span class="tag">⚡ Ollama local</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Zone question ─────────────────────────────────────────────────────────────
col_q, col_btn = st.columns([6, 1])
with col_q:
    default_q = st.session_state.get("question_input",
                                      "Combien d'entreprises de transport en France ?")
    question = st.text_input("q", value=default_q,
                             placeholder="Ex. : Quelles entreprises tech sont à Paris ?",
                             label_visibility="collapsed")
with col_btn:
    st.write("")
    run = st.button("Analyser →")

st.markdown("<br>", unsafe_allow_html=True)

# ── Traitement ────────────────────────────────────────────────────────────────
if run and question.strip():

    with st.spinner("Agent 1 analyse la question… MCP interroge SIRENE… Agent 2 rédige l'analyse…"):
        try:
            data = call_webhook(question)
        except requests.exceptions.ConnectionError:
            st.error("❌ Impossible de joindre n8n. Vérifie que le workflow est actif sur localhost:5678")
            st.stop()
        except requests.exceptions.Timeout:
            st.error("⏱ Timeout — n8n ou Ollama met trop de temps à répondre.")
            st.stop()
        except Exception as e:
            st.exception(e)
            st.stop()

    analyse   = data.get("analyse", "Analyse non disponible.")
    kpi       = data.get("kpi", {})
    viz       = data.get("viz", {})
    params_ia = data.get("params_ia", {})
    top_depts = data.get("top_departements", [])
    top_ape   = data.get("top_secteurs", [])
    top_com   = data.get("top_communes", [])
    secteur   = data.get("secteur", "")
    zone_label= data.get("zone_label", "France")
    type_g    = viz.get("type_graphique", "bar")

    # ── Paramètres IA (transparence MCP) ──────────────────────────────────
    st.markdown("<div class='section-label'>Paramètres extraits par l'Agent 1 (MCP)</div>",
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="params-box">
        🤖 <b>Secteur :</b> {params_ia.get('secteur','—')} &nbsp;|&nbsp;
        🗺 <b>Zone :</b> {params_ia.get('zone_label','—')} &nbsp;|&nbsp;
        📊 <b>Graphique choisi :</b> {params_ia.get('type_graphique','—')} &nbsp;|&nbsp;
        ❓ <b>Type question :</b> {params_ia.get('type_question','—')} &nbsp;|&nbsp;
        🔢 <b>Top N :</b> {params_ia.get('top_n','—')}
    </div>
    """, unsafe_allow_html=True)

    # ── KPI ────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Indicateurs clés</div>",
                unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">🏢</div>
            <div class="kpi-label">Entreprises trouvées</div>
            <div class="kpi-val">{kpi.get('n_total', 0)}</div>
            <div class="kpi-sub">{zone_label}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">🗺</div>
            <div class="kpi-label">Départements</div>
            <div class="kpi-val">{kpi.get('n_departements', 0)}</div>
            <div class="kpi-sub">représentés</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">🏆</div>
            <div class="kpi-label">Département leader</div>
            <div class="kpi-val" style="font-size:1.3rem">{kpi.get('top_dept_nom','—')}</div>
            <div class="kpi-sub">{kpi.get('top_dept_nb', 0)} entreprises</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">⚙</div>
            <div class="kpi-label">Secteur APE dominant</div>
            <div class="kpi-val" style="font-size:0.95rem;line-height:1.3">{kpi.get('top_ape_label','—')}</div>
            <div class="kpi-sub">{kpi.get('top_ape_nb', 0)} entreprises</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Analyse IA ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Analyse de l'Agent 2</div>",
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-header">🤖 Synthèse — Agent 2 (Ollama llama3.1:8b)</div>
        <div class="insight-text">{analyse}</div>
    </div>""", unsafe_allow_html=True)

    # ── Visualisations ─────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Visualisations</div>",
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Par département",
        "🌳 Secteurs APE",
        "🍕 Répartition",
        "🏙 Communes",
        "📋 Données brutes"
    ])

    with tab1:
        st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
        bar_data = viz.get("bar", {}).get("data", [])
        if bar_data:
            fig = chart_bar(bar_data, viz.get("bar", {}).get("titre", ""))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas de données de département disponibles.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
        tree_data = viz.get("treemap", {}).get("data", [])
        if tree_data:
            fig = chart_treemap(tree_data, viz.get("treemap", {}).get("titre", ""))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas de données de secteur disponibles.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        col_a, col_b = st.columns([3, 2])
        with col_a:
            st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
            pie_data = viz.get("pie", {}).get("data", [])
            if pie_data:
                fig = chart_pie(pie_data, viz.get("pie", {}).get("titre", ""))
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col_b:
            if top_depts:
                total = sum(d["nb_entreprises"] for d in top_depts)
                st.markdown("**Part par département**")
                for d in top_depts:
                    pct = round(d["nb_entreprises"] / total * 100, 1) if total else 0
                    st.markdown(f"**{d.get('nom', d['departement'])}** — {pct}% ({d['nb_entreprises']})")

    with tab4:
        st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
        com_data = viz.get("commune", {}).get("data", [])
        if com_data:
            fig = chart_bar(com_data, viz.get("commune", {}).get("titre", "Top communes"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas de données de commune disponibles.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab5:
        entreprises = data.get("entreprises", [])
        if not entreprises:
            # Reconstruit depuis top_depts si pas d'entreprises individuelles
            st.info("Affichage des statistiques agrégées.")
            df_agg = pd.DataFrame(top_depts).rename(columns={
                "departement": "Code", "nom": "Département",
                "nb_entreprises": "Nb entreprises"
            })
            st.dataframe(df_agg, use_container_width=True, hide_index=True)
        else:
            df = pd.DataFrame(entreprises)
            cols = [c for c in ["nom","commune","dept_nom","activite_label",
                                  "code_postal","effectif","siren"] if c in df.columns]
            st.dataframe(df[cols].rename(columns={
                "nom": "Nom", "commune": "Commune", "dept_nom": "Département",
                "activite_label": "Secteur", "code_postal": "CP",
                "effectif": "Effectif", "siren": "SIREN"
            }), use_container_width=True, hide_index=True)

    # JSON brut
    with st.expander("🔧 JSON brut — réponse complète de n8n"):
        st.json(data)

elif run and not question.strip():
    st.warning("Saisis une question avant de lancer l'analyse.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Observatoire Économique · n8n · Ollama llama3.1:8b · MCP · API SIRENE · Streamlit")
