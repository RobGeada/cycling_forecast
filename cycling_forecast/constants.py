# specify your forecast constants in here

# === WEATHER ======================================================================================
MAXIMUM_EXPECTED_RAIN = 10
MAXIMUM_WINDSPEED = 30
OPTIMAL_TEMPERATURE = 20

# 0 skew is symmetric around opt temp
# positive skew makes warmer-than-optimal temps more suitable than proportionally colder temps
# (i.e., if optimal is 20C, a positive skew makes 25C more suitable than 15C)
# negative skew makes coloer-than-optimal temps more suitable than proportionally warmer temps
# 3 seems like a good default for this parameter
OPTIMAL_TEMPERATURE_SKEW = 3


# === FORECASTING ==================================================================================
# what hour should the forecast run?
SEND_TIME = 6

# the specified hours will be aggregated together for the morning and afternoon forecasts
MORNING_HOURS = [8, 9]
AFTERNOON_HOURS = [16, 17]

# the forecast is taken at the specified coordinates (the default is the center of the Town Moor)
LATITUDE = 54.990176
LONGITUDE = -1.6296674

# if you want to send your forecast from a different email address than the recipient address,
# specify it here. THIS ADDRESS MUST CORRELATE WITH YOUR GOOGLE OAUTH CREDENTIALS
FORECASTER_EMAIL_ADDRESS = None

# === SUITABILITY FLAVOR TEXT ======================================================================
# custom messages for different suitability scores
WEATHER_BLURBS = {
    90: "you gotta cycle bro come on it's perfect",
    80: "what a great day for a bike ride",
    70: "go for a ride!",
    60: "it's p decent out you should go",
    50: "could be fine, maybe?",
    40: "could be worse?",
    30: "probably not gonna be fun",
    20: "unpleasant",
    10: "it'd suck my dude",
    0: "nah"
}

# what's the forecaster look like?
FORECASTER_EMOJI = "🤖"
