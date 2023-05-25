import pandas as pd
import numpy as np

import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

colorScheme = ['#012A4A', '#013A63', '#01497C', '#014F86', '#2A6F97', '#2C7DA0', '#468FAF', '#61A5C2', '#89C2D9', '#A9D6E5']
colorScheme2 = ['#A5BE00', '#679436', '#EBF2FA', '#427AA1', '#05668D', '#468FAF', '#61A5C2', ]


data_archive = pd.read_csv('breach_report_archive.csv')

data_archive['Breach Submission Date'] = pd.to_datetime(data_archive['Breach Submission Date'])

data_archive['Breach Submission Date Monthly'] = data_archive['Breach Submission Date'].dt.to_period('M')
data_archive['Breach Submission Date Monthly'] = data_archive['Breach Submission Date Monthly'].astype(str)
data_archive['Breach Submission Date Monthly'] = pd.to_datetime(data_archive['Breach Submission Date Monthly']).dt.date.astype(str)


data_archive['Year'] = data_archive['Breach Submission Date'].dt.year

data_archive['weekday_num'] = data_archive['Breach Submission Date'].dt.dayofweek
data_archive['Weekday'] = np.where(data_archive['weekday_num']==0, 'Monday',
                                   np.where(data_archive['weekday_num']==1, 'Tuesday',
                                           np.where(data_archive['weekday_num']==2, 'Wednesday',
                                                   np.where(data_archive['weekday_num']==3, 'Thursday',
                                                           np.where(data_archive['weekday_num']==4, 'Friday',
                                                                   np.where(data_archive['weekday_num']==5, 'Saturday', 'Sunday'))))))

data_archive['Year'] = data_archive['Breach Submission Date'].dt.year

data_archive['Type of Breach'] = data_archive['Type of Breach'].replace({"Theft, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Loss, Theft": "Multiple",
                                                                        "Hacking/IT Incident, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Other, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Improper Disposal, Loss": "Multiple",
                                                                        "Improper Disposal, Loss, Theft": "Multiple",
                                                                        "Other, Theft": "Multiple",
                                                                        "Loss, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Other, Theft, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Hacking/IT Incident, Theft, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Other, Unknown": "Multiple",
                                                                        "Loss, Other": "Multiple",
                                                                        "Hacking/IT Incident, Other": "Multiple",
                                                                        "Hacking/IT Incident, Other": "Multiple",
                                                                        "Improper Disposal, Theft, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Loss, Other, Theft": "Multiple",
                                                                        "Hacking/IT Incident, Other, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Other, Unknown": "Multiple",
                                                                        "Loss, Other": "Multiple",
                                                                        "Hacking/IT Incident, Other": "Multiple",
                                                                        "Improper Disposal, Theft, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Loss, Other, Theft": "Multiple",
                                                                        "Hacking/IT Incident, Other, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Loss, Theft, Unauthorized Access/Disclosure, Unknown": "Multiple",
                                                                        "Improper Disposal, Theft": "Multiple",
                                                                        "Hacking/IT Incident, Theft": "Multiple",
                                                                        "Hacking/IT Incident, Improper Disposal, Loss, Other, Theft, Unauthorized Access/Disclosure, Unknown": "Multiple",
                                                                        "Loss, Unknown": "Multiple",
                                                                        "Improper Disposal, Unauthorized Access/Disclosure": "Multiple",
                                                                        "Loss, Unauthorized Access/Disclosure, Unknown": "Multiple",}) 

data_archive.sort_values(by='Breach Submission Date', ignore_index=True, inplace=True)


fig1 = make_subplots(rows=1, cols=3, specs=[[{"type": "pie"}, {"type": "pie"}, {"type": "pie"}]],
                   subplot_titles=['Breach Type Percentage', "Entity Type Percentage", "Breach Percentage by Weekday"])

breachTypes = data_archive['Type of Breach'].value_counts()
entityTypes = data_archive['Covered Entity Type'].value_counts()
pop_weekdays = data_archive['Weekday'].value_counts()

