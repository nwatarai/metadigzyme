#!/bin/env/python3
# -*- coding: utf-8 -*-
# Author: nwatarai

import numpy as np
import pandas as pd
import copy
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
    parser.add_argument(
        '-o', '--output',
        required=True,
        action='store', type=str,
        help='Output file.')
    args = parser.parse_args()
    return vars(args)


def parse_gff(gff):
    df = pd.read_csv(
        gff,
        header=None, index_col=None, comment="#", sep="\t")
    df.columns = [
        "file", "path", "feature", "start", "end",
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
        if gff[ec].sum() == 0:
            gff.drop(ec, axis=1)
        else:
            gff[ec] = gff[ec] / gff[ec].sum()
    return gff.iloc[:, 10:].astype(float)


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


def density_score(ex):
    base = ex.max(axis=0).sum()
    # return base * (ex.any(axis=0).astype(int).sum() - 0.999)
    return base


def cluster_indices(score, size):
    add = score.iloc[:size, :]
    add.index = add.index.map(lambda x: x + "_a")
    score = pd.concat([score, add], axis=0)
    density = []
    for i in range(score.shape[0] - size):
        density.append(density_score(score.iloc[i:i + size, :]))
    density = np.array(density)
    max_value = np.amax(density)
    return determine_cluster(density == max_value, size)


def window_score(score):
    genecount = score.astype(bool).astype(int).values.sum()
    return genecount * genecount / float(score.shape[0])


def fit_window(score, center, ex):
    ex = score.iloc[center - ex:center + ex, :]
    out = []
    for window in range(1, ex.shape[0]):
        for offset in range(ex.shape[0] - window):
            target = ex.iloc[offset:offset + window, :]
            out.append([target, window_score(target)])
    return sorted(out, key=lambda x: x[1])[-1]


def to_ec(score, gene):
    index = score.loc[gene].astype(bool)
    return "|".join(score.columns[index].tolist())


def output_metadigzyme_score(outs, outstrs):
    S = 1
    O = ""
    for i, o in enumerate(outs):
        S += o[1] - 1
        for gene in o[0].index:
            O += "cluster{}\t{}\t{}\t{}\n".format(
                i, gene, to_ec(o[0], gene), o[1])
    outstrs.append("#score={}\n{}\n".format(S, O))


def recursive_search(score, outs, args, outstrs):
    indices = cluster_indices(score, args["window"])
    print(indices)

    ex = int(args["window"] / 2)
    for i in indices:
        result = fit_window(score, i, ex)
        drop_index = result[0].columns[result[0].any(axis=0).values]
        _score = score.drop(drop_index, axis=1)
        _outs = copy.deepcopy(outs)
        if result[1] > 1:
            _outs.append(result)
        if _score.sum().sum() > 1 and _score.shape[1] > 1:
            recursive_search(_score, _outs, args, outstrs)
        else:
            if len(_outs) > 0:
                output_metadigzyme_score(_outs, outstrs)


def main(args):
    gff = parse_gff(args["gff"])
    gene_ec = pd.read_csv(args["gene_ec"], squeeze=True,
                          index_col=0, sep="\t")
    module_ec = open(args["module_ec"]).read().rstrip().split("\n")
    score = make_score_table(gff, gene_ec, module_ec, args["digit"])
    outstrs = []
    recursive_search(score, [], args, outstrs)
    outfile = open(args["output"], "w")
    outfile.write("".join(sorted(set(outstrs), reverse=True)))
    outfile.close()


if __name__ == '__main__':
    main(parser_setting())
