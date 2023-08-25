import datetime
import os.path
import threading
import socket
import json
import time
import logging

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
        self.fd_log = None

    def is_running(self) -> bool:
        if len(self.clients) == 0:
            self.running = False
        return self.running

    def get_host(self) -> str:
        return self.host

    def get_port(self) -> int:
        return self.port

    def start(self, miner, shares: Share):
        logging.info(f'Start pool on "{self.host}:{self.port}" !')

        log_filename = os.path.join('results', f'{miner.get_name()}_{self.algo}_stratum.log')
        logging.info(f'Stratum LOG => {log_filename}')
        self.fd_log = open(log_filename, 'w')

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
        logging.info(f'New Client!')
        self.clients.append(client)
        self.thread_recv = threading.Thread(target=self.__loop_recv_msg)
        self.thread_recv.start()

    def send(self, client, msg: str):
        try:
            msg_print = msg.replace("\n", "")
            if self.fd_log is not None:
                self.fd_log.write(f'[{datetime.datetime.now()}] ==> {msg_print}\n')
                self.fd_log.flush()
            if '\n' not in msg:
                msg = f'{msg}\n'
            client.sendall(bytes(msg, encoding="utf-8"))
        except Exception as error:
            logging.error(f'{error}.')
            self.running = False

    def close(self):
        self.disconnect_all()
        self.server.close()
        self.running = False
        # waiting thread __loop_notify terminated
        time.sleep(1)
        self.miner.stats.compute(self.fd_log)
        try:
            if self.fd_log is not None:
                self.fd_log.close()
                self.fd_log = None
        except Exception as error:
            logging.error(error)

    def disconnect_all(self):
        for client in self.clients:
            client.close()
        self.clients = list()

    def load_jobs(self):
        try:
            filename = os.path.join('jobs', f'{self.algo}.json')
            with open(filename) as fd:
                self.jobs = json.load(fd)

            for notify in self.jobs['notify']:
                notify['id'] = 0
                self.notifies.append(notify)
        except Exception as error:
            logging.error(f'{error}')
            return False
        return True

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
                        if self.fd_log is not None:
                            self.fd_log.write(f'[{datetime.datetime.now()}] <== {data}\n')
                            self.fd_log.flush()
                        if 'method' in data:
                            self.__dispatch_method(client, data)
        except ConnectionAbortedError:
            logging.info(f'Client has disconnected!')
            self.running = False
        except Exception as error:
            logging.error(f'{error}')
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
            logging.info(f'Send new job.')
            self.send(client, msg)
            for cnt in range(0, timeout):
                if self.is_running() is False:
                    return
                time.sleep(0.5)

    def __dispatch_method(self, client, data: dict):
        try:
            if self.algo == Algorithm.KAWPOW:
                self.__dispatch_kawpow(client, data)
            elif self.algo == Algorithm.FIROPOW:
                self.__dispatch_firopow(client, data)
            elif self.algo == Algorithm.AUTOLYKOS2:
                self.__dispatch_autolykos_v2(client, data)
            elif self.algo == Algorithm.ETHPOW:
                self.__dispatch_eth_pow(client, data)
            elif self.algo == Algorithm.ETCHASH:
                self.__dispatch_etchash(client, data)
        except Exception as error:
            logging.error(f'{error}')

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
            logging.info(f'{datetime.datetime.now()} shares count [{count}], time elapsed [{elapsed}].')
            nonce = data['params'][2]
            self.shares.add_share(self.miner.get_name(),
                                  int(elapsed.total_seconds()),
                                  nonce)
            response = '{"id":-1,"result":true,"error":null}'
            response = response.replace('-1', str(data["id"]))
            self.miner.stats.update_nonce(nonce)
            self.send(client, response)
        elif 'mining.extranonce.subscribe' == method:
            pass
        elif 'eth_submitHashrate' == method:
            pass
        else:
            logging.warning(f'Unknow method [{method}]!')

    def __dispatch_firopow(self, client, data: dict):
        method = data['method']
        if 'mining.subscribe' == method:
            request_id = data['id']
            extra_nonce = self.jobs['extra_nonce']
            result = '{'\
                     f'"id":{request_id}, ' \
                     f'"result":["{extra_nonce}", "{extra_nonce}"], ' \
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

            self.thread_notify = threading.Thread(target=self.__loop_notify, args=[client])
            self.thread_notify.start()
        elif 'mining.submit' == method:
            now = datetime.datetime.now()
            elapsed = now - self.chrono_start
            self.miner.increase_share()
            count = self.miner.get_shares()
            logging.info(f'{datetime.datetime.now()} shares count [{count}], time elapsed [{elapsed}].')
            self.shares.add_share(self.miner.get_name(),
                                  int(elapsed.total_seconds()),
                                  data['params'][2])
            self.miner.stats.update_nonce(data['params'][2])
            response = '{"id":-1,"result":true,"error":null}'
            response = response.replace('-1', str(data["id"]))
            self.send(client, response)
        elif 'mining.extranonce.subscribe' == method:
            pass
        elif 'eth_submitHashrate' == method:
            pass
        else:
            logging.warning(f'Unknow method [{method}]!')

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
            logging.info(f'{datetime.datetime.now()} shares count [{count}], time elapsed [{elapsed}].')
            self.shares.add_share(self.miner.get_name(),
                                  int(elapsed.total_seconds()),
                                  data['params'][4])
            self.miner.stats.update_nonce(data['params'][4])
            response = '{"id":-1,"result":true,"error":null}'
            response = response.replace('-1', str(data["id"]))
            self.send(client, response)
        elif 'mining.extranonce.subscribe' == method:
            pass
        else:
            logging.warning(f'Unknow method [{method}]')

    def __dispatch_eth_pow(self, client, data: dict):
        method = data['method']
        if 'mining.subscribe' == method:
            request_id = data['id']
            extra_nonce = self.jobs['extra_nonce']
            result = '{'\
                     f'"id":{request_id}, ' \
                     f'"result":[["mining.notify","1405ba371b0d0e4526961935bd5dbeee","EthereumStratum/1.0.0"],' \
                     f'"{extra_nonce}"],'\
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
                     f'"params":[{difficulty}]'\
                     '}'
            self.send(client, result)

            extra_nonce = self.jobs['extra_nonce']
            result = '{'\
                     '"id":null,' \
                     '"method":"mining.set_extranonce",' \
                     f'"params":["{extra_nonce}"]'\
                     '}'
            self.send(client, result)

            self.thread_notify = threading.Thread(target=self.__loop_notify, args=[client])
            self.thread_notify.start()
        elif 'mining.submit' == method:
            now = datetime.datetime.now()
            elapsed = now - self.chrono_start
            self.miner.increase_share()
            count = self.miner.get_shares()
            logging.info(f'{datetime.datetime.now()} shares count [{count}], time elapsed [{elapsed}].')
            self.shares.add_share(self.miner.get_name(),
                                  int(elapsed.total_seconds()),
                                  data['params'][2])
            self.miner.stats.update_nonce(data['params'][2])
            response = '{"id":-1,"result":true,"error":null}'
            response = response.replace('-1', str(data["id"]))
            self.send(client, response)
        elif 'mining.extranonce.subscribe' == method:
            id = data['id']
            result = '{' \
                     f'"id":{id},' \
                     f'"result":true,' \
                     f'"error":null' \
                     '}'
            self.send(client, result)
        elif 'eth_submitHashrate' == method:
            id = data['id']
            result = '{' \
                     f'"id":{id},' \
                     f'"result":true,' \
                     f'"error":null' \
                     '}'
            self.send(client, result)
        else:
            logging.warning(f'Unknow method [{method} - {data}]')

    def __dispatch_etchash(self, client, data: dict):
        method = data['method']
        if 'mining.subscribe' == method:
            request_id = data['id']
            extra_nonce = self.jobs['extra_nonce']
            result = '{'\
                     f'"id":{request_id},'\
                     f'"result":[["mining.notify","bdddd4d727fcb1944743a8051a01fa00","EthereumStratum/1.0.0"],'\
                     f'"{extra_nonce}"],'\
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
                     f'"params":[{difficulty}]'\
                     '}'
            self.send(client, result)

            extra_nonce = self.jobs['extra_nonce']
            result = '{'\
                     '"id":null,' \
                     '"method":"mining.set_extranonce",' \
                     f'"params":["{extra_nonce}"]'\
                     '}'
            self.send(client, result)

            self.thread_notify = threading.Thread(target=self.__loop_notify, args=[client])
            self.thread_notify.start()
        elif 'mining.submit' == method:
            now = datetime.datetime.now()
            elapsed = now - self.chrono_start
            self.miner.increase_share()
            count = self.miner.get_shares()
            nonce = data['params'][2]
            logging.info(f'{datetime.datetime.now()} shares count [{count}], time elapsed [{elapsed}].')
            self.shares.add_share(self.miner.get_name(),
                                  int(elapsed.total_seconds()),
                                  nonce)
            self.miner.stats.update_nonce(nonce)
            response = '{"id":-1,"result":true,"error":null}'
            response = response.replace('-1', str(data["id"]))
            self.send(client, response)
        elif 'mining.extranonce.subscribe' == method:
            id = data['id']
            result = '{'\
                     f'"id":{id},'\
                     f'"result":true,'\
                     f'"error":null'\
                     '}'
            self.send(client, result)
        elif 'eth_submitHashrate' == method:
            id = data['id']
            result = '{' \
                     f'"id":{id},' \
                     f'"result":true,' \
                     f'"error":null' \
                     '}'
            self.send(client, result)
        else:
            logging.warning(f'Unknow method [{method} - {data}]')