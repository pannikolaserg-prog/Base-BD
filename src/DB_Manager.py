from typing import List, Optional, Tuple

import psycopg2


class DBManager:
    def __init__(self, db_name: str, user: str, password: str) -> None:
        self.conn = psycopg2.connect(
            host="localhost",
            database=db_name,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

    def create_tables(self) -> None:
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS vacancies;
            DROP TABLE IF EXISTS companies;

            CREATE TABLE companies (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            );

            CREATE TABLE vacancies (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                url VARCHAR(255),
                company_id INTEGER REFERENCES companies(id)
            );
        """
        )
        self.conn.commit()

    def insert_company(self, id: int, name: str) -> None:
        """Добавление компании в БД"""
        self.cursor.execute(
            "INSERT INTO companies (id, name) VALUES (%s, %s)",
            (id, name)
        )
        self.conn.commit()

    def insert_vacancy(
        self,
        id: int,
        name: str,
        salary_from: Optional[int],
        salary_to: Optional[int],
        url: str,
        company_id: int
    ) -> None:
        """Добавление вакансии в БД"""
        self.cursor.execute(
            """
            INSERT INTO vacancies (id, name, salary_from, salary_to, url, company_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (id, name, salary_from, salary_to, url, company_id),
        )
        self.conn.commit()

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании
        """
        self.cursor.execute("""
            SELECT c.name, COUNT(v.id)
            FROM companies c
            LEFT JOIN vacancies v ON c.id = v.company_id
            GROUP BY c.name
        """)
        return self.cursor.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """
        Получает список всех вакансий
        """
        self.cursor.execute("""
            SELECT c.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
        """)
        return self.cursor.fetchall()

    def get_avg_salary(self) -> float:
        self.cursor.execute("""
            SELECT AVG(
                CASE
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                        THEN (salary_from + salary_to) / 2
                    WHEN salary_from IS NOT NULL THEN salary_from
                    WHEN salary_to IS NOT NULL THEN salary_to
                END
            )
            FROM vacancies
        """)
        result = self.cursor.fetchone()
        if result is None or result[0] is None:
            return 0.0
        return round(result[0], 2)

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """
        Получает список вакансий с зарплатой выше средней
        """
        avg = self.get_avg_salary()
        self.cursor.execute(
            """
            SELECT c.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            WHERE COALESCE(v.salary_from, v.salary_to, 0) > %s
            """,
            (avg,),
        )
        return self.cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """
        Получает список вакансий по ключевому слову в названии
        """
        self.cursor.execute(
            """
            SELECT c.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            WHERE v.name ILIKE %s
            """,
            (f"%{keyword}%",),
        )
        return self.cursor.fetchall()

    def close(self) -> None:
        """Закрытие соединения с БД"""
        self.cursor.close()
        self.conn.close()
