import shutil


def archive(dir_name, output_filename):
    """
    Архивирует заданную папку в zip-архив
    :param dir_name: архивируемая папка
    :param output_filename: имя создаваемого zip-архива
    """
    if output_filename.rfind(".zip") == len(output_filename)-4:
        output_filename = output_filename[:-4]
    shutil.make_archive(output_filename, "zip", dir_name)


def extract(file_name, extract_dir=""):
    """
    Разархивирует zip-архив в заданную папку
    :param file_name: имя zip-архива
    :param extract_dir: папка для разархивации
    """
    shutil.unpack_archive(file_name, extract_dir, "zip")


def create_empty(file_name):
    """
    Создает пустой архив
    :param file_name: имя создаваемого zip-архива
    """
    void_data = b"PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    with open(file_name, "wb") as zip_file:
        zip_file.write(void_data)
