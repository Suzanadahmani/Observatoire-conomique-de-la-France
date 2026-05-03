# Observatoire Économique de la France
**Interrogation en langage naturel de la base SIRENE via agents IA et protocole MCP**

Projet réalisé dans le cadre du Master 1 CSSD — Cybersécurité et Science des Données, Université Paris 8.

---

## Description

Application permettant d'interroger la base **SIRENE** (11 millions d'entreprises françaises, INSEE) en posant une question en français. Deux agents IA analysent la question, interrogent l'API via un serveur MCP Python, calculent des statistiques et génèrent une analyse textuelle avec visualisations automatiques.

**Exemples de questions :**
- *"Combien d'entreprises de tech sur Paris ?"*
- *"Répartition des restaurants en Île-de-France ?"*
- *"Top secteurs à Lyon ?"*
- *"Finance à Bordeaux ?"*

---

## Architecture

```
Question (français)
        ↓
  Streamlit — Interface utilisateur
        ↓ HTTP POST
   n8n Webhook
        ↓
  Agent 1 — Extraction d'intention
  (Groq / Llama-3.1-8b, température = 0)
        ↓ JSON structuré
  Client MCP JavaScript (n8n)
        ↓ JSON-RPC 2.0
  Serveur MCP Python — FastMCP (port 8000)
        ↓ API SIRENE (api.gouv.fr)
  Agent 2 — Analyse textuelle
  (Groq / Llama-3.1-8b, température = 0.3)
        ↓
  Assemblage final → Streamlit + Plotly
```

### 3 outils MCP exposés

| Outil | Rôle |
|---|---|
| `search_companies` | Recherche dans SIRENE (4 pages × 25 = 100 résultats) |
| `filter_by_geography` | Filtre par zone géographique |
| `compute_statistics` | Calcule top départements, APE, communes |

### 5 visualisations Plotly

| Onglet | Type |
|---|---|
| Départements | Barres horizontales |
| Secteurs APE | Treemap |
| Répartition | Camembert (donut) |
| Communes | Barres horizontales |
| Données | Tableau interactif |

---

## Structure du projet

```
observatoire-economique-sirene/
├── mcp_sirene_server_v2.py   # Serveur MCP Python (FastMCP, 3 outils)
├── app.py                    # Interface Streamlit + visualisations Plotly
├── Dataviz.json              # Workflow n8n complet (importable directement)
├── requirements.txt          # Dépendances Python
└── README.md
```

---

## Installation

```bash
# 1. Cloner le repo
git clone https://github.com/Suzanadahmani/observatoire-economique-sirene.git
cd observatoire-economique-sirene

# 2. Installer les dépendances Python
pip install -r requirements.txt
```

**Prérequis :**
- Python 3.10+
- n8n installé localement — `npm install -g n8n`
- Compte Groq gratuit → [console.groq.com](https://console.groq.com)

---

## Lancement

```bash
# Terminal 1 — Serveur MCP Python
python mcp_sirene_server_v2.py


# Terminal 2 — Interface Streamlit
streamlit run app.py

```


---

## Limites

- 100 résultats max par requête (échantillon — pas toute la base)
- Codes APE parfois imprécis (une startup tech peut avoir l'APE "conseil")
- Quota Groq sur le plan gratuit
- Le serveur MCP doit être lancé manuellement avant chaque session

---
