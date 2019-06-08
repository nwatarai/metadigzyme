#!/bin/env/python3
# -*- coding: utf-8 -*-
# Author: ynakamura

import sys

import pandas as pd

from argparse import ArgumentParser


def parser_setting():
    parser = ArgumentParser(
        prog='domsign_out2gene_enzyme.py',
        description='Convert Domsign output file to gene enzyme format.')
    parser.add_argument(
        'domsign_out',
        action='store', type=str,
        help='Domsign output file.')
    parser.add_argument(
        '-o', '--output',
        action='store', type=str,
        help='Gene enzyme formatted output file.')
    args = parser.parse_args()
    return (parser, args)


def main(domsign_out, output):
    df = pd.read_csv(domsign_out, sep='\t', header=None, index_col=None)

    df.iloc[:, 1] = df.iloc[:, 1].replace('EC=-.-.-.-', 'Non-enzyme')
    df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: x.replace('EC=', 'ec:'))
    df = df.loc[(df.iloc[:, 1] != 'Non-enzyme'), :]

    if output is None:
        out = sys.stdout
    else:
        out = open(output, 'w')
    df.to_csv(out, sep='\t', header=False, index=False)
    out.close()


if __name__ == '__main__':
    parser, args = parser_setting()

    main(**vars(args))
