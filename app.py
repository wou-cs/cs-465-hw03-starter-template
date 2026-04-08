from flask import Flask, request, abort, url_for
from datetime import datetime, timezone

app = Flask(__name__)


@app.route("/api/activities", methods=["GET"])
def get_activities_plural():
    return {'activities': []}, 200

