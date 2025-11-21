import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split

DATASET_PATH = Path(__file__).resolve().parents[2] / "dataset" / "data.csv"

FEATURE_COLUMNS = [
    "curricular_units_2nd_sem_approved",
    "curricular_units_1st_sem_approved",
    "curricular_units_2nd_sem_grade",
    "curricular_units_1st_sem_grade",
    "tuition_fees_up_to_date_1",
    "scholarship_holder_1",
    "debtor_0",
    "gender_0",
    "curricular_units_2nd_sem_enrolled",
    "curricular_units_1st_sem_enrolled",
    "tuition_fees_up_to_date_0",
    "age_at_enrollment",
    "application_mode",
    "scholarship_holder_0",
    "debtor_1",
    "gender_1",
]

ONE_HOT_COLUMNS = [
    "marital_status",
    "daytime_evening_attendance",
    "tuition_fees_up_to_date",
    "educational_special_needs",
    "displaced",
    "scholarship_holder",
    "gender",
    "debtor",
    "international",
]

_ARTIFACTS = None


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        col.replace(" ", "_")
        .replace("'s", "")
        .replace("\t", "")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
        .lower()
        for col in df.columns
    ]
    return df


def _remove_outliers(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=[np.number])
    z_scores = (numeric_df - numeric_df.mean()) / numeric_df.std(ddof=0)
    z_scores = z_scores.replace([np.inf, -np.inf], np.nan)
    outliers = (np.abs(z_scores) > threshold).any(axis=1)
    return df.loc[~outliers].copy()


def _apply_one_hot(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in ONE_HOT_COLUMNS:
        if column not in result.columns:
            continue
        result[column] = result[column].astype(float).astype(int)
        dummies = pd.get_dummies(result[column], prefix=column)
        result = pd.concat([result.drop(columns=[column]), dummies], axis=1)
    return result


def _prepare_training_frame():
    df = pd.read_csv(DATASET_PATH, sep=";")
    df = _clean_columns(df)
    df = _remove_outliers(df)
    df = _apply_one_hot(df)
    df = df[df["target"] != "Enrolled"].copy()
    class_names, y = np.unique(df["target"], return_inverse=True)
    X = df.drop(columns=["target"])
    return X, y, class_names


def _build_artifacts():
    X, y, class_names = _prepare_training_frame()
    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.2, random_state=1
    )

    missing = set(FEATURE_COLUMNS) - set(X_train.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    X_train_fs = X_train[FEATURE_COLUMNS]
    scaler = StandardScaler().fit(X_train_fs)
    X_train_sc = scaler.transform(X_train_fs)

    pca = PCA(n_components=len(FEATURE_COLUMNS), whiten=True).fit(X_train_sc)

    return {
        "scaler": scaler,
        "pca": pca,
        "class_names": tuple(class_names),
    }


def get_artifacts():
    global _ARTIFACTS
    if _ARTIFACTS is None:
        _ARTIFACTS = _build_artifacts()
    return _ARTIFACTS


def transform_feature_row(feature_row: dict) -> np.ndarray:
    artifacts = get_artifacts()
    df = pd.DataFrame([feature_row], columns=FEATURE_COLUMNS)
    scaled = artifacts["scaler"].transform(df)
    transformed = artifacts["pca"].transform(scaled)
    return transformed.astype(np.float32)

