import base64
import os
import pickle as pkl

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from email.utils import formataddr

from cycling_forecast.constants import WEATHER_BLURBS, FORECASTER_EMOJI


# === login via OAUTH2 to GMAIL CLIENT =============================================================
def find_credentials_file(directory):
    return [f for f in os.listdir(directory) if "client_secret" in f and "json" in f][0]


def get_gmail_creds(directory):
    creds = None
    if os.path.exists(directory / '.gmail_token.pkl'):
        with open(directory / '.gmail_token.pkl', 'rb') as token:
            creds = pkl.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            cred_file = find_credentials_file(directory)
            SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
            flow = InstalledAppFlow.from_client_secrets_file(directory / cred_file, SCOPES)
            flow_creds = flow.run_local_server(port=0)
            creds = flow.credentials

        with open(directory / '.gmail_token.pkl', 'wb') as token:
            pkl.dump(creds, token)
    return creds


# === create email HTML ============================================================================
def generate_email(date, morning_data, evening_data, score):
    return f"""
    <h1 id="today-s-weather-forecast">Today&#39;s Cycling Forecast</h1>
    <p>🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲</p>
    <p>{date}</p>
    <table>
    <thead>
    <tr>
    <th style="text-align:right">Time</th>
    <th style="text-align:center">Temp</th>
    <th style="text-align:center">Wind</th>
    <th style="text-align:center">Precipitation</th>
    <th style="text-align:center">% of P</th>
    <th style="text-align:center">Score</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td style="text-align:right">Morning</td>
    <td style="text-align:center">{morning_data['temp']:.0f} °F</td>
    <td style="text-align:center">{morning_data['wind']:.0f} mph</td>
    <td style="text-align:center">{morning_data['rain']:.1f} mm/h</td>
    <td style="text-align:center">{int(morning_data['pop']*100)}%</td>
    <td style="text-align:center">{int(morning_data['score']*100)}%</td>
    </tr>
    <tr>
        <td style="text-align:right">Evening</td>
    <td style="text-align:center">{evening_data['temp']:.0f} °F</td>
    <td style="text-align:center">{evening_data['wind']:.0f} mph</td>
    <td style="text-align:center">{evening_data['rain']:.1f} mm/h</td>
    <td style="text-align:center">{int(evening_data['pop']*100)}%</td>
    <td style="text-align:center">{int(evening_data['score']*100)}%</td>
    </tr>
    </tbody>
    </table>
    <p><strong>Total Score: {int(score*100)}%</strong></p>
    <p>The Forecaster says <em>&quot;{WEATHER_BLURBS[(score*100)//10*10]}&quot;</em> {FORECASTER_EMOJI}</p>
    <p>🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲🚲</p>
    """

# === login, build email, and send =================================================================
def email_forecast(date, morning_data, evening_data, score, from_email, to_email, directory):
    creds = get_gmail_creds(directory)
    service = build('gmail', 'v1', credentials=creds)
    msg = MIMEMultipart()
    msg.attach(MIMEText(generate_email(date, morning_data, evening_data, score), 'html'))

    msg['Subject'] = f"Cycling Forecast: {int(score*100)}%"
    msg['From'] = formataddr((str(Header('Cycling Forecaster', 'utf-8')), from_email))
    msg['To'] = to_email

    encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    send_message = (service.users().messages().send(userId="me", body=create_message).execute())
