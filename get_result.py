from sqlalchemy import func
from db import session, Requirement, vacancy_requirement_table, Vacancy
from sqlalchemy import or_
import csv
from constants import DATE_TODAY, BASE_DIR, RESULS_DIR


all_vacancy_count = session.query(func.count(Vacancy.id)).scalar()
all_requirement_count = session.query(func.count(Requirement.id)).scalar()

junior_vacancy_count = session.query(func.count(Vacancy.id)) \
    .filter(
        or_(
            Vacancy.vac_exp == '1–3 года',
            Vacancy.vac_exp == 'не требуется'
            )
    ) \
    .scalar()


# Создаем запрос к базе данных, который выбирает название требования и количество связей  # noqa
# между требованием и вакансиями
all_query = session.query(Requirement.name, func.count(vacancy_requirement_table.c.vacancy_id).label('count')) \
    .join(vacancy_requirement_table, Requirement.id == vacancy_requirement_table.c.requirement_id) \
    .group_by(Requirement.name)  # noqa


# Создаем запрос к базе данных, который выбирает название требования и количество связей  # noqa
# между требованием и вакансиями, где значение vac_exp равно 'от 1 до 3' или 'без опыта'  # noqa
junior_query = session.query(Requirement.name, func.count(vacancy_requirement_table.c.vacancy_id).label('count')) \
    .join(vacancy_requirement_table, Requirement.id == vacancy_requirement_table.c.requirement_id) \
    .join(Vacancy, Vacancy.id == vacancy_requirement_table.c.vacancy_id) \
    .filter(  # noqa
        or_(
            Vacancy.vac_exp == '1–3 года',
            Vacancy.vac_exp == 'не требуется'
            )
    ) \
    .group_by(Requirement.name)  # noqa

# Используем запрос для получения результата в виде списка кортежей
result = all_query.all()
result_junior = junior_query.all()
# Сортируем список кортежей по убыванию второго элемента
result_junior_sorted = sorted(result_junior, key=lambda x: x[1], reverse=True)

# percent_data = [[requirement, f'{count/junior_vacancy_count*100:.0f}%'] for requirement, count in result_junior_sorted if count/junior_vacancy_count*100 >= 10]  # noqa
percent_data = [[requirement, f'{count/junior_vacancy_count*100:.0f}'] for requirement, count in result_junior_sorted if count/junior_vacancy_count*100 >= 10]
# Задаем имя файла CSV для сохранения
report_file = BASE_DIR / RESULS_DIR / f'junior_reqirements_top_{DATE_TODAY}.csv'  # noqa

# Записываем результаты в файл CSV
with open(report_file, 'w', newline='') as file:
    writer = csv.writer(file)
    # Записываем заголовки, если необходимо
    writer.writerow(['Requirement', 'Percentage'])
    # Записываем данные
    writer.writerows(percent_data)

print(f'Результаты сохранены в файл {report_file}')
