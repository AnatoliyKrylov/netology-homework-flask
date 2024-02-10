from flask import Flask, jsonify, request
from flask.views import MethodView
from pydantic import ValidationError

from models import Session, Adv
from schema import CreateAdv, UpdateAdv

app = Flask("app")


class HttpError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({"error": error.message})
    response.status_code = error.status_code
    return response


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response):
    request.session.close()
    return response


def validate_json(schema_class, json_data):
    try:
        return schema_class(**json_data).dict(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise HttpError(400, error)


def get_adv_by_id(adv_id: int):
    adv = request.session.get(Adv, adv_id)
    if adv is None:
        raise HttpError(404, "Advertisement not found")
    return adv


def add_adv(adv: Adv):
    request.session.add(adv)
    request.session.commit()


class AdvView(MethodView):
    @property
    def session(self) -> Session:
        return request.session

    def get(self, adv_id):
        adv = get_adv_by_id(adv_id)
        return jsonify(adv.dict)

    def post(self):
        json_data = validate_json(CreateAdv, request.json)
        adv = Adv(**json_data)
        add_adv(adv)
        return jsonify({"id": adv.id})

    def patch(self, adv_id):
        json_data = validate_json(UpdateAdv, request.json)
        adv = get_adv_by_id(adv_id)
        for field, value in json_data.items():
            setattr(adv, field, value)
        add_adv(adv)
        return jsonify(adv.dict)

    def delete(self, adv_id):
        adv = get_adv_by_id(adv_id)
        self.session.delete(adv)
        self.session.commit()
        return jsonify({"status": "deleted"})


adv_view = AdvView.as_view("adv_view")

app.add_url_rule("/adv/", view_func=adv_view, methods=["POST"])
app.add_url_rule(
    "/adv/<int:adv_id>/", view_func=adv_view, methods=["GET", "PATCH", "DELETE"]
)


if __name__ == "__main__":
    app.run()
