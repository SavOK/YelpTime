from typing import List, Dict

from SQL import Session
from SQL import Category


def get_categries_list() -> List[Dict]:
    """ Get list of business categories 
    Returns:
        List[Dict]: list of categories
    """
    s = Session()
    q = s.query(Category)
    categories_list = []
    for c in q:
        categories_list.append({"label": c.title, "value": c.category_alias})
    s.close()
    return categories_list
