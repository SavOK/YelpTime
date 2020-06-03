import json
from pathlib import Path

import numpy as np
import requests

from APIs import YelpAuth, YelpAPI

box_dim = (23000, 25000)  # dim of the box in meters
step_size = 250  # in meters

num_steps = tuple([int(x / step_size) for x in box_dim])
box = {
    "SE": (42.3, -70.9),
    "NE": (42.5, -70.9),
    "SW": (42.3, -71.2),
    "NW": (42.5, -71.2),
    "grid_size": (100, 100),  # makes about 25k x 25k box with step 250
}
box["S_TO_N"] = np.linspace(box["SE"][0], box["NE"][0], box["grid_size"][0])
box["E_TO_W"] = np.linspace(box["SE"][1], box["SW"][1], box["grid_size"][1])
