import time

import db
import ram


def run():
    while True:
        db.clean()
        ram_usage = ram.usage()
        with open('ram.txt', 'a') as file:
            file.write(str(time.time()) + ',' + str(ram_usage) + '\n')

        time.sleep(10)


if __name__ == '__main__':
    run()