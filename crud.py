import datetime

from sqlalchemy.orm import Session

from constants import INCORRECT_REQUIREMENTS
from db import Requirement, Vacancy


def vacancy_exist(session: Session, vacancy_url: str) -> bool:
    """Проверяет есть ли в базе данных вакансия по url"""
    return session.query(Vacancy).filter_by(vac_url=vacancy_url).first()


def vacancy_old(session: Session, vacancy_url: str, time_old: int = 5) -> bool:
    """Проверяет есть ли в базе данных вакансия
    с давностью по умолчанию 5 и более дней по url"""
    params = '%Y-%m-%d'
    current_date = datetime.date.today()
    vacancy = session.query(Vacancy).filter_by(vac_url=vacancy_url).first()
    vacancy_date = datetime.datetime.strptime(vacancy.vac_date_parse, params).date()  # noqa
    delta = current_date - vacancy_date
    if delta.days > time_old:
        return True
    return False


def create_obj_in_db(data: dict, session: Session):
    """Создание объекта вакансии и требований в БД.
    Принимает на вход словарь.
    """
    existing_vacancy = session.query(Vacancy).filter_by(id=data['vac_number']).first()  # noqa

    if not existing_vacancy:
        obj = Vacancy(
            id=data['vac_number'],
            vac_url=data['vac_url'],
            vac_name=data['vac_name'],
            vac_exp=data['vac_exp'],
            vac_salary_min=data['vac_salary_min'],
            vac_salary_max=data['vac_salary_max'],
            vac_date_parse=data['vac_date_parse']
        )
        session.add(obj)
        # Создаем или находим объекты Requirement и связываем их с объектом Vacancy # noqa
        requirements = data.get('requirements', set())
        for requirement_name in requirements:
            # узнаю есть ли такое требование уже в базе
            existing_requirement = session.query(Requirement).filter_by(name=requirement_name).first()  # noqa
            if existing_requirement:
                # Если объект Requirement с таким именем уже существует, связываем его с объектом Vacancy # noqa
                obj.requirements.append(existing_requirement)
            else:
                # Если объект Requirement не существует,
                # проверяю на корректность и создаю новый
                if requirement_name not in INCORRECT_REQUIREMENTS:
                    requirement = Requirement(name=requirement_name)
                    obj.requirements.append(requirement)
        # Сохраняем изменения в базе данных
        session.commit()


def update_obj_in_db(data: dict, session: Session):
    """Обновляет данные вакансии и требований.
    Принимает на вход словарь"""
    existing_vacancy = session.query(Vacancy).filter_by(id=data['vac_number']).first()  # noqa

    if existing_vacancy:
        # Если объект Vacancy существует, просто обновляем его атрибуты
        existing_vacancy.vac_name = data['vac_name']
        existing_vacancy.vac_exp = data['vac_exp']
        existing_vacancy.vac_salary_min = data['vac_salary_min']
        existing_vacancy.vac_salary_max = data['vac_salary_max']
        existing_vacancy.vac_date_parse = data['vac_date_parse']
        session.add(existing_vacancy)
        # Создаем или находим объекты Requirement и связываем их с объектом Vacancy # noqa
        requirements = data.get('requirements', set())
        # Удаляем все текущие связи объекта Vacancy с Requirement
        existing_vacancy.requirements.clear()
        for requirement_name in requirements:
            # узнаю есть ли такое требование уже в базе
            existing_requirement = session.query(Requirement).filter_by(name=requirement_name).first()  # noqa
            if existing_requirement:
                # Если объект Requirement с таким именем уже существует, связываем его с объектом Vacancy # noqa
                existing_vacancy.requirements.append(existing_requirement)
            else:
                # Если объект Requirement не существует,
                # проверяю на корректность и создаю новый
                if requirement_name not in INCORRECT_REQUIREMENTS:
                    requirement = Requirement(name=requirement_name)
                    existing_vacancy.requirements.append(requirement)
        # Сохраняем изменения в базе данных
        session.commit()


def del_old_vacancies(session: Session) -> list:
    """Удаляет старые вакансии."""
    all_vacancies = session.query(Vacancy).all()
    killed_list = []
    for vacancy in all_vacancies:
        if vacancy_old(session, vacancy.vac_url):
            killed_list.append(vacancy.id)
            session.delete(vacancy)
    session.commit()
    return killed_list
