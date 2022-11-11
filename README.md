## financial_market_prediction_project
#Introduction
This is a group Project from Neural Network.
Financial market prediction models often fall short due to the volatile and chaotic nature of markets; the volatility creates unwanted noise when pricing many instruments, leading to over-fitting and poor model performance. Pricing data in short-term timeframes is susceptible to random fluctuations, this randomness increases with a lower amount of liquidity in the markets. However, in long-term timeframes, many financial instruments are found to form linear or exponential patterns. 
 
To capitalize on this, only highly liquid financial instruments are chosen, along with a combination of short and long term timeframes to give the model context of current market trends. To combat noise and volatility, a regression based smoothing technique is applied to market data by calculating the slope of a window of market data. The neural network is less susceptible to noise after smoothing the pricing data, allowing for a more accurate prediction of the trend. 

# Our method
We used Long Short Term Memory network for our model. Our input data were normallized using min-maxscaling.  we used linear regression to calculate our slope. We evaluated our model with mean squared and root mean squared error.

# Dataset
dataset:Our data set is 800,000 1 minute candles (1m) of 3 different types of cryptocurrencies against the US dollar, specifically XMRUSDT, BTCUSDT, ETHUSDT.
