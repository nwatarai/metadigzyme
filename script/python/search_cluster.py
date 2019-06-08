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
        default=None,
        help='Window size for searching \
              the cluster center. \
              (default: #genes * 2)')
    parser.add_argument(
        '-pt', '--peak_thresholds',
        action='store', type=int,
        default=15,
        help='Maximum number of peaks for search')
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
    df["gene"] = df['explanation'].map(lambda x: x.split(";")[0])
    df.index = df["gene"]
    df = df.sort_values(by="start")
    plus_df = df.copy()
    minus_df = df.copy()
    for i in df.index:
        if df.loc[i, "strand"] == "+":
            minus_df.loc[i, "gene"] = "comp_" + minus_df.loc[i, "gene"]
        else:
            plus_df.loc[i, "gene"] = "comp_" + plus_df.loc[i, "gene"]
    plus_df = plus_df.set_index("gene")
    minus_df = minus_df.set_index("gene")
    return pd.concat([plus_df, minus_df], axis=0)


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
            #gff[ec] = gff[ec] / gff[ec].sum()
            pass
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
    base = ex.sum().sum()
    #base = ex.max(axis=0).sum()
    # return base * (ex.any(axis=0).astype(int).sum() - 0.999)
    return base


def cluster_indices(score, size):
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
    for i, _o in enumerate(outs):
        name = "{}.{}".format(_o[0].split("/")[-1], _o[0].count("|") + 1)
        o = _o[1]
        S += o[1] - 1
        for gene in o[0].index:
            O += "cluster{}\t{}\t{}\t{}\n".format(
                name, gene, to_ec(o[0], gene), round(o[1], 2))
    outstrs.append("#score={}\n{}\n".format(round(S, 2), O))


def recursive_search(score, outs, args, outstrs, partial_results):
    if args["window"]:
        ws = args["window"]       
    else:
        ws = score.shape[1] * 2
    key = "|".join(score.columns.tolist())
    if key not in partial_results:
        indices = cluster_indices(score, ws)
        partial_results[key] = indices
    else:
        indices = partial_results[key]

    if len(indices) >= args["peak_thresholds"]:
        output_metadigzyme_score(copy.deepcopy(outs), outstrs)
        return 0
    print(indices)

    ex = int(ws / 2)
    for i in indices:
        key = "{}/{}".format("|".join(score.columns.tolist()), i)
        if key not in partial_results:
            result = fit_window(score, i, ex)
            partial_results[key] = result
        else:
            result = partial_results[key]
        drop_index = result[0].columns[result[0].any(axis=0).values]
        _score = score.drop(drop_index, axis=1)
        _outs = copy.deepcopy(outs)
        _outs.append([key, result])
        if _score.sum().sum() > 1 and _score.shape[1] > 1:
            recursive_search(_score, _outs, args, outstrs, partial_results)
        else:
            if len(_outs) > 0:
                output_metadigzyme_score(_outs, outstrs)

def uniq_results(outstrs):
    outs = []
    if len(outstrs) == 1:
        return outstrs
    s = sorted(set(outstrs), reverse=True, key=lambda x: len(x))
    for i in range(len(s))[1:]:
        flag = True
        _si = "\n".join(s[i].split("\n")[1:]).rstrip()
        for j in range(i):
            if _si in s[j]:
                flag = False
        if flag:
            outs.append(s[i])
    return sorted(outs, reverse=True)

def main(args):
    gff = parse_gff(args["gff"])
    gene_ec = pd.read_csv(args["gene_ec"], squeeze=True,
                          index_col=0, sep="\t")
    module_ec = open(args["module_ec"]).read().rstrip().split("\n")
    score = make_score_table(gff, gene_ec, module_ec, args["digit"])
    outstrs = []
    recursive_search(score, [], args, outstrs, {})
    outfile = open(args["output"], "w")
    outfile.write("".join(uniq_results(outstrs)))
    outfile.close()


if __name__ == '__main__':
    main(parser_setting())
