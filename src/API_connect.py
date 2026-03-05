import requests

def get_company(company_id):
    url = f"https://api.hh.ru/employers/{company_id}"
    return requests.get(url).json()


def get_vacancies(company_id):
    url = "https://api.hh.ru/vacancies"
    params = {'employer_id': company_id, 'per_page': 20}
    return requests.get(url, params=params).json().get('items', [])