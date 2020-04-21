# Trello Time Manager

This is a project for improving my own productivity using tools like Trello Dashboards and Telegram.  
Trello dashboards is used for tracking, planning and saving of my personal activity and Telegram is used to alert me about different changes on dashboards.

## Getting Started

Before starting you need:

* Obtain the **Trello API KEY** and **TOKEN** credentials and make sure they are valid
* Create Telegram bot and receive **telegram token**

### Prerequisites

Required software and libraries for working with the project:

* Python 3 (3.6.9)
* pip (pip3 9.0.1)
* Python libraries: reqeusts, schedule, pymongo
* Bash 4 (4.4.20)
* Docker and docker-compose
* OpenSSL 1.1.1
* curl
* jq 1.5.1

### Prepare config for running

For correct work of application it's necessary to prepare the following configuration file and store it along the path **./bot_config.json**:

```
{ 
    "trello_key": "<TRELLO API KEY>",
    "trello_token": "<TRELLO TOKEN>",
    "telegram_token": "<TELEGRAM TOKEN>",
    "server_listen_interface": "<0.0.0.0 OR SPECIFIC IPv4 INTERFACE TO LISTEN TRAFFIC>",
    "mongo_path": "<MONGO_DB URL WITH PROVIDED CREDENTIALS>"
}
```

### Running locally

If you have already installed everything you need from the previous paragraphs, then you can start the project as follows.

* Run local MongoDB database to store all necessary trello and telegram activity using Docker and docker-compose:
```
docker-compose -f ./infra-compose up -d
```

* Run application by provided shell script:

```
bash ./run_bot.sh "${ip_address}"
```

## Authors

* **Valentyn Riabukhin** - *Project owner* - [personal website link](http://valentine-riabukhin.pro)

See also the list of [contributors](http://valentine-riabukhin.pro) who participated in this project.