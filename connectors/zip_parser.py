import os
import tempfile
import zipfile


MAX_FILES = 100
MAX_TOTAL_SIZE = 100 * 1024 * 1024      # 100 MB


def extract_files(zip_path: str):

    if not zipfile.is_zipfile(zip_path):
        raise ValueError("Invalid ZIP file.")

    with zipfile.ZipFile(zip_path, "r") as archive:

        members = archive.infolist()

        # Limit number of files
        if len(members) > MAX_FILES:
            raise ValueError("ZIP contains too many files.")

        # Limit extracted size
        total_size = sum(member.file_size for member in members)

        if total_size > MAX_TOTAL_SIZE:
            raise ValueError("ZIP exceeds maximum allowed size.")

        temp_dir = tempfile.mkdtemp()

        for member in members:

            destination = os.path.abspath(
                os.path.join(temp_dir, member.filename)
            )

            if not destination.startswith(
                os.path.abspath(temp_dir)
            ):
                raise ValueError(
                     "Unsafe ZIP archive (Zip Slip detected)."
                )

            archive.extract(member, temp_dir)



    extracted_files = []

    for root, _, files in os.walk(temp_dir):

        for file in files:

            extracted_files.append(
                os.path.join(root, file)
            )

    return extracted_files
