from configPy import Config, EnvManager, DirManager

file_dir = Config.get_dir_files()
dataset_dir = file_dir["dataset"]

kagglenv = EnvManager.kaggleDataset()
dataset_name = kagglenv.KGG_DATASET

def  get_dataset_dir()->DirManager:
    for dir in list(dataset_dir.iter_dirs()):
        if dir.dir_path.name in dataset_name:
            return dir
    raise Exception(f"Erro: dataset {dataset_name} não encontrado")

if __name__ == "__main__":
    print(get_dataset_dir())