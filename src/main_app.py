from pathlib import Path
import pandas as pd

import plotly.graph_objects as go
import plotly.offline as pyo

from test_here import get_data

import config

mapbox_access_token = open(config.PROJECT_LOC + "/.configs/mapbox.api").read()


point = (42.306, -71.067)
data = get_data(point)

fig = go.Figure(
    data=[
        go.Scattermapbox(
            lat=data["latitude"],
            lon=data["longitude"],
            mode="markers",
            marker={"size": 15, "symbol": "restaurant", "allowoverlap": True},
            text=data["name"],
        ),
        go.Scattermapbox(
            lat=[point[0]],
            lon=[point[1]],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=18, color="rgb(242, 177, 172)",
            ),
            text=["You Are Here"],
        ),
    ]
)
fig.update_layout(
    autosize=True,
    hovermode="closest",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(lat=point[0], lon=point[1]),
        pitch=0,
        zoom=14,
    ),
    showlegend=False,
)

pyo.plot(fig, filename="test.html")
