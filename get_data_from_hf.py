import json
from huggingface_hub import HfApi
from huggingface_hub import ModelSearchArguments, DatasetSearchArguments


if __name__ == "__main__":
    api = HfApi()

    hugging_face_models = list(iter(api.list_models()))
    hugging_face_datasets = list(iter(api.list_datasets()))
    hugging_face_metrics = list(iter(api.list_metrics()))

    print(len(hugging_face_models))
    print(len(hugging_face_datasets))
    print(len(hugging_face_metrics))

    for i in range(len(hugging_face_models)):
        hugging_face_models[i] = hugging_face_models[i].__dict__
    for i in range(len(hugging_face_datasets)):
        hugging_face_datasets[i] = hugging_face_datasets[i].__dict__
    for i in range(len(hugging_face_metrics)):
        hugging_face_metrics[i] = hugging_face_metrics[i].__dict__

    hugging_face_model_args = ModelSearchArguments()
    hugging_face_dataset_args = DatasetSearchArguments()

    print(hugging_face_model_args)
    print(hugging_face_dataset_args)

    hugging_face_models_json = json.dumps(hugging_face_models)
    hugging_face_datasets_json = json.dumps(hugging_face_datasets)
    hugging_face_metrics_json = json.dumps(hugging_face_metrics)
    hugging_face_model_args_json = json.dumps(dict(hugging_face_model_args.items()))
    hugging_face_dataset_args_json = json.dumps(dict(hugging_face_model_args.items()))

    with open('models_json.json', 'w') as outfile:
        outfile.write(hugging_face_models_json)
    with open('datasets_json.json', 'w') as outfile:
        outfile.write(hugging_face_datasets_json)
    with open('metrics_json.json', 'w') as outfile:
        outfile.write(hugging_face_metrics_json)
    with open('model_args_json.json', 'w') as outfile:
        outfile.write(hugging_face_model_args_json)
    with open('dataset_args_json.json', 'w') as outfile:
        outfile.write(hugging_face_dataset_args_json)
