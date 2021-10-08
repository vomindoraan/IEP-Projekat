import re
from itertools import chain, zip_longest

import ujson
from flask import current_app
from flask_marshmallow import Marshmallow
from marshmallow import EXCLUDE, RAISE, ValidationError, post_dump, pre_load
from marshmallow.decorators import VALIDATES_SCHEMA
from marshmallow.exceptions import SCHEMA as SCHEMA_KEY

from common.utils import filter_dict, filter_values


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
        datetimeformat = 'iso'
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


# TODO: What happens on dump?
class CollapseErrorsMixin(Base):
    messages = {
        'missing': "Field {data_key} is missing.",
        'null':    "Field {data_key} may not be null.",
        'invalid': "Invalid {data_key}.",
        'unknown': "Unknown field {data_key}.",
    }

    def __init__(self, *args, **kwargs):
        self.field_mapping = {}
        super().__init__(*args, **kwargs)

    def on_bind_field(self, field_name, field_obj):
        self.field_mapping[field_name] = field_obj
        if dk := field_obj.data_key:
            self.field_mapping[dk] = field_obj

    @classmethod
    def make_message(cls, msg_key, data_key):
        return cls.messages[msg_key].format(data_key=data_key)

    def handle_error(self, error, data, *, many, **kwargs):
        if not current_app.config['COLLAPSE_ERROR_MESSAGES']:
            return

        if (missing := filter_dict(
            lambda dk, m: self._check_messages(dk, m, key_pattern=r'required'),
            error.messages,
        )) and (data_key := next(iter(missing))) != SCHEMA_KEY:
            message = self.make_message('missing', data_key)

        elif (null := filter_dict(
            lambda dk, m: self._check_messages(dk, m, key_pattern=r'null'),
            error.messages,
        )) and (data_key := next(iter(null))) != SCHEMA_KEY:
            message = self.make_message('null', data_key)

        elif (invalid := filter_dict(
            lambda dk, m: self._check_messages(
                dk, m, value_pattern=r"Invalid .+|Not a valid .+",
                key_pattern=r'invalid.*|validator_failed|type|format',
                data=data, many=many,
            ),
            error.messages,
        )):
            if (data_key := next(iter(invalid))) != SCHEMA_KEY:
                message = self.make_message('invalid', data_key)
            else:
                message = error.messages[SCHEMA_KEY]

        elif (unknown := filter_dict(
            lambda dk, m: self._check_messages(dk, m, key_pattern=r'unknown'),
            error.messages,
        )) and (data_key := next(iter(unknown))) != SCHEMA_KEY:
            message = self.make_message('unknown', data_key)

        else:
            other_keys = (error.messages.keys() - missing.keys()
                          - null.keys() - invalid.keys() - unknown.keys())
            message = error.messages[next(iter(other_keys))]

        if isinstance(message, list):
            message = message[0]
        raise ValidationError(message) from error

    def _check_messages(self, data_key, messages, *,
                        value_pattern=None, key_pattern=None,
                        data=None, many=None):
        if value_pattern:
            if any(re.fullmatch(value_pattern, m) for m in messages):
                return True
        matching = set()
        if key_pattern:
            matching.update(self._get_declared_messages(data_key, key_pattern))
        if data:
            matching.update(self._get_validator_messages(data_key, data, many))
        return bool(set(messages) & matching)

    def _get_declared_messages(self, data_key=None, key_pattern=r'.*'):
        all_msgs = self.error_messages.copy()
        if data_key in self.field_mapping:
            all_msgs.update(self.field_mapping[data_key].error_messages)
        return (m for k, m in all_msgs.items() if re.fullmatch(key_pattern, k))

    def _get_validator_messages(self, data_key, data, many=False):
        if data_key in self.field_mapping:
            field_obj = self.field_mapping[data_key]
            value = data[data_key]
            try:
                field_obj.deserialize(value, data_key, data)
            except ValidationError as e:
                yield from e.messages
        elif data_key == SCHEMA_KEY:
            vt = self._hooks.get((VALIDATES_SCHEMA, True),  [])
            vf = self._hooks.get((VALIDATES_SCHEMA, False), [])
            schema_validators = chain(zip_longest(vt, [], fillvalue=True),
                                      zip_longest(vf, [], fillvalue=False))
            for v_name, pass_many in schema_validators:
                v = getattr(self, v_name)
                try:
                    v(data, many=many) if pass_many else v(data)
                except ValidationError as e:
                    yield from e.messages.values()

# endregion


# region API schemas

class APIRequest(CollapseErrorsMixin, Base):
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
