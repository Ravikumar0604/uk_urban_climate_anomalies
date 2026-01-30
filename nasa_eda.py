#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np

DATA_PATH = "../data/raw/nasa_power_daily_raw.csv"

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])

df.head()


# In[3]:


print("Cities:", df["city"].nunique(), sorted(df["city"].unique()))
print("Date range:", df["date"].min().date(), "to", df["date"].max().date())
print("Total rows:", len(df))

# rows per city
df.groupby("city").size()


# In[4]:


df.isna().mean().sort_values(ascending=False)


# In[5]:


cols = [
    "city",
    "date",
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
]

df = df[cols].copy()
df.head()


# In[6]:


df["month"] = df["date"].dt.month

monthly_stats = (
    df.groupby(["city", "month"])
      .agg(
          mean_temp=("T2M", "mean"),
          std_temp=("T2M", "std")
      )
      .reset_index()
)

monthly_stats.head()


# In[7]:


df["year"] = df["date"].dt.year

annual_mean = (
    df.groupby(["city", "year"])["T2M"]
      .mean()
      .reset_index()
)

annual_mean.head()


# In[8]:


# monthly climatology per city
climatology = (
    df.groupby(["city", "month"])["T2M"]
      .mean()
      .reset_index()
      .rename(columns={"T2M": "monthly_clim"})
)

# merge back
df = df.merge(climatology, on=["city", "month"], how="left")

# deseasonalised temperature
df["T2M_deseasonal"] = df["T2M"] - df["monthly_clim"]

df[["city", "date", "T2M", "monthly_clim", "T2M_deseasonal"]].head()


# In[9]:


df = df.sort_values(["city", "date"])

for window in [7, 30]:
    df[f"roll_mean_{window}"] = (
        df.groupby("city")["T2M_deseasonal"]
          .transform(lambda x: x.rolling(window, center=True).mean())
    )

    df[f"roll_std_{window}"] = (
        df.groupby("city")["T2M_deseasonal"]
          .transform(lambda x: x.rolling(window, center=True).std())
    )

df.head()


# In[10]:


df.groupby("city")[["T2M_deseasonal"]].agg(["mean", "std", "min", "max"])

