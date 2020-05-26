import dash
import math
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input,Output

external_stylesheets = ['~/covid_dashb/assets/style.css','~/covid_dashb/assets/bootstyle.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'Covid-19 UK Cases and Deaths'

df_cases = pd.read_csv("coronavirus-cases_latest.csv")
df_deaths = pd.read_csv("coronavirus-deaths_latest.csv")
areas_df = df_cases.loc[(df_cases["Area type"] == "Region")]
max_deaths = df_deaths.loc[(df_deaths["Area type"] == "UK")]['Cumulative deaths'].max()
daily_deaths_increase = df_deaths.loc[(df_deaths["Area type"] == "UK")]['Daily change in deaths'].iloc[0]

def regionCheckBoxes():
    region_list = areas_df['Area name'].unique().tolist()
    dicts_list = []
    for region in region_list:
        dicts_list.append({'label':region,'value':region})

    return dcc.Dropdown(id='region-check-boxes',
        options=dicts_list,
        value='London',
        multi=False)

app.layout = html.Div(children=[
    html.Div([
        html.Div([html.H4('Covid-19 UK Cases and Deaths')],className='four columns'),
        html.Div([html.H4('Daily UK Deaths: {:,}'.format(int(daily_deaths_increase)))],style={'color': 'rgb(99,110,250)'},className='four columns'),
        html.Div([html.H4('Total UK Deaths: {:,}'.format(max_deaths))],style={'color': 'crimson'},className='four columns')
        ],className='twelve columns'),
    html.Div([
        html.Div([html.P('Select Region to see cases')],className='one columns'),
        html.Div([regionCheckBoxes()],className='five columns'),
        html.Div([html.P('Select Country to see cases')],className='one columns'),
        html.Div([dcc.Dropdown(id='uk-region-check-boxes', 
                options=[{'label':'England','value':'England'},
                {'label':'Wales','value':'Wales'},
                {'label':'Scotland','value':'Scotland'},
                {'label':'Northern Ireland','value':'Northern Ireland'}], 
                value='England', multi=False)],className='five columns') 
        ],className='twelve columns'),
    html.Div([
        html.Div([dcc.Graph(id='case-time-series-graph')],className = 'six columns'),
        html.Div([dcc.Graph(id='regions-deaths-bar-graph')],className = 'six columns')
        ]),
        html.Div([
    html.Div([dcc.Graph(id='case-time-series-death-graph')],className = 'seven columns'),
    html.Div([dcc.Graph(id='regions-bar-graph')],className = 'five columns')
    ],className = 'twelve columns'),
    html.Div(
        [html.Div([dcc.Graph(id='case-log-time-series-graph')],className = 'seven columns'),
        html.Div([dcc.Graph(id='cumulative-bar-graph')],className = 'five columns')
        ],className = 'twelve columns')
    ])

#start callbacks
@app.callback(Output(component_id='regions-bar-graph',component_property='figure'),
[Input('region-check-boxes','value')])
def makeBarGraph(input_choice):

    recent_cumulative = areas_df.head(9)
    recent_cumulative = recent_cumulative.sort_values('Daily lab-confirmed cases',ascending=False)

    colors = ['lightslategray',] * 9
    colors[0] = 'crimson'
    inf_date = recent_cumulative["Specimen date"].values[0]

    graph_fig = go.Figure(
    data=[go.Bar(x=recent_cumulative['Area name'], y=recent_cumulative['Daily lab-confirmed cases'],
        marker_color=colors,marker_line_color='rgba(0,0,0,0)')],
    layout=go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        xaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        font=dict(color="#B2B2B2"),
        title=go.layout.Title(text="Covid-19 Daily Lab Confirmed Cases by Region"))
    )

    return graph_fig

@app.callback(Output(component_id='cumulative-bar-graph',component_property='figure'),
[Input('region-check-boxes','value')])
def makeBarGraph(input_choice):

    recent_cumulative = areas_df.head(9)
    recent_cumulative = recent_cumulative.sort_values('Cumulative lab-confirmed cases',ascending=False)

    colors = ['lightslategray',] * 9

    inf_date = recent_cumulative["Specimen date"].values[0]

    graph_fig = go.Figure(
    data=[go.Bar(x=recent_cumulative['Area name'], 
                        y=recent_cumulative['Cumulative lab-confirmed cases'],
                       marker_color=colors,marker_line_color='rgba(0,0,0,0)')],
    layout=go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        xaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        font=dict(color="#B2B2B2"),
        title=go.layout.Title(text="Cumulative Lab Confirmed Cases by Region"))
    )

    return graph_fig

