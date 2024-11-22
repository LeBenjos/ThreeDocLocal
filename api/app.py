from clients.minio_client import MinioClient
from dotenv import load_dotenv
from openai import OpenAI
import os
import ollama

minio_client = MinioClient()
# NEED : Fichier sur minIO
rag_name = 'tdl-BufferGeometry.pdf'
rag_path = minio_client.get_rag(rag_name)

LLAMA_CHAT_COLOR = '\033[95m'
USER_CHAT_COLOR = '\033[93m'
COMMAND_COLOR = '\033[92m'
TEXT_COLOR = '\033[96m'
RESET_COLOR = '\033[0m'

# print(COMMAND_COLOR + "Parsing command-line arguments..." + RESET_COLOR)
# parser = argparse.ArgumentParser(description="Ollama Chat")
# parser.add_argument("--model", default="llama3.2", help="Ollama model to use (default: llama3.2)")
# args = parser.parse_args()

print(COMMAND_COLOR + "Initializing Ollama API client..." + RESET_COLOR)
client = OpenAI(
    base_url=os.getenv('OLLAMA_API_URL'),
    api_key=os.getenv('OLLAMA_API_KEY')
)

print(COMMAND_COLOR + "Loading vault content..." + RESET_COLOR)
vault_content = []
if os.path.exists(rag_path):
    with open(rag_path, "r", encoding='utf-8') as vault_file:
        vault_content = vault_file.readlines()

print(COMMAND_COLOR + "Generating embeddings for the vault content..." + RESET_COLOR)
vault_embeddings = []
for content in vault_content:
    response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
    vault_embeddings.append(response["embedding"])
