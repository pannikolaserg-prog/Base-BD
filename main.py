from src.DB_Manager import DBManager, get_company, get_vacancies

def main():
    # 10 компаний с hh.ru
    companies = [
        1740,  # Яндекс
        3529,  # Сбер
        15478,  # VK
        2180,  # Ozon
        3776,  # МТС
        87021,  # Wildberries
        3127,  # Мегафон
        2748,  # Ростелеком
        4233,  # Билайн
        78638  # Тинькофф
    ]

    # Подключение к БД (измени пароль!)
    db = DBManager('hh_db', 'postgres', 'your_password')

    try:
        db.create_tables()

        for company_id in companies:
            print(f"\nЗагрузка компании {company_id}...")

            # Компания
            data = get_company(company_id)
            db.insert_company(data['id'], data['name'])
            print(f"  + {data['name']}")

            # Вакансии
            vacancies = get_vacancies(company_id)
            for vac in vacancies:
                salary = vac.get('salary')
                salary_from = salary.get('from') if salary else None
                salary_to = salary.get('to') if salary else None

                db.insert_vacancy(
                    vac['id'],
                    vac['name'],
                    salary_from,
                    salary_to,
                    vac.get('alternate_url', ''),
                    company_id
                )
            print(f"  + {len(vacancies)} вакансий")

        # Примеры запросов
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТЫ")
        print("=" * 50)

        print("\n1. Компании и количество вакансий:")
        for name, count in db.get_companies_and_vacancies_count():
            print(f"  {name}: {count}")

        print(f"\n2. Средняя зарплата: {db.get_avg_salary()} руб.")

        print("\n3. Вакансии с Python:")
        for company, name, frm, to, url in db.get_vacancies_with_keyword('python')[:5]:
            salary = f"{frm or ''} - {to or ''}".strip(' -') or 'не указана'
            print(f"  {company}: {name} ({salary})")

    finally:
        db.close()


if __name__ == "__main__":
    main()