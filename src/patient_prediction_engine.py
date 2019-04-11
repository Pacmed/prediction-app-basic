# -*- encoding: utf-8 -*-
"""ICU Prediction API: Patient Prediction Engine.

Author: Bas Vonk
Date: 2019-04-01
"""

import math
import pandas as pd

CONSTANT = -5
COEFF_AGE = 0.1
COEFF_BLOOD_PRESSURE_LAST = 0.001
COEFF_RESPIRATION_RATE_MEAN = 0.03
COEFF_TEMPERATURE_STD = 0.02


class PatientPredictionEngine:
    """Class to make predictions for a single patient.

    Parameters
    ----------
    patient_id : int
        The ID of the patient for which to predict.
    icu_model_obj : ICUModel
        An instance of the ICUModel object.

    Attributes
    ----------
    patient : Dict[str, Union[str, int, datetime]]
        The ID of the patient for which to predict.
    icu_model_obj : ICUModel
        An instance of the ICUModel object.
    """

    def __init__(self, patient_id, icu_model_obj):

        self.icu_model_obj = icu_model_obj
        self.patient = icu_model_obj.get_patient(patient_id)

    def get_df_records(self):
        """Get the records (signal values) for a specific patient.

        Returns
        -------
        pd.DataFrame
            Pandas dataframe with the signal values (contains columns 'name', 'time' and 'value')

        """

        data = self.icu_model_obj.get_signal_values_for_patient(self.patient['id'])
        return pd.DataFrame(data)

    def get_features(self, df_records):
        """Get features (do feature engineering).

        Parameters
        ----------
        df_records : pd.DataFrame
            Pandas dataframe with the signal values (contains columns 'name', 'time' and 'value')

        Returns
        -------
        Dict[str, Union[int, float]]
            Dictionary with feature values.

        """

        df_records.sort_values(by=['time'], inplace=True)
        features = df_records.groupby('name').agg(['mean', 'std', 'last']).loc[:, 'value']

        assert 'blood_pressure' in set(df_records.name), "'blood pressure' signals are missing."
        assert 'respiration_rate' in set(df_records.name), "'respirate rate' signals are missing."
        assert 'temperature' in set(df_records.name), "'temperate' signals are missing."

        return {
            'age': self.patient['age'],
            'blood_pressure__last': features.loc['blood_pressure', 'last'],
            'respiration_rate__mean': features.loc['respiration_rate', 'mean'],
            'temperature__std': features.loc['temperature', 'std']
        }

    @staticmethod
    def predict(features):
        """Make and return a prediction.

        Parameters
        ----------
        features : Dict[str, Union[int, float]]
            Dictionary with the features.

        Returns
        -------
        float
            A float value with a risk probability

        """

        assert 'age' in features, "'age' feature is missing."
        assert 'blood_pressure__last' in features, "'blood pressure' feature is missing."
        assert 'respiration_rate__mean' in features, "'respirate rate' feature is missing."
        assert 'temperature__std' in features, "'temperate' feature is missing."

        # This is the model (in practice this will probably be a .pickle file)
        x_beta = CONSTANT + \
            COEFF_AGE * features['age'] + \
            COEFF_BLOOD_PRESSURE_LAST * features['blood_pressure__last'] + \
            COEFF_RESPIRATION_RATE_MEAN * features['respiration_rate__mean'] + \
            COEFF_TEMPERATURE_STD * features['temperature__std']

        return math.exp(x_beta) / (1 + math.exp(x_beta))

    def get_prediction(self):
        """Get a prediction for the patient."""

        # Extract raw data from the database
        df_records = self.get_df_records()

        # Do feature engineering
        features = self.get_features(df_records)

        # Make a prediction
        prediction = self.predict(features)

        return prediction
