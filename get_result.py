from sqlalchemy import func
from db import session, Requirement, vacancy_requirement_table, Vacancy
from sqlalchemy import or_
import csv
from constants import DATE_TODAY, BASE_DIR, RESULS_DIR

# Задаем имя файла CSV для сохранения требований
report_file = BASE_DIR / RESULS_DIR / f'junior_reqirements_top_{DATE_TODAY}.csv'  # noqa

# Задаем имя файла CSV для сохранения зарплат
salary_file = BASE_DIR / RESULS_DIR / f'junior_salary_data_{DATE_TODAY}.csv'  # noqa

salary_file_v2 = BASE_DIR / RESULS_DIR / f'junior_salary_data_v2_{DATE_TODAY}.csv'  # noqa

# подсчитаваю общее количество вакансий
all_vacancy_count = session.query(func.count(Vacancy.id)).scalar()

# подсчитываю общее количество требований
all_requirement_count = session.query(func.count(Requirement.id)).scalar()

# подсчитаваю джуновские вакансии
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
percent_data = [[requirement, f'{count/junior_vacancy_count*100:.0f}'] for requirement, count in result_junior_sorted if count/junior_vacancy_count*100 >= 10] # noqa


# Запрос на получение данных для зарплаты
junior_salary_query = session.query(Vacancy.vac_name, Vacancy.vac_salary_min, Vacancy.vac_salary_max) \
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
    ).filter(Vacancy.vac_salary_min > 20000
             ).all()


def normalize_salary(data):
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
        salary_data.append([name, salary])
    return sorted(salary_data, key=lambda x: x[1])


def avarage_salary(normalize_data):
    """ Считаем среднюю зп на джуна, срезав 20% крайних точек.
    """
    length = len(normalize_data)
    possible_error = round(length*0.2)
    cleared_selection = normalize_data[possible_error:-possible_error]
    total = 0
    for _, salary in cleared_selection:
        total += salary
    return total/len(cleared_selection)


# Записываем результаты в файл CSV
with open(report_file, 'w', newline='') as file:
    writer = csv.writer(file)
    # Записываем заголовки, если необходимо
    writer.writerow(['Requirement', 'Percentage'])
    # Записываем данные
    writer.writerows(percent_data)

print(f'Результаты сохранены в файл {report_file}')


with open(salary_file_v2, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Average junior salary (1-3 year exp)',
                     round(avarage_salary(
                         normalize_salary(junior_salary_query)))
                     ])
    writer.writerow(['**************************************'])
    # Записываем заголовки, если необходимо
    writer.writerow(['Name', 'Salary'])
    # Записываем данные
    writer.writerows(
        normalize_salary(junior_salary_query)
    )

print(f'Результаты сохранены в файл {salary_file_v2}')
# Дополнить количеством выборки
# Сколько всего, сколько использовано для выборки
# кажется не отсекаются плохие слова в названиях вакансий
