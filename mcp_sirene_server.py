"""
mcp_sirene_server_v2.py
───────────────────────
Serveur MCP SIRENE compatible mcp 1.27.0
Expose 3 outils via HTTP Streamable

Lancement :
    python mcp_sirene_server_v2.py

URL : http://localhost:8000/mcp
"""

import json
import httpx
from mcp.server.fastmcp import FastMCP

# ── Serveur MCP ───────────────────────────────────────────────
mcp = FastMCP(
    name="sirene-mcp",
    stateless_http=True
)

# ── Constantes ────────────────────────────────────────────────
BASE_URL = "https://recherche-entreprises.api.gouv.fr"

DEPT_IDF = {"75","77","78","91","92","93","94","95"}

DEPT_NAMES = {
    "75":"Paris","77":"Seine-et-Marne","78":"Yvelines",
    "91":"Essonne","92":"Hauts-de-Seine","93":"Seine-Saint-Denis",
    "94":"Val-de-Marne","95":"Val-d'Oise",
    "01":"Ain","02":"Aisne","03":"Allier","06":"Alpes-Maritimes",
    "13":"Bouches-du-Rhône","14":"Calvados","21":"Côte-d'Or",
    "25":"Doubs","29":"Finistère","31":"Haute-Garonne",
    "33":"Gironde","34":"Hérault","35":"Ille-et-Vilaine",
    "38":"Isère","44":"Loire-Atlantique","45":"Loiret",
    "49":"Maine-et-Loire","54":"Meurthe-et-Moselle",
    "57":"Moselle","59":"Nord","62":"Pas-de-Calais",
    "63":"Puy-de-Dôme","67":"Bas-Rhin","69":"Rhône",
    "72":"Sarthe","74":"Haute-Savoie","76":"Seine-Maritime",
    "80":"Somme","83":"Var","84":"Vaucluse","85":"Vendée",
    "971":"Guadeloupe","972":"Martinique",
    "973":"Guyane","974":"La Réunion"
}

APE_LABELS = {
    "62.02A":"Conseil informatique",
    "62.01Z":"Développement logiciel",
    "71.12B":"Ingénierie & études techniques",
    "49.41A":"Transport routier fret longue distance",
    "49.41B":"Transport routier fret proximité",
    "70.22Z":"Conseil en gestion",
    "73.11Z":"Publicité & communication",
    "68.20B":"Locations immobilières",
    "56.10A":"Restauration traditionnelle",
    "86.21Z":"Médecine générale",
    "85.59B":"Formation continue",
    "55.10Z":"Hôtels",
    "65.12Z":"Assurances",
    "64.19Z":"Intermédiation bancaire",
    "69.10Z":"Activités juridiques",
    "43.21A":"Travaux électriques",
    "41.20A":"Construction maisons individuelles"
}

VALID_DEPTS = {
    "01","02","03","04","05","06","07","08","09","10",
    "11","12","13","14","15","16","17","18","19","21",
    "22","23","24","25","26","27","28","29","30","31",
    "32","33","34","35","36","37","38","39","40","41",
    "42","43","44","45","46","47","48","49","50","51",
    "52","53","54","55","56","57","58","59","60","61",
    "62","63","64","65","66","67","68","69","70","71",
    "72","73","74","75","76","77","78","79","80","81",
    "82","83","84","85","86","87","88","89","90","91",
    "92","93","94","95","971","972","973","974","976"
}

# ── Helper normalisation ──────────────────────────────────────
def dept_from_cp(cp: str) -> str | None:
    if not cp or not isinstance(cp, str):
        return None
    cp = cp.strip()
    if cp.startswith("97"):
        return cp[:3]
    return cp[:2] if len(cp) >= 2 else None

def normalize(e: dict) -> dict:
    cp   = e.get("code_postal") or e.get("siege", {}).get("code_postal", "")
    dept = dept_from_cp(cp)
    ape  = (e.get("activite_principale") or
            e.get("unite_legale", {}).get("activite_principale", ""))
    return {
        "siren":              e.get("siren", ""),
        "nom":                e.get("nom_complet") or e.get("denomination", ""),
        "code_postal":        cp,
        "commune":            (e.get("commune") or
                               e.get("siege", {}).get("libelle_commune", "")),
        "departement":        dept,
        "dept_nom":           DEPT_NAMES.get(dept, dept) if dept else "",
        "activite_principale": ape,
        "activite_label":     APE_LABELS.get(ape, ape),
        "effectif":           e.get("tranche_effectif_salarie", "")
    }

