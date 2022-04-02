from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, desc, exc, func, or_

app = Flask(__name__, instance_relative_config=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sequences.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

STRING_FAIL = "fail"
STRING_SUCCESS = "success"


class Vendor(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(120), unique=True, index=True, nullable=False)
    urls = db.relationship("BaseUrl", backref="vendor", lazy=True)
    sequences = db.relationship("Sequence", backref="vendor", lazy=True)
    time_created = db.Column(DateTime(timezone=False), server_default=func.now())
    time_updated = db.Column(DateTime(timezone=False), onupdate=func.now())

    def __repr__(self):
        return f"<Vendor {self.name}>"


class BaseUrl(db.Model):  # type: ignore
    __table_name__ = "Base__Url"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    url = db.Column(db.String, nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    time_created = db.Column(DateTime(timezone=False), server_default=func.now())
    time_updated = db.Column(DateTime(timezone=False), onupdate=func.now())

    def __repr__(self):
        return f"<BaseUrl {self.url}>"


class Sequence(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)
    link = db.Column(db.String, nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    price = db.Column(db.String, nullable=True)
    time_created = db.Column(DateTime(timezone=False), server_default=func.now())
    time_updated = db.Column(DateTime(timezone=False), onupdate=func.now())

    __table_args__ = (
        db.UniqueConstraint("vendor_id", "name", "link", name="sequence_seq_store_idx"),
    )
    #  CREATE UNIQUE INDEX "sequence_seq_store_id" ON "sequence" ( "vendor_id",  "name",  "link")

    def __repr__(self):
        return f"<Sequence() {self.name} {self.link}>"


@app.route("/")
def index():
    newest_25_sequences = Sequence.query.order_by(desc(Sequence.time_created)).limit(25)
    vendor_count = Vendor.query.count()
    sequence_count = Sequence.query.count()

    return render_template(
        "sequence.html",
        title="25 Latest Sequences",
        sequences=newest_25_sequences,
        vendor_count=vendor_count,
        sequence_count=sequence_count,
        today=datetime.now()
    )


@app.route("/vendors")
def vendors():
    v = Vendor.query.all()
    return render_template("vendors.html", vendors=v)


@app.route("/register-vendor", methods=["POST"])
def register_vendor():
    form = request.form
    vendor = Vendor(name=form["name"])
    db.session.add(vendor)
    try:
        session_commit()
        return f"{vendor.name} successfully added vendor."
    except exc.IntegrityError:
        db.session.rollback()
        return "Error"


@app.route("/register-url", methods=["GET", "POST"])
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
    if request.method == "POST":
        search_string = request.form["search_string"]
        sequence_search_result = Sequence.query.filter(Sequence.name.contains(search_string))
        vendor_count = Vendor.query.count()
        sequence_count = Sequence.query.count()

        return render_template(
            "sequence.html",
            title=f"Sequence Search ({ search_string })",
            sequences=sequence_search_result,
            vendor_count=vendor_count,
            sequence_count=sequence_count,
            today=datetime.now()

        )

    return render_template("sequence.html", title="Find A Sequence")


app.config.from_object("config")


def session_commit():
    try:
        db.session.commit()
        return jsonify(meta=STRING_SUCCESS)
    except exc.IntegrityError:
        print("IntegrityError while adding new user")
        db.session.rollback()
        return jsonify(meta=STRING_FAIL)


if __name__ == "__main__":
    print("Creating database")
    db.create_all()
    app.run(debug=True, port=5000)
