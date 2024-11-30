# Alpaca Trading Systems


## Instructions
1) Clone the repository
2) Create a virtual env
3) Install all packages from requirements.txt
4) create a config directory in the repository
5) Setup the configuration as instructed below
6) Run main.py

## Configuration

To set up the Alpaca API, create a `config.yaml` file in the `config/` directory with the following structure:

```yaml
alpaca:
  data_api: <data_api>          # URL for Alpaca's data API
  paper_api: <paper_api>        # URL for Alpaca's paper trading API
  api_key: <your_api_key_here>  # Your Alpaca API key
  secret_key: <your_secret_key_here>  # Your Alpaca secret key

```

## 

## Project Structure

| Module/File   | Description                                                                          |
|:--------------|:-------------------------------------------------------------------------------------|
| api           | Make calls to external Alpaca API                                                    |
| config        | You need to make a config/config.yaml file which contains the api configuration keys |
| models        |                                                                                      |
| data          |                                                                                      |
| tests         |                                                                                      |
| utils         |                                                                                      |
| config_loader | use this file to load the configs from the .yaml file                                |
| main          |                                                                                      |       