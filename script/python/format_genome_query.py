#!/bin/env/python3
# -*- coding: utf-8 -*-
# Author: ynakamura

import itertools
import re
import sys

import pandas as pd

from argparse import ArgumentParser


def parser_setting():
    parser = ArgumentParser(
        prog='format_genome_query.py',
        description=('Format genome query file from '
                     'GFF and gene enzyme list file.'))
    parser.add_argument(
        'gff',
        action='store', type=str,
        help='GFF formatted file.')
    parser.add_argument(
        'ge_list',
        action='store', type=str,
        help='Gene enzyme list file.')
    parser.add_argument(
        '-gw', '--gene_window',
        action='store', type=int,
        default=3,
        help='Gene window size.')
    parser.add_argument(
        '-i', '--ignore',
        action='store_true',
        default=False,
        help='Ignore non enzyme.')
    parser.add_argument(
        '-o', '--output',
        action='store', type=str,
        help='Output file.')
    args = parser.parse_args()
    return (parser, args)


def gff_open(gff):
    df = pd.read_table(gff,
                       names=['seqname', 'source', 'feature',
                              'start', 'end', 'score',
                              'strand', 'frame', 'attribute'],
                       comment='#')
    df = df.loc[df.loc[:, 'feature'] == 'CDS', :]
    df.loc[:, 'genename'] = df.loc[:, 'attribute'].map(
        lambda x: re.split('\;|\ |\,', x)[0])
    return df


def ge_open(ge_list):
    df = pd.read_table(ge_list, comment='#')
    df = df.iloc[:, [0, 1]]
    df.columns = ['genename', 'ec number']
    df.loc[:, 'ec number'] = df.loc[:, 'ec number'].apply(
        lambda x: x.split(':')[1] if ':' in x else x)

    df = pd.DataFrame([
        [g, list(df.loc[df.loc[:, 'genename'] == g,
                        'ec number'].values)]
        for g in set(df.loc[:, 'genename'].values)],
        columns=df.columns)
    return df


def main(gff, ge_list, gene_window, ignore, output):
    gff_df = gff_open(gff)
    ge_df = ge_open(ge_list)

    merged_df = pd.merge(gff_df,
                         ge_df,
                         on='genename',
                         how='outer')
    merged_df.loc[:, 'ec number'] = merged_df.loc[:, 'ec number'].apply(
            lambda x: x if isinstance(x, list) else ['non-enzyme'])

    if ignore:
        merged_df = merged_df.loc[
            merged_df.loc[:, 'ec number'].apply(
                lambda x: False if 'non-enzyme' in x else True)]

    if output is None:
        out = sys.stdout
    else:
        out = open(output, 'w')

    for seqname in set(merged_df.loc[:, 'seqname'].values):
        for strand in set(merged_df.loc[:, 'strand'].values):
            df = merged_df.loc[
                ((merged_df.loc[:, 'seqname'] == seqname) &
                 (merged_df.loc[:, 'strand'] == strand)),
                :].sort_values(by='start')
            if len(df.index) >= gene_window:
                genes_df = pd.DataFrame()
                enzymes_df = pd.DataFrame()
                for i in range(gene_window):
                    genes_df[i] = df.iloc[
                        i:len(df.index) + i + 1 - gene_window, :].loc[
                        :, 'genename'].values
                    enzymes_df[i] = df.iloc[
                        i:len(df.index) + i + 1 - gene_window, :].loc[
                        :, 'ec number'].values
                genes = genes_df.T.apply(
                    lambda x: '/'.join(x)).values
                enzymes = enzymes_df.T.apply(
                    lambda x: itertools.product(*x)).map(
                    lambda x: ['/'.join(y) for y in x]).values
                for gene, enzyme in zip(genes, enzymes):
                    out.write(''.join([
                        '{0}\t{1}\n'.format(e, gene) for e in enzyme]))
    out.close()


if __name__ == '__main__':
    parser, args = parser_setting()

    main(**vars(args))