# ── OUTIL 1 : Recherche entreprises (4 pages = 100 résultats) ─
@mcp.tool()
async def search_companies(
    query: str,
    departement: str = "",
    per_page: int = 25
) -> str:
    """
    Recherche des entreprises françaises dans la base SIRENE.
    Fait 4 pages automatiquement pour retourner jusqu'à 100 résultats.

    Args:
        query: Mot-clé de recherche (ex: 'informatique', 'transport')
        departement: Code département optionnel (ex: '75', '69').
        per_page: Nombre de résultats par page (max 25)

    Returns:
        JSON avec la liste des entreprises normalisées (jusqu'à 100)
    """
    dept_clean = str(departement).strip() if departement else ""
    use_dept = dept_clean and dept_clean not in ("", "None") and dept_clean in VALID_DEPTS

    all_companies = []
    seen_sirens   = set()

    async with httpx.AsyncClient(timeout=60) as client:
        for page in range(1, 5):  # 4 pages x 25 = 100 résultats max
            params = {
                "q":        query,
                "per_page": 25,
                "page":     page
            }
            if use_dept:
                params["departement"] = dept_clean

            try:
                r = await client.get(f"{BASE_URL}/search", params=params)
                r.raise_for_status()
                data    = r.json()
                results = data.get("results", [])

                if not results:
                    break  # Plus de résultats disponibles

                for e in results:
                    company = normalize(e)
                    siren   = company.get("siren", "")
                    if siren and siren not in seen_sirens:
                        seen_sirens.add(siren)
                        all_companies.append(company)

            except Exception:
                break  # Arrête si erreur sur une page

    return json.dumps({
        "tool":        "search_companies",
        "query":       query,
        "departement": dept_clean or "tous",
        "total":       len(all_companies),
        "companies":   all_companies
    }, ensure_ascii=False)


# ── OUTIL 2 : Filtrage géographique ──────────────────────────
@mcp.tool()
def filter_by_geography(
    companies_json: str,
    zone: str = "france"
) -> str:
    """
    Filtre une liste d'entreprises par zone géographique.
    
    Args:
        companies_json: JSON string de la liste d'entreprises
        zone: 'france' = toute la France,
              'idf' = Île-de-France,
              code département ex: '75', '69', '13'
    
    Returns:
        JSON avec les entreprises filtrées
    """
    try:
        data      = json.loads(companies_json)
        companies = data.get("companies", data) if isinstance(data, dict) else data
    except Exception:
        return json.dumps({"error": "JSON invalide", "companies": []})

    z = zone.lower().strip()
    if z == "idf":
        filtered = [c for c in companies if c.get("departement") in DEPT_IDF]
    elif z == "france":
        filtered = [c for c in companies if c.get("departement")]
    else:
        filtered = [c for c in companies if c.get("departement") == z]

    return json.dumps({
        "tool":           "filter_by_geography",
        "zone":           zone,
        "total_filtered": len(filtered),
        "companies":      filtered
    }, ensure_ascii=False)


# ── OUTIL 3 : Statistiques ────────────────────────────────────
@mcp.tool()
def compute_statistics(
    companies_json: str,
    top_n: int = 10
) -> str:
    """
    Calcule des statistiques agrégées sur une liste d'entreprises.
    
    Args:
        companies_json: JSON string de la liste d'entreprises filtrées
        top_n: Nombre max de résultats dans chaque top
    
    Returns:
        JSON avec top_departements, top_secteurs, top_communes, n_total
    """
    try:
        data      = json.loads(companies_json)
        companies = data.get("companies", data) if isinstance(data, dict) else data
    except Exception:
        return json.dumps({"error": "JSON invalide"})

    dept_count:    dict = {}
    ape_count:     dict = {}
    commune_count: dict = {}

    for c in companies:
        d = c.get("departement") or "Inconnu"
        dept_count[d] = dept_count.get(d, 0) + 1

        a = c.get("activite_label") or c.get("activite_principale") or "Inconnu"
        ape_count[a] = ape_count.get(a, 0) + 1

        com = c.get("commune") or "Inconnue"
        commune_count[com] = commune_count.get(com, 0) + 1

    top_depts = sorted(
        [{"departement": k, "nom": DEPT_NAMES.get(k, k), "nb_entreprises": v}
         for k, v in dept_count.items()],
        key=lambda x: -x["nb_entreprises"]
    )[:top_n]

    top_ape = sorted(
        [{"label": k, "nb_entreprises": v} for k, v in ape_count.items()],
        key=lambda x: -x["nb_entreprises"]
    )[:top_n]

    top_communes = sorted(
        [{"commune": k, "nb_entreprises": v} for k, v in commune_count.items()],
        key=lambda x: -x["nb_entreprises"]
    )[:top_n]

    return json.dumps({
        "tool":             "compute_statistics",
        "n_total":          len(companies),
        "top_departements": top_depts,
        "top_secteurs":     top_ape,
        "top_communes":     top_communes
    }, ensure_ascii=False)


# ── Lancement ─────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("🚀 Serveur MCP SIRENE v2 démarré")
    print("   URL : http://localhost:8000/mcp")
    print("   Outils : search_companies, filter_by_geography, compute_statistics")
    
    app = mcp.streamable_http_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)