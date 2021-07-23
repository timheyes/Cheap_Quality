A long only algo written in python using the QuantConnect platform to invest in "cheap quality" equities. Creates a portfolio of 10 stocks with the highest earnings yield, that pass the screening metrics.

Rebalances: Yearly, in Jan.
Backtest period: 1999-2021.
Cheap Metric(s): EV/EBIT < 10, Earnings Yield
Quality Metric(s): D/E < 50%, TTM ROIC > 10%
Other Metric(s): Exclude Financial Services, REITs, ADRs, non-primary class shares, WTI, Top 1000 shares in dollar volume.

Performance Snapshot:

Sharpe Ratio: 0.635
Total Trades: 428
Average Win: 3.87%
Average Loss: -2.25%
Compounding Annual Return: 13.787%
Drawdown: 56.600%
Expectancy: 0.622
Net Profit: 1700.627%
Loss Rate: 40%
Win Rate: 60%
Profit-Loss Ratio: 1.72
Alpha: 0.064
Beta: 0.97
Annual Standard Deviation: 0.22
Annual Variance: 0.048
Information Ratio: 0.446
Tracking Error: 0.138
Treynor Ratio: 0.144


