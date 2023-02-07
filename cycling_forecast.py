import argparse
import numpy as np
import time
from datetime import datetime

import os
import os.path
import pickle as pkl
import sys
import json

from cycling_forecast import weather_metrics
from cycling_forecast import email_generator
from cycling_forecast import constants

import pathlib
this_directory = pathlib.Path(__file__).parent


# ===PARSE AND PROCESSS WEATHER DATA METRICS ========================================================
def process(data):
    now = datetime.now()
    morning_data, evening_data = [], []
    for hour_forecast in json.loads(data.text)['hourly']:
        dt = datetime.fromtimestamp(hour_forecast['dt'])

        # set the afternoon hours here
        if dt.hour in [16, 17] and dt.day == now.day:
            evening_data.append(weather_metrics.extract_from_forecast(hour_forecast))

        # set the morning hours here
        if dt.hour in [7, 8] and dt.day == now.day:
            morning_data.append(weather_metrics.extract_from_forecast(hour_forecast))

    if evening_data:
        evening_data = np.mean(np.array(evening_data), 0)
    else:
        evening_data = [-1, -1, -1, -1]

    if morning_data:
        morning_data = np.mean(np.array(morning_data), 0)
    else:
        morning_data = [-1, -1, -1, -1]

    evening_dict = {'temp':evening_data[0],
                    "wind":evening_data[1],
                    "pop":evening_data[2],
                    "rain":evening_data[3],
                    "score": weather_metrics.heuristic(*evening_data)}
    morning_dict = {'temp': morning_data[0],
                    "wind": morning_data[1],
                    "pop": morning_data[2],
                    "rain": morning_data[3],
                    "score": weather_metrics.heuristic(*morning_data)}

    score = (evening_dict['score'] + morning_dict['score'])/2
    date = now.strftime("%A, %B %d, %Y")

    return date, morning_dict, evening_dict, score


# ====================================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper parse")
    parser.add_argument('--now', dest='now', default=False, action='store_true')
    parser.add_argument('--plot_metrics', dest='plot_metrics', default=False, action='store_true')
    parser.add_argument('-k', '--api_key')
    parser.add_argument('-e', '--email')
    args = parser.parse_args()

    if args.plot_metrics:
        print("Plotting weather metrics...")
        weather_metrics.plot_metrics()
        sys.exit(0)

    while True:
        # check the most recent forecast timestamp
        if os.path.exists(this_directory / '.last_sent'):
            with open(this_directory / '.last_sent', 'rb') as f:
                last_sent = pkl.load(f)
            last_day, last_hour = last_sent.day, last_sent.hour
        else:
            last_day, last_hour = -1, -1
        retries = 0

        # do we want one now, or is it time to generate a new one?
        if args.now or \
            (last_day != datetime.now().day
             and datetime.now().hour == constants.SEND_TIME
             or not os.path.exists(this_directory / '.last_sent')):

            data = weather_metrics.get_weather(args.api_key, constants.LATITUDE, constants.LONGITUDE)
            date, morning_dict, evening_dict, score = process(data)
            from_email = args.email if not constants.FORECASTER_EMAIL_ADDRESS else constants.FORECASTER_EMAIL_ADDRESS
            email_generator.email_forecast(
                date,
                morning_dict,
                evening_dict,
                score,
                from_email,
                args.email,
                this_directory)

            with open(this_directory / '.last_sent', 'wb') as f:
                pkl.dump(datetime.now(), f)

            # if we just wanted one forecast, break
            if args.now:
                print(f"Forecast sent to {args.email}")
                break

        # if not time to generate, wait 10 minutes and check again
        if not args.now:
            time.sleep(600)
        else:
            break