import glob
import os
import time
import pickle

from colorama import Fore, Style
from tensorflow import keras
from google.cloud import storage

from params import LOCAL_REGISTRY_PATH, BUCKET_NAME

def save_model(model: keras.Model = None) -> None:
    """
    - Save model on our bucket on GCS at "models/{timestamp}.h5" --> unit 02 only
    """

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    # Save model locally
    model_path = os.path.join(LOCAL_REGISTRY_PATH, "models", f"safety-{timestamp}.h5")
    model.save(model_path)

    print("✅ Model saved locally")

    # Save model on GCS

    model_filename = f"Safety-map-model-{timestamp}" # e.g. "20230208-161047.h5" for instance
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"models/{model_filename}")
    blob.upload_from_filename(model_path)

    print("✅ Model saved to GCS")

    return None

def load_model() -> keras.Model:
    """
    Return a saved model:
    - from GCS (most recent one)
    Return None (but do not Raise) if no model is found
    """
    print(Fore.BLUE + f"\nLoad latest model from GCS..." + Style.RESET_ALL)

    client = storage.Client()
    blobs = list(client.get_bucket(BUCKET_NAME).list_blobs(prefix="model"))

    try:
        latest_blob = max(blobs, key=lambda x: x.updated)
        latest_model_path_to_save = os.path.join(LOCAL_REGISTRY_PATH, latest_blob.name)
        latest_blob.download_to_filename(latest_model_path_to_save)

        latest_model = keras.models.load_model(latest_model_path_to_save)

        print("✅ Latest model downloaded from cloud storage")

        return latest_model
    except:
        print(f"\n❌ No model found in GCS bucket {BUCKET_NAME}")

        return None
