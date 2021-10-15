#!/bin/sh
python tests/main.py --authentication-address http://0.0.0.0:9000 --administrator-address http://0.0.0.0:9010 --station-address http://0.0.0.0:9020 --with-authentication --jwt-secret 13С113ИЕП --roles-field role --administrator-role admin --user-role user --type election
