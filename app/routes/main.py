from flask import Blueprint


base_bp = Blueprint("base", __name__, url_prefix=None)


@base_bp.route("/", methods=["GET", "POST"])
def index():
    return {"message": "hello WORLDY"}
