import requests_mock
from src.API_connect import get_company, get_vacancies


def test_get_company():
    """Тест получения компании"""
    with requests_mock.Mocker() as m:
        m.get("https://api.hh.ru/employers/1740", json={"id": 1740, "name": "Яндекс"})

        result = get_company(1740)

        assert result["id"] == 1740
        assert result["name"] == "Яндекс"


def test_get_vacancies():
    """Тест получения вакансий"""
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.hh.ru/vacancies",
            json={"items": [{"id": 1, "name": "Python Dev"}]}
        )

        result = get_vacancies(1740)

        assert len(result) == 1
        assert result[0]["name"] == "Python Dev"