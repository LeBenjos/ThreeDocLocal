from minio import Minio
from dotenv import load_dotenv
import os

class MinioClient:
    def __init__(self, minio_url, access_key, secret_key):
        self.client = Minio(
            minio_url,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )

    def download_file(self, bucket_name, object_name, local_file_path):
        try:
            self.client.fget_object(bucket_name, object_name, local_file_path)
            print(f"Le fichier {object_name} a été téléchargé avec succès vers {local_file_path}.")
        except S3Error as e:
            print(f"Erreur lors du téléchargement du fichier : {e}")