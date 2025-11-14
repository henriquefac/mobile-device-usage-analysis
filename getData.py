from configPy import Config, EnvManager
import subprocess
from pathlib import Path
import sys
from zipfile import ZipFile
import os

kagglenv = EnvManager.kaggleDataset()
dataset_name = kagglenv.KGG_DATASET

file_dir = Config.get_dir_files()
dataset_dir = file_dir.create_dir("dataset")


def unzip_dataset(zip_path: Path, unzip_path: Path):
    try:
        with ZipFile(zip_path, "r") as zip_obj:
            zip_obj.extractall(path=unzip_path)
    except Exception as e:
        print(f"Erro ao extrair o arquivo zip: {e}")

    os.remove(str(zip_path))


# Comando correto da API Kaggle:
# kaggle datasets download -d <dataset> -p <path>
cmd = ["kaggle", "datasets", "download", "-d", dataset_name, "-p", str(dataset_dir)]

print("Baixando dataset:", dataset_name)
print("Destino:", dataset_dir)

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("Download finalizado.")
    print(result.stdout)

    # extrair zip
    listzip = [f for f in list(dataset_dir.iter_files()) if f.suffix == ".zip"]

    for zip_f in listzip:
        file_name = zip_f.stem
        unzip_dir = dataset_dir.create_dir(file_name)
        unzip_dataset(zip_f, unzip_path=unzip_dir.dir_path)

except subprocess.CalledProcessError as e:
    print("Erro ao baixar o dataset:")
    print(e.stderr)
    sys.exit(1)
