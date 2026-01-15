from flask import Flask, jsonify, abort, request, Response
import os
import json
from datetime import datetime
from MainArgs import parse_date, filter_objects
from billgetter import api_bill
from votegetter import api_vote
from lobbygetter import api_lobby
from debategetter import api_debate
from questiongetter import api_question
from pathlib import Path

DATA_FOLDER = Path(
    os.getenv("CIVIE_DATA_FOLDER", Path(__file__).resolve().parent / "Database")
)

app = Flask(__name__)
PAGE_SIZE = 50

@app.route("/API/")
def hello():
    return "API is connected"
@app.route("/API/sector/bill")
def run_bill():
    return api_bill()

@app.route("/API/sector/vote")
def run_vote():
    return api_vote()

@app.route("/API/sector/lobby")
def run_lobby():
    return api_lobby()

@app.route("/API/sector/debate")
def run_debate():
    return api_debate()

@app.route("/API/sector/question")
def run_question():
    return api_question()


@app.route("/API/<id>")
def get_member(id):
    #query params
    query = request.args.get("q", "").strip()
    before = request.args.get("before", "").strip()
    after = request.args.get("after", "").strip()
    
    #parse date params
    before_date = parse_date(before) if before else None
    after_date = parse_date(after) if after else None
    
    result = {}
    
    #fly thru subfolders
    for subfolder in os.listdir(DATA_FOLDER):
        subfolder_path = os.path.join(DATA_FOLDER, subfolder)
        if not os.path.isdir(subfolder_path):
            continue

        #finds jsons matching id
        for filename in os.listdir(subfolder_path):
            if filename.lower().endswith(".json") and id.lower() in filename.lower():
                file_path = os.path.join(subfolder_path, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                        #filter jsons
                        if query or before_date or after_date:
                            filtered_data = filter_objects(data, query, before_date, after_date)
                            if filtered_data:
                                result[subfolder] = filtered_data
                        else:
                            result[subfolder] = data
                        break  #first match per subfolder (there will only ever be 1 match through the whole subfolder)
                except json.JSONDecodeError as e:
                    print("Error decoding " + file_path + ": " + str(e))
                    continue

    if not result:
        error_msg = f"No matching results found for ID {id}"
        if query:
            error_msg += f" with query '{query}'"
        if before_date:
            error_msg += f" before {before}"
        if after_date:
            error_msg += f" after {after}"
        abort(404, description=error_msg)

    return jsonify(result)

if __name__ == "__main__":
    app.run()