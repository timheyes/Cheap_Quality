from QuantConnect.Data.UniverseSelection import *
import math
import numpy as np
import pandas as pd
import scipy as sp

class CalibratedVentralPrism(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(1999, 1, 1)  # Set Start Date
        self.SetCash(10000)  # Set Strategy Cash
        
        self.AddEquity("SPY", Resolution.Daily).Symbol
        self.UniverseSettings.Resolution = Resolution.Daily
        self.AddUniverse(self.CoarseSelectionFunction, self.FineSelectionFunction)
        
        self.num_screener = 50
        self.num_stocks = 10
        self.formation_days = 200
        
        self.UseMomentum = False # toggle momentum on or off
        self.momentum = False #false means take highest momentum (return) in last 200 days
        
        self.lastYear = -1
        
        self.symbols = None
        
    def CoarseSelectionFunction(self, coarse):
        
        # drop stocks which have no fundamental data or have too low prices
        selected = [x for x in coarse if (x.HasFundamentalData)]
        # rank the stocks by dollar volume 
        filtered = sorted(selected, key=lambda x: x.DollarVolume, reverse=True) 

        return [ x.Symbol for x in filtered[:1000]]
        
    def FineSelectionFunction(self, fine):
        
        filtered_fine = [x for x in fine if (x.ValuationRatios.EVtoEBIT < 10)
                                            and (x.ValuationRatios.EVtoEBIT > 0)
                                            and (x.OperationRatios.TotalDebtEquityRatio.OneMonth < 0.5)
                                            and (x.OperationRatios.ROIC.OneYear > 0.1)
                                            and (x.SecurityReference.IsDepositaryReceipt == 0)
                                            and (x.SecurityReference.IsPrimaryShare == 1)
                                            and (x.CompanyReference.IsREIT == 0)
                                            and (x.AssetClassification.MorningstarSectorCode != MorningstarSectorCode.FinancialServices)
                                            and (x.CompanyReference.PrimarySymbol != 'WTI')]

        top = sorted(filtered_fine, key = lambda x: x.ValuationRatios.EarningYield, reverse=False)[:self.num_screener]
        
        self.symbols = [x.Symbol for x in top]
        [self.Log(x.ValuationRatios.EVtoEBIT) for x in top]
        return self.symbols
        
    def OnData(self, data):
        
        
        if self.Time.year == self.lastYear:
            return
        
        self.lastYear = self.Time.year
        
        if self.symbols is None: return
    
        if self.UseMomentum == True:
            chosen_df = self.calc_return(self.symbols)
            self.Log("chosen_df after calc rets")
            self.Log(chosen_df)
            self.Debug(chosen_df)
            chosen_df = chosen_df.iloc[:self.num_stocks]
            chosen_df_list = []
            for i in range(len(chosen_df.index)):
                chosen_df_list.append(self.AddEquity(chosen_df.index[i], Resolution.Daily).Symbol)
            chosen_df = chosen_df_list
        else:
            #chosen_df = DataFrame(self.symbols[:self.num_stocks])
            chosen_df = self.symbols[:self.num_stocks]
        
        self.existing_pos = 0
        add_symbols = []
        
        for symbol in self.Portfolio.Keys:
            if (symbol.Value not in chosen_df):
                self.SetHoldings(symbol, 0)
            elif (symbol.Value in chosen_df): 
                self.existing_pos += 1
        
        if len(chosen_df) == 0: return   
        
        weight = 1/len(chosen_df)
        
        for symbol in chosen_df:
            self.Log("looking in portfolio keys")
            self.Log(symbol.Value)
            self.Log(chosen_df)
            self.AddEquity(symbol)
            self.SetHoldings(symbol, weight)
            
        self.changes = None
            
    def OnSecuritiesChanged(self, changes):
        self.changes = changes
        
    def calc_return(self, stocks):
        hist = self.History(stocks, self.formation_days, Resolution.Daily)
        current = self.History(stocks, 1, Resolution.Minute)
        
        self.price = {}
        ret = {}
     
        for symbol in stocks:
            try:
                if str(symbol) in hist.index.levels[0] and str(symbol) in current.index.levels[0]:
                    self.price[symbol.Value] = list(hist.loc[str(symbol)]['close'])
                    self.price[symbol.Value].append(current.loc[str(symbol)]['close'][0])
            except:
                pass
            
        for symbol in self.price.keys():
            ret[symbol] = (self.price[symbol][-1] - self.price[symbol][0]) / self.price[symbol][0]
        df_ret = pd.DataFrame.from_dict(ret, orient='index')
        df_ret.columns = ['return']
        sort_return = df_ret.sort_values(by = ['return'], ascending = self.momentum)

        
        return sort_return
