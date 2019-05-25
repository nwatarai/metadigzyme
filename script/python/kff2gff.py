#!/bin/env/python3
# -*- coding: utf-8 -*-
# Author: ynakamura

import sys

import pandas as pd

from argparse import ArgumentParser


def parser_setting():
    parser = ArgumentParser(
        prog='kff2gff.py',
        description='Convert KFF format to GFF format.')
    parser.add_argument(
        'kff',
        action='store', type=str,
        help='KFF formatted file.')
    parser.add_argument(
        '-o', '--output',
        action='store', type=str,
        help='Output file.')
    args = parser.parse_args()
    return (parser, args)


def main(kff, output):
    file_name = kff.split('/')[-1]

    kff_df = pd.read_table(kff,
                           index_col=False,
                           names=['genename', 'feature', 'alength',
                                  'nlength', 'position', '_', '__', '___',
                                  'name', 'KO', 'description'])
    kff_plasmid_df = kff_df.loc[kff_df.loc[:, 'position'].apply(
        lambda x: True if ':' in x else False), :]
    kff_df = kff_df.loc[kff_df.loc[:, 'position'].apply(
        lambda x: True if ':' not in x else False), :]

    gff_df = pd.DataFrame(index=kff_df.index,
                          columns=['seqname', 'source', 'feature',
                                   'start', 'end', 'score',
                                   'strand', 'frame', 'attribute'])
    gff_df.loc[:, 'seqname'] = file_name
    gff_df.loc[:, 'feature'] = kff_df.loc[:, 'feature']
    gff_df.loc[:, 'start'] = kff_df.loc[:, 'position'].apply(
        lambda x: x[11:-1] if 'complement' in x else x).apply(
        lambda x: x[5:-1] if 'join' in x else x).apply(
        lambda x: x.split('.')[0]).apply(
        lambda x: x[1:] if '<' in x else x)
    gff_df.loc[:, 'end'] = kff_df.loc[:, 'position'].apply(
        lambda x: x[11:-1] if 'complement' in x else x).apply(
        lambda x: x[5:-1] if 'join' in x else x).apply(
        lambda x: x.split('.')[-1]).apply(
        lambda x: x[1:] if '>' in x else x)
    gff_df.loc[:, 'strand'] = kff_df.loc[:, 'position'].apply(
        lambda x: '-' if 'complement' in x else '+')
    gff_df.loc[:, 'attribute'] = kff_df.loc[:, 'genename'].str.cat(
        kff_df.loc[:, 'name'], ';', na_rep='').str.cat(
        kff_df.loc[:, 'KO'], ';', na_rep='').str.cat(
        kff_df.loc[:, 'description'], ';', na_rep='')

    gff_plasmid_df = pd.DataFrame(index=kff_plasmid_df.index,
                                  columns=['seqname', 'source', 'feature',
                                           'start', 'end', 'score',
                                           'strand', 'frame', 'attribute'])
    gff_plasmid_df.loc[:, 'seqname'] = kff_plasmid_df.loc[:, 'position'].apply(
        lambda x: '{0}:{1}'.format(file_name, x.split(':')[0]))
    gff_plasmid_df.loc[:, 'feature'] = kff_plasmid_df.loc[:, 'feature']
    gff_plasmid_df.loc[:, 'start'] = kff_plasmid_df.loc[:, 'position'].apply(
        lambda x: x.split(':')[1] if ':' in x else x).apply(
        lambda x: x[11:-1] if 'complement' in x else x).apply(
        lambda x: x[5:-1] if 'join' in x else x).apply(
        lambda x: x.split('.')[0]).apply(
        lambda x: x[1:] if '<' in x else x)
    gff_plasmid_df.loc[:, 'end'] = kff_plasmid_df.loc[:, 'position'].apply(
        lambda x: x.split(':')[1] if ':' in x else x).apply(
        lambda x: x[11:-1] if 'complement' in x else x).apply(
        lambda x: x[5:-1] if 'join' in x else x).apply(
        lambda x: x.split('.')[-1]).apply(
        lambda x: x[1:] if '>' in x else x)
    gff_plasmid_df.loc[:, 'strand'] = kff_plasmid_df.loc[:, 'position'].apply(
        lambda x: '-' if 'complement' in x else '+')
    gff_plasmid_df.loc[:, 'attribute'] = kff_plasmid_df.loc[:, 'genename'].str.cat(
        kff_plasmid_df.loc[:, 'name'], ';', na_rep='').str.cat(
        kff_plasmid_df.loc[:, 'KO'], ';', na_rep='').str.cat(
        kff_plasmid_df.loc[:, 'description'], ';', na_rep='')

    gff_df = pd.concat([gff_df, gff_plasmid_df])
    gff_df.loc[:, 'source'] = kff
    gff_df.loc[:, 'score'] = '-'
    gff_df.loc[:, 'frame'] = gff_df.loc[:, 'start'].apply(lambda x: int(x) % 3)
    if output is None:
        out = sys.stdout
    else:
        out = open(output, 'w')
    gff_df.to_csv(out, sep='\t', header=False, index=False)
    out.close()


if __name__ == '__main__':
    parser, args = parser_setting()

    main(**vars(args))
