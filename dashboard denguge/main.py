import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Cargar datos
df = pd.read_csv('datos_abiertos_vigilancia_dengue_2000_2023.csv')

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Layout con filtros, gráficos y tabla de provincias
app.layout = html.Div(children=[
    html.H1('Dashboard de Casos de Dengue', style={'textAlign': 'center', 'color': '#333'}),

    # Primera fila: Filtros, gráficos y tabla
    html.Div(
        children=[




            # Filtro por provincia y gráfico de distritos
            html.Div(
                children=[
                    html.H3("Filtrar por Provincia"),
                    dcc.Dropdown(id='dropdown-provincia', options=[], value=None, style={'width': '100%'}),
                    dcc.Graph(id='graph-distrito', style={'width': '100%', 'height': '500px'})
                ],
                style={'width': '30%', 'padding': '20px'}
            ),
                        # Separador (Pipe) con total de casos y tabla de provincias
            html.Div(
                children=[
                    html.H3("Total de Casos"),
                    html.Div(id="total-casos", style={'fontSize': '24px', 'marginBottom': '20px', 'color': '#d9534f'}),
                    
                    html.H3("Casos por Provincia"),
                    dash_table.DataTable(
                        id='tabla-provincias',
                        columns=[
                            {"name": "Provincia", "id": "provincia"},
                            {"name": "Casos", "id": "Casos"},
                            {"name": "Porcentaje (%)", "id": "Porcentaje"}
                        ],
                        style_table={'width': '100%', 'margin': 'auto'},
                        style_cell={'textAlign': 'center', 'fontSize': '16px'}
                    )
                ],
                style={'width': '30%', 'textAlign': 'center', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}
            ),
                        # Filtro por departamento y gráfico de provincias (Pie)
            html.Div(
                children=[
                    html.H3("Filtrar por Departamento"),
                    dcc.Dropdown(
                        id='dropdown-departamento',
                        options=[{'label': i, 'value': i} for i in df['departamento'].unique()],
                        value='PIURA',
                        style={'width': '50%'}
                    ),
                    dcc.Graph(id='graph-provincia', style={'width': '100%', 'height': '500px'})
                ],
                style={'width': '20%', 'padding': '20px'}
            )
        ],
        style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-between'}
    ),

    # Segunda fila: Gráfico de línea de tiempo
html.Div(
    children=[
        html.Div(children=[
            html.H3("Evolución de Casos a lo Largo de los Años", style={'textAlign': 'center'}),
            dcc.Graph(id='graph-linea-tiempo', style={'width': '100%', 'height': '500px'})
        ],
        style={'width': '30%', 'padding': '20px'}
        ),
          html.Div(children=[
            html.H3("Recuento de pacientes por edad", style={'textAlign': 'center'}),
            # dcc.Dropdown(
            #             id='dropdown-sexo',
            #             options=[{'label': i, 'value': i} for i in df['departamento'].unique()],
            #             value='M',
            #             style={'width': '100%'}
            #         ),
            dcc.Graph(id='graph-pie-edad', style={'width': '100%', 'height': '500px'})
        ],
        style={'width': '30%', 'padding': '20px'}
        ),
                html.Div(children=[
            html.H3("Recuento de pacientes por sexo", style={'textAlign': 'center'}),
            # dcc.Dropdown(
            #             id='dropdown-sexo',
            #             options=[{'label': i, 'value': i} for i in df['departamento'].unique()],
            #             value='M',
            #             style={'width': '100%'}
            #         ),
            dcc.Graph(id='graph-pie-sex', style={'width': '100%', 'height': '500px'})
        ],
        style={'width': '20%', 'padding': '20px'}
        )
    ],
    style={'display': 'flex', 'justify-content': 'space-between', 'padding': '20px'}
)

])

