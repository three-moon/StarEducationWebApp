from flask import current_app
from app.extensions import db

Column = db.Column
relationship = db.relationship


class CRUDMixin(object):
    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance = instance.save()
        message = 'Объект %s создан' % instance
        for attr, value in kwargs.items():
            message += '\n"%s": "%s";' % (attr, value)
        current_app.logger.info(message)
        return instance

    def update(self, commit=True, **kwargs):
        obj = self.__repr__()
        message = ''
        for attr, value in kwargs.items():
            if hasattr(self, attr):
                old_value = getattr(self, attr)
                if type(value) == list:
                    rem = list(map(str, set(old_value) - set(value)))
                    add = list(map(str, set(value) - set(old_value)))
                    message += '\n"%s":%s%s' % (attr, "\nДобавлено:\n" + ";\n".join(add) + ";" if add else '',
                                                "\nУбрано:\n" + ";\n".join(rem) + ";" if rem else '')
                    setattr(self, attr, value)
                else:
                    setattr(self, attr, value)
                    message += '\n"%s": c "%s" на "%s";' % (attr, old_value, value)
            else:
                current_app.logger.warning('Некорректный атрибут "%s" для "%s"' % (attr, type(self)))
        current_app.logger.info('Данные "%s" изменены:%s' % (obj, message))
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        current_app.logger.info('Удален объект "%s"' % (self))
        db.session.delete(self)
        return commit and db.session.commit()
