# Mensa-Message

This is a small script that, when executed, retrieves the daily meal from the OpenMensa API and sends it to a Signal group chat by using the [Signal-Cli-REST-API](https://github.com/bbernhard/signal-cli-rest-api). If a critique by `mensa.out.of.10` has already been published on Instagram, the script embeds the rating and attaches the image to the message. 

The idea is, that before lunch time this script gets executed so one doesn't have to manually check the meal and its rating.

Steps to setup:
1. Pull the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install `signal-cli-rest-api`
4. Configure `config.json`
5. Test the script: `python main.py`
6. Add to crontab: `crontab -e` e.g. `0 11 * * * python /path/to/mensa-message/main.py`