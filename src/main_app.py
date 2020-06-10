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
from test_here import get_data

from help_functions_app import get_categries_list

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

mapbox_access_token = open(config.PROJECT_LOC + "/.configs/mapbox.api").read()


start_point = (42.355, -71.07)
# data = get_data(point)
# data.to_csv("./test.csv", index=False)
data = pd.read_csv("./test.csv")


def make_dash_table(df):
    """ Return a dash defintion of an HTML table from a Pandas dataframe. """
    df_to_show = df[["name", "address", "travelTime", "routeDistance"]].rename(
        columns={
            "name": "Name",
            "address": "Address",
            "travelTime": "Travel Time",
            "routeDistance": "Route Distance",
        }
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
                                    id="business-type-dropdown",
                                    options=get_categries_list(),
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
                                [dl.TileLayer(), dl.LayerGroup(id="my-position")],
                                id="result-map",
                                style={
                                    "width": "100%",
                                    "height": "100vh",
                                    "margin": "auto",
                                    "display": "block",
                                },
                                center=start_point,
                                zoom=13,
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


@app.callback(
    [Output("result-table", "children"), Output("my-position", 'children')],
    [Input("result-map", "click_lat_lng")],
)
def map_click(click_lat_lng):
    if click_lat_lng is None:
        raise PreventUpdate

    df = get_data(click_lat_lng)
    table = make_dash_table(df)
    center_marker = [
        dl.Marker(position=click_lat_lng, children=dl.Tooltip("You are here"))
    ]
    return table, center_marker


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=80)

# pyo.plot(fig, filename="test.html")
