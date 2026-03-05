import psycopg2


class DBManager:
    def __init__(self, db_name, user, password):
        self.conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="Base_2026"
        )
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute("""
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
        """)
        self.conn.commit()

    def insert_company(self, id, name):
        self.cursor.execute(
            "INSERT INTO companies (id, name) VALUES (%s, %s)",
            (id, name)
        )
        self.conn.commit()

    def insert_vacancy(self, id, name, salary_from, salary_to, url, company_id):
        self.cursor.execute("""
            INSERT INTO vacancies (id, name, salary_from, salary_to, url, company_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id, name, salary_from, salary_to, url, company_id))
        self.conn.commit()

    def get_companies_and_vacancies_count(self):
        self.cursor.execute("""
            SELECT c.name, COUNT(v.id)
            FROM companies c
            LEFT JOIN vacancies v ON c.id = v.company_id
            GROUP BY c.name
        """)
        return self.cursor.fetchall()

    def get_all_vacancies(self):
        self.cursor.execute("""
            SELECT c.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
        """)
        return self.cursor.fetchall()

    def get_avg_salary(self):
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
        return round(self.cursor.fetchone()[0] or 0, 2)

    def get_vacancies_with_higher_salary(self):
        avg = self.get_avg_salary()
        self.cursor.execute("""
            SELECT c.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            WHERE COALESCE(v.salary_from, v.salary_to, 0) > %s
        """, (avg,))
        return self.cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        self.cursor.execute("""
            SELECT c.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            WHERE v.name ILIKE %s
        """, (f'%{keyword}%',))
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

