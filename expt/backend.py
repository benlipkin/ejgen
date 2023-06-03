import os
import json

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS


class DictPersistJSON(dict):
    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self._load()
        self.update(*args, **kwargs)

    def _load(self):
        if os.path.isfile(self.filename) and os.path.getsize(self.filename) > 0:
            with open(self.filename, "r") as fh:
                self.update(json.load(fh))

    def _dump(self):
        with open(self.filename, "w") as fh:
            json.dump(self, fh)

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        self._dump()

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return "%s(%s)" % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
        self._dump()


app = Flask(__name__)
CORS(app)

N_SETS = 36
EPSILON = 0.01
DB_FILENAME = "db.json"
INIT_DB = lambda n: DictPersistJSON(DB_FILENAME, **{str(k + 1): 0.0 for k in range(n)})
if not os.path.isfile(DB_FILENAME):
    DATABASE = INIT_DB(N_SETS)
else:
    DATABASE = DictPersistJSON(DB_FILENAME)


def prep_stimuli(stim_id):
    fname = f"materials/stims_{int(stim_id):02d}.csv"
    table = pd.read_csv(fname)
    stimuli = [
        {"stimulus": "<p>" + stim.replace(".' ", ".'</p><p>") + "</p>"}
        for stim in table["stimulus"].values
    ]
    return stimuli


@app.route("/start", methods=["GET"])
def get_data_and_open_count():
    stim_id = min(DATABASE, key=DATABASE.get)
    DATABASE[stim_id] += EPSILON
    return jsonify({"stim_id": stim_id, "stim_contents": prep_stimuli(stim_id)})


@app.route("/complete", methods=["POST"])
def complete_view_and_close_count():
    stim_id = request.json["stim_id"]
    DATABASE[stim_id] += 1 - EPSILON
    return "OK"


@app.route("/status", methods=["GET"])
def get_current_progress_status():
    return jsonify(DATABASE)


@app.route("/reset", methods=["GET"])
def reset_database():
    global DATABASE
    DATABASE = INIT_DB(N_SETS)
    return "OK"


@app.route("/", methods=["GET"])
def test_connection():
    return "OK"


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=80)
