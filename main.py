import argparse
import json
from algorithm import Algorithm
from benchmark import Benchmark
from miner import GPUMiner
from stratum import Stratum

# Global Variables
miners = []
shares = {}

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
                    required=False,
                    default='kawpow',
                    type=str,
                    help="[kawpow]")

args = parser.parse_args()


# Check algorithm
if Algorithm.is_valid(args.algo) is False:
    print(f'Invalid algo [{args.algo}] !')
    exit(1)


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
    print(f'Error: {error}')
    exit(1)


# Start Stratum / Network
stratum = Stratum(args.algo, args.host, args.port)
if stratum.load_jobs() is False:
    exit(1)

# Run benchmark
for miner in miners:
    bench = Benchmark(miner, stratum)
    stratum.start(miner)
    bench.run()
    stratum.disconnect_all()
    stratum.close()
    shares[miner.get_name()] = miner.get_shares()
    break

for miner in miners:
    print(f'Miner {miner.get_name()} found {miner.get_shares()} shares.')

print('Benchmark finished!')