@app.callback(Output(component_id='case-time-series-graph',component_property='figure'),
[Input('region-check-boxes','value')])
def makeLineGraph(input_choice):
    if input_choice is None:
        input_choice = 'London'
    df_location = df_cases.loc[(df_cases["Area type"] == "Region") & (df_cases["Area name"] == input_choice)]

    line_fig = go.Figure(
        data=[go.Bar(x=df_location['Specimen date'], 
                    y=df_location['Daily lab-confirmed cases'],
                    name='cumulative cases for {0}'.format(input_choice),
                    marker_line_color='rgba(0,0,0,0)')

        ],
    layout=go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        xaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        font=dict(color="#B2B2B2"),
        title=go.layout.Title(text="Covid-19 Lab Confirmed Cases by Date for {0}".format(input_choice)))
        )

    return line_fig

@app.callback(Output(component_id='case-time-series-death-graph',component_property='figure'),
[Input('region-check-boxes','value')])
def makeNationLineGraph(input_choice):
    nat_df = df_cases.loc[(df_cases["Area type"] == "Nation")]
    uk_df = df_deaths.loc[(df_deaths["Area type"] == "UK")]

    line_fig = go.Figure(
    data=[go.Scatter(x=nat_df['Specimen date'], y=nat_df['Daily lab-confirmed cases'].rolling(7).mean(),
                    mode='lines',
                    name='Rolling Mean Daily Cases'),
    go.Scatter(x=uk_df['Reporting date'], y=uk_df['Daily change in deaths'].rolling(7).mean(),
                    mode='lines',
                    name='Rolling Mean Daily Deaths',
                    marker=dict(color='#DC143C')),
    go.Bar(x=nat_df['Specimen date'], y=nat_df['Daily lab-confirmed cases'],name='National Daily Cases',marker_line_color='rgba(0,0,0,0)'),
    go.Bar(x=uk_df['Reporting date'], y=uk_df['Daily change in deaths'],name='National Daily Deaths',marker_line_color='rgba(0,0,0,0)')],
    layout=go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        xaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        font=dict(color="#B2B2B2"),
        title=go.layout.Title(text="UK Covid-19 Lab Confirmed Deaths and Cases by Date"))
    )

    return line_fig

@app.callback(Output(component_id='case-log-time-series-graph',component_property='figure'),
[Input('region-check-boxes','value')])
def makeNationLineGraph(input_choice):
    nat_df = df_cases.loc[(df_cases["Area type"] == "Nation")]
    uk_df = df_deaths.loc[(df_deaths["Area type"] == "UK")]
    lowest_date = nat_df['Specimen date'].head(1)[0]
    log_cases = [math.log(x) if x > 0 else 0 for x in nat_df['Daily lab-confirmed cases']]
    log_deaths = [math.log(x) if x > 0 else 0 for x in uk_df['Daily change in deaths']]
    line_fig = go.Figure(
    data=[go.Scatter(x=nat_df['Specimen date'], y=log_cases,
                    mode='markers',
                    name='National Daily Cases'),
    go.Scatter(x=uk_df['Reporting date'], y=log_deaths,
                    mode='markers',
                    name='National Daily Deaths',
                    marker=dict(color='#DC143C'))],
    layout=go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        xaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        font=dict(color="#B2B2B2"),
        title=go.layout.Title(text="Log Transformed Covid-19 Lab Confirmed Cases and Deaths by Date"))
    )

    return line_fig

@app.callback(Output(component_id='regions-deaths-bar-graph',component_property='figure'),
[Input('uk-region-check-boxes','value')])
def makeDeathBarGraph(input_choice):

    if input_choice is None:
        input_choice = 'England'  

    region_l = input_choice

    uk_df = df_deaths.loc[(df_deaths["Area name"] == region_l)]
    all_uk_df = df_deaths.loc[(df_deaths["Area type"] == "UK")]
    
    graph_fig = go.Figure(
    data=[go.Bar(x=uk_df['Reporting date'], 
                y=uk_df['Daily change in deaths'],name='{0}'.format(input_choice),marker_line_color='rgba(0,0,0,0)'),
    go.Bar(x=all_uk_df['Reporting date'], y=all_uk_df['Daily change in deaths'],
        name='All UK',marker=dict(color='#DC143C'),marker_line_color='rgba(0,0,0,0)')],
    layout=go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        xaxis=dict(color = "#B2B2B2",
            linecolor ="#B2B2B2"),
        font=dict(color="#B2B2B2"),
        title=go.layout.Title(text="Daily Reported Deaths in {0} for Covid-19".format(region_l)))
    )

    return graph_fig

if __name__ == '__main__':
    app.run_server(debug=True)
