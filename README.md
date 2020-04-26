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
    "ip_address": "<PUBLIC HOST ADDRESS>",
    "trello_key": "<TRELLO API KEY>",
    "trello_token": "<TRELLO TOKEN>",
    "trello_secured_enpoint": "<RANDOM WORD TO SECURE ENDPOINT>",
    "trello_dashboard_fullname": "<DASHBOARD NAME>",
    "trello_daily_plan_list_name_regexp": "<DAILY COLUMN NAME IN REGEXP>",
    "trello_weekly_plan_list_name_regexp": "<WEEKLY COLUMN NAME IN REGEXP>",
    "trello_monthly_plan_list_name_regexp": "<MONTHLY COLUMN NAME IN REGEXP>",
    "trello_year_plan_list_name_regexp": "<YEAR COLUMN NAME IN REGEXP>",
    "telegram_token": "<TELEGRAM TOKEN>",
    "telegram_bot_invite_token": "<TELEGRAM BOT INVITE TOKEN>",
    "server_listen_interface": "<0.0.0.0 OR SPECIFIC IPv4 INTERFACE TO LISTEN TRAFFIC>",
    "mongo_path": "<MONGO_DB URL WITH PROVIDED CREDENTIALS>"
}
```

Here is an example of a working **./bot_config.json**:

```
{
    "ip_address": "10.0.34.2",
    "trello_key": "ec40882ffba956174d0892b5752d9979",
    "trello_token": "0987b26546931ec40882ffba969310856174d0892b5752d997933d93aef1becf",
    "trello_secured_enpoint": "9310856174d0892b5752d997933d93a40882ffa7",
    "trello_dashboard_fullname": "ProductivityDashboard",
    "trello_daily_plan_list_name_regexp": "^Daily Plan \\(([0-9]{1,2}.[0-9]{1,2})\\)$",
    "trello_weekly_plan_list_name_regexp": "^Weekly Plan \\(([0-9]{1,2}.[0-9]{1,2}) - ([0-9]{1,2}.[0-9]{1,2})\\)$",
    "trello_monthly_plan_list_name_regexp": "^Monthly Plan \\(([0-9]{1,2}.[0-9]{1,2})\\)$",
    "trello_year_plan_list_name_regexp": "^Plans for this year \\(([0-9]{4})\\)",
    "telegram_token": "8456306476:d9793d93a401713a7933d93a4882f085617",
    "telegram_bot_invite_token": "74d0892b265892b1ec493f198ffba",
    "server_listen_interface": "0.0.0.0",
    "mongo_path": "mongodb://iam:admin@127.0.0.1:27017/lukeskywalker"
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
bash ./run_bot.sh
```

## Authors

* **Valentyn Riabukhin** - *Project owner* - [personal website link](http://valentine-riabukhin.pro)

See also the list of [contributors](http://valentine-riabukhin.pro) who participated in this project.