# -*- encoding: utf-8 -*-
"""ICU Prediction API: ICU Model.

Author: Bas Vonk
Date: 2019-04-01
"""

from mysql_adapter import MySQL


class ICUModel:
    """Data-layer for the Prediction API application.

    Attributes
    ----------
    mysql_obj : MySQL
        An instance of the MySQL adapter.

    """

    def __init__(self):

        self.mysql_obj = MySQL()

    def __del__(self):
        """When an instance of this class is deleted, close the database connection."""

        self.mysql_obj.close_connection()

    def get_patients_in_ic(self):
        """Get the patients that are currently in the Intensive Care."""

        query = "SELECT * FROM patients WHERE datetime_discharge IS NULL"

        return self.mysql_obj.fetch_rows(query)

    def get_signal_values_for_patient(self, patient_id):
        """Get all signal values for patient.

        Parameters
        ----------
        patient_id : int
            Patient ID.

        Returns
        -------
        List[Dict[str, Union[str, int, float, datetime]]]
            Records with signal values.

        """

        query = \
            """
            SELECT s.name, psv.value, psv.time
            FROM patient_signal_values psv
            INNER JOIN signals s
                ON psv.signal_id = s.id
            WHERE patient_id = %(patient_id)s
            """

        params = {
            "patient_id": patient_id
        }

        return self.mysql_obj.fetch_rows(query, params)

    def get_patient(self, patient_id):
        """Get a patient.

        Parameters
        ----------
        patient_id : id
            Patient ID.

        Returns
        -------
        Dict[str, Union[str, int, float, datetime]]
            Description of returned object.

        """

        query = "SELECT * FROM patients WHERE id = %(patient_id)s"
        params = {"patient_id": patient_id}

        return self.mysql_obj.fetch_row(query, params)

    def get_current_simulated_time(self):
        """Get the current time when the simulation is running."""

        query = "SELECT MAX(time) FROM patient_signal_values"

        return self.mysql_obj.fetch_value(query)
