#!/usr/bin/env python
import unittest 
import sys 
import os 

sys.path.append(
        os.path.abspath(
                "/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin"
                ))

from json_annot_import import *

# https://realpython.com/python-testing/

os.listdir()

args = {"sample_id": "SRR11262179", 
        "database": "DPI_test.sqlite",
        "json": "SRR11262179.json"}


f = open(args["json"])
data = json.load(f)
f.close()

info = prep_info_df(data, args["sample_id"])
info.head()
df_to_database(info,args["database"], "annotation_info",if_exists='append')

features = prep_features_df(data, args["sample_id"])
features.head()
df_to_database(features,args["database"], "annotation_features",if_exists='append')

sequences = prep_sequences_df(data, args["sample_id"])
df_to_database(sequences,args["database"], "annotation_sequences",if_exists='append')

# This one was not working
# sequences = prep_sequences_df(data, args["sample_id"])
# sequences =pd.json_normalize(data['sequences'])
# sequences.head()
# sequences.dtypes

# sequences["length"][0:2]
# sequences["orig_id"][0:2]
# sequences["orig_description"][0:2]
# sequences[["genus", "species", "gcode", "topology"]] = sequences["description"].str.split(" ", expand=True)

# try: 
#         sequences[["len", "cov", "corr", "origname", "sw", "date"]] = sequences["orig_description"].str.split(" ", expand=True)
# except: 
#         # if it does not work we only report as empty - neabs the description is not complete
#         sequences[["len", "cov", "corr", "origname", "sw", "date"]] = pd.DataFrame(
#                 np.nan, 
#                 columns = ["len", "cov", "corr", "origname", "sw", "date"], 
#                 index = np.arange(len(sequences["orig_description"]))
#                                 )
# #sequences[["len", "cov", "corr", "origname", "sw", "date"]]
   
# sequences[["genus", "species", "gcode", "topology"]] = sequences["description"].str.split(" ", expand=True)
# sequences.drop(labels= ["orig_description", "description"], axis = 1)
# sequences.replace(["^.*=","]", "NaN"], "", inplace = True, regex = True)

# sequences.head()