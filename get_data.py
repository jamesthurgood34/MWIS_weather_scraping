import json
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://mwis.org.uk/forecasts/scottish/"
regions = [
    "the-northwest-highlands"
    , "west-highlands"
    , "cairngorms-np-and-monadhliath"
    , "southeastern-highlands"
]
forecast_headers = [f"Forecast{i}" for i in range(3)]
todays_date = datetime.today().strftime('%Y-%m-%d')
output_dir = "output/"
todays_output_dir = f"{output_dir}{todays_date}/"


def create_dir_if_not_exists(d):
    if not os.path.exists(d):
        os.mkdir(d)


create_dir_if_not_exists(output_dir)
create_dir_if_not_exists(todays_output_dir)

extracted_weather_info = {}
for region in regions:
    extracted_weather_info[region] = {}

    response = requests.get(base_url + region)
    soup = BeautifulSoup(response.text, "html.parser")

    for forecast_header in forecast_headers:
        extracted_weather_info[region][forecast_header] = {}

        forecast = soup.find_all("div", {"id": forecast_header})

        conditions = forecast[0].find_all("div", {"class": "row"})

        for condition in conditions:
            extracted_weather_info[region][forecast_header][condition.h4.text] = condition.p.text


output = {}
for i in range(3):
    output[f"Forecast{i}"] = {}
    for k in extracted_weather_info.keys():
        output[f"Forecast{i}"][k] = {}
        for obs, v in extracted_weather_info[k][f"Forecast{i}"].items():
            if obs.startswith("Headline"):
                output[f"Forecast{i}"][k]["Headline"] = extracted_weather_info[k][f"Forecast{i}"][obs]
            else:
                output[f"Forecast{i}"][k][obs] = extracted_weather_info[k][f"Forecast{i}"][obs]

with open(todays_output_dir + "extracted_weather_info.json", "w") as tf:
    json.dump(output, tf)

df = pd.concat([pd.DataFrame.from_records(output[f"Forecast{i}"]) for i in range(3)],
               keys=[f"Forecast{i}" for i in range(3)])

for c in df.columns:
     df[c] = df[c].str.replace("\r\n", "<br>")
     df[c] = df[c].str.replace("\n", "<br>")

df.to_html(output_dir + "WeatherLatest.html", escape=False)
