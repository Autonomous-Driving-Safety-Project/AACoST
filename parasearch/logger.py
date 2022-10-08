import pandas as pd
import os
from datetime import datetime


class Logger:
    def __init__(self, columns):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        self.__filename = "./logs/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".pkl"
        # self.__df = pd.DataFrame(columns=columns)
        self.__columns = columns
        self.__data = []

    def add_row(self, row):
        # row = pd.DataFrame(data=row, index=[0], columns=self.__columns)
        # self.__df = pd.concat([self.__df, row])
        self.__data.append(row)

    def dump(self):
        df = pd.DataFrame(data=self.__data, index=range(1, 1 + len(self.__data)), columns=self.__columns)
        df.to_pickle(self.__filename)
