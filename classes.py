import requests
from notifiers import get_notifier
import json
from os import getenv
from dotenv import load_dotenv


load_dotenv("discord.env")
TOKEN = getenv("DISCORD_TOKEN")
USERNAME = getenv("NICKNAME")
PASSWORD = getenv("PASSWORD")

EMAIL = getenv("EMAIL")
EMAIL_PASSWORD = getenv("EMAIL_PASSWORD")
HOST = getenv("HOST")

class MemeGenerator:
    def __init__(self) -> None:
        pass

    def list_memes(self) -> str:
        """
        I stored the content of the site into a variable "memes".
        For each meme in all_memes it will store an id
        and name of that meme into the variable meme_list (string).
        In the task it's said, that it should only return
        25 most popular memes, so that's why I have a condition there.
        """
        memes = requests.get("https://api.imgflip.com/get_memes").content
        json_memes_content: json = json.loads(memes)
        all_memes: dict = json_memes_content["data"]["memes"]
        memes: str = ""
        n: int = 0
        for meme in all_memes:
            if n < 25:
                memes += f"{str(meme['id']).ljust(10,' ')}{meme['name']}\n"
                n += 1
        return memes

    def make_meme(
            self, template_id: int, top_text: str, bottom_text: str) -> str:

        URL: str = "https://api.imgflip.com/caption_image"
        params: dict = {
            'username': USERNAME,
            'password': PASSWORD,
            'template_id': template_id,
            'text0': top_text,
            'text1': bottom_text
            }
        response = requests.request('POST', URL, params=params).json()
        # returns URL of the generated meme
        return response['data']['url']


class MentionsNotifier:
    subscribers = {}
    emails = {}

    def __init__(self) -> None:
        pass

    def subscribe(self, user_id: int, email: str) -> None:
        self.subscribers[user_id] = True
        self.emails[user_id] = email

    def unsubscribe(self, user_id: int) -> None:
        self.subscribers[user_id] = False

    def notify_about_mention(self, user_id: int, msg_content: str) -> None:
        # DONE
        email = get_notifier('email')
        settings = {
            'host': HOST,
            'port': 465,
            'ssl': True,

            'username': EMAIL,
            'password': EMAIL_PASSWORD,

            'to': self.emails[user_id],
            'from': EMAIL,

            'subject': "Discord Mention",
            'message': msg_content,
        }
        email.notify(**settings)


class Hangman():
    def __init__(
         self, player, guesses, lives, secret_word, wrong_or_right
         ) -> None:

        self.player = player
        self.guesses = guesses
        self.lives = lives
        self.secret_word = secret_word
        self.wrong_or_right = wrong_or_right

    def call_hangman(self):
        hangman_str: str = f"""
Player: {self.player}
Guesses: {self.guesses}
Lives: {self.lives}
Word: {self.secret_word}
{self.wrong_or_right}
"""
        return hangman_str
