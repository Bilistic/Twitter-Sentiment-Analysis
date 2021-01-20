import os
import sys
import datetime

import TimerClient
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)
time = 1
host = "localhost"
#  Change the time value to alter the tweet accounted for min = 1
#  dont forget a running server is required


def get_tweets(time_minutes):
    client = TimerClient.TweetRPCClient("web-client", host=host)
    tweets = eval(client.call(time_minutes).decode("utf-8"))
    client.close()
    return tweets


def get_key(entry):
    return float(entry.get("sentiment"))


@app.route('/favicon.ico/')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def message():
    return "append /index/ to your url (I could of just re routed you but...)"


@app.route('/<string:page_name>/')
def render_static(page_name):
    print("{} : connected".format(page_name))
    tweets = get_tweets(time)
    tweets = sorted(tweets, key=get_key, reverse=True)
    pos = tweets[:10]
    neg = tweets[-10:]
    if len(tweets) > 0:
        score = sum([float(tweet.get("sentiment")) for tweet in tweets]) / len(tweets)  #
    else:
        score = 0.00
    return render_template('%s.html' % page_name,time=time, entries=pos, neg_entries=neg, score=score)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        host = sys.argv[1]
    app.run(host='0.0.0.0', debug=True)
