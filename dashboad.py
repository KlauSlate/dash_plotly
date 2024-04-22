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
    dcc.Graph(id='treemap'),
    html.Hr(), # linea horizontal para separar los graficos
    html.H2('Heatmap de N° de inversores por industria'),
    dcc.Graph(id='heatmap')
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

def update_figure(selected_value):
    filtered_df = df[df['Industry'] == selected_value]
    heatmap_data = filtered_df.groupby(['Industry', 'Country']).size().unstack(fill_value=0)
    fig = px.imshow(heatmap_data.values,
                    labels=dict(x="Country", y="Industry", color="Count"),
                    x=list(heatmap_data.columns),
                    y=list(heatmap_data.index),
                    title="Heatmap de Numeros de inversore por Industria")
    return fig

# ejecutar la aplicacion
if __name__ == '__main__':
    app.run_server(debug=True)