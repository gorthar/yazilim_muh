from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
import os



studentController = Blueprint("studentController", __name__)

from models.model import students, enrolled_rooms, assignments, rooms, submitted_assignments
from main import app

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
    if request.method == "POST":
        sinif_kodu = request.form["sinif_kodu"]
        kayit_olunacak_sinif= rooms.get_room_by_adress(sinif_kodu)
        kayit_bilgisi=enrolled_rooms()
        kayit_bilgisi.student_id=session["student_id"]
        kayit_bilgisi.room_id=kayit_olunacak_sinif.room_id
        kayit_bilgisi.enroll_student()
        return redirect(url_for('studentController.student'))
    else:
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


@studentController.route('/studentroom/<room_id>')
def studentroom(room_id):
    session.pop("bulunan_oda_ogrenci", None)
    session["bulunan_oda_ogrenci"] = room_id
    sinifin_odevleri=assignments.get_assignments(room_id)
    tablo = []
    for odev in sinifin_odevleri:
        ogrencinin_odevi = submitted_assignments.get_submitted_assignment_by_assignment_and_student(
            odev.assignment_id, session["student_id"])
        if ogrencinin_odevi != "Öğrenci ödevi teslim etmemiştir.":
            ogrencinin_odev_durumu = True
        else:
            ogrencinin_odev_durumu = False

        odev_dic = {"odevno": str(odev.assignment_id),
                    "teslim": str(ogrencinin_odev_durumu),
                    "odevadi":odev.name,
                    "odevmesaj":odev.message
                    }
        tablo.append(odev_dic)
    return render_template("studentView/studentroom.html", tablo=tablo)




ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@studentController.route('/submit/<assignment_id>', methods=["POST", "GET"])
def submit(assignment_id):
    odev_teslim=submitted_assignments()
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        # print(files)
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                odev_teslim.path_of_image=filename
                odev_teslim.student_id=session["student_id"]
                odev_teslim.assignment_id=assignment_id
                odev_teslim.submit_assignment()
            print(file)


        flash('File(s) successfully uploaded')
        return redirect(url_for('studentController.submit', assignment_id=assignment_id))
    return render_template("studentView/submit.html", assignment_id=assignment_id)

@studentController.route('/slogout')
def slogout():
    session.clear()
    return render_template("index.html")