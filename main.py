import base64
import json
from pathlib import Path
import re
from instagrapi import Client
import requests
from datetime import datetime

from login_user import login_user
import config

today = datetime.today().strftime('%Y-%m-%d')
cl = Client()

# # # # # # Grab Insta-Data
login_user(cl, config.username, config.username)

user_id = 55356066885 # cl.user_id_from_username("mensa.out.of.10")

# get metadata of newest post
# return value is a list so convert it to string and strip open and closing brackets 
newest_post_metadata = str(cl.user_medias(user_id, 1))[1:-1]

# post only relevant if its from today
newest_post_date = re.search("\d{4}, \d{1,2}, \d{1,2}", newest_post_metadata).group()
datetime_object = datetime.strptime(newest_post_date, "%Y, %m, %d") # convert to correct format
newest_post_date = str(datetime_object.date())

rating = ""
if newest_post_date == today:
    # rating can be a float
    rating = re.search("(\d|\d\.\d+)\/10", newest_post_metadata).group()

    # pk is the only number exactly 19 characters long
    media_pk = re.search("\d{19}", newest_post_metadata).group()

    # somehow the downloaded photo has .heic file extension. convert it to jpg.
    photo_path = cl.photo_download(media_pk)
    photo_path = Path(photo_path)
    photo_path = photo_path.rename(Path(photo_path.parent, f"{photo_path.stem}.jpg"))

# # # # # # # # MENSA DATA
api_url = f"https://openmensa.org/api/v2/canteens/279/days/{today}/meals"
response = requests.get(api_url)

meal = ""
if response.status_code == 200:
    response_json = response.json()
    meal = (response_json[-1]["name"])[:-1]


# # # # # # # # SEND TO SIGNAL
if today == newest_post_date:
    with open(photo_path, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data)

headers = {'Content-Type': 'application/json'}

data = {
    'number': config.send_phone_no,
    'recipients': [config.rec_group_id],
}
if rating:
    data['message'] = f'{rating}: {meal}'
    data['base64_attachments'] = [encoded.decode()]
else:
    data['message'] = meal

if meal: 
    response = requests.post(f"{config.signal_api_ip}/v2/send", headers=headers, data=json.dumps(data))
    print(response)
