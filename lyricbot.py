#!/usr/local/opt/python/bin/python3.7

import tweepy
import json
import requests
from os import sep

import random

from lyrical import lyrics_from_genius_by_url
from lyrical import show_lyrics

from googleapi import make_snippet_list_from_doc

char_limit = 280

#Load creds for Twitter & Genius APIs
with open("credentials" + sep + "secret.json") as jf:
    creds = json.load(jf)


def setup_user(api_user):
    auth = tweepy.OAuthHandler(creds[api_user]['api_key'], creds[api_user]['api_secret'])
    auth.set_access_token(creds[api_user]['access_token'], creds[api_user]['access_secret'])
    return tweepy.API(auth)


artist_ids = {
    "Kero Kero Bonito":"231956",
    "Death Grips":"11778"
}


base_url = 'https://api.genius.com'


def get_artist_songs(aid): #Wholesale stolen from https://www.jw.pe/blog/post/quantifying-sufjan-stevens-with-the-genius-api-and-nltk/
    url = base_url + "/artists/" + aid + "/songs"
    token = "Bearer " + creds["genius"]["access_token"]
    headers = {"Authorization": token}

    current_page = 1
    next_page = True
    songs = []

    while next_page:
        response = requests.get(url=url, params={"page":current_page}, headers=headers).json()
        page_songs = response['response']['songs']

        if page_songs:
            songs += page_songs
            current_page += 1
        else:
            next_page = False

    return [s for s in songs if s["primary_artist"]['id'] == int(aid)]

def get_lyric_snippet(aid):
    passed = False

    if aid.isdigit():
        songs = get_artist_songs(aid)
    elif artist_ids.__contains__(aid):
        songs = get_artist_songs(artist_ids[aid])
    else:
        raise TypeError("Artist ID or shorthand cannot be found")

    lyrics = ""

    while not passed:
        song_choice = random.choice(songs)

        if song_choice['url'].endswith("lyrics"):
            lyrics = show_lyrics(lyrics_from_genius_by_url(song_choice['url']))
            lyric_string = ""
            for l in lyrics:
                lyric_string += l + "\n"
            if lyric_string.__len__() <= char_limit:
                return lyric_string.strip()

def make_tweet(user, content):
    api = setup_user(user)
    api.update_status(status=content)

def delete_tweet(user, tid):
    api = setup_user(user)
    api.destroy_status(tid)

def make_botgenius_tweet():
    botgenius_list = make_snippet_list_from_doc("16WNStYc5qNLGFOujF8EBywvFtIQWq56hhYwrh9PLp8c")

    with open('logs' + sep + 'botgenius.txt', 'a+') as lf:
        lf.seek(0)
        lines = (lf.read()).split("\n")
        if len(lines) >= 15:
            lines = lines[-15:]

        index = random.randint(0, len(botgenius_list) - 1)
        while lines.__contains__(index):
            index = random.randint(0, len(botgenius_list) - 1)
        lf.write(str(index)+"\n")

    make_tweet('bg_twitter', botgenius_list[index])




if __name__ == "__main__":
    # delete_tweet("kkb_twitter", "1154140506898612224")
    # make_tweet("kkb_twitter", get_lyric_snippet("Kero Kero Bonito"))
    # make_tweet("dg_twitter", get_lyric_snippet("Death Grips"))
    #make_botgenius_tweet()



    pass
