import pytest
from unittest.mock import MagicMock, patch
from src.DB_Manager import DBManager


@pytest.fixture
def db():
    """Фикстура с правильной настройкой моков"""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db = DBManager("test_db", "test_user", "test_pass")
        db.cursor = mock_cursor
        db.conn = mock_conn
        return db


def test_close_connection(db):
    """Тест закрытия соединения"""
    db.close()

    db.cursor.close.assert_called_once()
    db.conn.close.assert_called_once()


def test_get_companies_and_vacancies_count_empty(db):
    """Тест получения компаний когда их нет"""
    # Настраиваем возвращаемое значение
    db.cursor.fetchall.return_value = []

    result = db.get_companies_and_vacancies_count()

    assert result == []
    db.cursor.execute.assert_called_once()  # Проверяем что запрос был


def test_get_all_vacancies_empty(db):
    """Тест получения всех вакансий когда их нет"""
    db.cursor.fetchall.return_value = []

    result = db.get_all_vacancies()

    assert result == []
    db.cursor.execute.assert_called_once()


def test_get_vacancies_with_higher_salary(db):
    """Тест вакансий с з/п выше средней"""
    # Сначала для get_avg_salary
    db.cursor.fetchone.return_value = (100000,)

    # Потом для основного запроса
    mock_results = [
        ("Яндекс", "Senior Python", 150000, 200000, "url1"),
        ("Сбер", "Team Lead", 250000, 300000, "url2")
    ]
    db.cursor.fetchall.return_value = mock_results

    result = db.get_vacancies_with_higher_salary()

    assert len(result) == 2
    assert result[0][1] == "Senior Python"
    assert result[1][1] == "Team Lead"


def test_insert_vacancy_with_none(db):
    """Тест вставки вакансии с None значениями"""
    db.insert_vacancy(
        id=101,
        name="Стажер",
        salary_from=None,
        salary_to=None,
        url="https://hh.ru/101",
        company_id=1
    )

    # Проверяем что execute был вызван
    db.cursor.execute.assert_called_once()
    # Проверяем что commit был вызван
    db.conn.commit.assert_called_once()


def test_get_avg_salary_with_none(db):
    """Тест средней зарплаты когда нет данных"""
    db.cursor.fetchone.return_value = (None,)

    result = db.get_avg_salary()

    assert result == 0.0


def test_get_vacancies_with_keyword_empty(db):
    """Тест поиска по ключевому слову без результатов"""
    db.cursor.fetchall.return_value = []

    result = db.get_vacancies_with_keyword("nosql")

    assert result == []
    db.cursor.execute.assert_called_once()