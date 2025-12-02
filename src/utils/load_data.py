import pandas as pd
from .get_dataset_name import get_dataset_dir
from pathlib import Path

def load_data()->pd.DataFrame:
    dataset = get_dataset_dir()
    csv_file: Path = dataset.get_any("user_behavior_dataset.csv")
    df = pd.read_csv(csv_file)

    return df