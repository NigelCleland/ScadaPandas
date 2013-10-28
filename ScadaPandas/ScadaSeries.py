#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from pandas import Series

class ScadaSeries(Series):
    """docstring for ScadaSeries"""

    def __new__(cls, *args, **kwargs):

        arr = Series.__new__(cls, *args, **kwargs)

        if type(arr) is ScadaSeries:
            return arr
        else:
            return arr.view(ScadaSeries)


    def from_file(self, filename, columns=None):
        scada_date_format = "%d-%b-%y %H:%M:%S"
        data = pd.read_csv(filename)
        data["Timestamp"] = pd.to_datetime(data["Timestamp"], format=scada_date_format)
        data.set_index("Timestamp", inplace=True)

        if columns:
            cols = self._fuzzy_search(data.columns.tolist(), columns)
            data = data[cols]

        agg_data = data.sum(axis=1)

        return ScadaSeries(agg_data)

    def load_windfarm(self, filename, wind_farm):

        wind_columns = self.wind_mapping(wind_farm)
        return self.from_file(filename, columns=wind_columns)

    def _fuzzy_search(self, columns, search_pattern):
        if not isinstance(search_pattern, list):
            search_pattern = [search_pattern]
        return [x for x in columns if any([y in x for y in search_pattern])]

    def wind_mapping(self, farm):
        """ Map a String name to a column search parameter """

        wind_dictionary = {"West Wind": ["WWD"],
                           "Tararua": ["TWF", "TWC"],
                           "North Island": ["TWF", "TWC", "TUK", "TRH", "TAP",
                                            "WWD"],
                           "Tararua Sth": ["TWF", "TWC"],
                           "Tararua Nth": ["TAP", "TRH"],
                           "Te Apiti": ["TAP"],
                           "All Tararua": ["TWF", "TWC", "TRH", "TAP"],
                           "South Island": ["MAH", "WHL"],
                           "Te Uku": ["TUK"],
                           "Mahinerangi": ["MAH"],
                           "White Hill": ["WHL"],
                           "New Zealand": ["GENERAT"]
                           }

        return wind_dictionary.get(farm, None)

    def resample(self, time, how="mean"):
        return ScadaSeries(self.resample(time, how))

    def output_distribution(self, resample_time=None, inverse=False,
                            cumulative=True):
        if resample_time:
            distro = self.resample(resample_time)
        else:
            distro = self.copy()

        percentages = self._aggregate_cut(distro)
        percentages.index = percentages.index.map(self._split_cut_index)
        percentages = percentages.sort_index()

        if cumulative:
            if inverse:
                return percentages.cumsum()
            else:
                return 100 - percentages.cumsum()
        else:
            return percentages


    def _split_cut_index(self, cut_index):
        begin, end  = cut_index.split(', ')
        begin = float(begin[1:])
        end = float(end[:-1])
        return end


    def _aggregate_cut(self, series):
        cuts = pd.cut(series, np.arange(-1, series.max()+1, 1))
        values = pd.value_counts(cuts)
        percentages = values * 100. / float(len(series))
        return percentages



