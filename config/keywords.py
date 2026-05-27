# ============================================================
# config/keywords.py
# All search keyword combinations for Lagos & Abuja
# ============================================================

LAGOS_AREAS = [
    "Lekki", "Ikoyi", "Victoria Island", "VI", "Ajah", "Chevron",
    "Sangotedo", "Ikate", "Ikeja", "GRA Ikeja", "Maryland", "Gbagada",
    "Magodo", "Omole", "Ojodu Berger", "Yaba", "Surulere", "Festac",
    "Badore", "Ogombo", "Abraham Adesanya", "Ojo", "Apapa", "Satellite Town",
    "Ikorodu", "Agbara", "Arepo", "Berger", "Ketu", "Kosofe",
    "Mushin", "Oshodi", "Amuwo Odofin", "Isale Eko", "Lagos Island",
    "Ogudu", "Ojota", "Anthony", "Palm Grove", "Agege", "Alimosho",
    "Langbasa", "Ajiwe", "Addo Road", "Orchid Road", "Lafiaji",
    "Oniru", "Osapa London", "Ilasan", "Jakande", "Igbo Efon",
    "Awoyaya", "Bogije", "Lakowe", "Ibeju Lekki",
]

ABUJA_AREAS = [
    "Maitama", "Asokoro", "Wuse", "Wuse 2", "Garki", "Garki 2",
    "Gwarinpa", "Kubwa", "Lugbe", "Kuje", "Bwari", "Gwagwalada",
    "Jabi", "Utako", "Wuye", "Kado", "Nnewi", "Life Camp",
    "Katampe", "Lokogoma", "Durumi", "Apo", "Gudu", "Nbora",
    "Kabusa", "Pyakasa", "Galadimawa", "Dawaki", "Kaura",
    "Guzape", "Mabushi", "Berger", "Central Business District",
    "Kukwuaba", "Durumi 2", "Karsana", "Karmo", "Orozo",
    "Nyanya", "Karu", "Aso Drive",
]

ESTATE_KEYWORDS = [
    "gated estate",
    "residential estate",
    "estate management",
    "serviced apartments",
    "residential association",
    "smart estate",
    "luxury estate",
    "property management company",
    "estate office",
    "homeowners association",
    "residential community",
    "gated community",
    "estate developer",
    "property developer",
    "residents association",
    "estate security",
    "managed estate",
    "exclusive estate",
    "housing estate",
    "estate manager",
    "real estate management",
    "property management firm",
    "private estate",
    "upscale estate",
    "premium estate",
    "estate cooperative",
    "block of flats management",
    "serviced estate",
    "townhouse complex",
    "condominium management",
]

LUXURY_SIGNALS = [
    "luxury", "premium", "exclusive", "upscale", "elite", "high-end",
    "prestigious", "prime", "signature", "grand", "royal", "imperial",
    "platinum", "diamond", "gold", "silver", "executive", "deluxe",
    "sophisticated", "prime location", "gated", "secured",
]

TIER2_SIGNALS = [
    "estate", "serviced", "managed", "residential", "community",
    "housing", "complex", "close", "court", "crescent",
]


def generate_all_search_queries(state: str) -> list[dict]:
    """
    Generate all combinations of estate keywords × area names for a given state.
    Returns list of dicts: {"query": str, "state": str, "area": str}
    """
    areas = LAGOS_AREAS if state.lower() == "lagos" else ABUJA_AREAS
    queries = []
    for keyword in ESTATE_KEYWORDS:
        for area in areas:
            queries.append({
                "query": f"{keyword} {area}",
                "state": state,
                "area": area,
                "keyword": keyword,
            })
    return queries


def get_all_queries() -> list[dict]:
    """Get queries for all configured states."""
    all_queries = []
    for state in ["Lagos", "Abuja"]:
        all_queries.extend(generate_all_search_queries(state))
    return all_queries
