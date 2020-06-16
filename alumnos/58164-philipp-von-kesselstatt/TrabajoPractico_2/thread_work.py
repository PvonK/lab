

def change_LSB(byte, bit):
    if byte % 2 != bit:
        if bit == 1:
            byte += 1
        else:
            byte -= 1

    return byte


def thread_work(color, total_bytes, change, message):
    global reading
    global lock
    global barrier

    bits = [message[i] for i in range(color, len(message), 3)]
    written = 0
    while written < total_bytes:

        written = len(reading)

        # modifican bytes y guardan en lista
        while change != [] and change[0] < written:

            lock.acquire()

            index_to_change = change.pop(0)
            reading[index_to_change] = change_LSB(reading[index_to_change], int(bits.pop(0)))
            lock.release()

        barrier.wait()
