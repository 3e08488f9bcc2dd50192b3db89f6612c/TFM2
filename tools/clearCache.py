import shutil
import os

if __name__ == "__main__":
    for root, dirs, files in os.walk(os.getcwd()):
        for d in dirs:
            if d == '__pycache__':
                pycache_folder = os.path.join(root, d)
                print(f"Deleting {pycache_folder}")
                try:
                    shutil.rmtree(pycache_folder)
                except OSError as e:
                    print(f"Error: {e}")