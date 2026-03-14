from typing import Any, Dict, List, cast

import requests


def get_company(company_id: int) -> Dict[str, Any]:
    """Получение информации о компании"""
    url = f"https://api.hh.ru/employers/{company_id}"
    response = requests.get(url)
    response.raise_for_status()
    return cast(Dict[str, Any], response.json())


def get_vacancies(company_id: int) -> List[Dict[str, Any]]:
    """Получение вакансий компании"""
    url = "https://api.hh.ru/vacancies"
    params = {"employer_id": company_id, "per_page": 20}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return cast(List[Dict[str, Any]], data.get("items", []))
