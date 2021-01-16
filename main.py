from flask import Flask, render_template, session





app = Flask(__name__)

UPLOAD_FOLDER = 'static/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///models/test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "birzamanlarpythonprojesiyaparken"


from studentController import studentController
app.register_blueprint(studentController)

from teacherController import teacherController
app.register_blueprint(teacherController)

from models.model import db
db.init_app(app)

@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
    db.create_all()

