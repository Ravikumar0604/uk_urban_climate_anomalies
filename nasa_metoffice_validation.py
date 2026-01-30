#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
import numpy as np

NASA_PATH = "../data/raw/nasa_power_daily_raw.csv"
MET_PATH = "../data/raw/met_office/met_office_london_temp_daily_2016_2022.csv"

print("NASA exists:", NASA_PATH)
print("MET exists:", MET_PATH)



# In[6]:


nasa = pd.read_csv(NASA_PATH)
met = pd.read_csv(MET_PATH)

# parse dates
nasa["date"] = pd.to_datetime(nasa["date"])
met["date"] = pd.to_datetime(met["date"])

# keep London only
nasa_london = nasa[nasa["city"] == "London"].copy()

print("NASA London rows:", len(nasa_london))
print("Met rows:", len(met))
print("Met stations:", met["station"].nunique(), sorted(met["station"].unique()))

nasa_london.head()


# In[7]:


# Keep only what we need
nasa_london = nasa_london[["date", "T2M_MAX", "T2M_MIN"]].copy()
met = met[["station", "date", "tmax_c", "tmin_c"]].copy()

# Rename to common names
nasa_london.rename(columns={"T2M_MAX": "tmax_nasa", "T2M_MIN": "tmin_nasa"}, inplace=True)
met.rename(columns={"tmax_c": "tmax_met", "tmin_c": "tmin_met"}, inplace=True)

nasa_london.head(), met.head()


# In[8]:


joined = met.merge(nasa_london, on="date", how="inner")

print("Joined rows:", len(joined))
print("Stations:", joined["station"].nunique(), sorted(joined["station"].unique()))
print("Date range:", joined["date"].min().date(), "to", joined["date"].max().date())

joined.head()


# In[9]:


def mean_bias(pred, obs):
    # pred - obs
    return float(np.mean(pred - obs))

def rmse(pred, obs):
    return float(np.sqrt(np.mean((pred - obs) ** 2)))

def corr(pred, obs):
    return float(np.corrcoef(pred, obs)[0, 1])


# In[10]:


rows = []

for station, g in joined.groupby("station"):
    g = g.dropna()

    rows.append({
        "scope": station,
        "n_days": len(g),
        "bias_tmax": mean_bias(g["tmax_nasa"], g["tmax_met"]),
        "rmse_tmax": rmse(g["tmax_nasa"], g["tmax_met"]),
        "corr_tmax": corr(g["tmax_nasa"], g["tmax_met"]),
        "bias_tmin": mean_bias(g["tmin_nasa"], g["tmin_met"]),
        "rmse_tmin": rmse(g["tmin_nasa"], g["tmin_met"]),
        "corr_tmin": corr(g["tmin_nasa"], g["tmin_met"]),
    })

# overall (all stations pooled)
g = joined.dropna()
rows.append({
    "scope": "overall_pooled",
    "n_days": len(g),
    "bias_tmax": mean_bias(g["tmax_nasa"], g["tmax_met"]),
    "rmse_tmax": rmse(g["tmax_nasa"], g["tmax_met"]),
    "corr_tmax": corr(g["tmax_nasa"], g["tmax_met"]),
    "bias_tmin": mean_bias(g["tmin_nasa"], g["tmin_met"]),
    "rmse_tmin": rmse(g["tmin_nasa"], g["tmin_met"]),
    "corr_tmin": corr(g["tmin_nasa"], g["tmin_met"]),
})

metrics = pd.DataFrame(rows).sort_values("scope")
metrics


# In[11]:


joined["tmax_error"] = joined["tmax_nasa"] - joined["tmax_met"]
joined["tmin_error"] = joined["tmin_nasa"] - joined["tmin_met"]

summary = joined.groupby("station")[["tmax_error", "tmin_error"]].agg(["mean", "std", "median"])
summary


# In[12]:


out_metrics = "../data/raw/met_office/nasa_metoffice_validation_metrics.csv"
metrics.to_csv(out_metrics, index=False)
print("Saved:", out_metrics)

