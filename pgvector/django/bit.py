from django.db.models import Field


# https://docs.djangoproject.com/en/5.0/howto/custom-model-fields/
class BitField(Field):
    description = 'Bit string'

    def __init__(self, *args, length=None, **kwargs):
        self.length = length
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.length is not None:
            kwargs['length'] = self.length
        return name, path, args, kwargs

    def db_type(self, connection):
        if self.length is None:
            return 'bit'
        return 'bit(%d)' % self.length
