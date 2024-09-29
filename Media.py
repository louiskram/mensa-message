import re
import logging
from pathlib import Path
from instagrapi import Client
from login_user import login_user

class Media:
    def __init__(self, config):
        self.config = config
        self.instagram_client = Client()
        try:
            login_user(self.instagram_client, config['username'], config['password'])
            logging.info("Successfully logged in to Instagram")
        except Exception as e:
            logging.error(f"Failed to log in to Instagram: {e}")
            raise

        self.user_id = 55356066885 # instagram_client.user_id_from_username("mensa.out.of.10")

    def get_newest_post_metadata(self, user_id: int) -> dict:
        newest_post_metadata = self.instagram_client.user_medias(user_id, amount=1)
        newest_post_metadata = newest_post_metadata[0].dict()
        logging.info("Retrieved newest post metadata")
        return newest_post_metadata

    def get_newest_post_date(self, newest_post_metadata: dict) -> str:
        newest_post_date = newest_post_metadata["taken_at"]
        formatted_date = newest_post_date.strftime("%Y-%m-%d")
        logging.info(f"Newest post date: {formatted_date}")
        return formatted_date

    def get_rating(self, newest_post_metadata: dict) -> str:
        rating_pattern = r"(\d|\d(\.|,)\d+)\/10"
        try:
            rating = re.search(rating_pattern, newest_post_metadata["caption_text"]).group()
            logging.info(f"Retrieved rating: {rating}")
            return rating
        except AttributeError:
            logging.error("Failed to find rating in post caption")
            raise

    def get_photo(self, newest_post_metadata: dict) -> Path:
        media_pk = newest_post_metadata["pk"]
        photo_path = self.instagram_client.photo_download(media_pk)
        photo_path = Path(photo_path)
        photo_path = photo_path.rename(Path(photo_path.parent, f"{photo_path.stem}.jpg"))
        logging.info(f"Downloaded and converted photo: {photo_path}")
        return photo_path