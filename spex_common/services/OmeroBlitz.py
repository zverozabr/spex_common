import math
from typing import Generator


DEFAULT_BUFFER_SIZE = 65536


def __file_reader(reader, from_position, to_position, buffer_size) -> Generator:
    """
    Generator helper function that yields chunks of the file
    from from_position to to_position

    :type reader: file
    :param reader: filelike readable object
    :type from_position: int
    :param from_position: start position of bytes to read
    :type to_position: int
    :param to_position: end position of bytes to read
    :type buffer_size: int
    :param buffer_size: size of each chunk of data read from exporter that gets yielded
    :rtype: generator
    :return: generator of string buffers of size up to buffer_size read from exporter
    """
    pointer = from_position
    try:
        while pointer < to_position:
            size = min(buffer_size, to_position - pointer)
            yield reader.read(pointer, size)
            pointer += size
    finally:
        reader.close()


def get_image_size(gateway, image_id):
    exporter = gateway.createExporter()
    try:
        exporter.addImage(image_id)
        size = exporter.generateTiff(gateway.SERVICE_OPTS)
        return size
    finally:
        exporter.close()


def export_ome_tiff(
    gateway,
    image_id,
    from_position=0,
    to_position=math.inf,
    buffer_size=0
) -> tuple[int, Generator]:
    exporter = gateway.createExporter()
    exporter.addImage(image_id)
    size = exporter.generateTiff(gateway.SERVICE_OPTS)

    if from_position > to_position:
        tmp = to_position
        to_position = from_position
        from_position = tmp

    if from_position < 1:
        from_position = 0

    if to_position == math.inf or to_position > size:
        to_position = size

    if buffer_size < 1:
        buffer_size = DEFAULT_BUFFER_SIZE

    return (size, __file_reader(
        exporter,
        from_position,
        to_position,
        buffer_size
    ))
