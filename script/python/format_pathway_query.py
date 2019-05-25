#!/bin/env/python3
# -*- coding: utf-8 -*-
# Author: ynakamura

import itertools
import sys

from argparse import ArgumentParser
from urllib import request


def parser_setting():
    parser = ArgumentParser(
        prog='format_pathway_query.py',
        description=('Format pathway query file from '
                     'module - enzyme list file.'))
    parser.add_argument(
        '-i', '--module_enzyme',
        action='store', type=str,
        help=('Module - enzyme list file. '
              'If not selected, get from KEGG API.'))
    parser.add_argument(
        '-o', '--output',
        action='store', type=str,
        help='Output file.')
    parser.add_argument(
        '-l', '--length',
        action='store', type=int,
        help='Reaction length.')
    args = parser.parse_args()
    return (parser, args)


def main(module_enzyme, output, length):
    if module_enzyme is None:
        file = request.urlopen('http://rest.kegg.jp/link/module/ec')
    else:
        file = open(module_enzyme, 'r')

    dictionary = dict()
    for line in file:
        temp = line.decode('utf-8').rstrip('\n').split('\t')
        if temp[1] not in dictionary:
            dictionary[temp[1]] = list()
        dictionary[temp[1]].append(temp[0].split(':')[1])
    file.close()

    if output is None:
        out = sys.stdout
    else:
        out = open(output, 'w')

    result = list()
    for i in dictionary:
        if length is None:
            result.append(['/'.join(dictionary[i]), i])
        else:
            if len(dictionary[i]) >= length:
                for c in itertools.combinations(dictionary[i], length):
                    result.append(['/'.join(c), i])

    out.write(''.join([
        '{0}\t{1}\n'.format(i[0], i[1])
        for i in result]))
    out.close()


if __name__ == '__main__':
    parser, args = parser_setting()

    main(**vars(args))
