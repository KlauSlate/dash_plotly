# se importan las librerias
import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import warnings
warnings.filterwarnings('ignore')

# cargar los datos desde el archivos .csv
df = pd.read_excel('unicornio_startup.xlsx')

# crear la aplicacion de Dash
app = dash.Dash(__name__)

# obtener las opciones unicas de la columna 'industry'
industries = [{'label':industry, 'value':industry} for industry in df['Industry'].unique()]

# definir el diseño de la aplicacion
app.layout = html.Div([
    html.H1('Dashboard de Startup Unicornios', style={'textAlign': 'center'}),
    html.H4('Objetivo del Dashboard:'),
    html.H4('1.-Brindar información completa y actualizada sobre startups unicornio (empresas valoradas en más de mil millones de dólares) a potenciales inversionistas y startups'),
    html.H4('2.- Empoderar a los inversionistas ángeles con información completa y actualizada sobre startups unicornio para tomar decisiones de inversión más informadas y acceder a las oportunidades de inversión más prometedoras'),
    html.H4('3.- Brindar a las startups acceso a información valiosa sobre las empresas unicornio por industria y los inversores más interesados en cada una, para que puedan aprender de las mejores y posicionarse para el éxito.'),
    html.Label('Seleccionar una industria para visualizar el grafico:'),
    dcc.Dropdown(
        id='dropdown',
        options=industries,
        value=industries[0]['value']
    ),

    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Total de Startups", className="card-title"),
                    html.P(id='total-startups', className="card-text")
                ]),
                color="primary", inverse=True, body=True
            ),
            width=7
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Total de Inversores", className="card-title"),
                    html.P(id='total-inverstor', className="card-text")
                ]),
                color="info", inverse=True
            ),
            width=6
        )
    ]),

    html.Div([
        dcc.Graph(id='treemap', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='heatmap', style={'width': '50%', 'display': 'inline-block'})
    ]),
    html.Div([
        dcc.Graph(id='lineplot', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='investor1-histogram', style={'width': '50%', 'display': 'inline-block'})
    ]),
    html.Div([
        dcc.Graph(id='geographic-map', style={'width': '50%', 'display': 'inline-block'})
    ])
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
                    title=f'Mapa de startups para {selected_value}')
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
                    text_auto=True,
                    aspect='auto',
                    color_continuous_scale='purpor',
                    title=f"Cantidad inversores para la industria {selected_value} por pais")
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
                labels={'Valuation ($B)': 'Valorizacion USD Billones ($B)'},
                title=f"Valorizacion durante los años {lineplot_data.Año.min()} - {lineplot_data.Año.max()} para la industria {selected_value}")
    return fig

# definir el contenido del cuadro de texto para mostrar la suma de startups
@app.callback(
    Output('total-startups', 'children'),
    [Input('dropdown', 'value')]
)

def update_total_startups(selected_value):
    total_startups = df[df['Industry'] == selected_value].shape[0]
    return f"{total_startups}"

# Definir el contenido del cuadro de texto para mostrar la suma total de valuación
@app.callback(
    Output('total-inverstor', 'children'),
    [Input('dropdown', 'value')]
)

def update_total_valuation(selected_value):
    total_valuation = df[df['Industry'] == selected_value]['Numero Investor'].sum()
    return f"{total_valuation}"

# Definir la interactividad del histograma de Investor 1
@app.callback(
    Output('investor1-histogram', 'figure'),
    [Input('dropdown', 'value')]
)
def update_investor1_histogram(selected_value):
    df_filtered = df[df['Industry'] == selected_value]
    investor_per_industry = [df_filtered[["Industry", investor]].rename(lambda x: x.split()[0], axis=1) for investor in
                             df.columns if investor.startswith("Investor")]
    investors = pd.concat(investor_per_industry).dropna()
    top10 = investors.Investor.value_counts().nlargest(10).index.tolist()
    investors_filtered = investors[investors.Investor.isin(top10)]
    fig = px.histogram(investors_filtered, x='Investor', title=f"Número de startups por inversor TOP 10 {selected_value}")
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
                        locationmode='country names',
                        color='Industry',
                        title='Mapa Geográfico por Industria')
    return fig

# ejecutar la aplicacion
if __name__ == '__main__':
    app.run_server(debug=True)