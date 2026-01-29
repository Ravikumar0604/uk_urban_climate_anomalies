UK Urban Climate Anomaly Detection (2016–2022)
Project Overview
This project focuses on detecting climate anomalies in major UK urban environments using daily temperature data. The objective is to identify abnormal temperature behaviour in cities after removing regular seasonal patterns, enabling the analysis of unusual urban climate events.
The study uses a data-driven, unsupervised learning approach and is designed to be reproducible, scalable across cities, and suitable for time-series anomaly detection.
The project is developed using Python, Jupyter Notebooks, VS Code, and GitHub following a structured data science workflow.
Study Area
Five major UK cities are included to represent different urban environments:
London
Birmingham
Manchester
Leeds
Bristol
Time Period
Daily data from 1 January 2016 to 31 December 2022.
Data Sources
1. NASA POWER (Primary Dataset)
Provider: NASA Prediction Of Worldwide Energy Resources (POWER)
Data type: Daily gridded climate data
Spatial resolution: 0.5° × 0.5°
Variables used:
T2M – Daily mean temperature (°C)
T2M_MAX – Daily maximum temperature (°C)
T2M_MIN – Daily minimum temperature (°C)
Official website:
https://power.larc.nasa.gov/
NASA POWER is used as the primary multi-city dataset due to its consistent coverage and suitability for comparative urban analysis.
2. UK Met Office (Validation Dataset)
Provider: UK Met Office – MIDAS Open
Data type: Daily station observations
Stations used:
Heathrow
Kew Gardens
Northolt
Official access portal:
https://catalogue.ceda.ac.uk/
Met Office data is used to validate the accuracy and temporal behaviour of NASA POWER temperature data, not to replace it.
Machine Learning Models
The project will apply unsupervised anomaly detection models suitable for deseasonalised climate time-series data:
1. Isolation Forest
Detects anomalies based on data isolation
Well-suited for high-dimensional and non-Gaussian data
Efficient for large time-series datasets
2. LSTM Autoencoder
Captures temporal dependencies in sequential data
Learns normal temperature patterns and flags deviations
Suitable for detecting complex and persistent anomalies
Model selection and evaluation will focus on robustness, interpretability, and suitability for urban climate analysis.
