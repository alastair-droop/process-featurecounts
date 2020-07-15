#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sys import stdin, stderr, exit
import argparse
import re
import logging
from os.path import abspath, join, dirname

# Get the version:
version = {'__version__':'1.0.1-standalone'}

# Handle broken pipes:
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL) 

# A function to quit with an error:
def error(msg, exit_code=1):
    logging.error(msg)
    exit(exit_code)

def main():
    # Set the defaults:
    defaults = {'verbosity':'warning', 'id_regex':'^([^.]+)\.\d+(.*)$', 'sample_regex':'^(.*)$', 'id_col':1, 'skip_cols':'2,3,4,5,6'}
    
    # Create thew CLI:
    parser = argparse.ArgumentParser(description='Reformat featureCounts output files')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s {0}'.format(version['__version__']))
    parser.add_argument('-v', '--verbose', dest='verbosity', default=defaults['verbosity'], choices=['error', 'warning', 'info', 'debug'], help='Set logging level (default {verbosity})'.format(**defaults))
    parser.add_argument('-r', '--id-regex', dest='id_regex', metavar='<re>', default=defaults['id_regex'], help='row ID regular expression to use (default "{id_regex}")'.format(**defaults))
    parser.add_argument('-s', '--sample-regex', dest='sample_regex', metavar='<re>',default=defaults['sample_regex'], help='sample name regular expression to use (default "{sample_regex}")'.format(**defaults))
    parser.add_argument('-e', '--include-header', dest='include_headers', action='store_true', default=False, help='include header comments')
    parser.add_argument('-i', '--id-col', dest='id_col', metavar='<n>',type=int, default=defaults['id_col'], help='gene ID column (default {id_col})'.format(**defaults))
    parser.add_argument('-k', '--skip', dest='skip_cols', metavar='<n,[n]>',default=defaults['skip_cols'], help='comma-separated columns to skip (default {skip_cols})'.format(**defaults))
    parser.add_argument(dest='input_file', metavar='<file>', type=argparse.FileType('rt'), default=stdin, help='input featureCounts file')
    args = parser.parse_args()
    
    # Set up the logging
    logging.basicConfig(format='%(levelname)s: %(message)s', level=args.verbosity.upper())
    
    # Build the regexes:
    try:
        logging.debug('building row regular expression as "{}"'.format(args.id_regex))
        id_re = re.compile(args.id_regex)
    except: error('failed to build ID regular expression')
    try:
        logging.debug('building sample ID regular expression as "{}"'.format(args.sample_regex))
        sample_re = re.compile(args.sample_regex)
    except: error('failed to build sample regular expression')
    
    # Sort the columns:
    try:
        if args.skip_cols == 'n':
            skip_cols = []
        else:
            skip_cols = [int(i) - 1 for i in args.skip_cols.split(',')]
        logging.info('skipping columns: {}'.format(', '.join([str(i + 1) for i in skip_cols])))
    except: error('invalid skip column definition "{}"'.format(args.skip_cols))
    id_col = args.id_col - 1
    logging.info('id column: {}'.format(id_col + 1))
    if id_col in skip_cols: error('can not skip ID column')
    
    # Read through the header lines:
    logging.debug('reading header comments')
    while True:
        line = args.input_file.readline().strip()
        if not line.startswith('#'): break
        if args.include_headers is True: print(line)

    # Process the headers:
    input_headers = line.split('\t')
    output_headers = ['' for i in range(len(input_headers))]
    col_order = []
    for i in range(len(input_headers)):
        col_type = 'sample'        
        if i == id_col:
            col_type = 'id'
            output_headers[i] = 'id'
            col_order.append(i)
        if i in skip_cols:
            col_type = 'skip'
        if col_type == 'sample':
            col_order.append(i)
            match = sample_re.match(input_headers[i])
            if match is None:
                logging.warning('sample header "{}" does not match sample regular expression'.format(input_headers[i]))
                output_headers[i] = input_headers[i]
            else:
                output_headers[i] = ''.join(match.groups())
            logging.info('column header {:2} ({:6}): {} -> {}'.format(i + 1, col_type, input_headers[i], output_headers[i]))
        else: logging.debug('column header {:2} ({:6}): {}'.format(i + 1, col_type, input_headers[i]))
    # Print out the headers:
    print('\t'.join([output_headers[i] for i in col_order]))
    
    # Process the remaining (data) lines:
    for line in args.input_file.readlines():
        line_data = line.strip().split('\t')
        line_data = [line_data[i] for i in col_order]
        match = id_re.match(line_data[id_col])
        if match is None:
            logging.warning('ID {} does not match regular expression'.format(line_data[id_col]))
        else:
            new_id = ''.join(match.groups())
            logging.debug('row ID {} -> {}'.format(line_data[id_col], new_id))
            line_data[id_col] = new_id
        print('\t'.join(line_data))

if __name__ == "__main__":
    main()
