import logging
import os
import re
from datetime import datetime
from urllib.parse import urlsplit

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, and_, desc, exc, func, or_
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, instance_relative_config=True)
logging.basicConfig(
    filename="app.log",
    level=logging.WARN,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)


auth = HTTPBasicAuth()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sequences.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

STRING_FAIL = "fail"
STRING_SUCCESS = "success"

load_dotenv()  # take environment variables from .env.
PASSWORD = os.getenv("PASSWORD", "Missing admin password")

users = {
    "admin": generate_password_hash(PASSWORD),
}


class Vendor(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(120), unique=True, index=True, nullable=False)
    urls = db.relationship("BaseUrl", backref="vendor", lazy=True)
    sequences = db.relationship("Sequence", backref="vendor", lazy=True)
    time_created = db.Column(DateTime(timezone=False), server_default=func.now())
    time_updated = db.Column(
        DateTime(timezone=False), server_default=func.now(), onupdate=func.now()
    )
    sequence_count = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Vendor {self.name}>"


class BaseUrl(db.Model):  # type: ignore
    __table_name__ = "Base__Url"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    url = db.Column(db.String, nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    time_created = db.Column(DateTime(timezone=False), server_default=func.now())
    time_updated = db.Column(
        DateTime(timezone=False), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<BaseUrl {self.url}>"


class Sequence(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)
    link = db.Column(db.String, nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    price = db.Column(db.String, nullable=True)
    time_created = db.Column(DateTime(timezone=False), server_default=func.now())
    time_updated = db.Column(
        DateTime(timezone=False), server_default=func.now(), onupdate=func.now()
    )
    time_price_changed = db.Column(DateTime(timezone=False), server_default=func.now())

    __table_args__ = (
        db.UniqueConstraint("vendor_id", "name", "link", name="sequence_seq_store_idx"),
    )
    #  CREATE UNIQUE INDEX "sequence_seq_store_id" ON "sequence" ( "vendor_id",  "name",  "link")

    def __repr__(self):
        return f"<Sequence() {self.name} {self.link}>"


@app.route("/")
def index():
    app.logger.info("Top 25")
    newest_25_sequences = Sequence.query.order_by(desc(Sequence.time_created)).limit(25)
    vendor_count = Vendor.query.count()
    sequence_count = Sequence.query.count()

    return render_template(
        "mainpage.html",
        title="25 Latest Sequences",
        tabtitle="Sequence Index",
        sequences=[normalize_price(x) for x in newest_25_sequences],
        vendor_count=vendor_count,
        sequence_count=sequence_count,
        today=datetime.now(),
    )


@app.route("/vendors")
@auth.login_required
def vendors():
    v = Vendor.query.all()
    return render_template("vendors.html", vendors=v)


@app.route("/register-vendor", methods=["POST"])
@auth.login_required
def register_vendor():
    form = request.form
    vendor = Vendor(name=form["name"])
    app.logger.info("Adding vendor: {%s}", vendor)
    db.session.add(vendor)
    try:
        session_commit()
        return f"{vendor.name} successfully added vendor."
    except exc.IntegrityError:
        db.session.rollback()
        return "Error"


@app.route("/urls", methods=["GET", "POST"])
@auth.login_required
def register_url():
    if request.method == "POST":
        form = request.form
        if form["url"] and form["vendor_id"]:
            baseurl = BaseUrl(url=form["url"], vendor_id=form["vendor_id"])
            db.session.add(baseurl)
            session_commit()
            return f"{baseurl.url} successfully created."
        else:
            return "Missing values."
    else:
        v = Vendor.query.order_by(Vendor.name)
        u = (
            BaseUrl.query.join(Vendor)
            .add_columns(Vendor.name.label("vendor_name"))
            .order_by(Vendor.name, BaseUrl.url)
            .all()
        )
    return render_template("urls.html", vendors=v, baseurls=u)


@app.route("/search", methods=["GET", "POST"])
def sequence():
    if request.method == "GET" and request.args.get("query") is None:
        return redirect(url_for("index"))

    if request.method == "GET":
        search_string = request.args.get("query")
        search_type = "all"
    else:
        search_string = request.form["search_string"]
        search_type = request.form["search_type"]

    print("Search: {%s} {%s}" % (search_string, search_type))
    app.logger.info("Search: {%s} {%s}", search_string, search_type)

    if search_type == "free":
        sequence_search_result = Sequence.query.join(Vendor).filter(
            and_(Sequence.price == "Free"),
            or_(
                Sequence.name.contains(search_string),
                Vendor.name.contains(search_string),
            ),
        )
    elif search_type == "paid":
        sequence_search_result = Sequence.query.join(Vendor).filter(
            and_(Sequence.price != "Free"),
            or_(
                Sequence.name.contains(search_string),
                Vendor.name.contains(search_string),
            ),
        )
    elif search_type == "uxsg":
        sequence_search_result = Sequence.query.join(Vendor).filter(
            and_(Vendor.name != "UXSG"),
            or_(
                Sequence.name.contains(search_string),
                Vendor.name.contains(search_string),
            ),
        )
    elif search_type == "freeuxsg":
        sequence_search_result = Sequence.query.join(Vendor).filter(
            and_(Vendor.name != "UXSG"),
            and_(Sequence.price == "Free"),
            or_(
                Sequence.name.contains(search_string),
                Vendor.name.contains(search_string),
            ),
        )
    else:
        sequence_search_result = Sequence.query.join(Vendor).filter(
            or_(
                Sequence.name.contains(search_string),
                Vendor.name.contains(search_string),
            )
        )
    vendor_count = Vendor.query.count()
    sequence_count = Sequence.query.count()

    return render_template(
        "sequence.html",
        title=f"Sequence Search ({ search_string })",
        sequences=[normalize_price(x) for x in sequence_search_result],
        vendor_count=vendor_count,
        sequence_count=sequence_count,
        today=datetime.now(),
        search_string=search_string,
    )


@app.route("/vendor-list", methods=["GET"])
def vendor_list():
    app.logger.info("Vendor List")
    vendorquery = Vendor.query.order_by(Vendor.name).all()

    # This extra logic is needed because some vendors don't have urls in the database.
    vendorlist = []
    for vendor in vendorquery:
        try:
            url = f"https://{urlsplit(vendor.urls[0].url).netloc}"
        except IndexError:
            url = ""

        name = vendor.name
        sequence_count = vendor.sequence_count
        vendorlist.append({"name": name, "url": url, "sequence_count": sequence_count})

    return render_template("vendor_list.html", title="Vendor List", vendors=vendorlist)


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username, ""), password):
        return username


app.config.from_object("config")


def session_commit():
    try:
        db.session.commit()
        return jsonify(meta=STRING_SUCCESS)
    except exc.IntegrityError:
        print("IntegrityError while adding new user")
        db.session.rollback()
        return jsonify(meta=STRING_FAIL)


def normalize_price(sequence: Sequence) -> Sequence:
    price = sequence.price
    if "free" in price.lower():
        sequence.price = "Free"
        return sequence

    try:
        price = float(re.sub(r"[^0-9\.]", "", price))
        sequence.price = f"${price:.2f}"
    except ValueError:
        sequence.price = "Unknown"

    return sequence


if __name__ == "__main__":
    print("Creating database")
    db.create_all()
    app.run(debug=True, port=5000)
