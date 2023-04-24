from psutil import virtual_memory


total = virtual_memory().total / 1048576

def usage():
    return virtual_memory()[3] / 1048576