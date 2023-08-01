import requests
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Make HTTP request to COVID-19 API endpoint
response = requests.get('https://api.covid19api.com/live/country/united-states')

# Load JSON data into pandas DataFrame
# Dataframe comes from panda and we can use it to create a 2 dimensional spreadsheet looking like structure to store the data.
data = pd.DataFrame(response.json())

# Group data by Province and Date and sum up the Death values
# The group by bellow will be using the data from above to group identical data and also apply function to determine the total death.
# The .reset_index() function will reset the index to the original since the dataframe will be assigning new values as indexes
grouped_data = data.groupby(['Province', 'Date']).sum()['Deaths'].reset_index()

# Convert the date string to a pandas DatetimeIndex and extract only the date part
grouped_data['Date'] = pd.DatetimeIndex(grouped_data['Date']).date

# Group data by Date and sum up the Death values to get total deaths over time for all states
total_deaths_data = data.groupby('Date').sum()['Deaths'].reset_index()

# Convert the date string to a pandas DatetimeIndex and extract only the date part
total_deaths_data['Date'] = pd.DatetimeIndex(total_deaths_data['Date']).date

# Create Dash application
app = dash.Dash(__name__)

# Define options for dropdown menu
# This will return a sorted list based on the unique value which is the state.
options = [{'label': state, 'value': state} for state in sorted(grouped_data['Province'].unique())]

# Define layout of Dash application
app.layout = html.Div([
    html.H1('COVID-19 Deaths by State'),
    dcc.Dropdown(
        id='state-dropdown',
        options=options,
        value=['New York'],
        multi=True
    ),
    dcc.Graph(id='state-deaths-graph'),
    html.H2('Total COVID-19 Deaths in the United States'),
    dcc.Graph(id='total-deaths-graph', figure=px.line(total_deaths_data, x='Date', y='Deaths'))
])

# Define callback function to update line graph when dropdown menu is changed
@app.callback(Output('state-deaths-graph', 'figure'),
              [Input('state-dropdown', 'value')])
def update_figure(selected_states):
    filtered_data = grouped_data[grouped_data['Province'].isin(selected_states)]
    fig = px.line(filtered_data, x='Date', y='Deaths', color='Province')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
