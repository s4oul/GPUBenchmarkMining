import sys
import argparse
import json
from algorithm import Algorithm
from benchmark import Benchmark
from miner import GPUMiner
from stratum import Stratum
from share import Share

# Global Variables
miners = []
shares = Share()

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
                    help="[kawpow]")
parser.add_argument('--mining_duration',
                    default=20,
                    type=int,
                    help="Minutes")

parser.add_argument('--show_mining_output', action='store_false')
parser.add_argument('--no_show_mining_output', dest='show_mining_output', action='store_false')
parser.set_defaults(feature=True)

args = parser.parse_args()


# Check algorithm
if Algorithm.is_valid(args.algo) is False:
    sys.exit(f'Invalid algo [{args.algo}] !')

try:
    with open('miners.json') as fd:
        miner_json = json.load(fd)
        # Check mandatory keys
        if 'miners' not in miner_json:
            print('Bad config file')
        # Loads all miners from config file
        for miner in miner_json['miners']:
            gpu_miner = GPUMiner(miner)
            if gpu_miner.download() is True:
                miners.append(gpu_miner)
            else:
                print(f'Skip miner {gpu_miner.get_name()}!')
except Exception as error:
    sys.exit(f'Stop benchmark ! {error}')

# Start Stratum / Network
stratum_client = Stratum(args.algo, args.host, args.port)
if stratum_client.load_jobs() is False:
    sys.exit('Jobs not found !')

# Run benchmark
for miner in miners:
    shares.add_miner(miner.get_name())
    bench = Benchmark(args.mining_duration, miner, stratum_client)
    stratum_client.start(miner, shares)
    bench.run(args.show_mining_output)
    stratum_client.disconnect_all()
    stratum_client.close()

shares.draw_graph()

with open('result_benchmark', 'w') as fd:
    for miner in miners:
        print(f'Miner {miner.get_name()} found {miner.get_shares()} shares.')
        fd.write(f'Miner {miner.get_name()} found {miner.get_shares()} shares.')

print('Benchmark finished!')
