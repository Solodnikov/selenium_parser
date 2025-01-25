from __future__ import annotations
from typing import List, Optional

from sqlalchemy import (create_engine, Column, Integer,
                        String, Table,
                        )
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


Base = declarative_base()


engine = create_engine('sqlite:///sqlite.db', echo=True)
session = Session(engine)


vacancy_requirement_table = Table(
    'vacancy_requirement_table',
    Base.metadata,
    Column('requirement_id', ForeignKey('requirement.id'), primary_key=True),
    Column('vacancy_id', ForeignKey('vacancy.id'), primary_key=True),
)


class Company(Base):
    __tablename__ = 'company'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(50), default=None)
    rank: Mapped[int | None] = mapped_column(Integer, default=None)
    location: Mapped[str | None] = mapped_column(String(50), default=None)
    vacancy: Mapped[Optional["Vacancy"]] = relationship(back_populates="company")


# class CompanyActivity(Base):
#     __tablename__ = 'company_activity'
#     id: Mapped[int] = mapped_column(primary_key=True)


class Vacancy(Base):
    __tablename__ = 'vacancy'
    id: Mapped[int] = mapped_column(primary_key=True)
    # requirement: Mapped[Optional["Requirement"]] = relationship(
    #     secondary=vacancy_requirement_table,
    #     back_populates="vacancy")
    requirements: Mapped[List["Requirement"]] = relationship(
        secondary=vacancy_requirement_table,
        back_populates="vacancies",
    )
    vac_name: Mapped[str | None] = mapped_column(String(200), default=None)
    vac_exp: Mapped[str | None] = mapped_column(String(200), default=None)
    vac_salary_min: Mapped[int | None] = mapped_column(Integer, default=None)
    vac_salary_max: Mapped[int | None] = mapped_column(Integer, default=None)
    vac_url: Mapped[str] = mapped_column(String(200), default=None)
    vac_date_parse: Mapped[str] = mapped_column(String(200), default=None)
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey('company.id'))
    company: Mapped[Optional["Company"]] = relationship(back_populates="vacancy")

    def __repr__(self) -> str:
        return f"{self.id}, {self.vac_name}, {self.vac_exp}"


class Requirement(Base):
    __tablename__ = 'requirement'
    id: Mapped[int] = mapped_column(primary_key=True)
    # vacancy: Mapped[List['Vacancy'] | None] = relationship(
    #     secondary=vacancy_requirement_table,
    #     back_populates="requirement")
    vacancies: Mapped[List["Vacancy"]] = relationship(
        secondary=vacancy_requirement_table,
        back_populates="requirements",
    )
    name: Mapped[str] = mapped_column(String(200), default=None)
    # in_stock: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return self.name


def create_obj_in_db(data: dict, session: Session):
    # TODO настроить обработку, если объект давно парсился или не создан
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
            # узнаю есть ли такое тревание уже в базе
            existing_requirement = session.query(Requirement).filter_by(name=requirement_name).first()  # noqa
            if existing_requirement:
                # Если объект Requirement с таким именем уже существует, связываем его с объектом Vacancy # noqa
                # obj.requirement.append(existing_requirement)
                obj.requirements.append(existing_requirement)
            else:
                # Если объект Requirement не существует, создаем новый
                new_requirement = Requirement(name=requirement_name)
                # obj.requirement.append(requirement)
                obj.requirements.append(new_requirement)
        # Сохраняем изменения в базе данных
        session.commit()


def update_obj_in_db(data: dict, session: Session):
    """На вход получает данные вакансии и обновляет все данные объекта."""
    # TODO настроить обработку, если объект давно парсился или не создан
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
        existing_vacancy.requirement.clear()
        for requirement_name in requirements:
            # узнаю есть ли такое тревание уже в базе
            existing_requirement = session.query(Requirement).filter_by(name=requirement_name).first()  # noqa
            if existing_requirement:
                # Если объект Requirement с таким именем уже существует, связываем его с объектом Vacancy # noqa
                existing_vacancy.requirement.append(existing_requirement)
            else:
                # Если объект Requirement не существует, создаем новый
                requirement = Requirement(name=requirement_name)
                existing_vacancy.requirement.append(requirement)
        # Сохраняем изменения в базе данных
        session.commit()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
