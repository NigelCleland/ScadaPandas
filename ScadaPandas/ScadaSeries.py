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

