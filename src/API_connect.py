from typing import Any, Dict, List

import requests


def get_company(company_id: int) -> Dict[str, Any]:
    url = f"https://api.hh.ru/employers/{company_id}"
    response = requests.get(url)
    data: Dict[str, Any] = response.json()
    return data


def get_vacancies(company_id: int) -> List[Dict[str, Any]]:
    url = "https://api.hh.ru/vacancies"
    params = {"employer_id": company_id, "per_page": 20}
    response = requests.get(url, params=params)
    data: Dict[str, Any] = response.json()
    return data.get("items", [])
