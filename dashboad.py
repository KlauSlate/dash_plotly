# se importan las librerias
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

# cargar los datos desde el archivos .csv
df = pd.read_csv('Unicorn_Clean.csv')

# iniciar la aplicacion
app = dash.Dash(__name__)

# diseño de la aplicacion Dash
app.layout = html.Div([
    html.H1('Dashboard de Starptup Unicornio'),

    # dropdown para seleccionar el pais
    dcc.Dropdown(
        id = 'dropdown-pais',
        options = [{'label':pais, 'values':pais} for pais in df['country'].unique()],
        value= 'USA', # valor predeterminado
        clearable = False, # no permitir borrar la seleccion
        searchable = True, # permitir buscar en la lista
        placeholder='Seleccionar un pais'
    ),

    # grafico de barras para visualizar el numero de unicornios por año
    dcc.Graph(id='grafico-unicornios'),
])

# funcion de callback para actualizar el grafico de barras
@app.callback(
    Output('grafico-unicornio', 'figure'),
    [Input('dropdown-pais', 'value')]
)

def update_graph(seleted_country):
    filtered_df = df[df['country'] == seleted_country]
    unicorn_count = filtered_df.groupby('founded_year').size()

    return{
        'data': [{'x':unicorn_count.index, 'y':unicorn_count.values, 'type':'bar'}],
        'layout': {'title': f'Numero de StartUp Unicornios en {seleted_country} por año'}
    }

# ejecutar la aplicacion
if __name__ == '__main__':
    app.run_server(debug=True)