fig1.add_trace(go.Pie(
     values=breachTypes.values,
     labels=breachTypes.index,
    hole=.3,
     domain=dict(x=[0, 0.3])), 
     row=1, col=1)

fig1.add_trace(go.Pie(
     values=entityTypes.values,
     labels=entityTypes.index,
    hole=.3,
     domain=dict(x=[0.3, 0.6])), 
     row=1, col=2)

fig1.add_trace(go.Pie(
    values=pop_weekdays.values,
    labels=pop_weekdays.index,
    hole=.3,
     domain=dict(x=[0.6, 1])), 
     row=1, col=3)
fig1.update(layout_showlegend=False)
fig1.update_traces(textinfo='percent+label', marker=dict(colors=colorScheme2))


map_data = data_archive.groupby(['State', 'Breach Submission Date'])['State'].count().rename('Count').to_frame()
map_data = map_data.reset_index()
map_data['Breach Submission Date'] = map_data['Breach Submission Date'].dt.to_period('M')
map_data['Breach Submission Date'] = map_data['Breach Submission Date'].astype(str)

map_data['Breach Submission Date'] = pd.to_datetime(map_data['Breach Submission Date']).dt.date.astype(str)
map_data = map_data.sort_values("Breach Submission Date")

fig2 = px.choropleth(map_data,
                    locations='State', 
                    locationmode="USA-states", 
                    scope="usa",
                    color='Count',
                    color_continuous_scale="blues",
                    animation_frame='Breach Submission Date',
                    title='Monthly Breach Count by State <br> (Drag the circle below to right or left to get a specific date.)',
                    height=650)

individuals_affected = data_archive.groupby(['Type of Breach', 'Business Associate Present'])['Individuals Affected'].sum().to_frame()
individuals_affected = individuals_affected.reset_index()
individuals_affected.sort_values(by='Individuals Affected', ascending=False, inplace=True)

fig5 = px.bar(individuals_affected, x='Type of Breach', y='Individuals Affected', color='Business Associate Present',
             barmode='group', text_auto='.3s',
             title='Individuals Affected by Breach type and Business Asscoiate Status',
             color_discrete_sequence=colorScheme2)



external_stylesheets = [dbc.themes.FLATLY]
# FLATLY, JOURNAL, ZEPHYR,

