#!/usr/bin/env python
# coding: utf-8

# London-area stations:
# - Heathrow
# - Kew Gardens
# - Northolt
# 
# The data is used only for validation and bias checking against NASA POWER.
# 

# In[1]:


import os
import glob
import pandas as pd

BASE_DIR = os.path.join("..", "data", "raw", "met_office")
print("Base dir:", BASE_DIR)


# In[2]:


def read_badc_csv(file_path: str) -> pd.DataFrame:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if line.strip().lower() == "data":
                skiprows = i + 1
                break
        else:
            raise ValueError(f"No 'data' section found in {file_path}")

    return pd.read_csv(file_path, skiprows=skiprows)


# In[3]:


pattern = os.path.join(BASE_DIR, "*", "*.csv")
files = sorted(glob.glob(pattern))

print("Total CSV files found:", len(files))
for f in files[:6]:
    print(" -", f)


# In[4]:


frames = []

for fp in files:
    station = os.path.basename(os.path.dirname(fp))
    year = int(os.path.splitext(os.path.basename(fp))[0])

    df = read_badc_csv(fp)
    df.insert(0, "station", station)
    df.insert(1, "year", year)

    frames.append(df)

met = pd.concat(frames, ignore_index=True)

print("Rows:", len(met))
print("Stations:", met["station"].nunique(), sorted(met["station"].unique()))
met.head()


# In[5]:


met["ob_end_time"] = pd.to_datetime(met["ob_end_time"], errors="coerce")

keep_cols = [
    "station",
    "ob_end_time",
    "max_air_temp",
    "min_air_temp",
]

met = met[keep_cols].copy()

# Filter strictly to 2016–2022
met = met[
    (met["ob_end_time"] >= "2016-01-01") &
    (met["ob_end_time"] <= "2022-12-31 23:59:59")
]

met["max_air_temp"] = pd.to_numeric(met["max_air_temp"], errors="coerce")
met["min_air_temp"] = pd.to_numeric(met["min_air_temp"], errors="coerce")

met.head()


# In[6]:


met["date"] = met["ob_end_time"].dt.date

met_daily = (
    met.groupby(["station", "date"], as_index=False)
       .agg(
           tmax_c=("max_air_temp", "max"),
           tmin_c=("min_air_temp", "min"),
       )
)

print("Daily rows:", len(met_daily))
print("Stations:", met_daily["station"].nunique(), sorted(met_daily["station"].unique()))
print("Min date:", met_daily["date"].min())
print("Max date:", met_daily["date"].max())

met_daily.head()


# In[7]:


out_path = os.path.join(
    "..", "data", "raw", "met_office",
    "met_office_london_temp_daily_2016_2022.csv"
)

met_daily.to_csv(out_path, index=False)
print("Saved:", out_path)

