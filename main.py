import argparse
import re
import time
import os
from urllib.parse import quote

from lyricsgenius import Genius
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv

# I mean, if you're gonna spam someone with song lyrics, might as well do it in style!

WHATSAPP_URL = "https://web.whatsapp.com/send?phone={}&text={}"
XPATH_SEND_BUTTON = '//span[@data-testid="send"]'
INPUT_XPATH = "//div[@id='main']/footer/div/div/span[2]/div/div[2]/div/div/div/p"


def fetch_lyrics(token, song_title):
    # fetch some lyrics!
    try:
        genius = Genius(token)
        song = genius.search_song(song_title)
        return song.lyrics if song else None

    except Exception as e:
        print(f"Oopsie daisy, couldn't fetch the lyrics: {e}")
        return None


def clean_lyrics(text):
    # Clean up the mess, so we can impress!
    try:
        pattern = r"\[.*\]"
        result = re.split(pattern, text)
        result[-1] = re.sub(r"Embed|\d+", "", result[-1])
        text = "".join(filter(lambda x: x.strip(), result[1:]))
        return [line for line in text.split("\n") if line.strip()]

    except Exception as e:
        print(f"Yikes! Couldn't clean the lyrics: {e}")
        return []


def initialize_driver():
    # Get our fancy pants chrome driver ready!
    try:
        driver = webdriver.Chrome()
        return driver

    except Exception as e:
        print(f"Driver decided to take a break today: {e}")
        return None


def send_msg_via_whatsapp(driver, phone, msg, initial_load):
    # Let's slide into those DMs!
    try:
        encoded_msg = quote(msg)

        if initial_load:
            driver.get(WHATSAPP_URL.format(phone, encoded_msg))
            print("Hold on, warm up for 20 seconds!")

            time.sleep(20)

        else:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, INPUT_XPATH))
            )
            element.send_keys(msg)

            time.sleep(1)

        element = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_SEND_BUTTON))
        )
        element.click()

        time.sleep(2)

    except Exception as e:
        print(f"WhatsApp is playing hard to get: {e}")


def main(token, song_title, recipient):
    # Main party starts here!
    lyrics = fetch_lyrics(token, song_title)

    if not lyrics:
        print(f"Couldn't find lyrics for {song_title}. Maybe it's too deep?")
        return

    cleaned_lyrics = clean_lyrics(lyrics)

    driver = initialize_driver()

    if not driver:
        print("Driver's gone missing!")
        return

    initial_load = True

    for msg in cleaned_lyrics:
        send_msg_via_whatsapp(driver, recipient, msg, initial_load)
        initial_load = False

    driver.quit()

    print("And... we're done! Mic drop LOL!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wanna send song lyrics via WhatsApp? Let's do it!"
    )
    parser.add_argument("-s", "--song", required=True, help="What's the jam?")
    parser.add_argument("-r", "--recipient", required=True, help="Who's the target?")
    args = parser.parse_args()
    load_dotenv()
    token = os.environ.get("GENIUS_API_TOKEN")
    if not token:
        print("No GENIUS_API_TOKEN?.")
        exit(1)
    main(token, args.song, args.recipient)
