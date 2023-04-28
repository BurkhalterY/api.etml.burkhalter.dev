from dataclasses import fields

import strawberry


class BaseStrawberryType:
    _model = strawberry.Private[object]
    _record = strawberry.Private[object]

    def __init__(self, rec=None, id=None):
        if id:
            rec = self._model.select().where(self._model.id == id).first().run_sync()
        for field in fields(self):
            setattr(self, field.name, rec.get(field.name))
