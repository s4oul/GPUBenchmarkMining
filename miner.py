import datetime
import os
import zipfile
import psutil
import subprocess
import urllib.request

from stratum import Stratum


class GPUMiner:

    def __init__(self, json_data: dict, wallet: str):
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
        self.fd = None

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
            print(f'Downloading {self.get_name()}')
            print(f'\tVersion: {self.get_version()}')
            print(f'\tFolder: {self.get_folder_extracted()}')

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
            print(f'\tURL: {url}')

            folder_miner = os.path.join('miners', f'{self.name}_{self.version}')
            if os.path.exists(folder_miner):
                print(f'Folder {folder_miner} already exist.')
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
            print(f'\tOutput: {output_file}')
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
            print(f'Error: {error}')
            return False
        return True

    def __get_fd(self, show_stdout: bool):
        local_fd = subprocess.PIPE

        if show_stdout is False:
            log_file = os.path.join('results', f'{self.name}.log')
            print(f'{self.name} is writing LOG => {log_file}.')
            self.fd = open(log_file, 'w')
            local_fd = self.fd

        return local_fd

    def run(self, stratum: Stratum, algo_name: str, show_stdout: bool):
        exe = f'{"./" if os.name != "nt" else ""}{self.exe}{".exe" if os.name == "nt" else ""}'

        params_args = self.get_args()
        if '<HOST>' not in params_args:
            print(f'<HOST> not found !')
            return
        if '<PORT>' not in params_args:
            print(f'<PORT> not found !')
            return
        if '<WALLET>' not in params_args:
            print(f'<WALLET> not found !')
            return

        parameters = self.get_args() \
            .replace('<HOST>', stratum.get_host()) \
            .replace('<PORT>', str(stratum.get_port()))\
            .replace('<WALLET>', self.get_wallet())

        cmd_algo = self.get_algos(algo_name)

        cmd = f'cd {self.get_folder_extracted()} && {exe} {cmd_algo} {parameters}'

        self.running = True
        local_fd = self.__get_fd(show_stdout)
        self.process = subprocess.Popen(
            cmd,
            stdout=local_fd,
            stderr=local_fd,
            shell=True)

    def kill(self):
        try:
            self.running = False
            system_process = psutil.Process(self.process.pid)
            for proc in system_process.children(recursive=True):
                proc.kill()
            system_process.kill()
            try:
                if self.fd is not None:
                    self.fd.close()
            except Exception:
                # I dont know why Windows have an error here.
                pass
        except psutil.NoSuchProcess:
            pass

    def increase_share(self):
        self.share += 1
