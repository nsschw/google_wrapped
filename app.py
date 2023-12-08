from dash import Dash, dcc, html, State, Input, Output, callback
import dash_bootstrap_components as dbc
from data_processor import DataProcessor
from dash.long_callback import DiskcacheLongCallbackManager
import diskcache


cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

                    


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'], long_callback_manager=long_callback_manager)
app.layout = html.Div([
     html.Div(children='Google Wrapped', className="headline"),
     dbc.Row([html.Div(children='Select your data', style={"font-weight": "bold"})]),
     
     # path to json file and date range
     dbc.Row([
          dbc.Col([
               html.Div(children='Path to your JSON file'),
               dcc.Input(id="path", type="text", placeholder="Enter a path...", className="input-text"),
          ], width={"size": 6}, className="input-row"),

           dbc.Col([
               html.Div(children='From'),
               dcc.Input(id='from_date', type='text', placeholder="YYYY-MM-DD", className="input-text", style={"height": "45%"}),
          ], width={"size": 3}),          

          dbc.Col([
               html.Div(children='Until'),
               dcc.Input(id='until_date', type='text', placeholder="YYYY-MM-DD", className="input-text", style={"height": "45%"}),
          ], width={"size": 3}),
     ]),

     # language and submit button
     dbc.Row([
          dbc.Col([
               html.Div(children='Language'),
               dcc.Dropdown(
                    id='language',
                    options=[
                         {'label': 'English', 'value': 'en'},
                         {"label": "German", "value": "de"},
                    ],
                    value='en'
               ),
          ], width={"size": 6}),
          
          dbc.Col([], width={"size": 3}),
          dbc.Col([
                  html.Div(style={"height": "22px"}),
               dbc.Button("Submit", id="submit-button", color="primary", className="button-1", style={"width": "100%"}),
          ], width={"size": 3}),    
     ], className="input-row"),

     # thin line
     html.Div(style={"height": "15px"}),
     html.Div(style={"width": "100%", "height": "2px", "background-color": "#E0E0E0"}),
     html.Div(style={"height": "15px"}),      

     # results
     dbc.Row(id="output_results"),
     
     html.Div(style={"height": "100px"}),
         

], className="wrapper")


@app.long_callback(
     Output("output_results", "children"),
     Input("submit-button", "n_clicks"),
     State("path", "value"),
     State("language", "value"),
     State("from_date", "value"),
     State("until_date", "value"),
     running = [(Output("submit-button", "disabled"), True, False)],
     prevent_initial_call=True,
    )
def update_output(n_clicks, path, language, from_date, until_date):
     
     # load data
     data_processor = DataProcessor(path, lang=language, from_date=from_date, until_date=until_date)     
     basic_facts = data_processor.basic_facts()

     results = [
     
     # Basic Facts
     dbc.Row([
           dbc.Col(
                html.Div([
                     html.H3("Basic Facts", style={"text-align": "center", "font-size": "24px", "font-weight": "bold"}),
                     html.P([html.I(className="fas fa-search"), " Total number of searches: " + str(basic_facts["count_searches"])], style={"text-align": "center", "font-size": "16px"}),
                     html.P([html.I(className="fas fa-calendar-alt"), " Most searches on one day: " +  str(basic_facts["amount_most_searches"][0]) + " on " + str(basic_facts["date_most_searches"])], style={"text-align": "center", "font-size": "16px"}),
                     html.P([html.I(className="fas fa-clock"), " Longest time span without searching: " +  str(basic_facts["longest_pause"])], style={"text-align": "center", "font-size": "16px"}),
                ])
           )], class_name="results"),

     # Searches over time
     dbc.Row([dcc.Graph(figure=data_processor.searches_per_week(), config={"displayModeBar": False})], class_name="results"),   
     dbc.Row([dcc.Graph(figure=data_processor.searches_heatmap(fill_nan=True), config={"displayModeBar": False})], class_name="results"),
     dbc.Row([dcc.Graph(figure=data_processor.searched_most(n=20), config={"displayModeBar": False})], class_name="results"),
     ]

     return results


if __name__ == "__main__":
    app.run_server(debug=True)