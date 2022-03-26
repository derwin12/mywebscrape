from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, or_, UniqueConstraint

app = Flask(__name__, instance_relative_config=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sequences.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

STRING_FAIL = 'fail'
STRING_SUCCESS = 'success'


class Vendor(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(120), unique=True, index=True, nullable=False)
    urls = db.relationship('BaseUrl', backref='vendor')

    def __repr__(self):
        return f"<Vendor %r>" % self.name


class BaseUrl(db.Model):  # type: ignore
    __table_name__ = 'Base__Url'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    url = db.Column(db.String, nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)

    def __repr__(self):
        return f"<BaseUrl %r>" % self.url


class Sequence(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)
    link = db.Column(db.String, nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    __table_args__ = (
        UniqueConstraint('vendor_id', 'name', name='sequence_seq_store_idx'),
    )

    def __repr__(self):
        return f"<Sequence() %r %r>" % (self.name, self.link)


@app.route("/")
def index():
    sequences = Sequence.query.join(Vendor)\
        .add_columns(Sequence.id, Sequence.name, Sequence.link, Vendor.name.label("vendor_name"))\
        .limit(25)

    return render_template(
        "sequence.html",
        title="List Sequences",
        sequences=sequences,
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
    if request.method == 'POST':
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
        u = BaseUrl.query.join(Vendor).add_columns(Vendor.name.label("vendor_name")).order_by(Vendor.name, BaseUrl.url).all()
    return render_template('urls.html', vendors=v, baseurls=u)


@app.route("/search", methods=["GET", "POST"])
def sequence():
    if request.method == "POST":
        ss = request.form["search_string"]

        looking_for = '%{0}%'.format(ss)
        sequences = Sequence.query.join(Vendor)\
            .add_columns(Sequence.id, Sequence.name, Sequence.link, Vendor.name.label("vendor_name"))\
            .filter(or_(Sequence.name.ilike(looking_for), Vendor.name.ilike(looking_for)))\
            .order_by(Vendor.name, Sequence.name)

        return render_template(
             "sequence.html",
             title="Sequence Search (" + request.form["search_string"] + ")",
             sequences=sequences,
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


if __name__ == '__main__':
    print("Creating database")
    db.create_all()
    app.run(debug=True, port=5000)
