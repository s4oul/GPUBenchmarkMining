import datetime
import logging


class Statistical:

    def __init__(self):
        self.time_first_nonce = None
        self.first_nonce = -1
        self.time_last_nonce = None
        self.last_nonce = -1

    def update_nonce(self, nonce):
        if self.first_nonce == -1:
            self.first_nonce = int(nonce, 16)
            self.time_first_nonce = datetime.datetime.now()
        self.last_nonce = int(nonce, 16)
        self.time_last_nonce = datetime.datetime.now()

    def compute(self, file_fd):
        if self.time_last_nonce is None:
            logging.error(f'No datas cannot compute Hashrate!')
            return
        if self.time_first_nonce is None:
            logging.error(f'No datas cannot compute Hashrate!')
            return

        elapsed = int((self.time_last_nonce - self.time_first_nonce).total_seconds())
        if elapsed <= 0:
            logging.error(f'Elapsed time is 0 second!')
            return

        total_nonce = self.last_nonce - self.first_nonce
        hashrate = total_nonce / elapsed
        m_hashrate = round(float(hashrate / 1000000), 2)
        logging.info(f'Elapsed[{elapsed}]')
        logging.info(f'TotalNonce[{total_nonce}]')
        logging.info(f'Hashrate[{hashrate}] H/S - {m_hashrate} MH/S')

        file_fd.write(f'Elapsed[{elapsed}]\n')
        file_fd.write(f'TotalNonce[{total_nonce}]\n')
        file_fd.write(f'Hashrate[{hashrate}] H/S - {m_hashrate} MH/S\n')
