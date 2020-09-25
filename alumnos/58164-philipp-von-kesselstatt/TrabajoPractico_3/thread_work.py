import array


def thread_red_filter(block, size, scale, mv):

    ss = len(block)
    if ss % 3 != 0:
        ss -= 1
        block = block[:-1]
    for p in range(0, ss, 3):
        block[p] = round(block[p] * scale) if block[p] * scale <= mv else mv

    return array.array('B', block)


def thread_green_filter(block, size, scale, mv):
    ss = len(block)
    if ss % 3 != 0:
        ss -= 1
        block = block[:-1]
    for p in range(0, ss, 3):
        block[p+1] = round(block[p+1] * scale) if block[p+1] * scale <= mv else mv

    return array.array('B', block)


def thread_blue_filter(block, size, scale, mv):
    ss = len(block)
    if ss % 3 != 0:
        ss -= 1
        block = block[:-1]

    print([scale])
    for p in range(0, ss, 3):

        block[p+2] = round(block[p+2] * scale) if block[p+2] * scale <= mv else mv

    return array.array('B', block)


def thread_black_white(block, size, scale, max_v):
    ss = len(block)
    if ss % 3 != 0:
        ss -= 1
        block = block[:-1]
    for pixel in range(0, ss, 3):
        pixel_average = (block[pixel] + block[pixel+1] + block[pixel+2])/3
        pixel_average = round(pixel_average*scale)
        if pixel_average > max_v:
            pixel_average = max_v

        block[pixel] = pixel_average
        block[pixel+1] = pixel_average
        block[pixel+2] = pixel_average

    image = array.array('B', block)

    return image
