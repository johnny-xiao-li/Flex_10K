# **Predicting Annualized Volatility from Form 10-K Item 1a: Model Performance**

## **Overview**

This document presents the supplementary results for our study on predicting stock market annualized volatility. The predictions are derived from the textual content of Item 1a (Risk Factors) in corporate annual reports (Form 10-K). We evaluate the performance of four different models: **XGBoost, FinBERT, RoBERTa, and Longformer**.

## **Methodology**

To assess the predictive accuracy of each model, we employed a **time-series cross-validation** approach. The dataset was split chronologically, and predictions were generated using expanding window sizes of 3, 7, 15, 30, 60, and 90 days.

The **actual annualized volatility** ($\sigma_{\text{annual}}$) is calculated based on historical log returns using the following formula:

$$\sigma_{\text{annual}} = \sqrt{\frac{1}{n-1}\sum_{i=1}^{n} (r_i - \bar{r})^2} \times \sqrt{252} \quad (1)$$

Where:
* $\sigma_{\text{annual}}$ is the annualized volatility
* $r_i$ is the log return on day $i$
* $\bar{r}$ is the average daily return
* $n$ is the length of the observation window
* $252$ represents the typical number of trading days in U.S. financial markets, excluding weekends and holidays.

The performance of each model is quantified by the **Mean Squared Error (MSE)** between the predicted and actual annualized volatility. A lower MSE indicates better predictive accuracy. The MSE is calculated as follows:

$$\text{MSE} = \frac{1}{N} \sum_{j=1}^{N} (Y_j - \hat{Y}_j)^2$$

Where:
* $N$ is the total number of predictions
* $Y_j$ is the actual annualized volatility for prediction $j$
* $\hat{Y}_j$ is the predicted annualized volatility for prediction $j$

The values presented in the table below are the annually-averaged MSEs, calculated by taking the mean of the MSEs from the different window size experiments for each given year.

## **Results**

The table below summarizes the annually-averaged MSE for each model from 2006 to 2024.

<div align="center">

| Year | XGBoost | FinBERT | RoBERTa | Longformer |
| :--- | :------ | :------ | :------ | :--------- |
| 2006 | 0.0117 | 0.0163 | 0.0132 | 0.0131 |
| 2007 | 0.0137 | 0.0152 | 0.0154 | 0.0158 |
| 2008 | 0.0665 | 0.0756 | 0.0776 | 0.0772 |
| 2009 | 0.1953 | 0.2278 | 0.2173 | 0.2285 |
| 2010 | 0.0516 | 0.0232 | 0.0277 | 0.0185 |
| 2011 | 0.0145 | 0.0225 | 0.0245 | 0.0171 |
| 2012 | 0.0116 | 0.0250 | 0.0292 | 0.0201 |
| 2013 | 0.0096 | 0.0213 | 0.0198 | 0.0164 |
| 2014 | 0.0068 | 0.0149 | 0.0154 | 0.0114 |
| 2015 | 0.0086 | 0.0149 | 0.0163 | 0.0174 |
| 2016 | 0.0181 | 0.0215 | 0.0212 | 0.0214 |
| 2017 | 0.0123 | 0.0204 | 0.0212 | 0.0149 |
| 2018 | 0.0098 | 0.0101 | 0.0095 | 0.0090 |
| 2019 | 0.0103 | 0.0144 | 0.0136 | 0.0131 |
| 2020 | 0.3410 | 0.3151 | 0.3086 | 0.3261 |
| 2021 | 0.2045 | 0.1187 | 0.1142 | **0.0183** |
| 2022 | 0.0430 | 0.0600 | 0.0506 | 0.0547 |
| 2023 | 0.0262 | 0.0255 | 0.0188 | 0.0165 |
| 2024 | 0.0142 | 0.0185 | 0.0188 | 0.0224 |
---
</div>

![Yearly Trend: MSE][./figures/mse_yearly_trend.pdf]

## **Key Observations**

* **Overall Performance:** Generally, the models demonstrate varying degrees of predictive accuracy, with MSE values typically lower in stable market periods and significantly higher during periods of increased market volatility (e.g., 2008-2009, 2020-2021).
* **Impact of Market Volatility:** The substantially higher MSE values in 2008, 2009, and especially 2020, highlight the challenges in predicting volatility during periods of extreme market turbulence, such as the Global Financial Crisis and the COVID-19 pandemic.
* **Longformer's Outlier Performance in 2021:** A notable finding is Longformer's significantly lower MSE (0.0183) in 2021 compared to other models and its own performance in other high-volatility years. This suggests that Longformer, with its ability to process longer textual sequences, may have been uniquely effective in capturing crucial risk information relevant to the evolving market conditions of that year.
* **Comparative Model Strengths:** While XGBoost generally shows strong performance, particularly in less volatile periods, the transformer-based models (FinBERT, RoBERTa, Longformer) also exhibit competitive results, especially in adapting to changing market dynamics. FinBERT and RoBERTa often show comparable performance, while Longformer's architecture may provide an edge in specific complex scenarios.

---