import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def download_kaggle_dataset():
    """
    Downloads the customer support on twitter dataset from Kaggle.
    Requires kaggle.json to be present in ~/.kaggle/ or provided via environment variables.
    """
    dataset = "thoughtvector/customer-support-on-twitter"
    output_dir = "data"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logger.info(f"Attempting to download dataset {dataset}...")

    try:
        # We use the kaggle CLI to download the dataset
        # The user must have kaggle.json configured in ~/.kaggle/
        cmd = ["kaggle", "datasets", "download", "-d", dataset, "-p", output_dir, "--unzip"]
        subprocess.run(cmd, check=True)
        logger.info(f"Successfully downloaded and unzipped {dataset} to {output_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download dataset. Ensure kaggle CLI is installed and kaggle.json is configured. Error: {e}")
    except FileNotFoundError:
        logger.error("Kaggle CLI not found. Please install it using 'pip install kaggle'.")

if __name__ == "__main__":
    download_kaggle_dataset()