# Callback para actualizar el gráfico de provincias, dropdown de provincia y tabla
@app.callback(
    Output('graph-provincia', 'figure'),
    Output('dropdown-provincia', 'options'),
    Output('dropdown-provincia', 'value'),
    Output('tabla-provincias', 'data'),
    Output('total-casos', 'children'),
    Input('dropdown-departamento', 'value')
)
def update_provincia_graph(selected_department):
    filtered_df = df[df['departamento'] == selected_department]
    grouped_df = filtered_df.groupby('provincia').size().reset_index(name='Casos')
    total_cases = grouped_df['Casos'].sum()
    grouped_df['Porcentaje'] = (grouped_df['Casos'] / total_cases * 100).round(2)

    # Gráfico de Pie para provincias
    fig = px.pie(grouped_df, names="provincia", values="Casos", title=f'Casos en {selected_department}')

    # Opciones del dropdown de provincia
    provincia_options = [{'label': p, 'value': p} for p in grouped_df['provincia'].unique()]
    provincia_value = provincia_options[0]['value'] if provincia_options else None

    return fig, provincia_options, provincia_value, grouped_df.to_dict('records'), f'Total: {total_cases} casos'

# Callback para actualizar el gráfico de distritos
@app.callback(
    Output('graph-distrito', 'figure'),
    Input('dropdown-departamento', 'value'),
    Input('dropdown-provincia', 'value')
)
def update_distrito_graph(selected_department, selected_province):
    if not selected_province:
        return px.bar()

    filtered_df = df[(df['departamento'] == selected_department) & (df['provincia'] == selected_province)]
    grouped_df = filtered_df.groupby('distrito').size().reset_index(name='Casos')

    fig = px.bar(grouped_df, x="distrito", y="Casos", color="distrito", barmode="group")
    fig.update_layout(title=f'Casos en {selected_province}', template="plotly_white")

    return fig

# Callback para actualizar el gráfico de línea de tiempo (total de casos por año)
@app.callback(
    Output('graph-linea-tiempo', 'figure'),
    Input('dropdown-departamento', 'value'),
    Input('dropdown-provincia', 'value')
)
def update_linea_tiempo_graph(selected_department, selected_province):
    # Filtrar por departamento y provincia
    filtered_df = df[df['departamento'] == selected_department]
    if selected_province:
        filtered_df = filtered_df[filtered_df['provincia'] == selected_province]

    # Agrupar por año y contar casos
    grouped_df = filtered_df.groupby('ano').size().reset_index(name='Casos')

    # Gráfico de línea
    fig = px.line(grouped_df, x="ano", y="Casos", markers=True, title="Evolución de Casos a lo Largo de los Años")
    fig.update_layout(template="plotly_white", xaxis_title="Año", yaxis_title="Casos", hovermode="x unified")

    return fig


# Callback para actualizar el gráfico de línea de tiempo (total de casos por año)
@app.callback(
    Output('graph-pie-sex', 'figure'),
    Input('dropdown-departamento', 'value'),
    Input('dropdown-provincia', 'value')
)

def update_sex_graph(selected_department, selected_province):
    filtered_df = df[df['departamento'] == selected_department]
    if selected_province:
         filtered_df = filtered_df[filtered_df['provincia'] == selected_province]

    grouped_df = filtered_df.groupby('sexo').size().reset_index(name='Casos')
    total_cases = grouped_df['Casos'].sum()
    grouped_df['Porcentaje'] = (grouped_df['Casos'] / total_cases * 100).round(2)

    # Gráfico de Pie para provincias
    fig = px.pie(grouped_df, names="sexo", values="Casos", title=f'Casos en {selected_department}')



    return fig

# Callback para actualizar el gráfico de línea de tiempo (total de casos por año)
@app.callback(
    Output('graph-pie-edad', 'figure'),
    Input('dropdown-departamento', 'value'),
    Input('dropdown-provincia', 'value')
)
def update_age_graph(selected_department, selected_province):
    filtered_df = df[df['departamento'] == selected_department]
    if selected_province:
         filtered_df = filtered_df[filtered_df['provincia'] == selected_province]

    grouped_df = filtered_df.groupby('edad').size().reset_index(name='Casos')
    total_cases = grouped_df['Casos'].sum()
    grouped_df['Porcentaje'] = (grouped_df['Casos'] / total_cases * 100).round(2)

    # Gráfico de barras
    fig = px.bar(
        grouped_df, 
        x="edad", 
        y="Casos", 
        title=f'Casos por edad en {selected_department}',
        labels={'edad': 'Edad', 'Casos': 'Número de Casos'},
        text="Casos"
    )
    
    fig.update_traces(textposition='outside')  # Muestra los valores sobre las barras
    fig.update_layout(xaxis_title="Edad", yaxis_title="Número de Casos")


    return fig
# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
