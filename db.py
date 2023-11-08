from __future__ import annotations
from sqlalchemy import create_engine, Column, Integer, String, Table
from sqlalchemy.orm import declarative_base, Session

from typing import List

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


class Vacancy(Base):
    __tablename__ = 'vacancy'
    id: Mapped[int] = mapped_column(primary_key=True)
    requirement: Mapped[List["Requirement"] | None] = relationship(
        secondary=vacancy_requirement_table,
        back_populates="vacancy")
    vac_name: Mapped[str | None] = mapped_column(String(200), default=None)
    vac_exp: Mapped[str | None] = mapped_column(String(200), default=None)
    vac_salary_min: Mapped[int | None] = mapped_column(Integer, default=None)
    vac_salary_max: Mapped[int | None] = mapped_column(Integer, default=None)
    vac_url: Mapped[str] = mapped_column(String(200), default=None)
    vac_date_parse: Mapped[str] = mapped_column(String(200), default=None)

    def __repr__(self) -> str:
        return f"{self.id}, {self.vac_name}, {self.vac_exp}"


class Requirement(Base):
    __tablename__ = 'requirement'
    id: Mapped[int] = mapped_column(primary_key=True)
    vacancy: Mapped[List['Vacancy'] | None] = relationship(
        secondary=vacancy_requirement_table,
        back_populates="requirement")
    name: Mapped[str] = mapped_column(String(200), default=None)

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
                obj.requirement.append(existing_requirement)
            else:
                # Если объект Requirement не существует, создаем новый
                requirement = Requirement(name=requirement_name)
                obj.requirement.append(requirement)
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
