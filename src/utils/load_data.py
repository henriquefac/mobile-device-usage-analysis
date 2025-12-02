import pandas as pd
from .get_dataset_name import get_dataset_dir
from typing import Union

def load_data(file: Union[DirManager, Path]):
    if isinstance(file, DirManager):
        csv_file: Path = file.get_any("user_behavior_dataset.csv")
    csv_file: Path = file

    df = pd.read_csv(csv_file)

    return df