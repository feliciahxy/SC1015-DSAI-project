# Team 10 – Final Project
- Heng Xin Yu Felicia (U2321432B)
- Sun SiTong (U2322401J)
- Tan Hsuen Yin Andria (U2320699F)

## Problem Definition 
Our team identified a common and relevant challenge in Singapore’s real estate scene: How can we accurately predict private residential property prices?

Instead of using public housing data (which is tightly regulated), we focused on private property prices, which are largely influenced by market forces. We explored how location, remaining lease duration, floor area, transaction timing, and other factors affect prices — and how we can use machine learning to model and predict these outcomes.

## Data Preparation & Cleaning 
We merged private property transaction data from URA between 2020–2025 and supplemented it with:

- Geolocation Data: Used OneMap API to map coordinates for each property and obtain the coorodinates of the nearest MRT stations.

- Distance to MRT: Calculated the distance using the coordinates of the property and the nearest MRT stations. 

Feature Engineering:

- Extracted lease start year, lease duration, and remaining lease.

- Standardized pricing using unit Price instead of total transaction price as there may be multiple units transacted in 1 transaction.

- Removed redundant or sparse columns such as Area (SQM), Unit Price ($PSM) and Nett Price ($).

- Converted temporal features to date-time format and binned lease durations for modeling.

## Exploratory Data Analysis & Visualization 
We visualized various relationships to better understand our data:

Univariate: KDE plots and boxplots of price distributions.

Bivariate:

- Scatterplot and regression line of Area vs Price (strong positive correlation)

- Scatterplot and regression line of Distance to MRT vs Price (weak, slightly negative)

- Box plot of Remaining Lease vs Price (stronger impact on landed homes)

- Box plot of Postal District vs Price (location matters!)

Temporal Trends:

- Used Plotly for interactive visualizations of trends over time.

- Tracked pricing dynamics across property types and sale types from 2020 to 2025.

Location:
- Use the latitude and longitude to map out all data points (prices, location) on a Singapore map using plotly and clustering

- Explored price trends (e.g % price increases) for each location cluster

## Machine Learning Models 
We built and tested 3 ML models to predict housing prices:

### XGBoost 
Distributed gradient-boosted decision tree for efficient handling of complex, non-linear relationships.

Most important features determined: Area (SQFT), Type of Sale, Postal District.

### Random Forest

Combine multiple decision trees to produce final output that is more accurate compared to single decision tree. 

Most important features determined: Area (SQFT), Remaining lease years, Postal District.

### Artificial Neural Network (ANN)

Capture complex interactions with high accuracy by adjusting weights of connections and activation functions in layers of neurons to minimize prediction errors. 

### Evaluation Metrics:

MAE, MSE, R² Score — ANN consistently had the lowest error and best fit.

## Insights & Recommendations 
- **Random forest** is the most efficient and appropriate model for predicting housing prices. 
- Area (SQFT) is by far the most influential feature, followed by remaining lease duration and location. 

### Model Utility:

Such predicition ML algorithm can be embedded in platforms like PropertyGuru to provide live estimates. This helps buyers, sellers, and agents make informed, data-driven decisions when it comes to private property. 

## Presentation Quality 
We delivered a structured and visual-heavy presentation, covering:

- Motivation and methodology

- Deep-dive into EDA and modeling

- Clear comparison of ML models (XGBoost, Random Forest, ANN)

- Market implications and real-world applications

## Learning & Going Beyond the Course 
We pushed beyond the syllabus by:

- Applying clustering to identify price trends by region.

- Using advanced visualizations with Plotly and seaborn.

- Experimenting with ANN, XGBoost and random forest ML models.
