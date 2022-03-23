from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sequences.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Vendor(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(120), unique=True, index=True, nullable=False)
    urls = db.relationship("Base_Url", backref="vendor", lazy=True)
    sequences = db.relationship("Sequence", backref="vendor", lazy=True)

    def __repr__(self):
        return f"<Vendor %r>" % self.name


class Sequence(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True, unique=True)
    link = db.Column(db.String, nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)

    def __repr__(self):
        return f"<Sequence %r>" % self.name


class Base_Url(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    url = db.Column(db.String, nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"))

    def __repr__(self):
        return f"<Base_Url %r>" % self.url


@app.route("/")
def index():
    return render_template("main.html")
    # con = sqlite3.connect("sequence.db")
    # cur = con.cursor()
    # cur.execute("SELECT * FROM sequences ORDER BY storename, name")
    # rows = cur.fetchall()

    # return render_template("sequences.html", title="Sequences list", rows=rows)


@app.route("/vendors")
def vendors():
    return render_template("vendors.html")


@app.route("/register-vendor", methods=["POST"])
def register_vendor():
    form = request.form
    vendor = Vendor(name=form["name"])
    db.session.add(vendor)
    db.session.commit()
    return "Successfully added vendor"


@app.route("/register-url", methods=["POST"])
def register_url():
    return "Form Submitted"


@app.route("/search", methods=["GET", "POST"])
def sequence():
    # if request.method == "POST":
    #     con = sqlite3.connect("sequence.db")
    #     cur = con.cursor()

    #     cur.execute(
    #         "SELECT storename, name, url FROM sequences "
    #         + "where lower(name) like lower(?) ORDER BY storename, name",
    #         ("%{}%".format(request.form["search_string"]),),
    #     )
    #     return render_template(
    #         "sequence.html",
    #         title="Found Sequences (" + request.form["search_string"] + ")",
    #         records=cur.fetchall(),
    #     )

    return render_template("sequence.html", title="Find A Sequence")


app.config.from_object("config")


if "__main__" == __name__:
    db.create_all()
    app.run(debug=True, port=8080)
