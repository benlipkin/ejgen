import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

N_SETS = 36
EPSILON = 0.01
INIT_DB = lambda n: {k + 1: 0.0 for k in range(n)}
DATABASE = INIT_DB(N_SETS)


def prep_stimuli(stim_id):
    fname = f"materials/stims_{stim_id:02d}.csv"
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
