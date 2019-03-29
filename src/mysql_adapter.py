# -*- encoding: utf-8 -*-
"""ICU Prediction API: MySQL adapter.

Author: Bas Vonk
Date: 2019-04-01
"""

import MySQLdb
from config import MYSQL_CONFIG


class MySQL:
    """MysQL adapter.

    Attributes
    ----------
    connection : connection
        MySQL connection
    cursor : MySQLdb.cursor
        MySQL cursor
    """

    def __init__(self):

        self.connection = MySQLdb.connect(**MYSQL_CONFIG)
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=None):
        """Execute a query and put the results on the cursor.

        Parameters
        ----------
        query : str
            Query
        params : Dict[str, Union[str, int, float, datetime]]
            Parameters to be used with the query

        """

        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_rows(self, query, params=None):
        """Fetch rows.

        Parameters
        ----------
        query : str
            Query
        params : Dict[str, Union[str, int, float, datetime]]
            Parameters to be used with the query

        Returns
        -------
        List[Dict[str, Union[str, int, float, datetime]]]
            Result of the database query

        """

        self.execute_query(query, params)
        result = self.cursor.fetchall()
        return result

    def fetch_row(self, query, params=None):
        """Fetch a row.

        Parameters
        ----------
        query : str
            Query that should return ONE row
            (when more row are returned, only the first is returned)
        params : Dict[str, Union[str, int, float, datetime]]
            Parameters to be used with the query

        Returns
        -------
        Dict[str, Union[str, int, float, datetime]]
            Result of the database query

        """

        self.execute_query(query, params)
        result = self.cursor.fetchone()
        return result

    def fetch_value(self, query, params=None):
        """Fetch a single value.

        Parameters
        ----------
        query : str
            Query that should return ONE value
            (when more values are returned, only the first is returned)
        params : Dict[str, Union[str, int, float, datetime]]
            Parameters to be used with the query

        Returns
        -------
        Union[str, int, float, datetime]
            Result of the database query

        """

        self.execute_query(query, params)
        result = self.cursor.fetchone()
        return list(result.values())[0]

    def close_connection(self):
        """Close the database connection."""

        return self.connection.close()
