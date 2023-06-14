import threading
import time

from miner import GPUMiner
from stratum import Stratum


class Benchmark:

    def __init__(self, miner: GPUMiner, stratum: Stratum):
        self.time_bench = 2 * 60
        self.miner = miner
        self.thread = None
        self.stratum = stratum

    def __async_run(self):
        self.miner.run()
        time.sleep(self.time_bench)
        self.miner.kill()

    def run(self):
        print(f'Running miner [{self.miner.get_name()}]')
        self.thread = threading.Thread(target=self.__async_run, args=())
        self.thread.start()
        self.thread.join()
