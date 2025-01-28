import csv

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from constants import (BASE_DIR, DATE_TODAY, MAX_BORDER_SALARY,
                       MIN_BORDER_SALARY, RESULS_DIR)
from db import Requirement, Vacancy, session, vacancy_requirement_table

# Задаем имя файла CSV для сохранения требований
report_file = BASE_DIR / RESULS_DIR / f'junior_reqirements_top_{DATE_TODAY}.csv'  # noqa

# Задаем имя файла CSV для сохранения зарплат
salary_file = BASE_DIR / RESULS_DIR / f'junior_salary_data_{DATE_TODAY}.csv'  # noqa

salary_file_v2 = BASE_DIR / RESULS_DIR / f'junior_salary_data_v2_{DATE_TODAY}.csv'  # noqa


# Создаем запрос к базе данных, который выбирает название требования и количество связей  # noqa
# между требованием и вакансиями
all_query = session.query(Requirement.name, func.count(vacancy_requirement_table.c.vacancy_id).label('count')) \
    .join(vacancy_requirement_table, Requirement.id == vacancy_requirement_table.c.requirement_id) \
    .group_by(Requirement.name)  # noqa


def get_junior_query_requirements(
        session: Session,
        percent_cutoff: int = 5):
    """ Возвращает список, списков по убыванию int(процент),
    в формате list[list[str,int]]
    """
    junior_vacancy_count = session.query(func.count(Vacancy.id)) \
        .filter(
            or_(
                Vacancy.vac_exp == '1–3 года',
                Vacancy.vac_exp == 'не требуется'
            )
        ) \
        .scalar()

    junior_query = session.query(Requirement.name, func.count(vacancy_requirement_table.c.vacancy_id).label('count')) \
        .join(vacancy_requirement_table, Requirement.id == vacancy_requirement_table.c.requirement_id) \
        .join(Vacancy, Vacancy.id == vacancy_requirement_table.c.vacancy_id) \
        .filter(  # noqa
            or_(
                Vacancy.vac_exp == '1–3 года',
                Vacancy.vac_exp == 'не требуется'
            )
        ) \
        .group_by(Requirement.name).all()
    # Сортируем список кортежей по убыванию второго элемента
    sorted_junior_query = sorted(
        junior_query,
        key=lambda x: x[1],
        reverse=True)
    # формирую список списков
    return [[requirement, f'{count/junior_vacancy_count*100:.0f}'] for requirement, count in sorted_junior_query if count/junior_vacancy_count*100 >= percent_cutoff] # noqa


# Запрос на получение данных для зарплаты
def get_junior_salary(session: Session):
    """ Получаю query по зарплате в виде кортежа,
    формата tuple[str, int|None, int|None].
    """
    return session.query(Vacancy.vac_name, Vacancy.vac_salary_min, Vacancy.vac_salary_max) \
        .filter(  # noqa
            or_(
                Vacancy.vac_exp == '1–3 года',
                Vacancy.vac_exp == 'не требуется'
                )
        ).filter(
            or_(
                Vacancy.vac_salary_min.isnot(None),
                Vacancy.vac_salary_max.isnot(None)
                )
        ).all()


def normalize_salary(data,
                     min_border: int = MIN_BORDER_SALARY,
                     max_border: int = MAX_BORDER_SALARY):
    """ обрабатываю мин и макс показатели,
    получаю среднюю сумму для дальнейшей обработки.
    """
    salary = None
    salary_data = []
    for name, low, high in data:
        if low and high:
            salary = round((low + high)/2)
        elif low:
            salary = round(low + low * 0.10)
        elif high:
            salary = high
        if salary >= min_border and salary <= max_border:
            salary_data.append([name, salary])
    return sorted(salary_data, key=lambda x: x[1])


def avarage_salary(normalized_data,
                   border_persent: int = 0):
    """ Считаем среднюю зп на джуна,
    срезав крайние точки, если задано.
    """
    if border_persent:
        possible_error = round(len(normalized_data)*border_persent)
        normalized_data = normalized_data[possible_error:-possible_error]
    total = 0
    for _, salary in normalized_data:
        total += salary
    return round(total/len(normalized_data))


# Записываем в файл результаты по требования/процент популярности
with open(report_file, 'w', newline='') as file:
    writer = csv.writer(file)
    # Записываем заголовки, если необходимо
    writer.writerow(['Requirement', 'Percentage'])
    # Записываем данные
    # writer.writerows(percent_data)
    writer.writerows(
        get_junior_query_requirements(session))
print(f'Результаты сохранены в файл {report_file}')


# Записываем в файл результаты вакансий с зарплатами
with open(salary_file_v2, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    salary_data = normalize_salary(
        get_junior_salary(session)
    )
    writer.writerow(
        ['Vacancy count analized', len(salary_data)]
    )
    writer.writerow(
        ['Lower border normalize salary',
         MIN_BORDER_SALARY]
    )
    writer.writerow(
        ['Upper border normalize salary',
         MAX_BORDER_SALARY]
    )
    writer.writerow(
        ['Average junior salary (1-3 year exp)',
         avarage_salary(salary_data)]
    )
    writer.writerow(['**************************************'])
    writer.writerow(['Name', 'Salary'])
    writer.writerows(salary_data)

print(f'Результаты сохранены в файл {salary_file_v2}')
