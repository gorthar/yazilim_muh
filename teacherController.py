from functools import wraps

from flask import Blueprint, render_template, request, session, flash, redirect, url_for

teacherController = Blueprint("teacherController", __name__)

from models.model import teacher as teacher_model, rooms as siniflar, enrolled_rooms,assignments


# Bu fonksiyon sayfaya ulaşılması için login olunmasını gerekli kılmaktadır
def teacher_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not session.get(
                "teacher_name") is None:  # Session da teacher_name bilgisinin varlığını kontrol ederek yapmaktadır.
            return f(*args, **kwargs)
        else:
            flash("Lütfen sisteme giriş yapınız")
            return redirect(url_for("index"))

    return wrap


@teacherController.route('/tlogin', methods=["POST", "GET"])
def tlogin():
    if request.method == "POST":
        email = request.form["email"]
        logging_teacher = teacher_model.getTeacher(email)
        if logging_teacher != "Kullanıcı Bulunamadı":
            if logging_teacher.password == request.form["password"]:
                ogretmen_adi = logging_teacher.name
                session["teacher_name"] = ogretmen_adi
                session["teacher_email"] = logging_teacher.email

                return redirect(url_for("teacherController.teacher"))
            else:
                flash("Kullanıcı adı veya parola hatalı")
                return render_template("teacherView/tlogin.html")
        else:
            flash("Kullanıcı adı veya parola hatalı")
            return render_template("teacherView/tlogin.html")
    else:
        return render_template("teacherView/tlogin.html")


@teacherController.route('/tsignup', methods=["POST", "GET"])
def tsignup():
    if request.method == "POST":
        logging_teacher = teacher_model.getTeacher(request.form["email"])
        if isinstance(logging_teacher, teacher_model):
            flash("Bu e-posta kullanılmaktadır")
            return redirect(url_for("teacherController.tsignup"))
        else:
            if request.form["password"] == request.form["password_check"]:
                logging_teacher = teacher_model(request.form["email"], request.form["isim"], request.form["password"])
                logging_teacher.setTeacher()
                flash("Kayıt başarıyla gerçekleştirilmiştir")
                return redirect(url_for("teacherController.tlogin"))
            else:
                flash("Parolalar uyuşmamaktadır.")
                return redirect(url_for("teacherController.tsignup"))
    else:
        return render_template("teacherView/tsignup.html")


@teacherController.route('/teacher', methods=["POST", "GET"])
@teacher_login_required
def teacher():
    if request.method == "POST":
        sinif_adi = request.form["sinif_adi"]
        ogretmenin_maili = session["teacher_email"]
        yeni_sinif = siniflar()
        yeni_sinif.teacher_mail = ogretmenin_maili
        yeni_sinif.room_name = sinif_adi
        yeni_sinif.set_room()
        return redirect(url_for("teacherController.teacher"))

    else:
        ogretmen_maili = session["teacher_email"]
        ogretmen_rooms = siniflar.get_rooms(ogretmen_maili)
        return render_template("teacherView/teacher.html", ogrtn_rooms=ogretmen_rooms)


# @teacherController.route('/room')
# @teacher_login_required
# def room():
#     return render_template("teacherView/room.html")


@teacherController.route('/room/<int:room_id>')
@teacher_login_required
def room(room_id):
    gelen_sinif = siniflar.get_room(room_id)
    if gelen_sinif != "Sınıf bulunamadı":  # sınıfın varlığının kontrolü
        if session.get("teacher_name") == gelen_sinif.teacher_mail:  # öğretmenin tanımladığı sınfın kontrolü
            siniftaki_ogrenciler=enrolled_rooms.get_students_id_from_room_id(room_id)
            sinifin_odevleri=assignments.get_assignments(room_id)
            for student in siniftaki_ogrenciler:

            return render_template("teacherView/room.html", gln_snf=gelen_sinif)

    return render_template("teacherView/room.html")


@teacherController.route('/createroom')
def createroom():
    return render_template("teacherView/createroom.html")


@teacherController.route('/createassignment')
def createassignment():
    return render_template("teacherView/createassignment.html")


@teacherController.route('/checkassignment')
def checkassignment():
    return render_template("teacherView/checkassignment.html")


@teacherController.route('/accinfo')
def accinfo():
    return render_template("teacherView/accinfo.html")


@teacherController.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))
