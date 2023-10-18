from __future__ import annotations
from sqlalchemy import create_engine, Column, Integer, String, Table
from sqlalchemy.orm import declarative_base, Session
from tqdm import tqdm

from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy import func


Base = declarative_base()


engine = create_engine('sqlite:///sqlite.db', echo=True)
session = Session(engine)


# class Vacancy(Base):
#     __tablename__ = 'vacancy'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     requirement: Mapped[List["Requirement"] | None] = relationship(back_populates="vacancy")
#     vac_name: Mapped[str | None] = mapped_column(String(200), default=None)
#     vac_exp: Mapped[str | None] = mapped_column(String(200), default=None)
#     vac_salary_net: Mapped[str | None] = mapped_column(String(200), default=None)
#     vac_salary_gross: Mapped[str | None] = mapped_column(String(200), default=None)
#     vac_number: Mapped[int | None] = mapped_column(default=None)
#     vac_url: Mapped[str] = mapped_column(String(200), default=None)
#     vac_date_parse: Mapped[str] = mapped_column(String(200), default=None)

#     # def __repr__(self) -> str:
#     #     return f"{self.vac_number}, {self.vac_name}, {self.vac_url}"


# class Requirement(Base):
#     __tablename__ = 'requirement'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     vacancy_id: Mapped[int | None] = mapped_column(ForeignKey("vacancy.id"))
#     vacancy: Mapped[Vacancy | None] = relationship(back_populates="requirement")
#     name: Mapped[str] = mapped_column(String(200), default=None)


# new classes

vacancy_requirement_table = Table(
    'vacancy_requirement_table',
    Base.metadata,
    Column('requirement_id', ForeignKey('requirement.id'), primary_key=True),
    Column('vacancy_id', ForeignKey('vacancy.id'), primary_key=True),
)


class Vacancy(Base):
    __tablename__ = 'vacancy'
    id: Mapped[int] = mapped_column(primary_key=True)
    requirement: Mapped[List["Requirement"] | None] = relationship(
        secondary=vacancy_requirement_table,
        back_populates="vacancy")
    vac_name: Mapped[str | None] = mapped_column(String(200), default=None)
    vac_exp: Mapped[str | None] = mapped_column(String(200), default=None)
    vac_salary_net: Mapped[str | None] = mapped_column(String(200), default=None)
    vac_salary_gross: Mapped[str | None] = mapped_column(String(200), default=None)
    # vac_number: Mapped[int | None] = mapped_column(default=None)
    vac_url: Mapped[str] = mapped_column(String(200), default=None)
    vac_date_parse: Mapped[str] = mapped_column(String(200), default=None)

    # def __repr__(self) -> str:
    #     return f"{self.vac_number}, {self.vac_name}, {self.vac_url}"


class Requirement(Base):
    __tablename__ = 'requirement'
    id: Mapped[int] = mapped_column(primary_key=True)
    # vacancy_id: Mapped[int | None] = mapped_column(ForeignKey("vacancy.id"))
    vacancy: Mapped[List['Vacancy'] | None] = relationship(
        secondary=vacancy_requirement_table,
        back_populates="requirement")
    name: Mapped[str] = mapped_column(String(200), default=None)


def create(array: list, session):
    for row in tqdm(array):
        obj = Vacancy(
            vac_name=row[1],
            vac_exp=row[2],
            vac_salary_net=row[3],
            vac_salary_gross=row[4],
            skills=row[5],
            vac_url=row[6])
        session.add(obj)
        session.commit()


