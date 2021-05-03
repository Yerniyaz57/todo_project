from todo_service_api.models import Task
from todo_service_api.extensions import ma, db


class TaskSchema(ma.SQLAlchemyAutoSchema):
    id = ma.Int(dump_only=True)

    class Meta:
        model = Task
        sqla_session = db.session
        load_instance = True
