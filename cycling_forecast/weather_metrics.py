import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skewnorm
import requests

from cycling_forecast.constants import *

plt.style.use('https://raw.githubusercontent.com/RobGeada/stylelibs/main/material_white.mplstyle')

# === WEATHER API PARSING ==========================================================================
# grab weather at specified coordinates
def get_weather(api_key, lat, long):
    return requests.get(
        f"https://api.openweathermap.org/data/3.0/onecall?lat="
        f"{lat}"
        f"&lon="
        f"{long}"
        f"&exclude=minutely,alerts,current,daily&appid={api_key}&units=imperial")


def extract_from_forecast(forecast):
    t = forecast['feels_like']
    w = forecast['wind_speed']
    p = forecast['pop']
    r = forecast.get("rain",{"1h":0})["1h"]
    return t,w,p,r


# === WEATHER METRICS ==============================================================================
# precip metric:
# 100% suitable: 0% of 0mm/hr of rain
# 0% suitable at MAXIMUM_EXPECTED_RAIN
def precip_score(rain_probability, rain_volume):
    expected_rain = rain_volume * rain_probability
    return np.maximum(0, (MAXIMUM_EXPECTED_RAIN - expected_rain))/MAXIMUM_EXPECTED_RAIN


# wind metric:
# 100% suitable: 0 mph
# 0% suitable at MAXIMUM_WINDSPEED
def wind_score(windspeed):
    return np.maximum(0, (MAXIMUM_WINDSPEED - windspeed))/MAXIMUM_WINDSPEED


# temp metric:
# skewed normal distribution centered at OPTIMAL_TEMPERATURE
def skew_func(temp):
    skew = OPTIMAL_TEMPERATURE_SKEW
    scale = 25
    return skewnorm.pdf(temp, a=skew, loc=OPTIMAL_TEMPERATURE-scale/skew, scale=scale)


def temp_score(temp):
    distribution_range = np.linspace(-10, 45, 100)
    domain = skew_func(distribution_range)
    norm = 1/max(domain)
    offset = OPTIMAL_TEMPERATURE - distribution_range[np.argmax(domain)]
    distribution = skew_func(temp - offset) * norm
    return np.minimum(1,  distribution)


# plot the metrics to see if they align with your views of "suitability"
def plot_metrics():
    plt.subplot(3,1, 1)
    xs = np.linspace(0, MAXIMUM_EXPECTED_RAIN, 10)
    plt.plot(xs, precip_score(1, xs), color="b", label="Suitability")
    plt.xlabel("Rain Probability * Rain Volume (mm)")
    plt.axvline(MAXIMUM_EXPECTED_RAIN, color="r", label="Maximum Expected Rain")
    plt.ylabel("Suitability")
    plt.legend()

    plt.subplot(3,1, 2)
    xs = np.linspace(0, MAXIMUM_WINDSPEED, 10)
    plt.plot(xs, wind_score(xs), color="b", label="Suitability")
    plt.xlabel("Wind Speed (mph)")
    plt.axvline(MAXIMUM_WINDSPEED, color="r", label="Maximum Windspeed")
    plt.ylabel("Suitability")
    plt.legend()

    plt.subplot(3,1, 3)
    xs = np.linspace(-10, 45, 1000)
    plt.plot(xs, temp_score(xs), color="b", label="Suitability")
    plt.xlabel("Temperature (C)")
    plt.axvline(OPTIMAL_TEMPERATURE, color="r", label="Optimal Temperature")
    plt.ylabel("Suitability")
    plt.legend()

    plt.tight_layout()
    plt.savefig("plots/weather_metrics.png")
    plt.show()


# given weather data, compute all the weather metrics and multiply them
def heuristic(temp, windspeed, precip_prob, precip_volume):
    return np.prod([
        wind_score(windspeed),
        temp_score(temp),
        precip_score(precip_prob, precip_volume)
    ])
