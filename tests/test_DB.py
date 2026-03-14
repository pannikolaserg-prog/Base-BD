import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, patch
from src.DB_Manager import DBManager


def test_create_database_called():
    """Тест что метод create_database существует"""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db = DBManager("test_db", "test_user", "test_pass")

        assert hasattr(db, 'create_database')
        assert mock_connect.called


def test_create_database_handles_error():
    """Тест что метод не падает при ошибке"""
    with patch('psycopg2.connect') as mock_connect:
        # Важно! Первый вызов (к postgres) падает, второй (к test_db) работает
        mock_connect.side_effect = [
            Exception("Any error"),  # первый вызов - create_database
            MagicMock()  # второй вызов - __init__
        ]

        # Должно работать без исключений
        db = DBManager("test_db", "test_user", "test_pass")
        assert db is not None


@pytest.fixture
def db():
    """Фикстура с правильной настройкой моков"""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Важно! reset_mock после создания
        db = DBManager("test_db", "test_user", "test_pass")
        db.cursor = mock_cursor
        db.conn = mock_conn

        # Сбрасываем счетчики вызовов после __init__
        mock_cursor.reset_mock()
        mock_conn.reset_mock()

        return db


def test_close_connection(db):
    """Тест закрытия соединения"""
    db.close()

    db.cursor.close.assert_called_once()
    db.conn.close.assert_called_once()


def test_get_companies_and_vacancies_count_empty(db):
    """Тест получения компаний когда их нет"""
    db.cursor.fetchall.return_value = []

    # Сбрасываем execute перед тестом
    db.cursor.execute.reset_mock()

    result = db.get_companies_and_vacancies_count()

    assert result == []
    db.cursor.execute.assert_called_once()


def test_get_all_vacancies_empty(db):
    """Тест получения всех вакансий когда их нет"""
    db.cursor.fetchall.return_value = []

    db.cursor.execute.reset_mock()

    result = db.get_all_vacancies()

    assert result == []
    db.cursor.execute.assert_called_once()


def test_insert_vacancy_with_none(db):
    """Тест вставки вакансии с None значениями"""
    db.cursor.execute.reset_mock()
    db.conn.commit.reset_mock()

    db.insert_vacancy(
        id=101,
        name="Стажер",
        salary_from=None,
        salary_to=None,
        url="https://hh.ru/101",
        company_id=1
    )

    db.cursor.execute.assert_called_once()
    db.conn.commit.assert_called_once()


def test_get_vacancies_with_keyword_empty(db):
    """Тест поиска по ключевому слову без результатов"""
    db.cursor.fetchall.return_value = []

    db.cursor.execute.reset_mock()

    result = db.get_vacancies_with_keyword("nosql")

    assert result == []
    db.cursor.execute.assert_called_once()


# Эти тесты работают без изменений
def test_get_vacancies_with_higher_salary(db):
    """Тест вакансий с з/п выше средней"""
    db.cursor.fetchone.return_value = (100000,)
    mock_results = [
        ("Яндекс", "Senior Python", 150000, 200000, "url1"),
        ("Сбер", "Team Lead", 250000, 300000, "url2")
    ]
    db.cursor.fetchall.return_value = mock_results

    result = db.get_vacancies_with_higher_salary()

    assert len(result) == 2
    assert result[0][1] == "Senior Python"


def test_get_avg_salary_with_none(db):
    """Тест средней зарплаты когда нет данных"""
    db.cursor.fetchone.return_value = (None,)

    result = db.get_avg_salary()

    assert result == 0.0
