# ICU Prediction API: Exercises

1. Make sure you understand the difference between the 'Model' as in [Model-View-Controller](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) (*ic_model.py*) and the prediction model to avoid confusion. They carry the same name but are two entirely different concepts.

#### Find the model
2. Update the model (\*)
  - Update `x_beta` to be `-5 + 0.01 * age + 0.001 * blood_pressure__last + 0.03 * respiration_rate__mean + 0.02 * temperature_std` in the application.
  - Check whether this indeed greatly influences the risk probability (\*).

#### Play around with the API endpoints
3. Add another API endpoint `/healtcheck` (\*\*).
  - Returns plain text `I'm healthy!` when called.
  - Check whether it works


4. Add the length of stay in hours to the `/get_prediction_for_single_patient` endpoint (\*\*).
  - Only modify *api.py*.
  - (TIP: `g.current_datetime` is available in all API endpoints.)
  - Verify your work


5. Return empty JSON on `/get_prediction_for_single_patient` when the patient left the IC (\*\*).
  - Only modify *api.py*.
  - (TIP: use the `datetime_discharge` attribute of a patient)
  - Verify your work


6. Add another API endpoint `/get_predictions_for_all_patients` (\*\*\*).
  - Return the JSON as in */get_patients_in_ic*, but add the risk probability for each patient.

#### Add logging
7. Add logging to API endpoints (\*\*\*).
  - For each API call (`get_patients_in_ic` and `get_prediction_for_single_patient`), log the JSON response. Look at *mysql_adapter.py* for examples.
  - Check your logging by running the command `docker logs -f api` from the terminal.


8. Store all predictions in the database (\*\*\*).
  - Add a table to the Pacmed database (TIP: use the database manager). This table should have columns for the patient_id, time and risk_probability.
  - Modify the __patient prediction engine__ to store predictions as well as returning them.
  - Make some API calls. Check whether predictions are indeed logged in the database.

#### Extend the cluster with caching and logging in Elasticsearch
9. Add caching to the application (\*\*\*\*).
  - Add [Redis](https://docs.docker.com/compose/gettingstarted/) to the cluster.
  - Replace the *get_prediction* method with an *add_prediction_to_cache* method. Make sure this function adds the risk_probability to Redis.
  - Make the prediction engine loop continuously. Tip: don't forget to also loop over patients to avoid making predictions for one patient only.
  - Modify the `/get_prediction_for_single_patient` endpoint to get the risk predictions from the cache.


10. Add external logging to the application (\*\*\*\*\*).
  - Add Elasticsearch and Kibana to the cluster.
  - Add logging to the API endpoints.
  - Configure Kibana.
  - Validate the results by checking whether logs are streaming in when you call the API.
