from clients.minio_client import MinioClient

rag_name = 'tdl-BufferGeometry.pdf'

minio_client = MinioClient()
minio_client.get_rag(rag_name)
