#!/bin/env/python3
# -*- coding: utf-8 -*-
# Author: ynakamura

import sys

from argparse import ArgumentParser


def parser_setting():
    parser = ArgumentParser(
        prog='match.py',
        description='Match Genome and Pathway.')
    parser.add_argument(
        'genome',
        action='store', type=str,
        help='List of multiple adjacent genes on genome.')
    parser.add_argument(
        'pathway',
        action='store', type=str,
        help='List of multiple adjacent reactions on pathway.')
    parser.add_argument(
        '-o', '--output',
        action='store', type=str,
        help='Output file.')
    parser.add_argument(
        '-d', '--digit',
        action='store', type=int,
        default=3, choices=[1, 2, 3, 4],
        help='Digit of EC number.')
    parser.add_argument(
        '-t', '--threshold',
        nargs=2, metavar=('DIGIT', 'NUMBER'),
        action='store', type=int,
        default=[3, 1],
        help='Match number threshold.')
    args = parser.parse_args()
    return (parser, args)


def load(file_name):
    data = list()
    with open(file_name, 'r') as file:
        for line in file:
            temp = line.rstrip('\n').split('\t')
            data.append({
                'enzymes': temp[0].split('/'),
                'id': temp[1],
                'line': line})
    return data


def match(enzymes1, enzymes2, digit):
    score = list()
    matched = list()
    value = 0
    for i in range(0, digit):
        matched.append(list())
        e1 = [x.split('.')[: i + 1] for x in enzymes1]
        e2 = [x.split('.')[: i + 1] for x in enzymes2]
        for n, enzyme in enumerate(e1):
            if enzyme in e2:
                value += 1
                e2.remove(enzyme)
                matched[i].append('.'.join(enzyme))
        score.append(value)
        value = 0
    matched = ['/'.join(x) if len(x) > 0 else '-' for x in matched]
    return score, matched


def main(genome, pathway, output, digit, threshold):
    g_data = load(genome)
    p_data = load(pathway)

    if threshold[1] > min(len(g_data[0]['enzymes']),
                          len(p_data[0]['enzymes'])):
        message = ('Score threshold must be smaller than '
                   'gene and reaction window size.')
        raise ValueError(message)

    if output is None:
        out = sys.stdout
    else:
        out = open(output, 'w')

    for g in g_data:
        for p in p_data:
            # print(g['enzymes'], p['enzymes'])
            score, matched = match(g['enzymes'], p['enzymes'], digit)
            if score[threshold[0] - 1] >= threshold[1]:
                out.write(
                    '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(
                        g['id'], '/'.join(g['enzymes']),
                        p['id'], '/'.join(p['enzymes']),
                        '\t'.join([str(x) for x in score]),
                        '\t'.join(matched)))
    out.close()


if __name__ == '__main__':
    parser, args = parser_setting()

    main(**vars(args))
