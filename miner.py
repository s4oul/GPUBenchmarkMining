import datetime
import os
import zipfile
import psutil
import subprocess
import urllib.request
from stratum import Stratum


class GPUMiner:

    def __init__(self, json_data: dict):
        self.share = 0
        self.process = None
        self.name = json_data['name']
        self.version = json_data['version']
        self.url = json_data['url']
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
                self.folder_extracted = os.path.join(self.folder_extracted)

    def get_name(self) -> str:
        return self.name

    def get_url(self) -> str:
        return self.url

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
            folder_miner = os.path.join('miners', f'{self.name}_{self.version}')
            if os.path.exists(folder_miner):
                print(f'Folder {folder_miner} already exist.')
                return True

            os.makedirs(folder_miner)

            print(f'Downloading {self.name}')
            print(f'\tVersion: {self.version}')
            print(f'\tFolder: {self.get_folder_extracted()}')
            print(f'\tURL: {self.url}')
            if os.name == 'nt':
                if self.name != 'pickminer':
                    miner_package = os.path.join(folder_miner, 'miner.zip')
                else:
                    miner_package = os.path.join(folder_miner, 'setup.exe')
            output_file, _ = urllib.request.urlretrieve(self.url, miner_package)
            print(f'\tOutput: {output_file}')
            if os.name == 'nt':
                if self.name != 'pickminer':
                    with zipfile.ZipFile(miner_package, 'r') as zip_ref:
                        zip_ref.extractall(os.path.join(folder_miner, 'extracted'))
                else:
                    cmd = f'{output_file} /SILENT'
                    subprocess.check_output(cmd, shell=True)
        except Exception as error:
            print(f'Error: {error}')
            return False
        return True

    def run(self, stratum: Stratum, show_stdout: bool):

        exe = f'{self.exe}{".exe" if os.name == "nt" else ""}'
        parameters = self.get_args()\
            .replace('<HOST>', stratum.get_host())\
            .replace('<PORT>', str(stratum.get_port()))

        cmd = f'cd {self.get_folder_extracted()} && {exe} {parameters}'

        self.process = subprocess.Popen(
            cmd,
            stdout=None if show_stdout is True else subprocess.PIPE,
            shell=True)

    def kill(self):
        system_process = psutil.Process(self.process.pid)
        for proc in system_process.children(recursive=True):
            proc.kill()
        system_process.kill()

    def increase_share(self):
        self.share += 1
