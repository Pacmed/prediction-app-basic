from random import random, choice, randint, uniform, randrange
from numpy.random import normal
from pprint import pprint
from faker import Faker
from sys import exit
from datetime import datetime, timedelta
from time import sleep
from config import MYSQL_CONFIG
import MySQLdb
import logging
import coloredlogs

SECONDS_IN_MINUTE = 60
MINUTES_IN_DAY = 1440

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

FLIP_A_COIN = 0.5

# SIMULATION PARAMETERS:
PATIENTS_ADMITTED_PER_DAY = 2
PATIENTS_DISCHARGED_PER_DAY = 2
MEASUREMENTS_PER_DAY_PER_SIGNAL = 144

FREQ_ADMISSION = PATIENTS_ADMITTED_PER_DAY / MINUTES_IN_DAY
FREQ_DISCHARGE = PATIENTS_DISCHARGED_PER_DAY / MINUTES_IN_DAY
FREQ_MEASUREMENTS = MEASUREMENTS_PER_DAY_PER_SIGNAL / MINUTES_IN_DAY

DATETIME_START = "2019-01-01 00:00:00"

MIN_AGE = 10
MAX_AGE = 100

# a day takes 1440 iterations/minutes. For a fake day to last 5 minutes, we need to sleep
# 1 / 24 seconds for each minute
SLOW_FACTOR = 1 / 24

AVAILABLE_BEDS = ['BED_01', 'BED_02', 'BED_03', 'BED_04', 'BED_05', 'BED_06', 'BED_07', 'BED_08',
                  'BED_09', 'BED_10', 'BED_11', 'BED_12', 'BED_13', 'BED_14', 'BED_15', 'BED_16',
                  'BED_17', 'BED_18', 'BED_19', 'BED_20', 'BED_21', 'BED_22', 'BED_23', 'BED_24']
IC_AVERAGE_PATIENT_AMOUNT = int(len(AVAILABLE_BEDS) / 2)

LOGGER = logging.getLogger('Simulator')
coloredlogs.install(logger=LOGGER)


