import ujson
from flask_marshmallow import Marshmallow
from marshmallow import EXCLUDE, RAISE, post_dump, pre_load

from common.utils import filter_values


MM = Marshmallow()


# region Base schemas

class BaseMeta(type(MM.Schema)):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.ONE = cls()
        cls.MANY = cls(many=True)


class BaseOpts(MM.Schema.OPTIONS_CLASS):
    def __init__(self, meta, **kwargs):
        super().__init__(meta, **kwargs)
        self.envelope_key = getattr(meta, 'envelope_key', None)
        self.envelope_many_key = getattr(meta, 'envelope_many_key', None)


class Base(MM.Schema, metaclass=BaseMeta):
    OPTIONS_CLASS = BaseOpts

    class Meta:  # Schema options, not related to metaclass.
        dateformat = 'iso'
        render_module = ujson
        unknown = EXCLUDE

    @post_dump(pass_many=True)
    def wrap_envelope(self, data, many, **kwargs):
        if not many and self.opts.envelope_key is not None:
            return {self.opts.envelope_key: data}
        if many and self.opts.envelope_many_key is not None:
            return {self.opts.envelope_many_key: data}
        return data

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        if not many and self.opts.envelope_key is not None:
            return data[self.opts.envelope_key]
        if many and self.opts.envelope_many_key is not None:
            return data[self.opts.envelope_many_key]
        return data

# endregion


# region Mixins

class SQLAlchemyMixinMeta(BaseMeta, type(MM.SQLAlchemySchema)):
    pass


class SQLAlchemyMixinOpts(BaseOpts, MM.SQLAlchemySchema.OPTIONS_CLASS):
    pass


class SQLAlchemyMixin(MM.SQLAlchemySchema, metaclass=SQLAlchemyMixinMeta):
    OPTIONS_CLASS = SQLAlchemyMixinOpts

# endregion


# region API schemas

class APIRequest(Base):
    class Meta(Base.Meta):
        ordered = True
        unknown = RAISE

    @pre_load
    def treat_empty_string_as_missing(self, data, **kwargs):
        return filter_values(lambda v: v != '', data)


class APIResponse(Base):
    pass


class APIQuery(APIRequest):
    pass


class EmptyRequest(APIRequest):
    pass


class EmptyResponse(APIResponse):
    pass

# endregion
