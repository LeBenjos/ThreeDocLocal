from clients.minio_client import MinioClient
from dotenv import load_dotenv
from openai import OpenAI
import os
import ollama
import torch
import argparse
import json

minio_client = MinioClient()
# NEED : Fichier sur minIO
rag_name = 'tdl-BufferGeometry.pdf'
rag_path = minio_client.get_rag(rag_name)

LLAMA_CHAT_COLOR = '\033[95m'
USER_CHAT_COLOR = '\033[93m'
COMMAND_COLOR = '\033[92m'
INFORMATION_COLOR = '\033[96m'
ERROR_COLOR = "\033[31m"
RESET_COLOR = '\033[0m'

def print_colored_message(color, message):
    print(color + message + RESET_COLOR)

def load_vault_content(path):
    vault_content = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding='utf-8') as vault_file:
                vault_content = vault_file.readlines()
        except Exception as e:
            print_colored_message(ERROR_COLOR, f"Error loading vault content: {e}")
    else:
        print_colored_message(COMMAND_COLOR, f"Vault file does not exist at: {path}")
    return vault_content

def generate_embeddings(vault_content):
    vault_embeddings = []
    for content in vault_content:
        try:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            vault_embeddings.append(response["embedding"])
        except Exception as e:
            print_colored_message(ERROR_COLOR, f"Error generating embeddings for content: {e}")
    return vault_embeddings

def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:
        return []

    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    top_k = min(top_k, len(cos_scores))
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    relevant_context = [vault_content[idx].strip() for idx in top_indices]
    return relevant_context

def rewrite_query(user_input_json, conversation_history, ollama_model):
    user_input = json.loads(user_input_json)["Query"]
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-2:]])
    prompt = f"""Rewrite the following query by incorporating relevant context from the conversation history.
    The rewritten query should:

    - Preserve the core intent and meaning of the original query
    - Expand and clarify the query to make it more specific and informative for retrieving relevant context
    - Avoid introducing new topics or queries that deviate from the original query
    - DONT EVER ANSWER the Original query, but instead focus on rephrasing and expanding it into a new query

    Return ONLY the rewritten query text, without any additional formatting or explanations.

    Conversation History:
    {context}

    Original query: [{user_input}]

    Rewritten query: 
    """
    response = client.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
        n=1,
        temperature=0.1,
    )
    rewritten_query = response.choices[0].message.content.strip()
    return json.dumps({"Rewritten Query": rewritten_query})

def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})

    if len(conversation_history) > 1:
        query_json = {
            "Query": user_input,
            "Rewritten Query": ""
        }
        rewritten_query_json = rewrite_query(json.dumps(query_json), conversation_history, ollama_model)
        rewritten_query_data = json.loads(rewritten_query_json)
        rewritten_query = rewritten_query_data["Rewritten Query"]
        print_colored_message(INFORMATION_COLOR, "Original Query: ")
        print_colored_message(INFORMATION_COLOR, "Rewritten Query: ")
    else:
        rewritten_query = user_input

    relevant_context = get_relevant_context(rewritten_query, vault_embeddings, vault_content)
    if relevant_context:
        context_str = "\n".join(relevant_context)
        print_colored_message(INFORMATION_COLOR, f"Context Pulled from Documents: \n\n{context_str}")
    else:
       print_colored_message(INFORMATION_COLOR, "No relevant context found.",)

    user_input_with_context = user_input
    if relevant_context:
        user_input_with_context = user_input + "\n\nRelevant Context:\n" + context_str

    conversation_history[-1]["content"] = user_input_with_context

    messages = [
        {"role": "system", "content": system_message},
        *conversation_history
    ]

    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages,
        max_tokens=2000,
    )

    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})

    return response.choices[0].message.content

print_colored_message(COMMAND_COLOR, "Parsing command-line arguments...")
parser = argparse.ArgumentParser(description="Ollama Chat")
parser.add_argument("--model", default="llama3.2:1b", help="Ollama model to use (default: llama3.2:1b)")
args = parser.parse_args()

print_colored_message(COMMAND_COLOR, "Initializing Ollama API client...")
client = OpenAI(
    base_url=os.getenv('OLLAMA_API_URL'),
    api_key=os.getenv('OLLAMA_API_KEY')
)

print_colored_message(COMMAND_COLOR, "Loading vault content...")
vault_content = load_vault_content(rag_path)

print_colored_message(COMMAND_COLOR, "Generating embeddings for the vault content...")
vault_embeddings = generate_embeddings(vault_content)

print_colored_message(COMMAND_COLOR, "Converting embeddings to tensor...")
vault_embeddings_tensor = torch.tensor(vault_embeddings)

print_colored_message(COMMAND_COLOR, "Starting conversation loop...")
conversation_history = []
system_message = (
    "You are a helpful assistant with expertise in Three.js, capable of extracting "
    "key information from its documentation and explaining complex concepts clearly. "
    "You also bring in additional relevant details and examples from external sources to "
    "help the user fully understand their query. And You love Bruno SIMON"
)

while True:
    user_input = input(USER_CHAT_COLOR + "Ask a query about your documents (or type 'quit' to exit): " + RESET_COLOR)
    
    if user_input.lower() == 'quit':
        print_colored_message(COMMAND_COLOR, "Exiting the conversation loop.")
        break

    try:
        response = ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, args.model, conversation_history)
        print_colored_message(LLAMA_CHAT_COLOR, f"Response: \n\n{response}")
    except Exception as e:
        print_colored_message(ERROR_COLOR, f"Error during chat response: {e}")
