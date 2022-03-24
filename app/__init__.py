from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

app = Flask(__name__, instance_relative_config=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sequences.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

STRING_FAIL = 'fail'
STRING_SUCCESS = 'success'


class Vendor(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(120), unique=True, index=True, nullable=False)
    urls = db.relationship('Base_Url', backref='vendor')

    def __repr__(self):
        return f"<Vendor %r>" % self.name


class Base_Url(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    url = db.Column(db.String, nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)

    def __repr__(self):
        return f"<Base_Url %r>" % self.url


class Sequence(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True, unique=True)
    link = db.Column(db.String, nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)

    def __repr__(self):
        return f"<Sequence %r>" % self.name


@app.route("/")
def index():
#   return render_template("main.html")
    # con = sqlite3.connect("sequence.db")
    # cur = con.cursor()
    # cur.execute("SELECT * FROM sequences ORDER BY storename, name")
    # rows = cur.fetchall()

    return render_template("sequence.html", title="Find A Sequence")


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
        return "Successfully added vendor"
    except exc.IntegrityError:
        db.session.rollback()
        return "Error"


#@login_required
@app.route("/register-url", methods=["GET", "POST"])
def register_url():
    if request.method == 'POST':
        form = request.form
        if form["url"] and form["vendor_id"]:
            base_url = Base_Url(url=form["url"], vendor_id=form["vendor_id"])
            db.session.add(base_url)
            db.session.commit()
            return f"{base_url.url} successfully created."
        else:
            return "Missing values."
    else:
        v = Vendor.query.all()
        u = Base_Url.query.all()
    return render_template('urls.html', vendors=v, base_urls=u)


@app.route("/search", methods=["GET", "POST"])
def sequence():
    if request.method == "POST":
        print("Searching...")
        id = 1
        res = Sequence.query.get(id)
        print("Results", res)
    #     con = sqlite3.connect("sequence.db")
    #     cur = con.cursor()

    #     cur.execute(
    #         "SELECT storename, name, url FROM sequences "
    #         + "where lower(name) like lower(?) ORDER BY storename, name",
    #         ("%{}%".format(request.form["search_string"]),),
    #     )
        return render_template(
             "sequence.html",
             title="Found Sequences (" + request.form["search_string"] + ")",
             records={},
         )

    return render_template("sequence.html", title="Find A Sequence")


app.config.from_object("config")


def session_commit():
    try:
        db.session.commit()
        return jsonify(meta = STRING_SUCCESS)
    except exc.IntegrityError:
        print("IntegrityError while adding new user")
        db.session.rollback()
        return jsonify(meta = STRING_FAIL)


if __name__ == 'app':
    db.create_all()
    app.run(debug=True, port=8080)
