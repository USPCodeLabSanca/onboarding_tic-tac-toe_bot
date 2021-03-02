# Onboarding's Tic-Tac-Toe Telegram Bot

Hi! This is a Telegram bot that let's you play tic-tac-toe with your friends!

## Getting started

First, make sure you have python3 and pip installed in your machine. Then, follow this steps:

### Activate virtualenv

We are going to use virtualenvs so that none of you have to install the packages we are going to use in your machine's base environment. If you don't have virtualenv installed, just use:

``` bash
pip install virtualenv
```

With virtualenv at your disposal, run

``` bash
source venv/bin/activate
```

If you're in Linux or 

``` bash
venv\Scripts\activate
```

If you're in Windows.

### Install dependencies

To install the dependencies needed, simple run

``` bash
pip install -f requirements.txt
```

### Running the bot

To run it, simple use

``` bash
python network.py
```

or

``` bash
python game.py
```

Depending on which team you are working: "network.py" is for team 1 and "game.py" is for team 2.

You can also use [nodemon](https://www.npmjs.com/package/nodemon "Nodemon's Homepage") to run the bots. Simply use:

``` bash
nodemon [bot_name].py
```
