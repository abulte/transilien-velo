import json
import os
import traceback

from datetime import timedelta, datetime
from functools import cache

import human_readable
import requests

from flask import Flask, render_template, request

from mappings import pm_imgs, mode_imgs

app = Flask(__name__)

NAVITIA_COVERAGE = "fr-idf"
NAVITIA_URL = f"https://api.navitia.io/v1/coverage/{NAVITIA_COVERAGE}"
NAVITIA_AUTH = {"headers": {"Authorization": os.getenv("NAVITIA_TOKEN")}}


@cache
def get_place(query: str) -> dict:
    app.logger.debug(f"Getting place for {query}...")
    r = requests.get(f"{NAVITIA_URL}/places?q={query}", **NAVITIA_AUTH)
    r.raise_for_status()
    return r.json()["places"][0]["id"]


def get_journey(params: dict) -> dict:
    if test_file := request.form.get("test"):
        app.logger.debug(f"Using test file {test_file}...")
        with open(f"static/data/{test_file}.json") as f:
            return json.load(f)
    app.logger.debug(f"Searching itinerary for {params}...")
    r = requests.get(f"{NAVITIA_URL}/journeys", params=params, **NAVITIA_AUTH)
    r.raise_for_status()
    return r.json()


@app.route("/")
def home():
    return render_template("index.html.j2")


@app.route("/search", methods=["POST"])
def search():
    try:
        departure = get_place(request.form["departure"])
        arrival = get_place(request.form["arrival"])
        dt = request.form.get("datetime")
        dt_type = request.form["dt_type"]
        authorize_bus = request.form.get("authorize_bus")
        forbidden_uris = ["commercial_mode:Metro"]
        if not authorize_bus:
            forbidden_uris.append("commercial_mode:Bus")
        params = {
            "from": departure,
            "to": arrival,
            "first_section_mode[]": "bike",
            "last_section_mode[]": ["bike", "bss"],
            "forbidden_uris[]": forbidden_uris,
            "max_bike_direct_path_duration": 3600,
            "max_bike_duration_to_pt": 3600,
        }
        if dt:
            params["datetime"] = dt
            params["datetime_represents"] = dt_type
        data = get_journey(params)
    except Exception as error:
        app.logger.error(error, exc_info=True)
        tb = traceback.format_exc() if app.debug else None
        return render_template("error.html.j2", error=error, traceback=tb)

    return render_template("results.html.j2", data=data, pm_imgs=pm_imgs, mode_imgs=mode_imgs)


@app.template_filter(name="duration")
def tpl_duration(value: int) -> str:
    # TODO: in request middleware?
    human_readable.i18n.activate("fr_FR")
    duration = timedelta(seconds=value)
    return human_readable.precise_delta(duration, minimum_unit="minutes", formatting="0.0f")


@app.template_filter(name="datetime")
def tpl_datetime(value: str) -> str:
    dt = datetime.strptime(value, "%Y%m%dT%H%M%S")
    return dt.strftime("%Hh%M")
