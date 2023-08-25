import sys
import argparse
import json
import os
import logging

from algorithm import Algorithm
from benchmark import Benchmark
from miner import GPUMiner
from stratum import Stratum
from share import Share

# Global Variables
miners = []
shares = Share()

log_level = logging.INFO
logging.basicConfig(
    format='[%(levelname)s][%(asctime)s]: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    encoding='utf-8',
    level=log_level)

# Arguments
parser = argparse.ArgumentParser(description='')
parser.add_argument('--host',
                    type=str,
                    default='127.0.0.1',
                    help="")
parser.add_argument('--port',
                    type=str,
                    default='7878',
                    help="")
parser.add_argument('--algo',
                    default='kawpow',
                    type=str,
                    help="[kawpow, autolykos2]")
parser.add_argument('--mining_duration',
                    default=20,
                    type=int,
                    help="Minutes")
parser.add_argument('--device_type',
                    default='both',
                    type=str,
                    help="[both, amd, nvidia]")

args = parser.parse_args()


logging.info('BENCHMARK GPU MINING')
logging.info(f'\tHost: {args.host}')
logging.info(f'\tPort: {args.port}')
logging.info(f'\tAlgorithm: {args.algo}')
logging.info(f'\tDuration: {args.mining_duration}min')


# Check algorithm
if Algorithm.is_valid(args.algo) is False:
    sys.exit(f'Invalid algo [{args.algo}] !')

try:
    with open('miners.json') as fd:
        miner_json = json.load(fd)

        # Check mandatory keys
        if 'miners' not in miner_json:
            sys.exit('Bad config file, missing [miners]')
        if 'wallets' not in miner_json:
            sys.exit('Bad config file, missing [wallets]')
        if 'miner_device_available' not in miner_json:
            sys.exit('Bad config file, missing [miner_device_available]')
        if 'miner_algo' not in miner_json:
            sys.exit('Bad config file, missing [miner_algo]')

        # Loads all miners from config file
        for miner in miner_json['miners']:
            gpu_miner = GPUMiner(miner, miner_json['wallets'][args.algo])
            gpu_miner_name = gpu_miner.get_name()

            # Check if the miner software is compatible with device in rig.
            device_in_amd = True if gpu_miner_name in miner_json['miner_device_available']['amd'] else False
            device_in_nvidia = True if gpu_miner_name in miner_json['miner_device_available']['nvidia'] else False
            if args.device_type == 'both':
                if device_in_amd is False or device_in_nvidia is False:
                    continue
            elif args.device_type == 'amd':
                if device_in_amd is False:
                    continue
            elif args.device_type == 'nvidia':
                if device_in_nvidia is False:
                    continue

            # Check if the miner software is compatible with algorithm

            device_in_algo = True if gpu_miner_name in miner_json['miner_algo'][args.algo] else False
            if device_in_algo is False:
                continue

            if gpu_miner.download() is True:
                miners.append(gpu_miner)
            else:
                logging.warning(f'Skip miner {gpu_miner.get_name()}!')
except Exception as error:
    sys.exit(f'Stop benchmark ! {error}')


# Start Stratum / Network
stratum_client = Stratum(args.algo, args.host, args.port)
if stratum_client.load_jobs() is False:
    sys.exit('Jobs not found !')

result_output = os.path.join('results')
if os.path.exists(result_output) is False:
    os.makedirs(result_output)

# Run benchmark
for miner in miners:
    shares.add_miner(miner.get_name())
    bench = Benchmark(args.mining_duration, miner, stratum_client)
    stratum_client.start(miner, shares)
    bench.run(args.algo)
    stratum_client.close()

shares.draw_graph()

with open(os.path.join('results', 'result_benchmark.log'), 'w') as fd:
    for miner in miners:
        logging.info(f'Miner {miner.get_name()} found {miner.get_shares()} shares.')
        fd.write(f'Miner {miner.get_name()} found {miner.get_shares()} shares.\n')

logging.info('Benchmark finished!')
