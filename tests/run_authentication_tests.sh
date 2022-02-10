#!/bin/sh
python tests/main.py --authentication-address http://localhost:9000 --administrator-address http://localhost:9010 --station-address http://localhost:9020 --with-authentication --jwt-secret 13С113ИЕП --roles-field role --administrator-role admin --user-role user --type authentication
