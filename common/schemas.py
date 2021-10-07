import re
from functools import partial
from itertools import chain, zip_longest

import ujson
from flask_marshmallow import Marshmallow
from marshmallow import EXCLUDE, RAISE, ValidationError, post_dump, pre_load
from marshmallow.decorators import VALIDATES_SCHEMA
from marshmallow.exceptions import SCHEMA as SCHEMA_ERROR_KEY

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


class CollapseErrorsMixin(Base):
    def handle_error(self, error, data, *, many, **kwargs):
        if (missing := filter_dict(
            partial(self._check_messages, key_pattern=r'required'),
            error.messages,
        )) and (field := next(iter(missing))) != SCHEMA_ERROR_KEY:
            message = f"Field {field} is missing."

        elif (null := filter_dict(
            partial(self._check_messages, key_pattern=r'null'),
            error.messages,
        )) and (field := next(iter(null))) != SCHEMA_ERROR_KEY:
            message = f"Field {field} may not be null."

        elif (invalid := filter_dict(
            partial(self._check_messages,
                    key_pattern=r'invalid.*|validator_failed|type|format',
                    # msg_pattern=r"Invalid .+|Not a valid .+",
                    data=data, many=many),
            error.messages,
        )) and (field := next(iter(invalid))) != SCHEMA_ERROR_KEY:
            message = f"Invalid {field}."

        elif (unknown := filter_dict(
            partial(self._check_messages, key_pattern=r'unknown'),
            error.messages,
        )) and (field := next(iter(unknown))) != SCHEMA_ERROR_KEY:
            message = f"Unknown field {field}."

        else:
            other_keys = (error.messages.keys() - missing.keys()
                          - null.keys() - invalid.keys() - unknown.keys())
            message = error.messages[next(iter(other_keys))]

        # TODO: Replace with internal exception.
        raise ValidationError(message) from error

    def _check_messages(self, field_name, messages, *,
                        msg_pattern=None, key_pattern=None,
                        data=None, many=None):
        matching = set()
        if msg_pattern:
            matching.update(m for m in messages if re.fullmatch(msg_pattern, m))
        if key_pattern:
            matching.update(self._get_declared_messages(key_pattern, field_name))
        if data:
            matching.update(self._get_validator_messages(data, many, field_name))
        return bool(set(messages) & matching)

    def _get_declared_messages(self, key_pattern=r'.*', field_name=None):
        all_msgs = self.error_messages.copy()
        if field_name in self.fields:
            all_msgs.update(self.fields[field_name].error_messages)
        return (m for k, m in all_msgs.items() if re.fullmatch(key_pattern, k))

    def _get_validator_messages(self, data, many, field_name=None):
        vt = self._hooks.get((VALIDATES_SCHEMA, True),  [])
        vf = self._hooks.get((VALIDATES_SCHEMA, False), [])
        schema_validators = chain(zip_longest(vt, (), fillvalue=True),
                                  zip_longest(vf, (), fillvalue=False))
        for v_name, pass_many in schema_validators:
            v = getattr(self, v_name)
            try:
                v(data, many=many) if pass_many else v(data)
            except ValidationError as e:
                yield from e.messages.values()
        if field_name in self.fields:
            for v in self.fields[field_name].validators:
                try:
                    v(data[field_name])
                except ValidationError as e:
                    yield from e.messages

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
