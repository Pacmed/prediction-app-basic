# -*- encoding: utf-8 -*-
"""ICU Prediction API: API.

Author: Bas Vonk
Date: 2019-04-01
"""

from flask import Flask, jsonify, request, g
from src.patient_prediction_engine import PatientPredictionEngine
from src.icu_model import ICUModel

# Initialize the app and define the folder with the builds and static files
app = Flask(__name__)


@app.before_request
def get_icu_model():
    """Before every call, get an instance of the ICUModel."""

    g.icu_model_obj = ICUModel()
    g.current_datetime = g.icu_model_obj.get_current_simulated_time()


@app.teardown_appcontext
def close_connection(error):
    """Delete the ICUModel instance after every call (also closing the MySQL connection)."""

    del g.icu_model_obj


@app.route('/get_patients_in_ic')
def get_patients_in_ic():
    """Get all patients currently in the IC.

    Response format:
    {
      "data": [
        {
          "age": 64,
          "bed": "BED_20",
          "date_of_birth": "Thu, 07 Mar 1974 00:00:00 GMT",
          "datetime_admission": "Fri, 18 Oct 2019 19:46:00 GMT",
          "datetime_discharge": null,
          "first_name": "Milan",
          "id": 1047,
          "last_name": "van den Brink"
        },
        ...
      ],
      "links": {
        "self": "http://localhost/get_patients_in_ic"
      }
    }
    """

    response = {
        "data": g.icu_model_obj.get_patients_in_ic(),
        "links": {
            "self": request.url
        },
    }
    return jsonify(response)


@app.route('/get_prediction_for_single_patient/<int:patient_id>')
def get_prediction_for_single_patient(patient_id):
    """Get a prediction for a single patient.

    Response format:
    {
      "data": {
        "patient": {
          "age": 55,
          "bed": "BED_10",
          "date_of_birth": "Fri, 23 Jun 2017 00:00:00 GMT",
          "datetime_admission": "Tue, 01 Jan 2019 00:00:00 GMT",
          "datetime_discharge": "Fri, 04 Jan 2019 07:32:00 GMT",
          "first_name": "Cornelis",
          "id": 490,
          "last_name": "van Egisheim"
        },
        "risk_probability": 0.0150183224986214
      },
      "links": {
        "self": "http://localhost/get_prediction_for_single_patient/490"
      }
    }
    """

    prediction_engine_obj = PatientPredictionEngine(patient_id, g.icu_model_obj)

    response = {
        "data": {
            "patient": prediction_engine_obj.patient,
            "risk_probability": prediction_engine_obj.get_prediction()
        },
        "links": {
            "self": request.url
        },
    }

    return jsonify(response)


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True, host='0.0.0.0', port=80)
