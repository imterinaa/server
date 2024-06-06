from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    date_of_upload = db.Column(db.Date)
    data = db.Column(db.JSON)

    @classmethod
    def get_note_by_id(cls, note_id):
        return cls.query.get(note_id)

    @classmethod
    def get_all_notes(cls):
        return cls.query.all()

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth,
            "date_of_upload": self.date_of_upload,
            "data": self.data
        }

    @classmethod
    def create_note(cls, date_of_birth, date_of_upload, first_name, last_name, data):
        note = cls(
            date_of_birth=date_of_birth,
            date_of_upload=date_of_upload,
            first_name=first_name,
            last_name=last_name,
            data=data
        )
        db.session.add(note)
        db.session.commit()
