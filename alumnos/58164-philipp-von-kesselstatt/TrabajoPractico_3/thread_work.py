
def thread_red_filter(block, scale, max_v):

    for p in range(0, len(block), 3):

        new_value = min(round(block[p] * scale), max_v)

        block = block[:p] + bytes([new_value]) + block[p+1:]

    return block


def thread_green_filter(block, scale, max_v):

    for p in range(1, len(block), 3):

        new_value = min(round(block[p] * scale), max_v)

        block = block[:p] + bytes([new_value]) + block[p+1:]

    return block


def thread_blue_filter(block, scale, max_v):

    for p in range(2, len(block), 3):

        new_value = min(round(block[p] * scale), max_v)

        block = block[:p] + bytes([new_value]) + block[p+1:]

    return block


def thread_black_white(block, scale, max_v):

    for pixel in range(0, len(block)-1, 3):

        pixel_average = (block[pixel] + block[pixel+1] + block[pixel+2])/3
        pixel_average = min(round(pixel_average*scale), max_v)

        block = block[:pixel] + bytes([pixel_average])*3 + block[pixel+3:]

    return block