class Simulator:
    """Class to simulate daily life at the Intensive Care Unit .

    Attributes
    ----------
    mysql_connection : mysql connection
        Description of attribute `mysql_connection`.
    mysql_cursor : mysql cursor
        Description of attribute `mysql_cursor`.
    faker_obj : an instance of the Faker class
        Description of attribute `faker_obj`.
    current_datetime : type
        Description of attribute `current_datetime`.
    available_beds : type
        Description of attribute `available_beds`.
    patients_in_ic : type
        Description of attribute `patients_in_ic`.
    signals : type
        Description of attribute `signals`.
    get_signals : type
        Description of attribute `get_signals`.

    """

    def __init__(self):

        # Create necessary connections and objects
        self.mysql_connection = MySQLdb.connect(**MYSQL_CONFIG)
        self.mysql_cursor = self.mysql_connection.cursor()
        self.faker_obj = Faker('nl_NL')
        self.current_datetime = datetime.strptime(DATETIME_START, DATETIME_FORMAT)
        self.available_beds = AVAILABLE_BEDS
        self.patients_in_ic = []
        self.signals = self.get_signals()

    def get_signals(self):
        """Get all the signals from the database."""

        self.mysql_cursor.execute("SELECT * FROM signals")
        return list(self.mysql_cursor.fetchall())

    def reset_simulation(self):
        """Reset the simulation."""

        # Clean the database
        self.mysql_cursor.execute("DELETE FROM patients")
        self.mysql_cursor.execute("DELETE FROM patient_signal_values")
        self.mysql_connection.commit()

    def replace_into_database(self, table_name, values):
        """Replace a row into a specific database table."""

        # This is safe: https://stackoverflow.com/questions/835092/python-dictionary-are-keys-and-values-always-the-same-order  # noqa
        column_names = list(values.keys())
        values = list(values.values())

        # Dynamically build the query
        # Be aware that the %s is NOT string formatting but parameter binding
        query = 'REPLACE INTO ' + table_name + ' (' + ', '.join(column_names) + \
                ') VALUES (' + ', '.join(['%s'] * len(column_names)) + ')'

        # Execute the query and commit the results
        self.mysql_cursor.execute(query, tuple(values))
        self.mysql_connection.commit()

        return self.mysql_cursor.lastrowid

    def possibly_admit_patient(self, always_admit=False):
        """Admit a fake patient."""

        if (self.decision(FREQ_ADMISSION) and self.available_beds) or always_admit:

            # Get a bed from the available bed list while at the same time removing it from that
            # list
            bed = self.available_beds.pop(randrange(len(self.available_beds)))

            # Construct a fake patient
            patient = {
                "first_name": self.faker_obj.first_name(),
                "last_name": self.faker_obj.last_name(),
                "date_of_birth": self.faker_obj.date_of_birth(),
                "age": self.faker_obj.random_int(min=MIN_AGE, max=MAX_AGE),
                "datetime_admission": self.current_datetime,
                "bed": bed
            }

            patient['id'] = self.replace_into_database(table_name='patients', values=patient)
            self.patients_in_ic.append(patient)
            LOGGER.info(f"Patient admitted to the IC in bed: {bed}.")

    def possibly_discharge_patient(self):
        """Discharge a random patient."""

        # If the IC is already empty, discharge nobody
        if self.decision(FREQ_DISCHARGE * len(self.patients_in_ic) / IC_AVERAGE_PATIENT_AMOUNT):

            # Sometimes pick the patient longest in the IC, sometimes pick a random patient
            # (This is done to ensure people don't remain in the IC forever)
            patient = choice(self.patients_in_ic)

            # Discharge the patient in the database
            patient['datetime_discharge'] = self.current_datetime

            # Update the patient and
            # 1. Remove the patient from the IC
            # 2. Return the bed to the available beds
            self.replace_into_database(table_name='patients', values=patient)
            self.patients_in_ic.remove(patient)
            self.available_beds.append(patient['bed'])
            LOGGER.info("Patient discharged from the IC.")

    def simulate_values_for_patients_in_ic(self):
        """Simulate values for patients that are currently in the IC."""

        for patient in self.patients_in_ic:

            for signal in self.signals:

                if self.decision(FREQ_MEASUREMENTS):

                    row = {
                        'patient_id': patient['id'],
                        'signal_id': signal['id'],
                        'time': self.current_datetime,
                        'value': normal(signal['population_mean'], signal['population_std'])
                    }

                    self.replace_into_database(table_name='patient_signal_values', values=row)

    def next_minute(self):
        """Increase the current datetime with one minute."""

        # Increase to the next minute
        self.current_datetime = self.current_datetime + timedelta(seconds=SECONDS_IN_MINUTE)
        LOGGER.info(f"Current time: {self.current_datetime}")

    @staticmethod
    def decision(probability: float):
        """Get a True with certain probability, or a False otherwise.

        Parameters
        ----------
        probability : float
            The probability with which to return a True.

        Returns
        -------
        bool
            A decision on True or False

        """
        return random() < probability


def run_simulation():
    """Run the simulation."""

    simulator_obj = Simulator()

    simulator_obj.reset_simulation()

    # Admit initial patients
    for i in range(IC_AVERAGE_PATIENT_AMOUNT):
        simulator_obj.possibly_admit_patient(always_admit=True)

    while True:

        # Take a decision about discharge
        simulator_obj.possibly_discharge_patient()

        # Simulate values for all patients currently in the IC
        simulator_obj.simulate_values_for_patients_in_ic()

        # Take a decision about admission
        simulator_obj.possibly_admit_patient()

        # Move the to the next minute
        simulator_obj.next_minute()

        # Sleep for a given amount of time
        sleep(SLOW_FACTOR)


if __name__ == '__main__':

    run_simulation()
