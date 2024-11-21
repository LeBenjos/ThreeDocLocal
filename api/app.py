from databases.minio_client import MinioClient
from dotenv import load_dotenv
import os

load_dotenv()

minio_url = os.getenv('MINIO_URL')
access_key = os.getenv('MINIO_ACCESS_KEY')
secret_key = os.getenv('MINIO_SECRET_KEY')

bucket_name = 'tdl-bucket'
object_name = 'tdl-BufferGeometry.pdf'
local_file_path = './rags/tdl-BufferGeometry.pdf'

minio_client = MinioClient(minio_url, access_key, secret_key)
minio_client.download_file(bucket_name, object_name, local_file_path)
