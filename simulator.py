# -*- encoding: utf-8 -*-
"""ICU Prediction API: Simulator.

Author: Bas Vonk
Date: 2019-04-01
"""

from random import random, choice, randrange
from datetime import datetime, timedelta
from time import sleep
import logging
from numpy.random import normal
from faker import Faker
import coloredlogs
from src.mysql_adapter import MySQL
from sys import exit

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

# A day takes 1440 (24 * 60) iterations/minutes. For a fake day to last 5 minutes, we need to sleep
# 1 / 24 seconds for each iteration/minute
SLOW_FACTOR = 1 / 24

AVAILABLE_BEDS = ['BED_01', 'BED_02', 'BED_03', 'BED_04', 'BED_05', 'BED_06', 'BED_07', 'BED_08',
                  'BED_09', 'BED_10', 'BED_11', 'BED_12', 'BED_13', 'BED_14', 'BED_15', 'BED_16',
                  'BED_17', 'BED_18', 'BED_19', 'BED_20', 'BED_21', 'BED_22', 'BED_23', 'BED_24']
IC_AVERAGE_PATIENT_AMOUNT = int(len(AVAILABLE_BEDS) / 2)

# Define a logger
LOGGER = logging.getLogger('Simulator')
coloredlogs.install(logger=LOGGER)


class Simulator:
    """Class to simulate daily life at the Intensive Care.

    Attributes
    ----------
    mysql_obj : MySQL
        An instance of the MySQL class
    faker_obj : Faker
        An instance of the Faker class.
    current_datetime : datetime
        The current datetime (in the simulation, not the actual datetime)
    available_beds : List[str]
        Object that lists all available beds
    patients_in_ic : List[Dict[str, Union[str, datetime, int]]]
        List with patients that are currently in the IC
    signals : List[Dict[str, Union[str, datetime, int]]]
        List with all signals that are available for this simulation

    """

    def __init__(self):

        # Create necessary connections and objects
        self.mysql_obj = MySQL()
        self.faker_obj = Faker('nl_NL')
        self.current_datetime = datetime.strptime(DATETIME_START, DATETIME_FORMAT)
        self.available_beds = AVAILABLE_BEDS
        self.patients_in_ic = []
        self.signals = self.get_signals()

    def get_signals(self):
        """Get all the signals from the database."""

        return self.mysql_obj.fetch_rows("SELECT * FROM signals")

    def reset_simulation(self):
        """Reset the simulation."""

        # Clean the database from previous simulations
        self.mysql_obj.execute_query("TRUNCATE patients")
        self.mysql_obj.execute_query("TRUNCATE patient_signal_values")

    def possibly_admit_patient(self, always_admit=False):
        """Admit a fake patient."""

        # General strategy:
        # 1. Decide whether to admit a fake patient, based on chance and whether there are free beds
        # 2. Assign a bed (and remove it from the 'free beds' list)
        # 3. Build a fake patient object
        # 4. Add the fake patient to the database and to the patients_in_ic object

        if (self.decision(FREQ_ADMISSION) and self.available_beds) or always_admit:

            # Get a bed from the available bed list while at the same time removing it from that
            # list (a bed can only be assigned once)
            bed = self.available_beds.pop(randrange(len(self.available_beds)))

            # Simulate a date of birthe for this patient
            date_of_birth = self.faker_obj.date_of_birth()

            # Construct a fake patient
            patient = {
                "first_name": self.faker_obj.first_name(),
                "last_name": self.faker_obj.last_name(),
                "date_of_birth": date_of_birth,
                "age": (self.current_datetime.date() - date_of_birth).days / 365,
                "datetime_admission": self.current_datetime,
                "bed": bed
            }

            patient['id'] = self.mysql_obj.replace_into(table_name='patients', values=patient)
            self.patients_in_ic.append(patient)
            LOGGER.info(f"Patient admitted to the IC in bed: {bed}.")

    def possibly_discharge_patient(self):
        """Discharge a random patient."""

        # General strategy:
        # 1. Decide whether to admit a fake patient, based on chance:
        #    This is built in a way that the chance of discharge is actually influenced by
        #    the average amount of patients that can be in the IC. On average we discharge 2
        #    patients per day (same as the amount of patients admitted), but we increase the
        #    chance of discharge when there's many patients in the IC and decrease the change when
        #    there's little patients in the IC. The purpose is to always keep around 12 patients
        #    at the IC.
        # 2. Pick a random patient currently at the IC
        # 3. Set the discharge time (this is the 'current' time)
        # 4. Update the patient in the database
        # 5. Remove the patient from the list with patients currently in the IC
        # 6. Make the bed the patient was in available again
        #
        if self.decision(FREQ_DISCHARGE * len(self.patients_in_ic) / IC_AVERAGE_PATIENT_AMOUNT):

            # Sometimes pick the patient longest in the IC, sometimes pick a random patient
            # (This is done to ensure people don't remain in the IC forever)
            patient = choice(self.patients_in_ic)

            # Discharge the patient in the database
            patient['datetime_discharge'] = self.current_datetime

            # Update the patient and
            # 1. Remove the patient from the IC
            # 2. Return the bed to the available beds
            self.mysql_obj.replace_into(table_name='patients', values=patient)
            self.patients_in_ic.remove(patient)
            self.available_beds.append(patient['bed'])
            LOGGER.info("Patient discharged from the IC.")

    def simulate_values_for_patients_in_ic(self):
        """Simulate values for patients that are currently in the IC."""

        # General strategy:
        # 1. Loop over all patients
        #    1.1 Loop over all signals that are in the simulation
        #        1.1.1 For each signal build the row-object
        #              The value is drawn from a normal distribution with population meand and std
        #        1.1.2 Replace the row into the database

        for patient in self.patients_in_ic:

            for signal in self.signals:

                if self.decision(FREQ_MEASUREMENTS):

                    row = {
                        'patient_id': patient['id'],
                        'signal_id': signal['id'],
                        'time': self.current_datetime,
                        'value': normal(signal['population_mean'], signal['population_std'])
                    }

                    self.mysql_obj.replace_into(table_name='patient_signal_values', values=row)

    def next_minute(self):
        """Increase the current datetime with one minute."""

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

    # General strategy:
    # 1. Initialize the Simulator class
    # 2. Reset the simulation (remove all patients and values)
    # 3. Initially admit a certain amount of patients
    # 4. Start simulating minutes, for each minute:
    #    4.1 Possibly discharge a patient (on average 2 per day)
    #    4.2 Simulate values for the patients that are still in the IC
    #    4.3 Possibly admit a patient (on average 2 per day)
    #    4.4 Go to the next minute
    #    4.5 Sleep a while to control the speed of the simulation

    simulator_obj = Simulator()

    simulator_obj.reset_simulation()

    # Admit initial patients
    for _ in range(IC_AVERAGE_PATIENT_AMOUNT):
        simulator_obj.possibly_admit_patient(always_admit=True)

    while True:

        simulator_obj.possibly_discharge_patient()

        simulator_obj.simulate_values_for_patients_in_ic()

        simulator_obj.possibly_admit_patient()

        simulator_obj.next_minute()

        sleep(SLOW_FACTOR)


if __name__ == '__main__':

    run_simulation()
