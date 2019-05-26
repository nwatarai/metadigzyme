#!/bin/env/python3
# -*- coding: utf-8 -*-
# Author: nwatarai

import sys
import numpy as np
import pandas as pd
from argparse import ArgumentParser


def parser_setting():
    parser = ArgumentParser(
        prog='search_cluster.py',
        description='Search gene clusters \
        of a motabolism module from a genome.')
    parser.add_argument(
        '-g', '--gff',
        action='store', type=str,
        required=True,
        help='GFF file.')
    parser.add_argument(
        '-ge', '--gene_ec',
        action='store', type=str,
        required=True,
        help='Gene-EC list.')
    parser.add_argument(
        '-me', '--module_ec',
        action='store', type=str,
        required=True,
        help='EC list in a module.')
    parser.add_argument(
        '-o', '--output',
        action='store', type=str,
        required=True,
        help='Output file.')
    parser.add_argument(
        '-d', '--digit',
        action='store', type=int,
        default=3, choices=[1, 2, 3, 4],
        help='Digit of EC number for search.')
    parser.add_argument(
        '-w', '--window',
        action='store', type=int,
        default=12,
        help='Window size for searching \
              the cluster center.')
    args = parser.parse_args()
    return vars(args)

def parse_gff(gff):
    df = pd.read_csv(gff, 
        header=None, index_col=None, comment="#", sep="\t")
    df.columns = ["file", "path", "feature", "start", "end", 
                  "?", "strand", "frame", "explanation"]
    df.index = df['explanation'].map(lambda x: x.split(";")[0])
    return df.sort_values(by="start")

def cut_digit(string, digit):
    return ".".join(string.split(".")[:digit])

def to_EC(x, gene_ec, digit):
    if x in gene_ec.index:
        if isinstance(gene_ec[x], str):
            return cut_digit(gene_ec[x], digit)
        else:
            return "|".join(gene_ec[x].map(
                lambda x: cut_digit(x, digit)).tolist())
    return "None"

def make_score_table(gff, gene_ec, module_ec, digit):
    gff["EC"] = gff.index.map(lambda x: to_EC(x, gene_ec, digit))
    for i in module_ec:
        ec = ".".join(i.split(".")[:digit])
        gff[ec] = gff["EC"].map(lambda x: len(x.split(ec)) > 1)
        gff[ec] = gff[ec].astype(float)
        gff[ec] = gff[ec] / gff[ec].sum()
    return gff.iloc[:, - (len(module_ec) - 1):].astype(float)

def determine_cluster(array, size):
    consecutive = False
    out = []
    for i in range(array.shape[0]):
        if not consecutive and array[i]:
            start = i
            consecutive = True
        elif consecutive and not array[i]:
            end = i - 1
            consecutive = False
            out.append(int((end + start + size) / 2))
    return out

def cluster_indices(score, size):
    add = score.iloc[:size, :]
    add.index = add.index.map(lambda x: x + "_a")
    score = pd.concat([score, add], axis=0)
    density = []
    for i in range(score.shape[0] - size):
        density.append(score.iloc[i:i + size, :].max(axis=0).sum())
    density = np.array(density)
    max_value = np.amax(density)
    return determine_cluster(density == max_value, size)

def main(args):
    gff = parse_gff(args["gff"])
    gene_ec = pd.read_csv(args["gene_ec"], squeeze=True,
                          index_col=0, sep="\t")
    module_ec = open(args["module_ec"]).read().rstrip().split("\n")
    score = make_score_table(gff, gene_ec, module_ec, args["digit"])
    indices = cluster_indices(score, args["window"])
    ex = int(args["window"] / 2)
    print(gff.iloc[indices[0] - ex:indices[0] + ex, :])

if __name__ == '__main__':
    main(parser_setting())