app = Dash(__name__, external_stylesheets=external_stylesheets,
           meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
# server = app.server

card_content1 = [
    dbc.CardHeader("Breach Type Percentage"),
    dbc.CardBody(
        [html.H5("Key Insights:", className="card-title"),
         html.P("""Most common breach is "Hacking/IT Incident", second and third popular ones are "Unauthorized Access/Disclosure" and "Theft".""",
                className="card-text",),]
    ),]

card_content2 = [
    dbc.CardHeader("There are 4 types of covered entities in data."),
    dbc.CardBody(
        [html.H5("Here are the proportions of each one: ", className="card-title"),
         html.P(""" Healthcare Provider - 74%,  Business Associate - 13%,  Health Plan - 12.8%, Healthcare Clearing House - 0.2%""",
                className="card-text",),]
    ),]


card_content3 = [
    dbc.CardHeader("Breach Percentage by Weekday"),
    dbc.CardBody(
        [html.H5("Most active and passive days.", className="card-title"),
         html.P("""Highest amount of breaches are reported on Friday. Lowest amount of breaches are reported on Saturday and Sunday.""",
                className="card-text",),]
    ),]

card2 = dbc.Card(dbc.ListGroup(
        [
            dbc.ListGroupItem("""1. Texas,"""),
            dbc.ListGroupItem("""2. New York,"""),
            dbc.ListGroupItem("""3. California,"""),
            dbc.ListGroupItem("""4. Florida,"""),
            dbc.ListGroupItem("""5. Puerto Rico."""),
        ],
        flush=True,
    ),
)


card3 = dbc.Card(dbc.ListGroup(
        [
            dbc.ListGroupItem("""1. 81% of individuals were affected by an "Hacking/IT Incident" type of breach and 33% of them were Business Associates."""),
            dbc.ListGroupItem("""2. 8% of individuals were affected by an "Theft" type of breach and 40% of them were Business Associates."""),
            dbc.ListGroupItem("""3. Individuals were the least affected by the "Loss", "Improper Disposal" and "Other" types of breaches."""),
        ],
        flush=True,
    ),
)

layout = html.Div([
    
    html.H1("Heal Security Breach Report", style={"text-align": "center"}),
    
    html.Div([dbc.Row([
             
             dbc.Col(dcc.Graph(id="graph-1", figure=fig1, className="border")),
             html.H5(children="Insights:", style={'textAlign':'left','marginLeft': 10, "font-weight": "bold"}),
             dbc.Row([
                dbc.Col(dbc.Card(card_content1, color="light")),
                 dbc.Col(dbc.Card(card_content2, color="light")),
                dbc.Col(dbc.Card(card_content3, color="light")),
            ]),
    ])]),
    
    html.Div(children=[
        dcc.Graph(id="graph-2", figure=fig2),
        
    ]),
    
    dbc.Row([
        dbc.Col(html.H5(children="Select State:", style={'textAlign':'left','marginLeft': 10, "font-weight": "bold"})),
        dbc.Col(html.H5(children="Select Year:", style={'textAlign':'left','marginLeft': 10, "font-weight": "bold"}))
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Dropdown(options=[{'label': i, 'value': i} for i in data_archive['State'].unique()],
                 value='CA',
                 multi=False,
                 clearable=False,
                 disabled=False,
                 searchable=True,
                 placeholder='Select State',
                 id='dropdown-selection')),
        dbc.Col(dcc.Dropdown(options=[{'label': i, 'value': i} for i in data_archive['Year'].unique()],
                 value=[2008, 2009, 2010, 2011],
                 multi=True,
                 clearable=False,
                 disabled=False,
                 placeholder='Select Year',
                 id='dropdown-selection2')),]),
    html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(id="graph-3")),
                    dbc.Col(dcc.Graph(id="graph-4"))
            ])
    ]),

    
    html.Div([
         dbc.Row([
             html.H5(children="Top 5 states that have most reported breaches in from 2009-2023:", style={'textAlign':'left','marginLeft': 10, "font-weight": "bold"}),
             dbc.Row([card2]),
             dbc.Col(dcc.Graph(id="graph-5", figure=fig5, className="border")),
             html.H5(children="Insights:", style={'textAlign':'left','marginLeft': 10, "font-weight": "bold"}),
             dbc.Row([card3]),
         ])])
 
])


@app.callback(
    Output('graph-3', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('dropdown-selection2', 'value')
)
def update_output1(value, years):
    df = data_archive[(data_archive['State']==value)&(data_archive['Year'].isin(years))]
    df = df.groupby(['Type of Breach', 'Breach Submission Date Monthly'])['Type of Breach'].count().rename('Count').to_frame()
    df = df.reset_index()
        
    fig = px.line(df, x="Breach Submission Date Monthly", y="Count",
                  color='Type of Breach',
                  title='Breach Dynamic by State and Type',
                  color_discrete_sequence=colorScheme2)
    return fig
@app.callback(
    Output('graph-4', 'figure'),
    Input('dropdown-selection2', 'value')
)
def update_output2(years):
    states_breach = data_archive[data_archive['Year'].isin(years)].groupby(['State', 'Type of Breach'])['State'].count().rename('Count').to_frame()
    states_breach = states_breach.reset_index()
    states_breach.sort_values(by='Count', ascending=False, inplace=True)

    fig = px.bar(states_breach, x='State', y='Count', color='Type of Breach',
                title='Breach Count by State and Type',
                color_discrete_sequence=colorScheme2)
#     fig.update(layout_showlegend=False)
    return fig




