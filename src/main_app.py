from pathlib import Path
import json
import pandas as pd
import pprint

import dash
import dash_leaflet as dl
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from plotly import graph_objs as go

import plotly.offline as pyo

import config

import help_functions_app as hfa

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

mapbox_access_token = open(config.PROJECT_LOC + "/.configs/mapbox.api").read()


start_point = (42.355, -71.07)
# data = get_data(point)
# data.to_csv("./test.csv", index=False)
data = pd.read_csv("./test.csv")


def make_dash_table(df: pd.DataFrame):
    """ Return a dash defintion of an HTML table from a Pandas dataframe. """
    df_to_show = (
        df[["name", "address_display", "travel", "distance"]]
        .rename(
            columns={
                "name": "Name",
                "address_display": "Address",
                "travel": "Travel Time",
                "distance": "Route Distance",
            }
        )
        .sort_values(by=["Travel Time"])
    )
    table = dash_table.DataTable(
        id="formated-table",
        data=df_to_show.to_dict("records"),
        columns=[{"id": c, "name": c} for c in df_to_show.columns],
        fixed_rows={"headers": True},
        fixed_columns={"headers": True},
        style_table={"height": "40%", "overflowY": "auto", "overflowX": "auto"},
        page_size=10,
        style_data={"whiteSpace": "normal"},  # , "height": "auto"},
        style_cell_conditional=[
            {"if": {"column_id": "Address"}, "width": "40%", "textAlign": "left"},
            {"if": {"column_id": "Name"}, "width": "30%", "textAlign": "left"},
            {"if": {"column_id": "Travel Time"}, "width": "15%"},
            {"if": {"column_id": "Route Distance"}, "width": "15%"},
        ],
        style_cell={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
        sort_action="native",
        # sort_mode="single",
    )
    return table


def make_default_map(point):
    fig = go.Figure(data=[go.Scattermapbox(),])
    fig.update_layout(
        autosize=True,
        hovermode="closest",
        margin=go.layout.Margin(l=0, r=35, t=0, b=0),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(lat=point[0], lon=point[1]),
            pitch=0,
            zoom=13,
        ),
        showlegend=False,
    )
    return fig


# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.H2("DASH - Yelp Time"),
                        html.P(
                            """Select location on map. 
                            Select business type and transportation type in dropdown menu"""
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="list-state-dropdown",
                                    options=hfa.get_list_of_states(),
                                    placeholder="Select a state",
                                )
                            ],
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="business-type-dropdown",
                                    options=hfa.get_categories_list(),
                                    placeholder="Select a business type",
                                )
                            ],
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="transportation-type-dropdown",
                                            options=[
                                                {
                                                    "label": "Walking",
                                                    "value": "pedestrian",
                                                },
                                                {"label": "Driving", "value": "car"},
                                            ],
                                            placeholder="Select a transportation type",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-slider",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Slider(
                                            id="time-limit-slider",
                                            min=5,
                                            max=30,
                                            step=None,
                                            marks={
                                                5: "5 min",
                                                10: "10 min",
                                                15: "15 min",
                                                20: "20 min",
                                                30: "30 min",
                                            },
                                            value=5,
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dl.Map(
                            dl.Map(
                                [
                                    dl.TileLayer(),
                                    dl.LayerGroup(id="my-position"),
                                    dl.LayerGroup(id="places-markers"),
                                ],
                                id="result-map",
                                style={
                                    "width": "100%",
                                    "height": "100vh",
                                    "margin": "auto",
                                    "display": "block",
                                },
                                center=start_point,
                                zoom=10,
                            ),
                        ),
                        html.Div(
                            className="text-padding",
                            id="result-text",
                            children=["Places near by"],
                        ),
                        html.Div(id="result-table", children=[]),
                    ],
                ),
            ],
        )
    ]
)


@app.callback([Output("result-map", "center")], [Input("list-state-dropdown", "value")])
def move_to_state(value):
    if value is None:
        raise PreventUpdate
    state_dict = hfa.get_state_coord_dict()
    return [state_dict[value]]


@app.callback(
    [
        Output("result-table", "children"),
        Output("my-position", "children"),
        Output("places-markers", "children"),
    ],
    [
        Input("result-map", "click_lat_lng"),
        Input("business-type-dropdown", "value"),
        Input("transportation-type-dropdown", "value"),
        Input("time-limit-slider", "value"),
    ],
)
def map_click(click_lat_lng, business_type, transportation_type, time_limit):
    if click_lat_lng is None:
        raise PreventUpdate
    if business_type is None:
        raise PreventUpdate
    if transportation_type is None:
        raise PreventUpdate
    if time_limit is None:
        raise PreventUpdate

    time_limit = time_limit * 60
    print(click_lat_lng, time_limit, transportation_type, business_type)
    df = hfa.get_data_around_point(
        click_lat_lng, time_limit, transportation_type, business_type
    )
    if df is None:
        raise PreventUpdate
    table = make_dash_table(df)
    center_marker = [
        dl.Marker(position=click_lat_lng, children=dl.Tooltip("You are here"))
    ]
    df = df.sort_values(by="travel")
    markers = [
        dl.Marker(
            position=row[1][["latitude", "longitude"]].values,
            children=dl.Tooltip(row[1]["name"]),
        )
        for row in df.iterrows()
    ]

    return table, center_marker, markers


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=80)

# pyo.plot(fig, filename="test.html")
