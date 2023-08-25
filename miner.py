import datetime
import logging
import os
import zipfile
import psutil
import subprocess
import urllib.request
import logging

from stratum import Stratum
from statistical import Statistical


class GPUMiner:

    def __init__(self, json_data: dict, wallet: str):
        self.stats = Statistical()
        self.running = False
        self.share = 0
        self.process = None
        self.name = json_data['name']
        self.version = json_data['version']
        self.url_win = json_data['url_win']
        self.url_linux = json_data['url_linux']
        self.exe = json_data['exe']
        self.algos = json_data['algos']
        self.args = json_data['args']
        self.wallet = wallet
        self.folder_extracted = os.path.join('miners', f'{self.name}_{self.version}', 'extracted')
        self.fd_log = None

        if self.name == 'srbminer':
            self.folder_extracted = os.path.join(self.folder_extracted,
                                                 f'SRBMiner-Multi-{self.version.replace(".", "-")}')
        elif self.name == 'bzminer':
            self.folder_extracted = os.path.join(self.folder_extracted,
                                                 f'bzminer_v{self.version}_{"windows" if os.name == "nt" else "linux"}')
        elif self.name == 'pickminer':
            if os.name == 'nt':
                self.folder_extracted = os.path.join(os.environ["ProgramFiles(x86)"], 'pickminer')
            else:
                self.folder_extracted = os.path.join(self.folder_extracted,
                                                     f'pickminer_{self.version}')
        elif self.name == 'teamredminer':
            self.folder_extracted = os.path.join(self.folder_extracted,
                                                 f'teamredminer-v{self.version}-{"win" if os.name == "nt" else "linux"}')
        elif self.name == 'lolminer':
            self.folder_extracted = os.path.join(self.folder_extracted,
                                                 f'{self.version}')
        elif self.name == "nbminer":
            self.folder_extracted = os.path.join(self.folder_extracted,
                                                 f'NBMiner_{"Win" if os.name == "nt" else "Linux"}')

    def is_running(self) -> bool:
        try:
            psutil.Process(self.process.pid)
        except psutil.NoSuchProcess:
            self.running = False

        return self.running

    def get_name(self) -> str:
        return self.name

    def get_url(self) -> str:
        return self.url_win if os.name == 'nt' else self.url_linux

    def get_algos(self, algo_name) -> str:
        return self.algos[algo_name]

    def get_args(self) -> str:
        return self.args

    def get_wallet(self) -> str:
        return self.wallet

    def get_version(self) -> str:
        return self.version

    def get_folder_extracted(self) -> str:
        return self.folder_extracted

    def get_shares(self) -> int:
        return self.share

    def download(self) -> bool:
        try:
            logging.info(f'Downloading {self.get_name()}')
            logging.info(f'\tVersion: {self.get_version()}')
            logging.info(f'\tFolder: {self.get_folder_extracted()}')

            url = self.get_url()
            if self.get_name() == 'srbminer':
                url = url\
                    .replace('download/<VERSION>', f'download/{self.get_version()}')\
                    .replace('<VERSION>', self.get_version().replace('.', '_'))
            elif self.get_name() == 'gminer':
                url = url\
                    .replace('download/<VERSION>', f'download/{self.get_version()}')\
                    .replace('<VERSION>', self.get_version().replace('.', '_'))
            else:
                url = url.replace('<VERSION>', self.get_version())
            logging.info(f'\tURL: {url}')

            folder_miner = os.path.join('miners', f'{self.name}_{self.version}')
            if os.path.exists(folder_miner):
                logging.info(f'Folder {folder_miner} already exist.')
                return True

            os.makedirs(folder_miner)
            miner_filename = 'miner.' + ('zip' if os.name == 'nt' else 'gz')
            miner_package = os.path.join(folder_miner, miner_filename)

            # pickminer use a setup.exe to install the software.
            if os.name == 'nt':
                if self.name == 'pickminer':
                    miner_package = os.path.join(folder_miner, 'setup.exe')

            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context

            output_file, _ = urllib.request.urlretrieve(url, miner_package)
            logging.info(f'\tOutput: {output_file}')
            if os.name == 'nt':
                if self.name == 'pickminer':
                    cmd = f'{output_file} /SILENT'
                    subprocess.check_output(cmd, shell=True)
                else:
                    with zipfile.ZipFile(miner_package, 'r') as zip_ref:
                        zip_ref.extractall(os.path.join(folder_miner, 'extracted'))
            else:
                import tarfile
                file = tarfile.open(output_file)
                file.extractall(os.path.join(folder_miner, 'extracted'))
                file.close()

        except Exception as error:
            logging.error(f'{error}')
            return False
        return True

    def __set_fd_log(self, algo_name: str):
        log_file = os.path.join('results', f'{self.name}_{algo_name}.log')
        logging.info(f'{self.name} is writing LOG => {log_file}.')
        self.fd_log = open(log_file, 'w')

    def run(self, stratum: Stratum, algo_name: str):
        exe = f'{"./" if os.name != "nt" else ""}{self.exe}{".exe" if os.name == "nt" else ""}'

        params_args = self.get_args()
        if '<HOST>' not in params_args:
            logging.error(f'<HOST> not found !')
            return
        if '<PORT>' not in params_args:
            logging.error(f'<PORT> not found !')
            return
        if '<WALLET>' not in params_args:
            logging.error(f'<WALLET> not found !')
            return

        parameters = self.get_args() \
            .replace('<HOST>', stratum.get_host()) \
            .replace('<PORT>', str(stratum.get_port()))\
            .replace('<WALLET>', self.get_wallet())

        if self.name == 't_rex':
            parameters = parameters.replace('stratum', 'stratum2')

        cmd_algo = self.get_algos(algo_name)

        cmd_exe = f'{exe} {cmd_algo} {parameters}'
        cmd = f'cd {self.get_folder_extracted()} && {cmd_exe}'

        logging.info(cmd_exe)

        self.running = True
        self.__set_fd_log(algo_name)
        self.process = subprocess.Popen(
            cmd,
            stdout=self.fd_log,
            stderr=self.fd_log,
            shell=True)

    def kill(self):
        try:
            self.running = False
            system_process = psutil.Process(self.process.pid)
            for proc in system_process.children(recursive=True):
                proc.kill()
            system_process.kill()
            try:
                if self.fd_log is not None:
                    self.fd_log.close()
            except Exception:
                # I dont know why Windows have an error here.
                pass
        except psutil.NoSuchProcess:
            pass

    def increase_share(self):
        self.share += 1
