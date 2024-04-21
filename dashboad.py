# se importan las librerias
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

# cargar los datos desde el archivos .csv
df = pd.read_csv('Unicorn_Clean.csv')

def count_non_empty_investors(row):
    non_empty_count = sum([1 for investor in row if pd.notna(investor)])
    return non_empty_count

df['non_empty_investors'] = df[['Investor 1', 'Investor 2', 'Investor 3', 'Investor 4']].apply(count_non_empty_investors,
                                                                                                axis=1)

# crear la aplicacion Dash
app = dash.Dash(__name__)

# definir el diseñoo de la aplicacion Dash
app.layout = html.Div([
    html.H1('Dashboard Startup Unicornios'),

    html.Div([
        # grafico de treemap
        dcc.Graph(id='treemap', className='six columns'),

        # grafico heatmap
        dcc.Graph(id='heatmap', className='six columns')
    ], className='row')
])

# funcion de callback para actualizar el grafico treemap
@app.callback(
    [Output('treemap', 'figure'),
    Output('heatmap', 'figure')],
    [Input('treemap', 'clickData')]
)

def update_graph(clickData):
    if clickData is None:
        selected_category = 'Categoria Predeterminada' # define una categoria predeterminada
    else:
        selected_category = clickData['points'][0]['label']

    # filtrar el dataframe por la categoria seleccionada
    filtered_df = df[df['Industry'] == selected_category]

    # calcular el numero de inversores por pais para la categoria seleccionada
    inverstors_by_country = filtered_df.groupby('Country')['non_empty_investors'].sum().reset_index()

    # crear el treemap
    trace_treemap = go.Treemap(
        labels=filtered_df['Country'],
        parents=[''] * len(filtered_df),
        values=filtered_df['non_empty_investors']
    )
    layout_treemap = go.Layout(title=f'Distribucion de Inversores para la industria {selected_category}')
    fig_treemap = {'data': [trace_treemap], 'layout': layout_treemap}

    # crear el heatmap
    trace_heatmap = go.Heatmap(
        x=inverstors_by_country['Country'],
        y=['N° Inversores'],
        z=[inverstors_by_country['non_empty_investors']],
        colorscale= 'Viridis',
        colorbar=dict(title='N° de Inversores')
    )
    layout_heatmap = go.Layout(
        title='Numero de Inversores por Pais',
        xaxis=dict(title='Pais'),
        yaxis=dict(title=''),
        height=500
    )
    fig_heatmap = {'data': [trace_heatmap], 'layout': layout_heatmap}
    return fig_treemap, fig_heatmap

# ejecutar la aplicacion
if __name__ == '__main__':
    app.run_server(debug=True)