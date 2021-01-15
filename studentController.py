from flask import Blueprint, render_template, request, flash, redirect, url_for, session

studentController = Blueprint("studentController", __name__)

from models.model import students, enrolled_rooms, assignments, rooms


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
            flash("Girilen kod hatalı")
            return redirect(url_for("studentController.slogin"))


    return render_template("studentView/slogin.html")


@studentController.route('/student', methods=["POST", "GET"])
def student():
    kayintli_sinif_idleri = enrolled_rooms.get_rooms_id_from_student_id(session["student_id"])

    tablo = []
    if len(kayintli_sinif_idleri) != 0:
        for id in kayintli_sinif_idleri:
            siniftaki_ogrenci_sayisi = enrolled_rooms.get_students_id_from_room_id(id)
            odevler = assignments.get_assignments(id)
            room=rooms.get_room(id)
            sutun = {
                "sinif_adi": room.room_name,
                "sinif_id": room.room_id,
                "ogrenci_sayisi": len(siniftaki_ogrenci_sayisi),
                "odev_sayisi": len(odevler),
            }
            tablo.append(sutun)
        return render_template("studentView/student.html", tablo=tablo)

    return render_template("studentView/student.html")


@studentController.route('/studentroom')
def studentroom():
    return render_template("studentView/studentroom.html")

@studentController.route('/submit')
def submit():
    return render_template("studentView/submit.html")

@studentController.route('/slogout')
def slogout():
    session.clear()
    return render_template("index.html")