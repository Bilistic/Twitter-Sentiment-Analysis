import tweepy
import json
import Messenger
import re
import datetime
from textblob import TextBlob
import sys


class DataAnalysis:

    def clean(self, sentence):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", sentence).split())

    def analyze_sentiment(self, dataframe):
        dataframe["text"] = self.clean(dataframe["text"])
        analysis = TextBlob(dataframe["text"])
        dataframe["sentiment"] = str(analysis.sentiment.polarity)
        dataframe["creation_date"] = datetime.datetime.utcnow()
        return dataframe


class Listener(tweepy.streaming.StreamListener):

    def __init__(self, messenger_service=None):
        self._messenger = messenger_service
        self._data_analyzer = DataAnalysis()

    def on_data(self, data):
        data = json.loads(data)
        if "text" in data:
            data = {"text": data["text"], "length": len(data["text"]), "Likes": data["favorite_count"]}
            data = self._data_analyzer.analyze_sentiment(data)
            if self._messenger is not None:
                    self._messenger.send("", "data_stream", str(["save", data]))
            else:
                print(data)
        pass

    def on_error(self, status):
        self._messenger.close()
        print(status)

    def on_exception(self, exception):
        print(exception)
        print("This is a tweepy error that i cannot handle and happens when connection to twitter servers is broken")
        print("An open issue exists at: {}".format("https://github.com/tweepy/tweepy/issues/650"))
        return


class TwitterClient:

    def __init__(self, key, secret, ac_token, ac_secret):
        self.__consumer_key = key
        self.__consumer_secret = secret
        self.__ac_token = ac_token
        self.__ac_secret = ac_secret
        self.__twitterStream = None

    def authenticate(self):
        auth = tweepy.OAuthHandler(self.__consumer_key, self.__consumer_secret)
        auth.set_access_token(self.__ac_token, self.__ac_secret)
        return auth

    def stream(self, query, messenger=None):
        if self.__twitterStream is not None:
            self.stream_exit()
        self.__twitterStream = tweepy.Stream(self.authenticate(), Listener(messenger))
        self.__twitterStream.filter(track=[query], async=True)

    def stream_exit(self):
        self.__twitterStream.disconnect()


if __name__ == "__main__":
    host = "localhost"
    if len(sys.argv) > 1:
        host = sys.argv[1]
    print("Starting Twitter Streaming Service")
    tw = TwitterClient("OoQV6rAF5zNWluzF55KOM68gE", "F2GMwdgZUzCvYaaZGSHtcQCgZAfakFdqYxTOUCQyWJ6Wb1CaTS",
                       "2833680801-xXmzfVtjGQax2CrWBDAThgkpP9hFYXjA5OHV8kR",
                       "vY6vVzi8M5tuoQQD7pAehRB4if1NGvZSOTgCO4iJb1VCF")
    msg = Messenger.Messenger("Twitter Client", host=host)
    tw.stream("war", msg)
    _pass = None
    while not _pass:
        input("Press any key to exit: ")
        _pass = "-"
    msg.close()
    tw.stream_exit()
