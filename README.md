# Taxi_formula_revelation

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Predicting taxi-aggregator ride price with use of distance, traffic jam and weather information.

## Getting Started

To launch the program on your computer, follow these steps:

### 0. Install Docker And GitBash if needed
Currently avaliable installation websites links are: <br>
For Docker: https://docker-docs.uclv.cu/get-docker/ <br>
For GitBash: https://git-scm.com/downloads

### 1. Clone/fork this repository on your computer

Using GitBash:
```bash
git clone https://github.com/Kalmy8/Taxi_cost_formula_prediction
```
### 2. Create a `.env` File

Use the `env_template.env` file as a reference to create your `.env` file. This file should contain all the necessary environment variables required for the script to run.

## 3. Launch script
You can launch all scripts from the original repository manually, 
which requires proper environment setup which is described further.

For some other script using Docker is also an alternative.

### 3.1 Manual invokation

You can either manually create a Conda environment with the packages listed in `requirements.txt`, or use the provided Makefile target to create the environment for you:

- **Manual Setup**: 
    ```bash
    conda create --name your_environment_name --file requirements.txt
    conda activate your_environment_name
    ```

- **Automated setup**:
    ```bash
    make create_environment
    ```

### 3.2 Running the Data Mining Script
You can launch datamining process manually invoking `./taxi/data/launch_datamining.py` script.

The other option is using the `Makefile`, which automatically builds and start this process via docker.
You also have 2 options to choose on how to store mined data:

- **Save mined data locally**:
    If you want mined data to be saved locally in the project folder, 
    use following command, passing the 'FREQUENCY' argument:
    ```bash
    make datamining FREQUENCY=10
    ```
    At the provided example, each new observation will be collected within 10 minutes


- **Auto-Push mined data to GitHub**
  If you want to automatically push mined data to the GitHub .env {DATA_BRANCH_NAME} repository,     
  use the following command, passing both the FREQUENCY and NEW_OBSERVATIONS_PER_PUSH parameters:
  ```bash
  make datamining FREQUENCY=10 NEW_OBSERVATIONS_PER_PUSH=5
  ```
  At the provided example, each new observation will be collected within 10 minutes,
  every five of them will be pushed to the remote branch 

  **Note:** This option requires additional variables to be specified in the .env file:

  ```dotenv
  # GitHub credentials for auto-pushing mined data to the specified repository
  GITHUB_USERNAME=YOUR_USERNAME
  GITHUB_TOKEN=YOUR_TOKEN
  GITHUB_EMAIL=YOUR_EMAIL
  REPO_URL=YOUR_REPO_URL

  # You should create a specific branch for storing data miner's work, for example 'data-branch'
  DATA_BRANCH_NAME=data-branch
  ```






## Project File Structure

```
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks including script's prototypes.
│
├── pyproject.toml     <- Project configuration file with package metadata
│                         and configuration for tools like black
│
├── Dockerfile         <- Dockerfile building image
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
└── taxi                <- Source code for use in this project.
    │
    ├── __init__.py    <- Makes taxi a Python module
    │
    ├── data           <- Scripts to download or generate data
    │   └── mine_taxi_website.py
    │   └── launch_datamining.py
    │
    ├── features       <- Scripts to turn raw data into features for modeling
    │   
    │
    ├── models         <- Scripts to train models and then use trained models to make
    │   │                 predictions
    │   ├── predict_model.py
    │   └── train_model.py
    │
    └── visualization  <- Scripts to create exploratory and results oriented visualizations
        └── visualize.py
```

--------

