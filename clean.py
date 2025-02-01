import os
import shutil

def clean_python_cache(directory: str):
    # Walk through all the subdirectories and files in the given directory
    for root, dirs, files in os.walk(directory, topdown=False):
        # Delete .pyc files
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                print(f"Deleting file: {file_path}")
                os.remove(file_path)
        
        # Delete __pycache__ directories
        for dir in dirs:
            if dir == '__pycache__':
                dir_path = os.path.join(root, dir)
                print(f"Deleting directory: {dir_path}")
                shutil.rmtree(dir_path)

# Run the function with the desired directory, or use the current directory
if __name__ == "__main__":
    directory = input("Enter the directory to clean Python cache (or press Enter to clean the current directory): ")
    if not directory:
        directory = os.getcwd()  # Default to current working directory
    clean_python_cache(directory)
    print("Cache cleaning completed.")
