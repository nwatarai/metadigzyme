import pandas as pd
import numpy as np
import argparse

def parser_setting():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-me', '--module_ec',
        action='store', type=str,
        required=True,
        help='module gene ec list')
    parser.add_argument(
        '-mi', '--module_id',
        action='store', type=str,
        required=True,
        help='module ID')
    parser.add_argument(
        '-o', '--output',
        action='store', type=str,
        required=True,
        help='output directory') 
    args = parser.parse_args()
    return vars(args)


def parse_module_ec(module_ec, module_id):
    df = pd.read_csv(module_ec, sep="\t", header=0, index_col=None)
    index = (df["module"] == module_id) 
    ex = df.loc[index, :]
    outs = []
    orgs = []
    for i in ex["org"].unique():
        orgs.append(i)
        outs.append(ex.loc[ex["org"] == i, "ec"].dropna().tolist())
    return outs, orgs

def main(args):
    module_ec, orgs = parse_module_ec(args["module_ec"], args["module_id"])
    for i, org in zip(module_ec, orgs):
        if len(i) > 1:
            o = open("{}/{}".format(args["output"], org), "w")
            o.write("\n".join(i))
            o.close()

if __name__ == "__main__":
    main(parser_setting())
