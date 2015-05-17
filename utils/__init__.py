from json import JSONEncoder


class PangeaMessageEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()

        return JSONEncoder.default(self, obj)


def json_date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj
