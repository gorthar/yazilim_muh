import random
from flask_sqlalchemy import SQLAlchemy


from datetime import datetime
db = SQLAlchemy()

class teacher(db.Model):
    __tablename__ = 'teacherTable'
    email = db.Column("email", db.String(100), primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    password = db.Column("password", db.String(100), nullable=False)

    def __init__(self, email, name, password):
        self.name = name
        self.email = email
        self.password = password

    def setTeacher(self):
        db.session.add(self)
        db.session.commit()

    def updateTeacher(self):
        updated_teacher = teacher.query.filter_by(email=self.email).first()
        updated_teacher.name = self.name
        updated_teacher.password = self.password
        db.session.commit()

    @classmethod
    def getTeacher(self, email):
        bulunan_teacher = teacher.query.filter_by(email=email).first()
        if bulunan_teacher:
            return bulunan_teacher
        else:
            return "Kullanıcı Bulunamadı"


class rooms(db.Model):
    __tablename__ = 'roomTable'
    room_id = db.Column(db.Integer, primary_key=True)
    teacher_mail = db.Column(db.String(100), db.ForeignKey(teacher.email), nullable=False)
    room_name = db.Column(db.String(100), nullable=False)
    announcement = db.Column(db.String(300), nullable=True)
    generated_address = db.Column(db.String(15), nullable=False, unique=True)

    def set_room(self):
        key = ""
        while True:
            key = self.create_key()
            if not key == rooms.query.filter_by(generated_address=key).first():
                break

        self.announcement = ""
        self.generated_address = key
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_rooms(cls, teachers_mail):
        gelen_mail = teachers_mail
        teachers_rooms = rooms.query.filter_by(teacher_mail=gelen_mail).all()
        if teachers_rooms:
            return teachers_rooms
        else:
            return "Öğretmenin kayıtlı sınıfı bulunmamaktadır."

    @classmethod
    def get_room(cls, room_id):
        single_room = rooms.query.filter_by(room_id=room_id).first()
        if single_room:
            return single_room
        else:
            return "Sınıf bulunamadı"
    @classmethod
    def get_room_by_adress(cls, generated_address):
        room_by_adress=rooms.query.filter_by(generated_address=generated_address).first()
        if room_by_adress:
            return room_by_adress
        else:
            return "Sınıf Bulunamadı"

    def create_key(self):
        length = 6
        characters = "ABCDEFGHIJKLMNOPRSTUVYZ0123456789"
        randoms = [random.choice(characters) for _ in range(length)]
        random_key = "".join(randoms)
        return random_key


class students(db.Model):
    __tablename__ = 'studentTable'
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def set_student(self,room_id):
        key = ""
        randomkey = rooms()
        while True:
            key = randomkey.create_key()  # 6 karakterli öğrenci giriş kodu oluşturulur
            if not key == students.query.filter_by(password=key).first():
                break
        self.password = key
        db.session.add(self)
        db.session.commit()
        students_new_acc=students.query.filter_by(password=self.password).first()
        new_enrollment=enrolled_rooms()
        new_enrollment.room_id=room_id
        new_enrollment.student_id=students_new_acc.student_id
        new_enrollment.enroll_student()

    @classmethod
    def get_student_by_password(cls, password):
        bulunan_student = students.query.filter_by(password=password).first()
        if bulunan_student:
            return bulunan_student
        else:
            return "Öğrenci bulunamadı"

    @classmethod
    def get_student_by_id(cls, student_id):
        bulunan_student = students.query.filter_by(student_id=student_id).first()
        if bulunan_student:
            return bulunan_student
        else:
            return "Öğrenci bulunamadı"

    def delete_student(self):
        db.session.delete(self)
        db.session.commit()

    def update_student(self):
        guncellenecek_ogrenci = students.query.filter_by(student_id=self.student_id).first()
        guncellenecek_ogrenci.name = self.name
        guncellenecek_ogrenci.password = self.password
        db.session.commit()


class enrolled_rooms(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey(students.student_id), nullable=False, primary_key=True,
                           autoincrement=False)
    room_id = db.Column(db.Integer, db.ForeignKey(rooms.room_id), nullable=False, primary_key=True, autoincrement=False)

    @classmethod
    def get_students_id_from_room_id(cls, room_id):  # sınıfa kayıtlı öğrencileri bulur (liste halinde)
        enrolled_students_list = [s.student_id for s in enrolled_rooms.query.filter_by(room_id=room_id).all()]
        return enrolled_students_list

    @classmethod
    def get_rooms_id_from_student_id(cls, student_id):  # ogrencinin kayıtlı oluğu sınıfları bulur (liste halinde)
        rooms_of_student = [r.room_id for r in enrolled_rooms.query.filter_by(student_id=student_id).all()]
        return rooms_of_student

    def enroll_student(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def remove_student_from_room(cls, student_id, room_id):
        cls.student_id = student_id
        cls.room_id = room_id
        db.session.delete(cls)
        db.session.commit()


class assignments(db.Model):
    assignment_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey(rooms.room_id), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    assignment_date = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def create_assignment(self):
        db.session.add(self)
        db.session.commit()

    def update_assignment(self):
        guncellenecek_odev = assignments.query.filter_by(assignment_id=self.assignment_id).first()
        guncellenecek_odev.message = self.message
        guncellenecek_odev.name = self.name
        db.session.commit()

    @classmethod
    def get_assignment(cls, assignment_id):
        aranan_odev = assignments.query.filter_by(assignment_id=assignment_id).first()
        if aranan_odev:
            return aranan_odev
        else:
            return "Ödev bulunamadı"

    @classmethod
    def get_assignments(cls, room_id):
        assignments_of_room = assignments.query.filter_by(room_id=room_id).all()
        return assignments_of_room

    def delete_assignment(self):
        db.session.delete(self)
        db.session.commit()


class submitted_assignments(db.Model):
    submitted_assignments_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey(assignments.assignment_id), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey(students.student_id), nullable=False)
    comment_of_teacher = db.Column(db.String(2000), nullable=True)
    path_of_image = db.Column(db.String(500), nullable=False)
    delivery_date = db.Column(db.DateTime, default=datetime.now())

    @classmethod
    def get_submitted_assignments_by_student_id(cls, student_id):
        ogrencinin_odevleri = submitted_assignments.query.filter_by(student_id=student_id).all()
        if ogrencinin_odevleri:
            return ogrencinin_odevleri
        else:
            return "Öğrencinin teslim ettiği ödev bulunmamaktadır"

    @classmethod
    def get_submitted_assignment_by_assignment_and_student(cls, assignment_id, student_id):
        ogrencinin_odevi = submitted_assignments.query.filter_by(assignment_id=assignment_id,
                                                                 student_id=student_id).first()
        if ogrencinin_odevi:
            return ogrencinin_odevi
        else:
            return "Öğrenci ödevi teslim etmemiştir."

    def submit_assignment(self):
        db.session.add(self)
        db.session.commit()
