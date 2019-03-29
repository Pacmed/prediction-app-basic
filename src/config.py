# -*- encoding: utf-8 -*-
"""ICU Prediction API: Config.

Author: Bas Vonk
Date: 2019-04-01
"""

from os import getenv
from MySQLdb import cursors

MYSQL_CONFIG = {
    "host": getenv("MYSQL_HOSTNAME"),
    "user": getenv("MYSQL_USERNAME"),
    "passwd": getenv("MYSQL_PASSWORD"),
    "db": getenv("MYSQL_DATABASE"),
    "use_unicode": True,
    "cursorclass": cursors.DictCursor
}
