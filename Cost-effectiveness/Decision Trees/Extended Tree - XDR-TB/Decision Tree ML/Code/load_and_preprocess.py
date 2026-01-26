# === modeling/load_and_preprocess.py ===
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def load_and_preprocess_data(df, drop_cols):
    df_filtered = df.drop(columns=drop_cols)
    df_filtered = df_filtered.fillna(0)

    label_encoders = {}
    for col in df_filtered.columns:
        if df_filtered[col].dtype == 'object' or df_filtered[col].apply(type).nunique() > 1:
            df_filtered[col] = df_filtered[col].astype(str)
            le = LabelEncoder()
            df_filtered[col] = le.fit_transform(df_filtered[col])
            label_encoders[col] = le

    return df_filtered, label_encoders