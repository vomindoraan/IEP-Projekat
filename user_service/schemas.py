from marshmallow import ValidationError
from marshmallow.validate import And, Email, Length, Regexp

from common.schemas import *
from . import models


# region Custom validators

def validate_jmbg(v):
    error = ValidationError("Invalid jmbg.")
    if len(v) != 13:
        raise error
    try:
        dd, mm, yyy, rr, bbb, checksum = map(int, (
            v[0:2], v[2:4], v[4:7], v[7:9], v[9:12], v[12]
        ))
    except ValueError:
        raise error
    if not (1 <= dd <= 31 and 1 <= mm <= 12 and 0 <= yyy <= 999
            and 70 <= rr <= 99 and 0 <= bbb <= 999):
        raise error
    a, b, c, d, e, f, g, h, i, j, k, l, _ = map(int, v)
    m = 11 - ((7*(a+g) + 6*(b+h) + 5*(c+i) + 4*(d+j) + 3*(e+k) + 2*(f+l)) % 11)
    if checksum != m:
        raise error


validate_password = And(
    Length(min=8, max=256),
    Regexp(r'^(?=.*?[0-9])(?=.*?[A-Z])(?=.*?[a-z]).+',
           error="Must contain at least one digit, one uppercase and "
                 "one lowercase letter."),
)

# endregion


# region User requests

class BaseUserRequest(SQLAlchemyMixin, APIRequest):
    class Meta(APIRequest.Meta):
        model = models.User


class UserRegistration(BaseUserRequest):
    jmbg = MM.auto_field(validate=validate_jmbg)
    email = MM.auto_field(validate=Email())
    password = MM.auto_field(validate=validate_password)
    forename = MM.auto_field()
    surname = MM.auto_field()


class UserLogin(BaseUserRequest):
    email = MM.auto_field(validate=Email())
    password = MM.auto_field()


class UserDeletion(BaseUserRequest):
    email = MM.auto_field(validate=Email())

# endregion


# region User responses

class AccessToken(APIResponse):
    access_token = MM.String(data_key='accessToken')  # TODO data_key/attribute


class TokenPair(APIResponse):
    access_token = MM.String(data_key='accessToken')
    refresh_token = MM.String(data_key='refreshToken')

# endregion