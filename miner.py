import datetime
import os
import zipfile
import psutil
import subprocess
import urllib.request

from stratum import Stratum


class GPUMiner:

    def __init__(self, json_data: dict):
        self.running = False
        self.share = 0
        self.process = None
        self.name = json_data['name']
        self.version = json_data['version']
        self.url_win = json_data['url_win']
        self.url_linux = json_data['url_linux']
        self.exe = json_data['exe']
        self.args = json_data['args']
        self.folder_extracted = os.path.join('miners', f'{self.name}_{self.version}', 'extracted')

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

    def get_args(self) -> str:
        return self.args

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
            print(f'\tURL: {self.get_url()}')

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

            output_file, _ = urllib.request.urlretrieve(self.get_url(), miner_package)
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

    def run(self, stratum: Stratum, show_stdout: bool):
        exe = f'{"./" if os.name != "nt" else ""}{self.exe}{".exe" if os.name == "nt" else ""}'
        parameters = self.get_args() \
            .replace('<HOST>', stratum.get_host()) \
            .replace('<PORT>', str(stratum.get_port()))

        cmd = f'cd {self.get_folder_extracted()} && {exe} {parameters}'

        self.running = True

        fd = None if show_stdout is True else subprocess.PIPE

        self.process = subprocess.Popen(
            cmd,
            stdout=fd,
            stderr=fd,
            shell=True)

    def kill(self):
        try:
            self.running = False
            system_process = psutil.Process(self.process.pid)
            for proc in system_process.children(recursive=True):
                proc.kill()
            system_process.kill()
        except psutil.NoSuchProcess:
            pass

    def increase_share(self):
        self.share += 1