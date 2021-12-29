import sys
from typing import Generator
from omero.gateway import ImageWrapper, WellWrapper

DEFAULT_BUFFER_SIZE = 65536


def __file_reader(
    reader,
    size,
    from_position=0,
    to_position=sys.maxsize,
    buffer_size=0
) -> Generator:
    """
    Generator helper function that yields chunks of the file
    from from_position to to_position

    :type reader: file
    :param reader: filelike readable object
    :type size: int
    :param size: size of the file
    :type from_position: int
    :param from_position: start position of bytes to read
    :type to_position: int
    :param to_position: end position of bytes to read
    :type buffer_size: int
    :param buffer_size: size of each chunk of data read from exporter that gets yielded
    :rtype: generator
    :return: generator of string buffers of size up to buffer_size read from exporter
    """
    if from_position > to_position:
        tmp = to_position
        to_position = from_position
        from_position = tmp

    if from_position < 1:
        from_position = 0

    if to_position == sys.maxsize or to_position > size:
        to_position = size
        if from_position > to_position:
            from_position = to_position

    if buffer_size < 1:
        buffer_size = DEFAULT_BUFFER_SIZE

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
    to_position=sys.maxsize,
    buffer_size=0
) -> tuple[int, Generator]:
    exporter = gateway.createExporter()
    exporter.addImage(image_id)
    size = exporter.generateTiff(gateway.SERVICE_OPTS)

    return (size, __file_reader(
        exporter,
        size,
        from_position,
        to_position,
        buffer_size
    ))


def can_download(gateway, image_id):
    image: ImageWrapper = gateway.getObject('Image', image_id)
    if image is None:
        return False

    try:
        well = image.getParent().getParent()
    except Exception:
        if hasattr(image, "canDownload"):
            return image.canDownload()
    else:
        if well and isinstance(well, WellWrapper):
            if hasattr(well, "canDownload"):
                return well.canDownload()

    return True


def get_original_files_info(gateway, image_id) -> dict:
    image: ImageWrapper = gateway.getObject('Image', image_id)
    return image.getImportedFilesInfo()


def download_original_files(
    gateway,
    image_id,
    from_position=0,
    to_position=sys.maxsize,
    buffer_size=0
) -> tuple[int, Generator, str]:
    image: ImageWrapper = gateway.getObject('Image', image_id)
    flat_map = {}
    for item in image.getImportedImageFiles():
        flat_map[item.getId()] = item
    files = list(flat_map.values())
    file = files[0]
    size = file.getSize()
    filename = file.getName().replace(" ", "_").replace(",", ".")

    reader = file.asFileObj()

    return (size, __file_reader(
        reader.rfs,
        size,
        from_position,
        to_position,
        buffer_size
    ), filename)
