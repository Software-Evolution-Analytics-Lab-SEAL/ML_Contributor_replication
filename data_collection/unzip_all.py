import os
import zipfile
import argparse
import py7zr

def extract_zip(zip_path, extract_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(f"Extracted: {zip_path} -> {extract_path}")
    except zipfile.BadZipFile:
        print(f"Error: {zip_path} is not a valid zip file.")
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")

def extract_7z(archive_path, extract_path):
    try:
        with py7zr.SevenZipFile(archive_path, mode='r') as archive:
            archive.extractall(path=extract_path)
        print(f"Extracted: {archive_path} -> {extract_path}")
    except Exception as e:
        print(f"Error extracting {archive_path}: {e}")

def unzip_files_in_directory(root_dir):
    """
    Recursively search for zip and 7z files in the given directory and its subdirectories,
    then extract them in their respective locations without creating additional folders.
    """
    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.zip'):
                zip_path = os.path.join(foldername, filename)
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(foldername)
                    print(f"Extracted: {zip_path} in {foldername}")
                except zipfile.BadZipFile:
                    print(f"Error: {zip_path} is not a valid zip file.")
                except Exception as e:
                    print(f"Error extracting {zip_path}: {e}")
            elif filename.endswith('.7z'):
                archive_path = os.path.join(foldername, filename)
                try:
                    with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                        archive.extractall(path=foldername)
                    print(f"Extracted: {archive_path} in {foldername}")
                except Exception as e:
                    print(f"Error extracting {archive_path}: {e}")
                
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively unzip all .zip and .7z files in a directory and its subdirectories.")
    parser.add_argument("directory", help="Path to the directory to search for archive files")
    args = parser.parse_args()
    
    if os.path.exists(args.directory):
        unzip_files_in_directory(args.directory)
    else:
        print("Invalid directory path.")
