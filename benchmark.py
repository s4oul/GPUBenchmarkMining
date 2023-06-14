import threading
import time

from miner import GPUMiner
from stratum import Stratum


class Benchmark:

    def __init__(self, mining_duration: int, miner: GPUMiner, stratum: Stratum):
        self.duration_bench = 10 # mining_duration * 60
        self.miner = miner
        self.thread = None
        self.stratum = stratum

    def __async_run(self, show_stdout: bool):
        self.miner.run(self.stratum, show_stdout)
        time.sleep(self.duration_bench)
        self.miner.kill()

    def run(self, show_stdout: bool):
        print(f'Running miner [{self.miner.get_name()}]')
        self.thread = threading.Thread(target=self.__async_run, args=[show_stdout])
        self.thread.start()
        self.thread.join()
