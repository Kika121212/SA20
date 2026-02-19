import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    style={'backgroundColor': '#111111', 'color': '#FFFFFF'},
    children=[
        html.H1(children='Graph Tabs', style={'textAlign': 'center'}),
        dcc.Tabs(
            id='tabs',
            value='tab-1',
            style={'backgroundColor': '#333333'},
            children=[
                dcc.Tab(label='Tab 1', value='tab-1'),
                dcc.Tab(label='Tab 2', value='tab-2'),
                dcc.Tab(label='Tab 3', value='tab-3'),
                dcc.Tab(label='Tab 4', value='tab-4'),
                dcc.Tab(label='Tab 5', value='tab-5')
            ]
        ),
        html.Div(id='tabs-content')
    ]
)

@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Content of Tab 1'),
            # Add graph here for Tab 1
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Content of Tab 2'),
            # Add graph here for Tab 2
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Content of Tab 3'),
            # Add graph here for Tab 3
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Content of Tab 4'),
            # Add graph here for Tab 4
        ])
    elif tab == 'tab-5':
        return html.Div([
            html.H3('Content of Tab 5'),
            dcc.Dropdown(
                id='dropdown',
                options=[
                    {'label': 'Run Worm', 'value': 'run_worm'},
                    {'label': 'Manhattan', 'value': 'manhattan'},
                    {'label': 'Run Rate', 'value': 'run_rate'}
                ],
                value='run_worm'
            ),
            dcc.Graph(id='graph')
        ])

@app.callback(Output('graph', 'figure'), [Input('dropdown', 'value')])
def update_graph(selected_option):
    # Example data
    x = [1, 2, 3, 4]
    y = [10, 15, 13, 17]

    if selected_option == 'run_worm':
        # Create data for Run Worm graph
        return {'data': [go.Scatter(x=x, y=y, mode='lines+markers')], 'layout': go.Layout(title='Run Worm Graph', template='plotly_dark')}
    elif selected_option == 'manhattan':
        # Create data for Manhattan graph
        return {'data': [go.Bar(x=x, y=y)], 'layout': go.Layout(title='Manhattan Graph', template='plotly_dark')}
    elif selected_option == 'run_rate':
        # Create data for Run Rate graph
        return {'data': [go.Box(y=y)], 'layout': go.Layout(title='Run Rate Graph', template='plotly_dark')}

# Add download button functionality
if __name__ == '__main__':
    app.run_server(debug=True)