from flask import Flask, jsonify, abort, request, Response
import json
from api.MainArgs import parse_date, filter_objects
from pathlib import Path

PAGE_SIZE = 50 

BASE_DIR = Path(__file__).resolve().parent
BILLS = BASE_DIR / "Database" / "json-all" / "bills.json"

def api_bill():
    page = request.args.get("page", 1, type=int)
    query = request.args.get("q", "").strip()
    before = request.args.get("before", "").strip()
    after = request.args.get("after", "").strip()

    before_date = parse_date(before) if before else None
    after_date = parse_date(after) if after else None

    try:
        with open(BILLS, "r", encoding="utf-8") as f:
            data = json.load(f)

            #filter for query
            if query or before_date or after_date:
                filtered_data = filter_objects(data, query, before_date, after_date)
                full_list = filtered_data if filtered_data else []
            else:
                full_list = data

            #is list
            if isinstance(full_list, dict):
                full_list = list(full_list.values())

            start_idx = (page - 1) * PAGE_SIZE
            end_idx = start_idx + PAGE_SIZE
            paginated_list = full_list[start_idx:end_idx]

            full_list_length = len(full_list)
            full_list = []  # free memory

    except json.JSONDecodeError as e:
        abort(500, description=f"Error decoding {BILLS}: {e}")

    if not paginated_list:
        abort(404, description="No results found")

    response_data = {
        "page": page,
        "page_size": PAGE_SIZE,
        "total_objects": full_list_length,
        "data": paginated_list
    }

    return Response(
        json.dumps(response_data, ensure_ascii=False),
        mimetype="application/json"
    )
