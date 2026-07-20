from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent
BROCHURE_PATH = BASE_DIR / "data" / "company_brochure.txt"


def retrieve_context(customer_query: str) -> str:
    """
    Retrieves relevant company information for the customer's query.

    For now, since we only have one brochure, we return the entire brochure.
    This can later be replaced with keyword search or vector search.
    """

    try:
        return BROCHURE_PATH.read_text(encoding="utf-8")

    except FileNotFoundError:
        return (
            "Company brochure could not be found. "
            "Please contact the administrator."
        )