# def create_obj_in_db(data: dict, session: Session):
    # TODO настроить обработку, если объект давно парсился или не создан
    # existing_vacancy = session.query(Vacancy).filter_by(id=data['vac_number']).first() 
    # if existing_vacancy:
    #     # Если объект Vacancy существует, просто обновляем его атрибуты
    #     existing_vacancy.vac_url = data['vac_url']
    #     existing_vacancy.vac_name = data['vac_name']
    #     existing_vacancy.vac_exp = data['vac_exp']
    #     existing_vacancy.vac_salary_net = data['vac_salary_net']
    #     existing_vacancy.vac_salary_gross = data['vac_salary_gross']
    #     existing_vacancy.vac_date_parse = data['vac_date_parse']
    
    
    # else:
    #     # Если объект Vacancy не существует, создаем новый
    # obj = Vacancy(
    #     id=data['vac_number'],
    #     vac_url=data['vac_url'],
    #     vac_name=data['vac_name'],
    #     vac_exp=data['vac_exp'],
    #     vac_salary_net=data['vac_salary_net'],
    #     vac_salary_gross=data['vac_salary_gross'],
    #     vac_date_parse=data['vac_date_parse']
    #     )
    # session.add(obj)

    # # Создаем или находим объекты Requirement и связываем их с объектом Vacancy
    # requirements = data.get('requirements', set())
    # for requirement_name in requirements:
    #     # existing_requirement = session.query(Requirement).filter_by(name=requirement_name).first()
    #     existing_requirement = session.query(Requirement).filter(func.lower(Requirement.name) == requirement_name.lower()).first()
    #     if existing_requirement:
    #         # Если объект Requirement с таким именем уже существует, связываем его с объектом Vacancy
    #         obj.requirement.append(existing_requirement)
    #     else:
    #         # Если объект Requirement не существует, создаем новый
    #         requirement = Requirement(name=requirement_name)
    #         obj.requirement.append(requirement)

    # # Сохраняем изменения в базе данных
    # session.commit()


# def create_objs_in_db(data: dict, session: Session):
#     """ Создаем объект вакансия и отсутствующие в базе требования.
#     """
#     # Создаем объект Vacancy
#     vacancy = Vacancy(
#         id=data['vac_number'],
#         vac_url=data['vac_url'],
#         vac_name=data['vac_name'],
#         vac_exp=data['vac_exp'],
#         vac_salary_net=data['vac_salary_net'],
#         vac_salary_gross=data['vac_salary_gross'],
#         vac_date_parse=data['vac_date_parse']
#     )
    
#     # Добавляем объект Vacancy в сессию
#     session.add(vacancy)

#     # Создаем или находим объекты Requirement и связываем их с объектом Vacancy
#     requirements = data.get('requirements', set())
#     for requirement_name in requirements:
#         existing_requirement = session.query(Requirement).filter(func.lower(Requirement.name) == requirement_name.lower()).first()
#         if existing_requirement:
#             # Если объект Requirement с таким именем уже существует, связываем его с объектом Vacancy
#             vacancy.requirement.append(existing_requirement)
#         else:
#             # Если объект Requirement не существует, создаем новый
#             requirement = Requirement(name=requirement_name)
#             vacancy.requirement.append(requirement)
#             # Добавляем новый объект Requirement в сессию
#             session.add(requirement)

#     # Сохраняем изменения в базе данных
#     session.commit()

def create_obj_in_db(data: dict, session: Session):
    # TODO настроить обработку, если объект давно парсился или не создан
    existing_vacancy = session.query(Vacancy).filter_by(id=data['vac_number']).first()  # noqa
    # if existing_vacancy:
    #     # Если объект Vacancy существует, просто обновляем его атрибуты
    #     existing_vacancy.vac_url = data['vac_url']
    #     existing_vacancy.vac_name = data['vac_name']
    #     existing_vacancy.vac_exp = data['vac_exp']
    #     existing_vacancy.vac_salary_net = data['vac_salary_net']
    #     existing_vacancy.vac_salary_gross = data['vac_salary_gross']
    #     existing_vacancy.vac_date_parse = data['vac_date_parse']
    # else:
    #     # Если объект Vacancy не существует, создаем новый
    if not existing_vacancy:
        obj = Vacancy(
            id=data['vac_number'],
            vac_url=data['vac_url'],
            vac_name=data['vac_name'],
            vac_exp=data['vac_exp'],
            vac_salary_net=data['vac_salary_net'],
            vac_salary_gross=data['vac_salary_gross'],
            vac_date_parse=data['vac_date_parse']
        )
        session.add(obj)
        # Создаем или находим объекты Requirement и связываем их с объектом Vacancy
        requirements = data.get('requirements', set())
        for requirement_name in requirements:
            # узнаю есть ли такое тревание уже в базе
            existing_requirement = session.query(Requirement).filter_by(name=requirement_name).first()  # noqa
            if existing_requirement:
                # Если объект Requirement с таким именем уже существует, связываем его с объектом Vacancy
                obj.requirement.append(existing_requirement)
            else:
                # Если объект Requirement не существует, создаем новый
                requirement = Requirement(name=requirement_name)
                obj.requirement.append(requirement)
        # Сохраняем изменения в базе данных
        session.commit()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
