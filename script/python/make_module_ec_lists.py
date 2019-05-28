#!/bin/env/python3
# -*- coding: utf-8 -*-
# Author: nwatarai

import sys
import numpy as np
import pandas as pd
import copy
from argparse import ArgumentParser

def parser_setting():
    parser = ArgumentParser(
        prog='make_module_ec_lists.py',
        description='make module_ec lists for each.')
    parser.add_argument(
        'module_ec',
        action='store', type=str,
        help='Original module_ec lists.')
    parser.add_argument(
        '-o', '--out_dir',
        action='store', type=str,
        required=True,
        help='output_directory.')
    args = parser.parse_args()
    return vars(args)

def main(args):
    module_ec = pd.read_csv(args["module_ec"], index_col=None,
                            header=None, sep="\t")
    for i in module_ec[1].unique():
        outfile = "{}/{}".format(args["out_dir"], i.split(":")[-1])
        index = module_ec[1] == i
        l = module_ec.loc[index, 0].tolist()
        if len(l) > 1:
            o = open(outfile, "w")
            o.write("\n".join(l) + "\n")
            o.close()

if __name__ == '__main__':
    main(parser_setting())
