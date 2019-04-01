# -*- encoding: utf-8 -*-
"""ICU Prediction API: MySQL adapter.

Author: Bas Vonk
Date: 2019-04-01
"""

import MySQLdb
from src.config import MYSQL_CONFIG
from time import sleep
import logging
import coloredlogs

MAX_RETRIES = 10

LOGGER = logging.getLogger('MySQL adapter')
coloredlogs.install(logger=LOGGER)

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

        for i in range(MAX_RETRIES):
            try:
                self.connection = MySQLdb.connect(**MYSQL_CONFIG)
                self.cursor = self.connection.cursor()
                LOGGER.info(f"Connection succeeded.")
                break
            except MySQLdb.Error:
                retry_interval = 2**i
                LOGGER.info(f"Connection failed, retrying in: {retry_interval} seconds.")
                sleep(retry_interval)
        else:
            raise SystemError

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

    def replace_into(self, table_name, values):
        """Replace a row into a specific database table."""

        # This is safe: https://stackoverflow.com/questions/835092/
        # python-dictionary-are-keys-and-values-always-the-same-order
        column_names = list(values.keys())
        values = list(values.values())

        # Dynamically build the query
        # Be aware that the %s is NOT string formatting but parameter binding
        query = 'REPLACE INTO ' + table_name + ' (' + ', '.join(column_names) + \
                ') VALUES (' + ', '.join(['%s'] * len(column_names)) + ')'

        # Execute the query and commit the results
        self.execute_query(query, tuple(values))

        return self.cursor.lastrowid

    def close_connection(self):
        """Close the database connection."""

        return self.connection.close()
