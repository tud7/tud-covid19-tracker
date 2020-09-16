import os
import urllib
import urllib.request
import urllib.error

import pandas as pd
from abc import ABC, abstractmethod


class DataSource(ABC):

    def __init__(self, url):

        self.df  = self.read_data(url=url)
        self._reformat_data()
        
        # unify 'date' column to the same data type for easy merging and plotting
        try:
            self.df['date'] = pd.to_datetime(self.df['date'])
        except:
            pass     

    @staticmethod
    def read_data(url):
        '''Read data from the url into the panda dataframe'''

        try:
            df = pd.read_csv(url)
            return df

        except urllib.error.HTTPError as ex:
            print('WARNING: Unable to retrieve data...')
            print(' - INFO:', ex)
        
        return None

    def get_full_data(self):
        '''Function to get full data frame'''
        return self.df

    @abstractmethod
    def get_US_data(self, copy=False):
        '''Funtion to return United States data'''
        pass

    def _reformat_data(self):
        pass

    def _to_pickle(self, filename):
        filename = '%s.pkl' %filename
        self.df.to_pickle(filename)


'''
Data from John Hopkins
'''
class JohnHopkins(DataSource):

    def __init__(self, url=None):
        super().__init__('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
        self._to_pickle(self.__class__.__name__)

    def _reformat_data(self):

        id_vars=['country', 'state', 'Lat', 'long']
        agg_dict = { 'cum_confirmed':sum }

        self.df = self.df.iloc[:, 6:]
        self.df = self.df.drop('Combined_Key', axis=1) 
        self.df = self.df.rename(columns={ 'Country_Region':'country', 'Province_State':'state', 'Long_':'long' }) 
        self.df = self.df.melt(id_vars=id_vars, var_name='date', value_name='cum_confirmed') 
        self.df = self.df.astype({'date':'datetime64[ns]', 'cum_confirmed':'Int64'}, errors='ignore') 
        self.df = self.df.groupby(['country', 'state', 'date']).agg(agg_dict).reset_index()

    def get_US_data(self, copy=False):
        return self.df


'''
Data from Covid Tracking Project
'''
class CovidTracking(DataSource):

    def __init__(self):
        super().__init__('https://covidtracking.com/api/v1/us/daily.csv')
        self._to_pickle(self.__class__.__name__)

    def _reformat_data(self):
        self.df = self.df.sort_values(by='date', ascending=True)

        # convert to string first since 'date' column is int64.
        # to_datetime() function won't work well with int64
        self.df['date'] = self.df['date'].astype(str)

    def get_US_data(self, copy=False):
        return self.df


'''
Data from Our World In Data
'''
class OurWorldInData(DataSource):

    def __init__(self):
        super().__init__('https://covid.ourworldindata.org/data/owid-covid-data.csv')
        self._to_pickle(self.__class__.__name__)        

    def get_US_data(self, copy=False):
        
        us_df = self.df[ self.df['iso_code']=='USA' ]
        if copy:
            return us_df.copy()

        return us_df
