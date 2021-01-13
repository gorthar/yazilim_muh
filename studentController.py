from flask import Blueprint, render_template

studentController = Blueprint("studentController", __name__)


@studentController.route('/slogin')
def slogin():
    return render_template("studentView/slogin.html")


@studentController.route('/smain')
def smain():
    return render_template("studentView/smain.html")


@studentController.route('/student')
def student():
    return render_template("studentView/student.html")


@studentController.route('/studentroom')
def studentroom():
    return render_template("studentView/studentroom.html")

@studentController.route('/submit')
def submit():
    return render_template("studentView/submit.html")

@studentController.route('/slogout')
def slogout():
    return render_template("index.html")