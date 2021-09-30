import ujson
from flask_marshmallow import Marshmallow
from marshmallow import EXCLUDE, RAISE


MM = Marshmallow()


class BaseMeta(type(MM.Schema)):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.ONE = cls()
        cls.MANY = cls(many=True)


class Base(MM.Schema, metaclass=BaseMeta):
    class Meta:  # Schema options, not related to metaclass.
        dateformat = 'iso'
        render_module = ujson
        unknown = EXCLUDE


# region Mixins

class SQLAlchemyMixinMeta(BaseMeta, type(MM.SQLAlchemySchema)):
    pass


class SQLAlchemyMixin(MM.SQLAlchemySchema, metaclass=SQLAlchemyMixinMeta):
    pass


class SQLAlchemyAutoMixinMeta(BaseMeta, type(MM.SQLAlchemyAutoSchema)):
    pass


class SQLAlchemyAutoMixin(MM.SQLAlchemyAutoSchema, metaclass=SQLAlchemyAutoMixinMeta):
    pass

# endregion


# region API schemas

class APIRequest(Base):
    class Meta(Base.Meta):
        unknown = RAISE


class APIResponse(Base):
    pass


class APIQuery(APIRequest):
    pass


class EmptyRequest(APIRequest):
    pass


class EmptyResponse(APIResponse):
    pass

# endregion
