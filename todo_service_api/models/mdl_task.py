from todo_service_api.extensions import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    done = db.Column(db.Boolean, default=False)
