import os.path
import threading
import time

from miner import GPUMiner
from stratum import Stratum


class Benchmark:

    def __init__(self, mining_duration: int, miner: GPUMiner, stratum: Stratum):
        self.duration_bench = mining_duration * 60
        self.miner = miner
        self.thread = None
        self.stratum = stratum

    def __async_run(self, algo_name: str, show_stdout: bool):
        self.miner.run(self.stratum, algo_name, show_stdout)
        timeout = self.duration_bench
        while self.miner.is_running() is True and timeout > 0:
            time.sleep(1)
            timeout -= 1
        self.miner.kill()

    def run(self, algo_name: str, show_stdout: bool):
        print(f'Running miner [{self.miner.get_name()}]')

        result_output = os.path.join('results')
        if os.path.exists(result_output) is False:
            os.makedirs(result_output)

        self.thread = threading.Thread(target=self.__async_run, args=[algo_name, show_stdout])
        self.thread.start()
        self.thread.join()
