# ICU Prediction API

## Disclaimer
This tool is optimised for educational purposes, do **not** use this in production!

## Folder structure
```
├── LICENSE
├── README.md          <- The top-level README for developers using this project
├── EXERCISES.md       <- Contains the exercises for this case
├── data
│   ├── db_data        <- Empty folder. MySQL docker container persists storage here
│   └── db_structure   <- Contains a .sql file with the structure for the database
│
├── docker-compose.yml <- The docker-compose file for this project
├── Dockerfile         <- Dockerfile for the API and the simulator
├── requirements.txt   <- Lists all packages required to run this software
├── setup.cfg          <- Contains configuration for pycodestyle and pydocstyle
├── setup.py           <- Makes this package installable
├── simulator.py       <- Simulator script that simulates daily life at the IC
├── src                <- Source code for use in this project.
│   ├── templates      <- Folder with the templates for the application
│   │   └── dashboard.html <- The template for the dashboard endpoint  
│   ├── __init__.py    <- Makes src a Python module
│   ├── api.py         <- Script with the Flask/API-code
│   ├── config.py      <- Script with configuration
│   ├── icu_model.py   <- Script with a data-layer for the ICU
│   ├── mysql_adapter.py <- code with an adapter for the Python MySQLdb package
│   └── patient_prediction_engine.py <- Script to make a prediction for a single patient (contains the prediction model)
│
└── .gitignore         <- Indicates which files should never be uploaded to git
```

## Prerequisites
- [Docker](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Get started
- Make sure Docker is running
- Open the terminal
- Make sure docker-compose is available by running `docker-compose -v`
- Run `docker-compose up -d` from the root of this repository
- Make sure that four containers are running with `docker ps`
- Check whether required services are accessible in the browser:
  1. Application:
     - `localhost/dashboard`
  2. API:
     - `localhost/api/get_patients_in_ic`
     - `localhost/api/get_prediction_for_single_patient/{patient_id}`. Replace `{patient_id}` with a patient id to be found in the response of the first call.
  3. Database Manager: ```localhost:8080``` with credentials *icu_username/icu_password*
