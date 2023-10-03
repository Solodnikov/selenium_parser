from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from tqdm import tqdm


Base = declarative_base()

engine = create_engine('sqlite:///sqlite.db', echo=True)
session = Session(engine)


class Vacancy(Base):
    __tablename__ = 'vacancy'
    id = Column(Integer, primary_key=True)
    vac_name = Column(String(200), default=None)
    vac_exp = Column(String(200), default=None)
    vac_salary_net = Column(String(200), default=None)
    vac_salary_gross = Column(String(200), default=None)
    skills = Column(String(200), default=None)
    vac_url = Column(String(200), default=None)


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


if __name__ == '__main__':
    Base.metadata.create_all(engine)
