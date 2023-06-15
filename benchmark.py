import threading
import time

from miner import GPUMiner
from stratum import Stratum


class Benchmark:

    def __init__(self, mining_duration: int, miner: GPUMiner, stratum_client: Stratum):
        self.duration_bench = mining_duration * 60
        self.miner = miner
        self.thread = None
        self.stratum_client = stratum_client

    def __async_run(self, show_stdout: bool):
        self.miner.run(self.stratum_client, show_stdout)
        timing = self.duration_bench
        while self.miner.is_running() is True and timing > 0:
            time.sleep(1)
            timing -= 1
        self.miner.kill()

    def run(self, show_stdout: bool):
        print(f'Running miner [{self.miner.get_name()}]')
        self.thread = threading.Thread(target=self.__async_run, args=[show_stdout])
        self.thread.start()
        self.thread.join()
