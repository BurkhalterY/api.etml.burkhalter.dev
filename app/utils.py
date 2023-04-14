from dataclasses import fields


class BaseStrawberryType:
    _model = ""

    def __init__(self, rec=None, id=None):
        if id:
            rec = self._model.select().where(self._model.id == id).first().run_sync()
        for field in fields(self):
            setattr(self, field.name, rec.get(field.name))
