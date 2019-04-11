# ICU Prediction API: Technical Exercises

1. Get familiarized with all the files in the repository. Make sure you understand the difference between the 'Model' as in [Model-View-Controller](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) (*ic_model.py*) and the prediction model to avoid confusion. They carry the same name but are two entirely different concepts.

#### Find the model
2. Locate and update the model (\*)
  1. Go the URL http://localhost/api/get_prediction_for_single_patient/1
  2. Check the order of magnitude of the risk_probability
  3. Open the file */src/patient_prediction_engine.py*. Change the value for *COEFF_AGE* to 0.1.
  4. Refresh http://localhost/api/get_prediction_for_single_patient/1. Did the order of magnitude of the risk_probability indeed change?
  5. Go to the function in line 84 (*src/patient_prediction_engine.py*). What do you think you just did?

#### Play around with the API endpoints
3. We can now visit *localhost/dashboard*, *localhost/api/get_patients_in_ic* and *localhost/api/get_prediction_for_single_patient/{patient_id}*. In this exercise we're going to add *localhost/healthcheck* (\*\*).
  1. Open _src/api.py_
  2. Right before the block with _def dashboard():_ (line 32) add a function `def healthcheck():` that returns "I'm healthy!" (`return "I'm healthy!"`).
  3. Add the _decorator_ `@app.route('/healthcheck')` right above the function. Look at `dashboard()` for an example. What do you think this decorator actually does?
  4. Check in your terminal whether the API container is still running (_docker ps_). If not, run _docker-compose up -d_ to start it up again.
  4. Check whether it works by visiting *localhost/healthcheck* in the browser. If it doesn't work, run _docker logs api_ to see what might be going wrong.


4. Return empty JSON on `/get_prediction_for_single_patient` when the patient left the IC (\*\*).
  1. Locate *get_prediction_for_single_patient* in *src/api.py*.
  2. Right before the line where _response_ is defined, place the following: `if prediction_engine_obj.patient['datetime_discharge'] is not None: return jsonify({})`
  3. Verify your work by looking at the 'dashboard' and finding an ID that's no longer in the IC. Then use that ID in the `/get_prediction_for_single_patient`-url.


5. Add the length of stay in hours to the `/get_prediction_for_single_patient` endpoint (\*\*).
  - Only modify the *get_prediction_for_single_patient*-function in *api.py*.
  - TIP: use both `g.current_datetime` and `prediction_engine_obj.patient['datetime_admission']` to obtain the time difference in hours.x
  - Verify your work by visiting the proper URL.


6. Add the length of stay in hours to the `/dashboard` interface (\*\*\*).
  - You need to modify multiple files.
  - (TIP: `g.current_datetime` is available in all API endpoints.)


7. Add another API endpoint `/get_predictions_for_all_patients` (\*\*\*).
  - Return the JSON as in */get_patients_in_ic*, but add the risk probability for each patient.

#### Add logging
8. Add logging to API endpoints (\*\*\*).
  - For each API call (`get_patients_in_ic` and `get_prediction_for_single_patient`), log the JSON response. Look at *mysql_adapter.py* for examples.
  - Check your logging by running the command `docker logs -f api` from the terminal.


9. Store all predictions in the database (\*\*\*).
  - Add a table to the Pacmed database (TIP: use the database manager). This table should have columns for the patient_id, time and risk_probability.
  - Modify the __patient prediction engine__ to store predictions as well as returning them.
  - Make some API calls. Check whether predictions are indeed logged in the database.
  - (TIP: Use `def replace_into` of the mysql_adapter)

#### Extend the cluster with caching and logging in Elasticsearch
10. Add caching to the application (\*\*\*\*).
  - Add [Redis](https://docs.docker.com/compose/gettingstarted/) to the cluster.
  - Replace the *get_prediction* method with an *add_prediction_to_cache* method. Make sure this function adds the risk_probability to Redis.
  - Make the prediction engine loop continuously. Tip: don't forget to also loop over patients to avoid making predictions for one patient only.
  - Modify the `/get_prediction_for_single_patient` endpoint to get the risk predictions from the cache.


11. Add external logging to the application (\*\*\*\*\*).
  - Add Elasticsearch and Kibana to the cluster.
  - Add logging to the API endpoints.
  - Configure Kibana.
  - Validate the results by checking whether logs are streaming in when you call the API.
