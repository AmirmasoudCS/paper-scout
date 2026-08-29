# Research Report: LSTM in predicting the trading stocks

*Generated 2026-08-29 14:58 UTC · 10 papers*

## Table of Contents

- [Cross-Paper Synthesis](#cross-paper-synthesis)
- [Future Work Ideas](#future-work-ideas)
- [Future Work Ideas (Inferred)](#future-work-ideas-inferred)
- [Papers](#papers)
  - [1. Predicting Stock Market Time-Series Data using CNN-LSTM Neural Network
  Model](#1-predicting-stock-market-time-series-data-using-cnn-lstm-neural-network-model)
  - [2. Stock Portfolio Optimization Using a Deep Learning LSTM Model](#2-stock-portfolio-optimization-using-a-deep-learning-lstm-model)
  - [3. Forecasting directional movements of stock prices for intraday trading using LSTM and random forests](#3-forecasting-directional-movements-of-stock-prices-for-intraday-trading-using-lstm-and-random-forests)
  - [4. The Interpretability of LSTM Models for Predicting Oil Company Stocks: Impact of Correlated Features](#4-the-interpretability-of-lstm-models-for-predicting-oil-company-stocks-impact-of-correlated-features)
  - [5. Robust Portfolio Design and Stock Price Prediction Using an Optimized LSTM Model](#5-robust-portfolio-design-and-stock-price-prediction-using-an-optimized-lstm-model)
  - [6. Precise Stock Price Prediction for Optimized Portfolio Design Using an
  LSTM Model](#6-precise-stock-price-prediction-for-optimized-portfolio-design-using-an-lstm-model)
  - [7. Analysis of Sectoral Profitability of the Indian Stock Market Using an
  LSTM Regression Model](#7-analysis-of-sectoral-profitability-of-the-indian-stock-market-using-an-lstm-regression-model)
  - [8. Deep learning for Stock Market Prediction](#8-deep-learning-for-stock-market-prediction)
  - [9. A Novel Deep Reinforcement Learning Based Automated Stock Trading System Using Cascaded LSTM Networks](#9-a-novel-deep-reinforcement-learning-based-automated-stock-trading-system-using-cascaded-lstm-networks)
  - [10. Stock Price Prediction Using a Hybrid LSTM-GNN Model: Integrating
  Time-Series and Graph-Based Analysis](#10-stock-price-prediction-using-a-hybrid-lstm-gnn-model-integrating-time-series-and-graph-based-analysis)

## Cross-Paper Synthesis

The dominant approaches across these papers center on leveraging LSTM networks for stock prediction, often in conjunction with other techniques or model architectures. A significant subset of the research focuses on applying LSTMs within the context of portfolio optimization and risk management, with several studies specifically targeting the Indian stock market using historical data from 2016 to 2020 for this purpose [2], [5], and [6]. Furthermore, researchers are exploring hybrid models to enhance predictive power; for instance, combining LSTMs with CNNs [1] or integrating them with Graph Neural Networks (GNNs) to model inter-stock relationships [10]. Another advanced methodology involves embedding LSTMs within Deep Reinforcement Learning (DRL) frameworks to build automated trading systems [9].

Agreement is evident in the consistent reliance on LSTMs to capture temporal dependencies in stock data [2], [5], [6], [7], [8], and [10]. Several papers also focus on quantitative performance metrics, reporting high accuracy levels or low Mean Squared Error (MSE) values when the LSTM is applied to prediction tasks [1], [5], [6], and [10]. Specifically, the use of LSTMs for predicting portfolio returns or optimizing sector allocations is a recurring theme, showing high predictive capability in these scenarios [2], [5], and [6]. Moreover, the comparison of LSTMs against other models, such as Random Forests [3] or various tree-based ensembles [8], is a common comparative element.

Divergences appear in the scope and complexity of the modeling approach. Some papers focus narrowly on time-series prediction for single stocks or sectors [7], while others build significantly more complex systems. For example, [9] proposes a DRL system using cascaded LSTMs, which is a distinct methodological leap from the direct regression or classification approaches seen in [2] or [5]. Furthermore, there is a divergence in feature engineering; while some utilize basic price returns [3], others incorporate technical indicators [8] or model explicit correlations using GNNs [10]. A notable divergence in interpretation is found in [4], which explicitly questions the interpretability of LSTM models, suggesting that adding correlated features does not improve interpretability, contrasting with the general assumption of model improvement seen elsewhere.

Collectively, the set of papers exhibits a strong focus on *prediction* and *optimization* using LSTMs, but there are notable gaps. Firstly, while [4] addresses interpretability, no paper provides a comprehensive analysis of *why* the internal states of the LSTM models are difficult to interpret, beyond stating the difficulty. Secondly, while multiple papers use Indian market data [2], [5], and [6], the application of LSTMs to the Tehran stock exchange [8] or the US/Chinese markets [9] represents distinct geographical and market structure contexts that are not compared against the Indian market findings. Finally, the utility of the prediction in terms of actionable, post-transaction cost analysis is not universally covered; [3] provides a detailed return calculation including benchmark comparisons, whereas the high accuracy reported in several portfolio papers [2], [5], and [6] does not always translate to a direct, cost-adjusted trading strategy comparison.

## Future Work Ideas

Here are 4 concrete future-work directions derived solely from the provided "Author-stated Limitations and Future Work" text:

**1. Developing Computationally Efficient Hybrid Architectures for Real-Time Use**
*   **Gap Addressed:** The current hybrid models (like LSTM-GNN) suffer from high computational complexity and memory demands, making them impractical for real-time or high-frequency trading environments. Furthermore, the need for frequent retraining due to the expanding window approach adds significant computational load.
*   **Citation:** [10]
*   **Signal Strength:** Single paper citation.

**2. Robust Validation Strategies for Time-Series Forecasting with Expanding Windows**
*   **Gap Addressed:** The expanding window approach, while improving adaptability, complicates model validation because it lacks a dedicated, separate validation set, thereby increasing the risk of overfitting.
*   **Citation:** [10]
*   **Signal Strength:** Single paper citation.

**3. Improving Model Generalizability Beyond Historical Patterns**
*   **Gap Addressed:** The current models assume that past relationships will continue into the future. This assumption is potentially flawed during periods of unprecedented market events or significant structural economic changes, leading to reduced predictive accuracy.
*   **Citation:** [10]
*   **Signal Strength:** Single paper citation.

**4. Mitigating Data Quality Issues in Model Deployment**
*   **Gap Addressed:** The model's performance is shown to be sensitive to data imperfections, specifically mentioning the issues associated with missing values or anomalies in the input data.
*   **Citation:** [10]
*   **Signal Strength:** Single paper citation.

## Future Work Ideas (Inferred)

*The directions below are inferred by the model from each paper's problem/method/key-result summary, for papers that had no extractable Limitations/Future Work section. Unlike the section above, these are not statements the authors themselves made — treat them as speculative.*

[Inferred, not author-stated] Comparative Market Analysis: To compare the predictive performance across different geographical markets, the model trained on the Indian stock market data could be applied to the US and Chinese markets, or vice versa, to test the generalizability of the LSTM architecture. This is suggested by the multiple studies focusing on specific regional markets ([2], [5], [6]) contrasted with the models trained on US/Chinese markets ([9]).
[Inferred, not author-stated] Incorporating Transaction Costs: To provide a more realistic assessment of the profitability reported by the models, the current framework should be adapted to incorporate explicit transaction costs into the final performance evaluation, especially for intraday trading strategies. This is suggested by the focus on return calculation in [3] and the general goal of optimization in [2], [5], and [6], which do not appear to include this cost adjustment.
[Inferred, not author-stated] Interpretability of Feature Interactions: Given that several papers utilize multiple features (e.g., technical indicators, correlated assets), future work should focus on developing methods to map the contribution of specific feature *interactions* within the LSTM's internal states, moving beyond the general statement of difficulty in interpretation. This is suggested by the feature inclusion in [8] and the interpretability discussion in [4].
[Inferred, not author-stated] Multi-Horizon Forecasting Comparison: Since several papers establish high accuracy for short-term prediction (e.g., one-day forecast in [5] or 1-30 days in [8]), a systematic comparison of the model's predictive decay rate and performance degradation when extending the forecast horizon beyond the currently tested window would be beneficial. This is suggested by the fixed short-term horizons used in [5] and [8].

## Papers

### 1. Predicting Stock Market Time-Series Data using CNN-LSTM Neural Network
  Model

Aadhitya A, Rajapriya R, Vineetha R S, et al. · 2023-05-21 · *HF Papers*

[View source](https://huggingface.co/papers/2305.14378)

**Problem:** The paper addresses the difficulty of predicting stock market performance due to constantly changing prices and the lack of sufficient stocks for companies to perform well in finance.

**Method:** The authors propose a custom CNN-LSTM Neural Network model that identifies features from stock data by converting them into tensors, processes these features through a CNN, and then uses an LSTM neural network to detect patterns for prediction.

**Key result:** The model achieved high accuracy when trained on real-time stock market data, predicting up to 99% of stocks for the NIFTY dataset during testing, with MSE values ranging from 0.001 to 0.05 during training and 0.002 to 0.1 during validation.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 2. Stock Portfolio Optimization Using a Deep Learning LSTM Model

Jaydip Sen, Abhishek Dutta, Sidra Mehtab · 2021-11-08 · *HF Papers*

[View source](https://huggingface.co/papers/2111.04709)

**Problem:** The paper addresses the complex task of predicting future stock prices and movement patterns to build optimized portfolios that balance return and risk for nine different sectors of the Indian stock market.

**Method:** The study analyzes historical price time series from January 1, 2016, to December 31, 2020, designs and fine-tunes a long-and-short-term memory (LSTM) model for price prediction, and constructs optimum portfolios for each sector before evaluating them after a five-month hold-out period.

**Key result:** The LSTM model demonstrated high precision in predicting future stock prices over a short time horizon, resulting in predicted portfolio returns that were found to be high compared to actual returns.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 3. Forecasting directional movements of stock prices for intraday trading using LSTM and random forests

Pushpendu Ghosh, Ariel Neufeld, Jajati Keshari Sahoo · 2020-04-21 · *arXiv*

[View source](http://arxiv.org/abs/2004.10178v2)

**Problem:** The paper addresses the problem of forecasting out-of-sample directional movements of S&P 500 constituent stocks for intraday trading between January 1993 and December 2018.

**Method:** The authors employ random forests and CuDNNLSTM networks using a multi-feature setting that includes returns relative to closing prices, opening prices, and intraday returns. The trading strategy involves buying the 10 stocks with the highest predicted probability and shorting the 10 stocks with the lowest probability on each trading day.

**Key result:** The multi-feature setting achieved a daily return of 0.64% using LSTM networks and 0.54% using random forests prior to transaction costs, outperforming benchmark strategies that used only closing price returns which yielded 0.41% and 0.39% respectively.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 4. The Interpretability of LSTM Models for Predicting Oil Company Stocks: Impact of Correlated Features

Javad T. Firouzjaee, Pouriya Khaliliyan · 2022-01-02 · *arXiv*

[View source](http://arxiv.org/abs/2201.00350v5)

**Problem:** The study investigates the impact of correlated features on the interpretability of Long Short-Term Memory (LSTM) models used for predicting oil company stocks.

**Method:** The researchers designed a Standard LSTM network and trained it using various datasets containing correlated features, such as crude oil prices, gold prices, and the US dollar, while employing complexity analysis to support their arguments.

**Key result:** The results demonstrate that adding a feature correlated with oil stocks does not improve the interpretability of LSTM models, although these models can achieve high accuracy in predicting stock prices. The study concludes that the internal states and weight parameters of these models are difficult to interpret and do not provide clear insights into the underlying factors driving stock price movements.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 5. Robust Portfolio Design and Stock Price Prediction Using an Optimized LSTM Model

Jaydip Sen, Saikat Mondal, Gourab Nath · 2022-03-02 · *arXiv*

[View source](http://arxiv.org/abs/2204.01850v1)

**Problem:** The paper addresses the challenges of accurately predicting future stock prices and designing optimized portfolios that balance return and risk for four critical economic sectors in India.

**Method:** The authors extract historical stock prices from January 1, 2016, to December 31, 2020, and build sector-wise portfolios based on the ten most significant stocks. They design two types of portfolios (optimum risk and eigen) and develop an LSTM model with a one-day forecast horizon to predict future stock prices.

**Key result:** After a six-month hold-out period starting July 1, 2021, the study computes actual and predicted returns for the portfolios. The comparison indicates that the LSTM model achieves a high accuracy level in predicting future portfolio returns.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 6. Precise Stock Price Prediction for Optimized Portfolio Design Using an
  LSTM Model

Jaydip Sen, Sidra Mehtab, Abhishek Dutta, et al. · 2022-03-02 · *HF Papers*

[View source](https://huggingface.co/papers/2203.01326)

**Problem:** The paper addresses the difficulty of accurately predicting future stock prices and designing optimized portfolios with proper weight allocations to achieve optimized return and risk values.

**Method:** The authors extract past stock prices from January 1, 2016, to December 31, 2020, for seven sectors of the Indian economy to design optimized portfolios. They also design an LSTM regression model to predict future stock prices, evaluating accuracy by comparing predicted and actual returns after a five-month holdout period starting June 1, 2021.

**Key result:** The study presents seven optimized portfolios based on critical sectors of India. The LSTM model is found to be highly accurate in predicting stock prices over a short horizon, with predicted and actual returns indicating very high accuracy.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 7. Analysis of Sectoral Profitability of the Indian Stock Market Using an
  LSTM Regression Model

Jaydip Sen, Saikat Mondal, Sidra Mehtab · 2021-11-09 · *HF Papers*

[View source](https://huggingface.co/papers/2111.04976)

**Problem:** The paper addresses the challenge of accurately predicting future stock prices for volatile and stochastic markets to inform buy and sell transactions.

**Method:** An optimized Long-and-Short-Term Memory (LSTM) regression model is used, with layers designed suitably and regularized using dropout. Historical data for 70 stocks across seven sectors from the Indian National Stock Exchange (NSE) was automatically extracted from Jan 1, 2010 to Aug 26, 2021 to train the model.

**Key result:** The model demonstrated high accuracy in predicting future stock prices using Huber loss, mean absolute error, and accuracy score metrics. Sector profitability analysis revealed that the pharma sector was the most profitable, while the media sector was the least profitable over the study period.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 8. Deep learning for Stock Market Prediction

Mojtaba Nabipour, Pooyan Nayyeri, Hamed Jabani, et al. · 2020-03-31 · *HF Papers*

[View source](https://huggingface.co/papers/2004.01497)

**Problem:** The paper addresses the challenge of predicting future values for four specific stock market groups (diversified financials, petroleum, non-metallic minerals, and basic metals) from the Tehran stock exchange to help investors detect accurate profits and reduce potential risks.

**Method:** The study employs a regression approach using ten technical indicators as inputs, evaluating both tree-based ensemble models (Decision Tree, Bagging, Random Forest, Adaboost, Gradient Boosting, XGBoost) and deep learning algorithms (ANN, RNN, LSTM) with exponentially smoothed features for predictions made 1 to 30 days in advance.

**Key result:** Among all tested algorithms, the Long Short-Term Memory (LSTM) model demonstrated the most accurate results and highest model fitting ability, while tree-based models showed intense competition between Adaboost, Gradient Boosting, and XGBoost.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 9. A Novel Deep Reinforcement Learning Based Automated Stock Trading System Using Cascaded LSTM Networks

Jie Zou, Jiashu Lou, Baohua Wang, et al. · 2022-12-06 · *arXiv*

[View source](http://arxiv.org/abs/2212.02721v2)

**Problem:** Deep reinforcement learning (DRL) methods originally used in gaming are not directly adaptable to financial data with low signal-to-noise ratios and unevenness, leading to performance shortcomings in automated stock trading systems.

**Method:** The authors propose a DRL-based stock trading system using cascaded LSTM networks that first extract time-series features from stock daily data using an LSTM, feed these features to the agent for training, and use another LSTM within the strategy functions for reinforcement learning training.

**Key result:** Experiments in the US (DJI) and Chinese (SSE50) markets show that the proposed model outperforms baseline models in cumulative returns and Sharpe ratio, with advantages being more significant in the Chinese market. The model demonstrates stronger profit-taking ability but is exposed to higher pullback risk while achieving high returns.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 10. Stock Price Prediction Using a Hybrid LSTM-GNN Model: Integrating
  Time-Series and Graph-Based Analysis

Meet Satishbhai Sonani, Atta Badii, Armin Moin · 2025-02-19 · *HF Papers*

[View source](https://huggingface.co/papers/2502.15813)

**Problem:** The paper addresses the challenge of enhancing stock market prediction accuracy by integrating temporal patterns and inter-stock relational data.

**Method:** The authors propose a hybrid model combining Long Short-Term Memory (LSTM) networks to capture time-series dynamics with Graph Neural Networks (GNNs) that leverage Pearson correlation and association analysis to model nonlinear polyadic dependencies between stocks. The model is trained using an expanding window validation approach to enable continuous learning and adaptation to evolving market conditions.

**Key result:** Extensive experiments show the hybrid LSTM-GNN model achieves a mean square error (MSE) of 0.00144, representing a 10.6% reduction compared to the standalone LSTM model's MSE of 0.00161. The hybrid model also outperforms traditional and advanced benchmarks including linear regression, CNNs, dense networks, and standalone LSTMs.

**Stated limitations:** The hybrid model has increased computational complexity requiring significant processing power and memory, and the expanding window approach complicates validation by lacking a separate validation set. Performance is sensitive to hyperparameter tuning, data limitations like missing values can degrade effectiveness, assuming past relationships persist may fail during unprecedented market events, and frequent retraining increases computational load which limits applicability in real-time or high-frequency trading environments.
