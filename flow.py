import subprocess
import sys

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas', 'SQLAlchemy', 'psycopg2-binary', 'huggingface_hub'])

import prefect

from prefect import task, Task, Flow
from prefect.tasks.secrets import PrefectSecret

from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine

from huggingface_hub import HfApi
import json


@task
def extract_models():
    logger = prefect.context.get("logger")
    
    api = HfApi()
    
    hugging_face_models = list(iter(api.list_models()))
    
    logger.info(len(hugging_face_models))
    
    for i in range(len(hugging_face_models)):
        hugging_face_models[i] = hugging_face_models[i].__dict__
    
    hugging_face_models_json = json.dumps(hugging_face_models)
    
    return hugging_face_models_json

@task
def extract_datasets():
    logger = prefect.context.get("logger")
    
    api = HfApi()
    
    hugging_face_datasets = list(iter(api.list_datasets()))
    
    logger.info(len(hugging_face_datasets))
    
    for i in range(len(hugging_face_datasets)):
        hugging_face_datasets[i] = hugging_face_datasets[i].__dict__
    
    hugging_face_datasets_json = json.dumps(hugging_face_datasets)
    
    return hugging_face_datasets_json

@task
def transform_models(hugging_face_models_json):
    logger = prefect.context.get("logger")
    
    models_slice_df = pd.read_json(hugging_face_models_json)
    
    domains = [
        "computer-vision",
        "natural-language-processing",
        "audio",
        "tabular",
        "multimodal",
        "reinforcement-learning",
        "unknown-domain",
        "time-series",
        "graph",
        "robotics"
    ]
    task2domain = {
        "text-classification":            "natural-language-processing",
        "reinforcement-learning":         "reinforcement-learning",
        "text2text-generation":           "natural-language-processing",
        "text-generation":                "natural-language-processing",
        "token-classification":           "natural-language-processing",
        "automatic-speech-recognition":   "audio",
        "fill-mask":                      "natural-language-processing",
        "question-answering":             "natural-language-processing",
        "text-to-image":                  "multimodal",
        "feature-extraction":             "multimodal",
        "image-classification":           "computer-vision",
        "conversational":                 "natural-language-processing",
        "translation":                    "natural-language-processing",
        "sentence-similarity":            "natural-language-processing",
        "summarization":                  "natural-language-processing",
        "unconditional-image-generation": "computer-vision",
        "audio-classification":           "audio",
        "object-detection":               "computer-vision",
        "multiple-choice":                "unknown-domain",
        "text-to-speech":                 "audio",
        "image-segmentation":             "computer-vision",
        "audio-to-audio":                 "audio",
        "image-to-text":                  "multimodal",
        "tabular-classification":         "tabular",
        "zero-shot-image-classification": "computer-vision",
        "zero-shot-classification":       "natural-language-processing",
        "video-classification":           "computer-vision",
        "image-to-image":                 "computer-vision",
        "tabular-regression":             "tabular",
        "table-question-answering":       "natural-language-processing",
        "depth-estimation":               "computer-vision",
        "document-question-answering":    "multimodal",
        "text-to-video":                  "multimodal",
        "visual-question-answering":      "multimodal",
        "voice-activity-detection":       "audio",
        "robotics":                       "robotics",
        "other":                          "unknown-domain",
        "graph-ml":                       "graph",
        "time-series-forecasting":        "time-series"
    }
    
    models_slice_df.fillna(value={"pipeline_tag": "unknown-tag"}, inplace=True)
    models_slice_df["author"] = models_slice_df.modelId.apply(lambda x: x.split("/")[0] if "/" in x else "unknown-author")
    models_slice_df["datasets"] = models_slice_df.tags.apply(lambda tags_array: [item for item in tags_array if "dataset:" in item])
    models_slice_df["has_space"] = models_slice_df.tags.apply(lambda tags_array: "has_space" in tags_array)
    models_slice_df["domain"] = models_slice_df.pipeline_tag.apply(lambda tag: task2domain.get(tag, "unknown-domain"))
    models_slice_df["slice_datetime"] = datetime.now()
    
    models_slice_df.rename(columns={col: col.lower() for col in models_slice_df.columns}, inplace=True)
    
    logger.info(models_slice_df.isna().sum())
    
    return models_slice_df

@task
def transform_datasets(hugging_face_datasets_json):
    logger = prefect.context.get("logger")
    
    datasets_slice_df = pd.read_json(hugging_face_datasets_json)
    
    datasets_slice_df["tasks"] = datasets_slice_df.tags.apply(lambda tags_array: [item.split(":")[1] for item in tags_array if "task_categories:" in item])
    datasets_slice_df["size"] = datasets_slice_df.tags.apply(lambda tags_array: [item.split(":")[1] for item in tags_array if "size_categories:" in item])
    datasets_slice_df["slice_datetime"] = datetime.now()
    
    datasets_slice_df.rename(columns={col: col.lower() for col in datasets_slice_df.columns}, inplace=True)
    datasets_slice_df.rename(columns={"id": "datasetid"}, inplace=True)
    
    logger.info(datasets_slice_df.isna().sum())
    
    return datasets_slice_df

@task
def load(models_slice_df, datasets_slice_df, db_host, db_user, db_password):
    logger = prefect.context.get("logger")
    
    engine = create_engine('postgresql://{}:{}@{}:5432/rpd_5310'.format(db_user, db_password, db_host))
    
    models_df = pd.read_sql('hugging_face_models', engine)
    datasets_df = pd.read_sql('hugging_face_datasets', engine)
    
    models_mask = [col for col in models_df.columns if col not in ["likes", "downloads"]]
    datasets_mask = [col for col in datasets_df.columns if col not in ["likes", "downloads"]]
    
    models_filter = ~models_slice_df.modelid.isin(models_df.modelid)
    datasets_filter = ~datasets_slice_df.datasetid.isin(datasets_df.datasetid)
    
    if len(models_slice_df[models_filter]) > 0:
        logger.info("Writing {} records to hugging_face_models table".format(len(models_slice_df[models_filter])))
        
        models_slice_df[models_filter][models_mask].to_sql('hugging_face_models', engine, if_exists='append', index=False)
    
    if len(datasets_slice_df[datasets_filter]) > 0:
        logger.info("Writing {} records to hugging_face_datasets table".format(len(datasets_slice_df[datasets_filter])))
        
        datasets_slice_df[datasets_filter][datasets_mask].to_sql('hugging_face_datasets', engine, if_exists='append', index=False)
    
    models_mask = ["modelid", "likes", "downloads", "slice_datetime"]
    datasets_mask = ["datasetid", "likes", "downloads", "slice_datetime"]
    
    logger.info("Writing {} records to hugging_face_models_daily_dynamics table".format(len(models_slice_df)))
    models_slice_df[models_mask].to_sql('hugging_face_models_daily_dynamics', engine, if_exists='append', index=False)
    
    logger.info("Writing {} records to hugging_face_datasets_daily_dynamics table".format(len(datasets_slice_df)))
    datasets_slice_df[datasets_mask].to_sql('hugging_face_datasets_daily_dynamics', engine, if_exists='append', index=False)

with Flow('update huggingface data') as flow:
    db_host = PrefectSecret("DB_HOST")
    db_user = PrefectSecret("DB_USER")
    db_password = PrefectSecret("DB_PASSWORD")
    
    models_slice_df = transform_models(extract_models())
    
    datasets_slice_df = transform_datasets(extract_datasets())
    
    load(models_slice_df, datasets_slice_df, db_host, db_user, db_password)
