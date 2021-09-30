import os
import glob
import re
import threading
import math
from typing import BinaryIO
from spex_common.modules.logging import get_logger


def extract_chunk_index(chunk):
    index, _ = os.path.splitext(chunk)
    index = index.split('.')[-1]
    return int(index)


class OmeroImageFileManager:
    __chunks = {}

    def __init__(self, omero_image_id: int, expected_file_size: int = 0, chunk_size: int = 0):
        self.__logger = get_logger(f'spex.models.{self.__class__.__name__}')
        self.__expected_file_size = expected_file_size
        self.__chunk_size = chunk_size
        self.__dir = f'{os.getenv("DATA_STORAGE")}/originals/{omero_image_id}'
        self.__path = os.path.join(self.__dir, 'image')
        self.__lock_path = f'{self.__path}.lock'
        self.__chunk_path = f'{self.__path}.chunk'
        self.__omero_image_id = omero_image_id

    def get_image_id(self):
        return self.__omero_image_id

    def set_expected_size(self, file_size):
        self.__expected_file_size = file_size
        return self

    def get_expected_file_size(self) -> int:
        return self.__expected_file_size

    def set_chunk_size(self, chunk_size):
        self.__chunk_size = chunk_size
        return self

    def get_chunk_size(self):
        return self.__chunk_size

    def exists(self) -> bool:
        return os.path.isfile(self.get_filename())

    def get_file_size(self) -> int:
        if not self.exists():
            return 0

        return os.path.getsize(self.get_filename())

    def get_filename(self) -> str:
        return f'{self.__path}.tiff'

    def __get_tmp(self) -> str:
        return f'{self.get_filename()}.tmp'

    def remove_chunk(self, chunk_id=None):
        chunks = glob.glob(f'{self.__chunk_path}.{chunk_id or "*"}')
        for chunk in chunks:
            os.remove(chunk)
        return self

    def clear(self):
        if not os.path.exists(self.__dir):
            return self

        self.remove_chunk()

        if os.path.exists(self.__get_tmp()):
            os.remove(self.__get_tmp())

        return self

    def __get_chunks(self, finished=False) -> list[str]:
        suffix = '*'
        if finished:
            suffix = f'*.finished'
        chunks = glob.glob(f'{self.__chunk_path}.{suffix}')
        chunks.sort(key=lambda item: int(re.sub('\\D', '', item)))
        return chunks

    def calc_number_of_chunks(self) -> int:
        if self.__chunk_size < 1:
            self.__logger.warn('chunk_size is too small')
            return 0

        if self.__expected_file_size < 1:
            self.__logger.warn('expected_file_size is too small')
            return 0

        if self.__chunk_size >= self.__expected_file_size:
            return 1

        return math.ceil(self.__expected_file_size / self.__chunk_size)

    def get_unfinished_chunks(self) -> list[int]:
        count = self.calc_number_of_chunks()
        chunks = self.__get_chunks(True)

        chunks = set(map(extract_chunk_index, chunks))

        result = set(range(count))

        return list(result.difference(chunks))

    def open_chunk(self, index: int) -> BinaryIO:
        os.makedirs(self.__dir, exist_ok=True)

        self.__chunks[index] = open(f'{self.__chunk_path}.{index}', 'wb')

        return self.__chunks[index]

    def close_chunk(self, index):
        if self.__chunks[index] is not None:
            self.__chunks[index].close()
            del self.__chunks[index]

        return self

    def finish_chunk(self, index: int):
        if self.__chunks[index] is not None:
            self.__chunks[index].close()
            del self.__chunks[index]
            os.rename(f'{self.__chunk_path}.{index}', f'{self.__chunk_path}.{index}.finished')

        return self

    def is_locked(self) -> bool:
        return os.path.exists(self.__lock_path)

    def lock(self):
        os.makedirs(self.__dir, exist_ok=True)
        open(self.__lock_path, 'a').close()
        return self

    def unlock(self):
        if self.is_locked():
            os.remove(self.__lock_path)

    def merge_chunks(self):
        if self.__chunk_size < 1:
            self.__logger.warn('chunk_size is too small')
            return self

        if self.__expected_file_size < 1:
            self.__logger.warn('expected_file_size is too small')
            return self

        os.makedirs(self.__dir, exist_ok=True)

        if os.path.exists(self.__get_tmp()):
            os.remove(self.__get_tmp())

        chunks = self.__get_chunks(True)

        if len(chunks) < 1:
            return

        tmp_file = self.__get_tmp()
        buffer_size = 1024*4096
        with open(tmp_file, 'wb') as result:
            for chunk in chunks:
                with open(chunk, 'rb') as file:
                    while threading.current_thread().is_alive():
                        part = file.read(buffer_size)
                        if not part:
                            break
                        result.write(part)

        size = os.path.getsize(tmp_file)
        if size == self.__expected_file_size:
            if os.path.exists(self.get_filename()):
                os.remove(self.get_filename())
            os.rename(tmp_file, self.get_filename())

        self.clear()

