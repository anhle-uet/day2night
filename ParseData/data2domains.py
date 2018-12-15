# Script parsing dataset folder to several domains by states from csv file

import pandas as pd
import os, sys
from shutil import copy, move

# ------------------------ Variables ------------------------ 
datapath = '/content/drive/datasets/nexet/nexet_2017_1/' # path to dataset directory
csvfile = '/content/drive/datasets/nexet/train.csv' # path to csv file
col_name = 'image_filename' # column name with dataset's filenames
col_state = 'lighting' # column name with dataset's states 
domains = {
            'TrainA' : 'Day',
            'TrainB' : ['Night', 'Twilight'],
            'TestA' : 'Day',
            'TestB' : ['Night', 'Twilight']
          }  # making domain directories {Domain_Name : States}
mode = 'move' # 'move' | 'copy' all files from dataset folder to domains
# -----------------------------------------------------------

# ------------------------ Arguments ------------------------ 
mode = sys.argv[1] if len(sys.argv) > 1 else mode
datapath = sys.argv[2] if len(sys.argv) > 2 else datapath
csvfile = sys.argv[3] if len(sys.argv) > 3 else csvfile
# -----------------------------------------------------------

class DomainShifter(object):
    """
        Class creating dataset's domains from csv 
    """

    def get_states(self, column):
        """ Getting states by csv file column """

        print(f'Searching states in {column}...')
        states = set()
        for state in self.csv[column]:
            states.add(state) 
        print("States:", *states)
        return states

    def __init__(self, data, file, domains, col_name, col_state, sep=','):
        
        # Check datasets paths
        if not os.path.exists(data):
            raise FileNotFoundError(f"No dataset '{os.path.abspath(data)}' folder found!")
        if not os.path.exists(file):
            raise FileNotFoundError(f"No csv file '{os.path.abspath(file)}' found!")

        def check_cols(*cols):
            """ Check if columns exist in csv """
            try:
                for col in cols:
                    self.csv[col]
            except:
                raise Exception(f'Column name "{col}" is not found in {self.file}!')
        
        # Initialize class local variables
        self.dataset = data # dataset path
        self.file = file # csv file path
        self.domains = domains # domains to create
        self.csv = pd.read_csv(file, sep=sep, encoding='utf8') # read csv with pandas
        check_cols(col_name, col_state) # check on column names exists
        self.states = self.get_states(col_state) # get all states from csv

    def shift_domains(self, mode='copy'):
        """ Creating domain folders and parsing dataset folder by csv """
        if mode == 'copy':
            shift = copy
        elif mode == 'move':
            shift = move
        else:
            raise Exception(f'Shift Domains: no {mode} found!')
        print('Shifting domains starts...')
        print(f'Mode: {shift.__name__}')
        # Caclculate splits
        domain_split = {}
        for state in self.states:
            domain_split[state] = sum(state in v for v in self.domains.values())
        self

        # Creating directories
        print('Creating directories...')
        base = self.dataset
        for ndir in self.domains.keys():
            path = os.path.join(base, ndir)
            if not os.path.isdir(path):
                os.mkdir(path)
                print(f'{path} created!')
        print('Created!')

        nrow = len(self.csv)
        with open('log.txt', 'a', encoding="utf-8") as log, open('err.txt', 'a', encoding="utf-8") as err:
            print('------------------', file=err)
            print('------------------', file=log)
            for i, row in self.csv.iterrows():
                if i % 1000 == 0:
                    print(str(i * 100 // nrow) + '% processed')
                name = str(row[col_name])
                src = os.path.join(base, name)
                is_shifted = False
                for item in self.domains.items():
                    if row[col_state] in item[1]:
                        dst = os.path.join(base, item[0])
                        dstname = os.path.exists(os.path.join(dst, name))
                        if os.path.exists(src) and (mode == 'move' or not os.path.exists(dstname)):
                            shift(src, dst)
                            print(f'{shift.__name__}: {src} → {dst}', file=log)
                            is_shifted = True
                        elif os.path.exists(dstname):
                            is_shifted = True
                        break
                if not is_shifted:
                    print(f'{row[col_name]} file not shifted', file=err)
        print('Shifiting completed!')

# Main
ds = DomainShifter(datapath, csvfile, domains, col_name, col_state)
ds.shift_domains(mode)

