import os, glob, pandas as pd
from sklearn.model_selection import train_test_split

INPUT_DIR = "/opt/ml/processing/input"
TRAIN_DIR = "/opt/ml/processing/output/train"
VAL_DIR   = "/opt/ml/processing/output/validation"

os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(VAL_DIR,   exist_ok=True)

files = glob.glob(f"{INPUT_DIR}/*.csv")
df    = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
df.dropna(inplace=True)

cols = ["label"] + [c for c in df.columns if c != "label"]
df   = df[cols]

train, val = train_test_split(df, test_size=0.2,
                               stratify=df["label"], random_state=42)

train.to_csv(f"{TRAIN_DIR}/train.csv",           index=False, header=False)
val.to_csv(f"{VAL_DIR}/validation.csv",          index=False, header=False)
print(f"Train: {len(train)} rows  |  Validation: {len(val)} rows")