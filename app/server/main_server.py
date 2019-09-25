from flask import Blueprint, jsonify
from app.server.util import stats

main = Blueprint('main', __name__)


@main.before_request
def before_request():
    stats.add_request()


@main.route("/stats", methods=["GET"])
def get_stats():
    return jsonify({'requests_per_second': stats.requests_per_second()})



