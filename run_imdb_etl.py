import argparse
import logging

import yaml
from lib.etl import ETL

LOGGER = logging.getLogger(__name__)

# Create argument parser
parser = argparse.ArgumentParser()
target = parser.add_mutually_exclusive_group(required=True)
target.add_argument('--all', '-a', action='store_true', default=False)
target.add_argument('--types', '-t', nargs='*')
parser.add_argument('--config', '-c', default='config')
parser.add_argument('--use-cache', action='store_true', default=False)

# Parse args
args = parser.parse_args()

# Generate target_type type list
type_list = yaml.safe_load(open(f'{args.config}/etl.yaml'))['definitions'].keys()
target_types = type_list if args.all else args.types

# For each target_type type, run the ETL process
for target_type in target_types:
    assert target_type in type_list, f'Provided types must be in {type_list}'
    etl = ETL(target_type)
    etl.run(use_cache=args.use_cache)

LOGGER.info('Done.')
