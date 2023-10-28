from flask import jsonify
import inspect


def create_response(item, serializer, status_code=200):

    if inspect.isclass(serializer):
        serializer = serializer()

    if not isinstance(item, dict):
        return jsonify(serializer.dump(item)), status_code
    item_selection = item["items"]
    item["items"] = serializer.dump(item_selection, many=True)
    return item, status_code
