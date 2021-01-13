from flask import Flask, render_template, session

from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///models/test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "birzamanlarpythonprojesiyaparken"


from studentController import studentController
app.register_blueprint(studentController)

from teacherController import teacherController
app.register_blueprint(teacherController)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
    db.create_all()

