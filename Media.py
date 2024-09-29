import re
import logging
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import os

class Media:
    def __init__(self, config):
        self.config = config
        self.instagram_client = Client()

        try:
            self.login_user(config['username'], config['password'])
            logging.info("Successfully logged in to Instagram")
        except Exception as e:
            logging.error(f"Failed to log in to Instagram: {e}")
            raise

        self.user_id = 55356066885 # self.instagram_client.user_id_from_username("mensa.out.of.10")

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
    
    def login_user(self, username: str, password: str):
        """
        Attempts to login to Instagram using either the provided session information
        or the provided username and password.
        """
        script_directory = os.path.dirname(os.path.abspath(__file__))
        filename = self.config["session_file"]
        full_path = os.path.join(script_directory, filename)

        session = self.instagram_client.load_settings(full_path)

        login_via_session = False
        login_via_pw = False

        if session:
            try:
                self.instagram_client.set_settings(session)
                self.instagram_client.login(username, password)

                # check if session is valid
                try:
                    self.instagram_client.get_timeline_feed()
                    logging.info("Successful login")
                except LoginRequired:
                    logging.info("Session is invalid, need to login via username and password")

                    old_session = self.instagram_client.get_settings()

                    # use the same device uuids across logins
                    self.instagram_client.set_settings({})
                    self.instagram_client.set_uuids(old_session["uuids"])

                    self.instagram_client.login(username, password)
                login_via_session = True
            except Exception as e:
                logging.info("Couldn't login user using session information: %s" % e)

            if not login_via_session:
                try:
                    logging.info("Attempting to login via username and password. username: %s" % username)
                    if self.instagram_client.login(username, password):
                        login_via_pw = True
                except Exception as e:
                    logging.info("Couldn't login user using username and password: %s" % e)

            if not login_via_pw and not login_via_session:
                raise Exception("Couldn't login user with either password or session")
