import json


class BaseVo:
    def to_Json(self):
        return json.dumps(self, default=lambda o: o.__dict__, allow_nan=False, sort_keys=False, indent=4)
