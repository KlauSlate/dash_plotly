# se importan las librerias
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

# cargar los datos desde el archivos .csv
df = pd.read_excel('unicornio_startup.xlsx')

# crear la aplicacion de Dash
app = dash.Dash(__name__)

# obtener las opciones unicas de la columna 'industry'
industries = [{'label':industry, 'value':industry} for industry in df['Industry'].unique()]

# definir el diseño de la aplicacion
app.layout = html.Div([
    html.H1('Dashboard de Startup Unicornios'),
    html.Label('Selecciona la industria para visualizar el grafico:'),
    dcc.Dropdown(
        id='dropdown',
        options=industries,
        value=industries[0]['value']
    ),
    dcc.Loading(
        id="loading-total-startups",
        children=[
            html.Div(id='total-startups', style={'background-color': 'red', 'color': 'white', 'padding': '10px', 'margin-top': '10px'}),
            html.Div(id='total-inverstor', style={'background-color': 'blue', 'color': 'white', 'padding': '10px', 'margin-top': '10px'})
        ]
    ),
    dcc.Graph(id='treemap'),
    html.Hr(), # linea horizontal para separar los graficos
    html.H2('Heatmap de N° de inversores por industria'),
    dcc.Graph(id='heatmap'),
    html.Hr(), # linea horizontal para separar los graficos
    html.H2('Linea de valorizacion en el tiempo'),
    dcc.Graph(id='lineplot'),
    html.Hr(), # linea horizontal para separar los graficos
    html.H2('Histograma de los mayores inversionistas'),
    dcc.Graph(id='investor1-histogram'),
    html.Hr(), # linea horizontal para separar los graficos
    html.H2('Mapa Coleptero'),
    dcc.Graph(id='geographic-map'),
])

# definir la interactividad del treemap
@app.callback(
    Output('treemap','figure'),
    [Input('dropdown','value')]
)

def update_treemap(selected_value):
    filtered_df = df[df['Industry'] == selected_value]
    fig = px.treemap(filtered_df, path=[px.Constant('Industry'),'Country','Company'],
                    values='Valuation ($B)',
                    title=f'Treemap de valorizacion para {selected_value}')
    return fig

# definir la interactividad del heatmap
@app.callback(
    Output('heatmap','figure'),
    [Input('dropdown','value')]
)

def update_heatmap(selected_value):
    filtered_df = df[df['Industry'] == selected_value]
    heatmap_data = filtered_df.groupby(['Industry', 'Country']).size().unstack(fill_value=0)
    fig = px.imshow(heatmap_data.values,
                    labels=dict(x="Country", y="Industry", color="Count"),
                    x=list(heatmap_data.columns),
                    y=list(heatmap_data.index),
                    title=f"Numero de inversores para la industria {selected_value} por pais")
    return fig

# definir la interactividad del line plot
@app.callback(
    Output('lineplot', 'figure'),
    [Input('dropdown', 'value')]
)

def update_lineplot(selected_value):
    filtered_df = df[df['Industry'] == selected_value]
    lineplot_data = filtered_df.groupby('Año')['Valuation ($B)'].sum().reset_index()
    fig = px.line(lineplot_data, x='Año',
                y='Valuation ($B)',
                title=f"Valorizacion durante los años para la industria {selected_value}")
    return fig

# definir el contenido del cuadro de texto para mostrar la suma de startups
@app.callback(
    Output('total-startups', 'children'),
    [Input('dropdown', 'value')]
)

def update_total_startups(selected_value):
    total_startups = df[df['Industry'] == selected_value].shape[0]
    return f"Total de Startups: {total_startups} para la industria {selected_value}"

# Definir el contenido del cuadro de texto para mostrar la suma total de valuación
@app.callback(
    Output('total-inverstor', 'children'),
    [Input('dropdown', 'value')]
)

def update_total_valuation(selected_value):
    total_valuation = df[df['Industry'] == selected_value]['Numero Investor'].sum()
    return f"Total del numero de inversores: {total_valuation}"

# Definir la interactividad del histograma de Investor 1
@app.callback(
    Output('investor1-histogram', 'figure'),
    [Input('dropdown', 'value')]
)
def update_investor1_histogram(selected_value):
    filtered_df = df[df['Industry'] == selected_value]
    fig = px.histogram(filtered_df, x='Investor 1', title="Histograma de Investor 1")
    return fig

# Definir la interactividad del coleoptero
@app.callback(
    Output('geographic-map', 'figure'),
    [Input('dropdown', 'value')]
)
def update_geographic_map(selected_value):
    filtered_df = df[df['Industry'] == selected_value]
    fig = px.choropleth(filtered_df,
                        locations='Country', 
                        color='Industry',
                        size='City',
                        title='Mapa Geográfico por Industria')
    return fig

# ejecutar la aplicacion
if __name__ == '__main__':
    app.run_server(debug=True)