import base64
import json
import os
import requests
import logging
from datetime import datetime
from Signal import Signal
from Media import Media

TODAY = datetime.today().strftime('%Y-%m-%d')
CONFIG_FILE = "config.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)-8s - %(message)s')

def load_config() -> dict:
    """
    Loads the configuration from the config.json file.
    """
    script_directory = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_directory, CONFIG_FILE)
    try:
        with open(full_path, 'r') as file:
            config = json.load(file)
        logging.info("Configuration loaded successfully")
        return config
    except FileNotFoundError:
        logging.error(f"Config file not found: {full_path}")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in config file: {full_path}")
        raise

def get_mensa_data(mensa_id: int) -> str:
    """
    Retrieves the meal data from the OpenMensa API.
    """
    api_url = f"https://openmensa.org/api/v2/canteens/{mensa_id}/days/{TODAY}/meals"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        meal = data[-1]["name"] if data else ""
        meal_formatted = meal.replace("\n", "")
        logging.info(f"Retrieved meal data: {meal_formatted}")
        return meal
    except requests.RequestException as e:
        logging.error(f"Error fetching mensa data: {e}")
        raise

def main():
    config = load_config()
    mensa_id = config["mensa_id"]
    meal = get_mensa_data(mensa_id)
    if not meal:
        logging.warning("No meal found for today")
        return

    media = Media(config)
    signal = Signal(config)

    newest_post_metadata = media.get_newest_post_metadata(media.user_id)
    newest_post_date = media.get_post_date(newest_post_metadata)

    if TODAY == newest_post_date:
        rating = media.get_rating(newest_post_metadata)
        photo_path = media.get_photo(newest_post_metadata)

        with open(photo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data)
        message = f'{rating}: {meal}'
        response = signal.send_image(encoded, message)

        logging.info("Removing photo")
        os.remove(photo_path)
    else:
        logging.info(f'Sending meal without rating and photo: {meal}')
        response = signal.send_message(meal)

if __name__ == "__main__":
    main()