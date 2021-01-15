from functools import wraps

from flask import Blueprint, render_template, request, session, flash, redirect, url_for

teacherController = Blueprint("teacherController", __name__)

from models.model import teacher as teacher_model, rooms as siniflar, enrolled_rooms, assignments, students, \
    submitted_assignments


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
                session["teacher_password"] = logging_teacher.password

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
    if request.method == "POST":  # POST mothodunda öğretmen yeni sınıf oluşturulmakta
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
        tablo=[]
        if ogretmen_rooms!="Öğretmenin kayıtlı sınıfı bulunmamaktadır.":
            for room in ogretmen_rooms:
                siniftaki_ogrenci_sayisi=enrolled_rooms.get_students_id_from_room_id(room.room_id)
                odevler=assignments.get_assignments(room.room_id)
                sutun={
                    "sinif_adi":room.room_name,
                    "sinif_id":room.room_id,
                    "ogrenci_sayisi":len(siniftaki_ogrenci_sayisi),
                    "odev_sayisi":len(odevler),
                }
                tablo.append(sutun)
        return render_template("teacherView/teacher.html", tablo=tablo)


@teacherController.route('/room/<int:room_id>')
@teacher_login_required
def room(room_id):
    session.pop("bulunan_oda", None)
    session["bulunan_oda"] = room_id
    gelen_sinif = siniflar.get_room(room_id)
    if gelen_sinif != "Sınıf bulunamadı":  # sınıfın varlığının kontrolü
        if session.get(
                "teacher_email") == gelen_sinif.teacher_mail:  # öğretmenin tanımladığı sınf olup olmadığının kontrolü
            siniftaki_ogrencilerin_idler = enrolled_rooms.get_students_id_from_room_id(room_id)
            sinifin_odevleri = assignments.get_assignments(room_id)
            x = 0
            y = 0
            tablo = []  # öğrencilerin ödev durumlarının listeleneceği tablo
            for student in siniftaki_ogrencilerin_idler:  # her satırın ilk hücresi öğrenci adı, id'si ve giriş kodu bilgilerini bulunduran bir dic
                ogr = students.get_student_by_id(student)
                ogr_dic = {"ogrno": str(ogr.student_id),
                           "ogradi": ogr.name,
                           "ogrpass": str(ogr.password)
                           }
                column = [ogr_dic]
                for odev in sinifin_odevleri:
                    ogrencinin_odevi = submitted_assignments.get_submitted_assignment_by_assignment_and_student(
                        odev.assignment_id, ogr.student_id)
                    if ogrencinin_odevi != "Öğrenci ödevi teslim etmemiştir.":
                        ogrencinin_odev_durumu = True
                    else:
                        ogrencinin_odev_durumu = False

                    odev_dic = {"ödevno": str(odev.assignment_id),
                                "teslim": str(ogrencinin_odev_durumu),
                                }
                    column.append(odev_dic)
                tablo.append(column)

            return render_template("teacherView/room.html", tablo=tablo, gelen_sinif=gelen_sinif)

    return redirect(url_for("teacherController.teacher"))


@teacherController.route('/addstudent', methods=["POST"])
@teacher_login_required
def add_student():
    yeni_ogrenci = students()
    yeni_ogrenci.name = request.form["odevadi"]
    yeni_ogrenci.set_student(session.get("bulunan_oda"))

    return redirect(url_for('teacherController.room', room_id=session.get("bulunan_oda")))


@teacherController.route('/updatestudent/<student_id>', methods=["POST"])
@teacher_login_required
def change_student(student_id):
    changed_student = students.get_student(student_id)
    if changed_student != "Öğrenci bulunamadı":
        changed_student.name = request.form["adi"]
        changed_student.update_student()
    return redirect(url_for('teacherController.room', room_id=session.get("bulunan_oda")))


@teacherController.route('/createassignment', methods=['POST', "GET"])
@teacher_login_required
def createassignment():
    if request.method == "POST":
        yeni_odev = assignments()
        yeni_odev.room_id = session.get("bulunan_oda")
        yeni_odev.name = request.form["odevadi"]
        yeni_odev.message = request.form["konu"]
        yeni_odev.create_assignment()
        return redirect(url_for('teacherController.room', room_id=yeni_odev.room_id))


    else:
        return redirect(url_for('teacherController.room', room_id=session.get("bulunan_oda")))


@teacherController.route('/checkassignment/<student_id>/<assignment_id>')
@teacher_login_required
def checkassignment(student_id, assignment_id):
    ogr = students.get_student_by_id(student_id)
    odev = assignments.get_assignment(assignment_id)
    teslim_edilen_odev = submitted_assignments.get_submitted_assignment_by_assignment_and_student(assignment_id,
                                                                                                  student_id)
    formatli_tarih = teslim_edilen_odev.delivery_date
    sayfada_gorulecek_veriler = dict([
        ("ogrenci_adi", ogr.name),
        ("odev_adi", odev.name),
        ("gorsel_path", teslim_edilen_odev.path_of_image),
        ("teslim_tarihi", formatli_tarih.strftime("%m/%d/%Y, %H:%M:%S"))
    ])

    return render_template("teacherView/checkassignment.html", sayfada_gorulecek_veriler=sayfada_gorulecek_veriler)


@teacherController.route('/editassignment', methods=["POST", "GET"])
@teacher_login_required
def editassignment():
    if request.method == "POST":
        gelen_odev = assignments()
        gelen_odev.assignment_id = request.form["id"]
        gelen_odev.name = request.form["odevadi"]
        gelen_odev.message = request.form["odevkonusu"]
        gelen_odev.update_assignment()
        return redirect(url_for('teacherController.editassignment'))
    else:
        rooms_assignments = assignments.get_assignments(session.get("bulunan_oda"))
        return render_template("teacherView/editassignment.html", rooms_assignments=rooms_assignments)


@teacherController.route('/deleteassignment/<assignment_id>', methods=["GET"])
@teacher_login_required
def deleteassignment(assignment_id):
    silinecek_odev = assignments.get_assignment(assignment_id)
    silinecek_odev.delete_assignment()
    return redirect(url_for("teacherController.editassignment"))


@teacherController.route('/accinfo', methods=['POST', "GET"])
@teacher_login_required
def accinfo():
    if request.method == "POST":
        parola = request.form["inputPassword"]
        eposta = session["teacher_email"]
        isim = request.form["inputName"]



        if request.form["inputPassword"] != request.form["inputPasswordCheck"]:
            flash("Parola bilgileri aynı değil!")

        else:
            parlosi_yeni_ogretmen = teacher_model(eposta, isim, parola)
            parlosi_yeni_ogretmen.updateTeacher()
            session["teacher_name"]= isim
            flash("Hesap başarıyla güncellenmiştir.")
        return redirect(url_for("teacherController.accinfo"))
    else:
        return render_template("teacherView/accinfo.html")


@teacherController.route('/logout')
@teacher_login_required
def logout():
    session.clear()
    return redirect(url_for("index"))
