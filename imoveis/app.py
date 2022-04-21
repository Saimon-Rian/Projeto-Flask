from os import environ
from flask import *
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from flask_login import LoginManager, login_user, login_required, UserMixin, current_user, logout_user
from form import LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:senha@127.0.0.1:3310/imoveis_db"
app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user = db.Column(db.String(100), unique=True) # Mudar de user para user_name
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(100))
    posts = db.relationship("Realty", backref='poster')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __init__(self, name, user, email, password):
        self.name = name
        self.user = user
        self.email = email
        self.password = password


class Realty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact = db.Column(db.String(150))
    realty = db.Column(db.String(200))
    state = db.Column(db.String(100))
    locality = db.Column(db.String(100))
    value = db.Column(db.Float())
    users_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __int__(self, name, contact, realty, state, locality, value):
        self.name = name
        self.contact = contact
        self.realty = realty
        self.state = state
        self.locality = locality
        self.value = value


# Home
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


# List
@app.route("/list")
@login_required
def list():
    realty = Realty.query.all()
    return render_template("list.html", realty=realty)


# Register realty
@app.route("/register_realty", methods=["GET", "POST"])
@login_required
def register():
    user_list = Users.query.all()
    if request.method == "POST":
        realty = Realty(name=request.form['name'], contact=request.form['contact'], realty=request.form['realty'],
                      state=request.form['state'], locality=request.form['locality'], value=request.form['value'],
                        users_id=request.form['owner'])
        db.session.add(realty)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template("register_realty.html", user_list=user_list)


# Delete
@app.route("/delete/<int:id>")
@login_required
def delete(id):
    realty = Realty.query.get(id)
    db.session.delete(realty)
    db.session.commit()
    return redirect(url_for("list"))


# Edit
@app.route("/edit/<int:id>", methods=["POST", "GET"])
@login_required
def edit(id):
    realty = Realty.query.get(id)
    if request.method == "POST":
        realty.id = request.form["id"]
        realty.name = request.form["name"]
        realty.contact = request.form["contact"]
        realty.realty = request.form["realty"]
        realty.state = request.form["state"]
        realty.locality = request.form["locality"]
        realty.value = request.form["value"]
        db.session.commit()
        return redirect(url_for("list"))
    return render_template("edit.html", realty=realty)


# Search
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "GET":
        q = request.args.get("q")
        realty = []
        realty = Realty.query.filter(
            Realty.name.contains(q) | Realty.realty.contains(q) | Realty.state.contains(q) |
            Realty.locality.contains(q) | Realty.value.contains(q))
    return render_template("result.html", realty=realty)


# Login
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = form.user.data
        password = form.password.data
        user = Users.query.filter_by(user=user).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Você está logado!')
                login_user(user, remember=True)
                return redirect(url_for('list'))
            else:
                flash('Senha incorreta! Tente novamente')
        else:
            flash('Email não cadastrado!')
    return render_template("login.html", form=form)


# Register user
@app.route('/register_user', methods=["GET", "POST"])
def register_user():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        user = form.user.data
        email = form.email.data
        password = form.password.data
        hash = generate_password_hash(password, method="sha256")

        new_user = Users(name=name, user=user, email=email, password=hash)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register_user.html', form=form)


# Logout
@app.route('/logout')
def logout():
    user = current_user
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
