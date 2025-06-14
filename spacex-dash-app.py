# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Get unique launch sites for the dropdown
# Obtener sitios de lanzamiento únicos para el menú desplegable
launch_sites = spacex_df['Launch Site'].unique().tolist()
# Add 'ALL' option to the beginning of the list
# Añadir la opción 'ALL' al principio de la lista
launch_sites.insert(0, 'ALL')

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                 dcc.Dropdown(id='site-dropdown',
                                              options=[
                                                  {'label': 'All Sites', 'value': 'ALL'}
                                              ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                              value='ALL', # Default value for the dropdown
                                              placeholder="Select a Launch Site here", # Placeholder text
                                              searchable=True # Enable search functionality
                                ),
                                 html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                               
                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                min=0,
                                max=10000,
                                step=1000,
                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                value=[min_payload, max_payload]
                                ),
                                html.Br(),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Filter for successful launches (Class == 1) across all sites
        # Filtrar lanzamientos exitosos (Class == 1) en todos los sitios
        # Calculate success counts for each site for the 'ALL' case
        filtered_df_success = spacex_df[spacex_df['class'] == 1]
        success_by_site = filtered_df_success.groupby('Launch Site')['class'].count().reset_index()
        fig = px.pie(success_by_site,
                     values='class',
                     names='Launch Site',
                     title='Total Successful Launches By Site')
        return fig
    else:
        # Filter data for the selected site
        # Filtrar datos para el sitio seleccionado
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count successful (1) and failed (0) launches for the selected site
        # Contar lanzamientos exitosos (1) y fallidos (0) para el sitio seleccionado
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count'] # Rename columns for clarity
        fig = px.pie(class_counts,
                     values='count',
                     names='class',
                     title=f'Total Launches for site {entered_site} (1=Success, 0=Failure)')
        return fig
 
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    # Filter by payload range first
    # Filtrar primero por rango de carga útil
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    if entered_site == 'ALL':
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title='Correlation Between Payload and Success for All Sites')
        return fig
    else:
        # Filter by selected site after filtering by payload range
        # Filtrar por sitio seleccionado después de filtrar por rango de carga útil
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=f'Correlation Between Payload and Success for {entered_site}')
        return fig


# Run the app
if __name__ == '__main__':
    app.run()
