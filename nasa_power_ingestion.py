#!/usr/bin/env python
# coding: utf-8

# In[11]:


cities = {
    "London": {
        "latitude": 51.5074,
        "longitude": -0.1278
    },
    "Birmingham": {
        "latitude": 52.4862,
        "longitude": -1.8904
    },
    "Manchester": {
        "latitude": 53.4808,
        "longitude": -2.2426
    },
    "Leeds": {
        "latitude": 53.8008,
        "longitude": -1.5491
    },
    "Bristol": {
        "latitude": 51.4545,
        "longitude": -2.5879
    }
}

cities



# In[12]:


print("Total cities:", len(cities))


# In[2]:


import os
import time
import requests
import pandas as pd


# In[4]:


START_DATE = "2016-01-01"
END_DATE = "2022-12-31"

# NASA POWER daily point endpoint
BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

# Variables (tight set; we can expand later if needed)
PARAMETERS = [
    "T2M",         # Temperature at 2m (°C)
    "T2M_MAX",     # Max temp at 2m (°C)
    "T2M_MIN",     # Min temp at 2m (°C)
    "PRECTOTCORR", # Precipitation corrected (mm/day)
    "RH2M",        # Relative humidity at 2m (%)
    "WS2M"         # Wind speed at 2m (m/s)
]

# Output
OUT_DIR = os.path.join("..", "data", "raw")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "nasa_power_daily_raw.csv")

print("Date range:", START_DATE, "to", END_DATE)
print("save to:", OUT_CSV)
print("Parameters:", PARAMETERS)


# In[5]:


cities = {
    "London": {"latitude": 51.5074, "longitude": -0.1278},
    "Birmingham": {"latitude": 52.4862, "longitude": -1.8904},
    "Manchester": {"latitude": 53.4808, "longitude": -2.2426},
    "Leeds": {"latitude": 53.8008, "longitude": -1.5491},
    "Bristol": {"latitude": 51.4545, "longitude": -2.5879},
}

assert len(cities) == 5
cities


# In[6]:


def fetch_nasa_power_daily(lat: float, lon: float, start: str, end: str, params: list[str]) -> pd.DataFrame:
    
    start_yyyymmdd = start.replace("-", "")
    end_yyyymmdd = end.replace("-", "")

    query = {
        "parameters": ",".join(params),
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": start_yyyymmdd,
        "end": end_yyyymmdd,
        "format": "JSON"
    }

    r = requests.get(BASE_URL, params=query, timeout=60)
    r.raise_for_status()
    payload = r.json()

    # Data is keyed by parameter -> date -> value
    param_block = payload["properties"]["parameter"]

    # Build a row per date
    dates = sorted(next(iter(param_block.values())).keys())

    rows = []
    for d in dates:
        row = {"date": d}
        for p in params:
            row[p] = param_block[p].get(d)
        rows.append(row)

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    return df


# In[7]:


all_frames = []

for city, meta in cities.items():
    print(f"Downloading: {city}")

    df_city = fetch_nasa_power_daily(
        lat=meta["latitude"],
        lon=meta["longitude"],
        start=START_DATE,
        end=END_DATE,
        params=PARAMETERS
    )

    # Add city + coordinates for traceability
    df_city.insert(0, "city", city)
    df_city.insert(1, "latitude", meta["latitude"])
    df_city.insert(2, "longitude", meta["longitude"])

    all_frames.append(df_city)

    
    time.sleep(1)

df_all = pd.concat(all_frames, ignore_index=True)

print("Rows:", len(df_all))
print("Cities:", df_all["city"].nunique())
df_all.head()


# In[8]:


df_all.to_csv(OUT_CSV, index=False)
print("Saved:", OUT_CSV)

check = pd.read_csv(OUT_CSV)
print("Saved rows:", len(check))
print("Saved cities:", check["city"].nunique())
print("Min date:", check["date"].min())
print("Max date:", check["date"].max())

check.head()


# In[13]:


import pandas as pd

df = pd.read_csv("../data/raw/nasa_power_daily_raw.csv")
df["date"] = pd.to_datetime(df["date"])

print("rows:", len(df))
print("cities:", df["city"].nunique(), sorted(df["city"].unique()))
print("min_date:", df["date"].min().date())
print("max_date:", df["date"].max().date())


# In[14]:


expected = {"London", "Birmingham", "Manchester", "Leeds", "Bristol"}
found = set(df["city"].unique())

missing = expected - found
extra = found - expected

assert not missing, f"Missing cities: {missing}"
assert not extra, f"Unexpected cities: {extra}"
print("City set", found)


# In[15]:


expected_days = pd.date_range("2016-01-01", "2022-12-31", freq="D")

coverage = (
    df.groupby("city")["date"]
      .apply(lambda s: (len(set(expected_days) - set(s)), len(set(s) - set(expected_days))))
      .to_frame("missing_days__extra_days")
)

coverage


# In[16]:


cols = ["T2M","T2M_MAX","T2M_MIN","PRECTOTCORR","RH2M","WS2M"]
missing_report = df[cols].isna().sum().to_frame("missing_count")
missing_report["missing_pct"] = (missing_report["missing_count"] / len(df)) * 100
missing_report

