import datetime
import os.path
import threading
import socket
import json
import time

from algorithm import Algorithm
from share import Share


class Stratum:

    def __init__(self, algo: str, host: str, port: int):
        self.algo = algo
        self.host = str(host)
        self.port = int(port)
        self.server = None
        self.running = False
        self.clients = list()
        self.thread = None
        self.thread_recv = None
        self.thread_notify = None
        self.notifies = []
        self.jobs = None
        self.miner = None
        self.shares = None
        self.chrono_start = None

    def is_running(self) -> bool:
        if len(self.clients) == 0:
            self.running = False
        return self.running

    def get_host(self) -> str:
        return self.host

    def get_port(self) -> int:
        return self.port

    def start(self, miner, shares: Share):
        print(f'Start pool on "{self.host}:{self.port}" !')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        self.running = True
        self.miner = miner
        self.shares = shares
        self.__listen()

    def __listen(self):
        self.thread = threading.Thread(target=self.__accept, args=())
        self.thread.start()

    def __accept(self):
        client, addr = self.server.accept()
        print(f'New Client!')
        self.clients.append(client)
        self.thread_recv = threading.Thread(target=self.__loop_recv_msg)
        self.thread_recv.start()

    def send(self, client, msg: str):
        try:
            msg_print = msg.replace("\n", "")
            print(f'[{datetime.datetime.now()}] ==> {msg_print}')
            if '\n' not in msg:
                msg = f'{msg}\n'
            client.sendall(bytes(msg, encoding="utf-8"))
        except Exception as error:
            print(f'ERROR: {error}.')
            self.running = False

    def close(self):
        self.disconnect_all()
        self.server.close()
        self.running = False
        # waiting thread __loop_notify terminated
        time.sleep(1)

    def disconnect_all(self):
        for client in self.clients:
            client.close()
        self.clients = list()

    def __loop_recv_msg(self):
        self.chrono_start = datetime.datetime.now()
        try:
            while self.is_running() is True:
                for client in self.clients:
                    raw = client.recv(2040)
                    if not raw:
                        return
                    messages = raw.decode("utf-8").split('\n')
                    for msg in messages:
                        if not msg:
                            continue
                        data = json.loads(msg)
                        print(f'[{datetime.datetime.now()}] <== {data}')
                        if 'method' in data:
                            self.__dispatch_method(client, data)
        except ConnectionAbortedError:
            print(f'Client has disconnected!')
            self.running = False
        except Exception as error:
            print(f'Error: {error}')
            self.running = False

    def __loop_notify(self, client: socket):
        timeout = int(self.jobs['delay']) * 2
        for i in range(0, len(self.notifies)):
            if self.is_running() is False:
                return
            notify = self.notifies[i]
            params = str(notify["params"])\
                .replace("'", '"')\
                .replace('True', 'true')\
                .replace('False', 'false')
            msg = '{' \
                  '"id": null, '\
                  '"method": "mining.notify", '\
                  f'"params": {params}'\
                  '}'
            self.send(client, msg)
            for cnt in range(0, timeout):
                if self.is_running() is False:
                    return
                time.sleep(0.5)

    def load_jobs(self):
        try:
            filename = os.path.join('jobs', f'{self.algo}.json')
            with open(filename) as fd:
                self.jobs = json.load(fd)

            for notify in self.jobs['notify']:
                notify['id'] = 0
                self.notifies.append(notify)
        except Exception as error:
            print(f'Error: {error}')
            return False
        return True

    def __dispatch_method(self, client, data: dict):
        try:
            if self.algo == Algorithm.KAWPOW:
                self.__dispatch_kawpow(client, data)
            elif self.algo == Algorithm.AUTOLYKOS2:
                self.__dispatch_autolykos_v2(client, data)
        except Exception as error:
            print(f'Error: {error}')

    def __dispatch_kawpow(self, client, data: dict):
        method = data['method']
        if 'mining.subscribe' == method:
            request_id = data['id']
            extra_nonce = self.jobs['extra_nonce']
            result = '{'\
                     f'"id":{request_id}, ' \
                     f'"result":[null, "{extra_nonce}"], ' \
                     f'"error":null' \
                     '}'
            self.send(client, result)
        elif 'mining.authorize' == method:
            id = data['id']
            result = '{'\
                     f'"id":{id},' \
                     f'"result":true,' \
                     f'"error":null'\
                     '}'
            self.send(client, result)

            target = self.jobs['set_target']
            result = '{'\
                     '"id":null,' \
                     '"method":"mining.set_target",' \
                     f'"params":["{target}"]'\
                     '}'
            self.send(client, result)

            self.thread_notify = threading.Thread(target=self.__loop_notify, args=[client])
            self.thread_notify.start()
        elif 'mining.submit' == method:
            now = datetime.datetime.now()
            elapsed = now - self.chrono_start
            self.miner.increase_share()
            count = self.miner.get_shares()
            print(f'{datetime.datetime.now()} shares count [{count}], time elapsed [{elapsed}].')
            self.shares.add_share(self.miner.get_name(),
                                  int(elapsed.total_seconds()),
                                  data['params'][2])
            response = '{"id":-1,"result":true,"error":null}'
            response = response.replace('-1', str(data["id"]))
            self.send(client, response)
        elif 'mining.extranonce.subscribe' == method:
            pass
        elif 'eth_submitHashrate' == method:
            pass
        else:
            print(f'Unknow method [{method}]!')

    def __dispatch_autolykos_v2(self, client, data: dict):
        method = data['method']
        if 'mining.subscribe' == method:
            request_id = data['id']
            extra_nonce = self.jobs['extra_nonce']
            result = '{'\
                     f'"id":{request_id}, ' \
                     f'"result":[null, "{extra_nonce}", {int(8 - len(extra_nonce) / 2)}], ' \
                     f'"error":null' \
                     '}'
            self.send(client, result)
        elif 'mining.authorize' == method:
            id = data['id']
            result = '{'\
                     f'"id":{id},' \
                     f'"result":true,' \
                     f'"error":null'\
                     '}'
            self.send(client, result)

            difficulty = self.jobs['difficulty']
            result = '{'\
                     '"id":null,' \
                     '"method":"mining.set_difficulty",' \
                     f'"params":["{difficulty}"]'\
                     '}'
            self.send(client, result)

            self.thread_notify = threading.Thread(target=self.__loop_notify, args=[client])
            self.thread_notify.start()
        elif 'mining.submit' == method:
            now = datetime.datetime.now()
            elapsed = now - self.chrono_start
            self.miner.increase_share()
            count = self.miner.get_shares()
            print(f'{datetime.datetime.now()} shares count [{count}], time elapsed [{elapsed}].')
            self.shares.add_share(self.miner.get_name(),
                                  int(elapsed.total_seconds()),
                                  data['params'][4])
            response = '{"id":-1,"result":true,"error":null}'
            response = response.replace('-1', str(data["id"]))
            self.send(client, response)
        elif 'mining.extranonce.subscribe' == method:
            pass
        else:
            print(f'Unknow method [{method}]')
