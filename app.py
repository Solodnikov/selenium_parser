# Import packages
from dash import Dash, html, dash_table, dcc
import pandas as pd
from constants import BASE_DIR, RESULS_DIR
import plotly.express as px
from db import engine, session, Vacancy
from sqlalchemy import or_, and_


data = BASE_DIR / RESULS_DIR / 'junior_reqirements_top_22_10_2023.csv'

# Incorporate data
# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')
df = pd.read_csv(data)

all_vacancy_junior = session.query(Vacancy).filter(
    or_(
        Vacancy.vac_exp == '1–3 года',
        Vacancy.vac_exp == 'не требуется'
        )).all()
count_all_vacancy = session.query(Vacancy).count()
count_all_vacancy_junior = session.query(Vacancy).filter(
    or_(
        Vacancy.vac_exp == '1–3 года',
        Vacancy.vac_exp == 'не требуется'
        )).count()

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='My First App with Data'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=30),
    dcc.Graph(figure=px.histogram(df,
                                  x='Requirement',
                                  y='Percentage',
                                  histfunc='avg'
                                  ))
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)