from flask import Blueprint, render_template, request, flash, redirect, url_for, session

studentController = Blueprint("studentController", __name__)


from models.model import students

@studentController.route('/slogin', methods=["POST", "GET"])
def slogin():
    if request.method == "POST":
        password = request.form["password"]
        logging_student = students.get_student_by_password(password)
        if logging_student != "Öğrenci bulunamadı":
            session["student_name"] = logging_student.name
            session["student_id"] = logging_student.student_id
            session["teacher_password"] = logging_student.password

            return redirect(url_for("studentController.student"))

        else:
            flash("Kullanıcı adı veya parola hatalı")
            return redirect(url_for("studentController.slogin"))


    return render_template("studentView/slogin.html")

#
# @studentController.route('/smain')
# def smain():
#     return render_template("studentView/smain.html")
#

@studentController.route('/student', methods=["POST", "GET"])
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