import json


def decode_jsonify(json_result):
    response_data, status_code = json_result
    response_data = json.loads(response_data.get_data(as_text=True))

    return response_data, status_code
