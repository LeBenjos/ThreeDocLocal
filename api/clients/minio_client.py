from minio import Minio
from minio.error import S3Error
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os

load_dotenv()

class MinioClient:
    def __init__(self):
        self.minio_url = os.getenv('MINIO_URL')
        self.access_key = os.getenv('MINIO_ACCESS_KEY')
        self.secret_key = os.getenv('MINIO_SECRET_KEY')

        if not all([self.minio_url, self.access_key, self.secret_key]):
            raise ValueError("Configuration MinIO manquante dans les variables d'environement.")

        self.client = Minio(
            self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False
        )

    def get_rag(self, rag_name):
        bucket_name = 'tdl-bucket'
        base_path = './rags/'
        pdf_file_path = base_path + 'temp.pdf'

        self.download_rag(bucket_name, rag_name, pdf_file_path)

        txt_file_path = base_path + rag_name.rsplit('.pdf', 1)[0] + '.txt'
        self.convert_pdf_to_txt(pdf_file_path, txt_file_path)

        self.remove_file(pdf_file_path)

    def download_rag(self, bucket_name, rag_name, local_file_path):
        try:
            self.client.fget_object(bucket_name, rag_name, local_file_path)
            print(f"Le fichier {rag_name} a été téléchargé avec succès vers {local_file_path}.")
        except S3Error as e:
            print(f"Erreur lors du téléchargement du fichier : {e}")
            raise

    def convert_pdf_to_txt(self, local_pdf_path, local_txt_path):
        try:
            if not os.path.exists(local_pdf_path):
                raise FileNotFoundError(f"Le fichier PDF spécifié n'existe pas : {local_pdf_path}")

            with open(local_pdf_path, 'rb') as pdf_file:
                reader = PdfReader(pdf_file)
                text = ""

                for i, page in enumerate(reader.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                    else:
                        print(f"Attention : Impossible d'extraire le texte de la page {i}.")

                text = text.strip()

                with open(local_txt_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(text)

            print(f"Conversion réussie : {local_pdf_path} -> {local_txt_path}")
        except FileNotFoundError as fnf_error:
            print(f"Erreur : {fnf_error}")
            raise
        except Exception as e:
            print(f"Erreur lors de la conversion du fichier PDF en TXT : {e}")
            raise

    def remove_file(self, file_path):
        try:
            os.remove(file_path)
            print(f"Fichier supprimé : {file_path}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier : {e}")
            raise
