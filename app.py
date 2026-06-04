from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)

# ---------- Config ----------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------- Model ----------
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500))
    short_code = db.Column(
        db.String(10),
        unique=True
    )

with app.app_context():
    db.create_all()

# ---------- Generate Code ----------
def generate_code(length=6):

    chars = string.ascii_letters + string.digits

    return "".join(
        random.choice(chars)
        for _ in range(length)
    )

# ---------- Create Short URL ----------
@app.route(
    "/shorten",
    methods=["POST"]
)
def shorten_url():

    data = request.get_json()

    short_code = generate_code()

    url = URL(
        original_url=data["url"],
        short_code=short_code
    )

    db.session.add(url)
    db.session.commit()

    return jsonify(
        {
            "original_url": data["url"],
            "short_code": short_code,
            "short_url":
            f"http://localhost:5000/{short_code}"
        }
    )

# ---------- Redirect ----------
@app.route("/<short_code>")
def redirect_url(short_code):

    url = URL.query.filter_by(
        short_code=short_code
    ).first()

    if url:
        return redirect(
            url.original_url
        )

    return jsonify(
        {
            "message": "URL not found"
        }
    ), 404

# ---------- View URLs ----------
@app.route("/urls")
def urls():

    data = URL.query.all()

    return jsonify([
        {
            "id": u.id,
            "original_url": u.original_url,
            "short_code": u.short_code
        }
        for u in data
    ])

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
