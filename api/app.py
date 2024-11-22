from clients.minio_client import MinioClient
from dotenv import load_dotenv
from openai import OpenAI
import os
import ollama
import torch
import argparse
import json
from typing import List, Dict

LLAMA_CHAT_COLOR = '\033[95m'
USER_CHAT_COLOR = '\033[93m'
COMMAND_COLOR = '\033[92m'
INFORMATION_COLOR = '\033[96m'
ERROR_COLOR = "\033[31m"
RESET_COLOR = '\033[0m'

def print_colored_message(color: str, message: str) -> None:
    print(f"{color}{message}{RESET_COLOR}")

def load_vault_content(path: str) -> List[str]:
    if not os.path.exists(path):
        print_colored_message(ERROR_COLOR, f"Vault file does not exist at: {path}")
        return []
    try:
        with open(path, "r", encoding='utf-8') as vault_file:
            return vault_file.readlines()
    except Exception as e:
        print_colored_message(ERROR_COLOR, f"Error loading vault content: {e}")
        return []

def generate_embeddings(vault_content: List[str]) -> List[List[float]]:
    vault_embeddings = []
    for content in vault_content:
        try:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            vault_embeddings.append(response["embedding"])
        except Exception as e:
            print_colored_message(ERROR_COLOR, f"Error generating embeddings for content: {e}")
    return vault_embeddings

def get_relevant_context(rewritten_input: str, vault_embeddings: torch.Tensor, vault_content: List[str], top_k: int = 3) -> List[str]:
    if vault_embeddings.nelement() == 0:
        return []
    try:
        input_embedding = torch.tensor(ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"])
        cos_scores = torch.cosine_similarity(input_embedding.unsqueeze(0), vault_embeddings)
        top_indices = torch.topk(cos_scores, k=min(top_k, len(cos_scores))).indices.tolist()
        return [vault_content[idx].strip() for idx in top_indices]
    except Exception as e:
        print_colored_message(ERROR_COLOR, f"Error retrieving relevant context: {e}")
        return []

def rewrite_query(user_input_json: str, conversation_history: List[Dict[str, str]], ollama_model: str) -> str:
    user_input = json.loads(user_input_json)["Query"]
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-2:]])
    prompt = f"""
    Rewrite the following query by incorporating relevant context from the conversation history.
    Preserve the core intent and meaning of the original query. Avoid introducing new topics.

    Conversation History:
    {context}

    Original query: {user_input}

    Rewritten query:
    """
    try:
        response = client.chat.completions.create(
            model=ollama_model,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=200,
            n=1,
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print_colored_message(ERROR_COLOR, f"Error rewriting query: {e}")
        return user_input

def ollama_chat(user_input: str, system_message: str, vault_embeddings: torch.Tensor, vault_content: List[str],
                ollama_model: str, conversation_history: List[Dict[str, str]]) -> str:
    conversation_history.append({"role": "user", "content": user_input})

    rewritten_query = user_input
    if len(conversation_history) > 1:
        try:
            query_json = json.dumps({"Query": user_input})
            rewritten_query = rewrite_query(query_json, conversation_history, ollama_model)
            print_colored_message(INFORMATION_COLOR, f"Rewritten Query: {rewritten_query}")
        except Exception as e:
            print_colored_message(ERROR_COLOR, f"Error during query rewriting: {e}")

    relevant_context = get_relevant_context(rewritten_query, vault_embeddings, vault_content)
    if relevant_context:
        context_str = "\n".join(relevant_context)
        print_colored_message(INFORMATION_COLOR, f"Context Pulled from Documents: \n\n{context_str}")
    else:
        print_colored_message(INFORMATION_COLOR, "No relevant context found.")

    user_input_with_context = f"{user_input}\n\nRelevant Context:\n{context_str}" if relevant_context else user_input
    conversation_history[-1]["content"] = user_input_with_context

    messages = [{"role": "system", "content": system_message}, *conversation_history]
    try:
        response = client.chat.completions.create(
            model=ollama_model,
            messages=messages,
            max_tokens=2000,
        )
        assistant_response = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_response})
        return assistant_response
    except Exception as e:
        print_colored_message(ERROR_COLOR, f"Error during chat response: {e}")
        return "An error occurred while processing your request."

if __name__ == "__main__":
    print_colored_message(COMMAND_COLOR, "Parsing command-line arguments...")
    parser = argparse.ArgumentParser(description="Ollama Chat with RAG and non-RAG options")
    parser.add_argument("--model", default="llama3.2:1b", help="Ollama model to use (default: llama3.2:1b)")
    parser.add_argument("--temperature", type=float, default=0.7, help="Set the temperature for responses (default: 0.7)")
    args = parser.parse_args()

    print_colored_message(COMMAND_COLOR, "Initializing Ollama API client...")
    client = OpenAI(
        base_url=os.getenv('OLLAMA_API_URL'),
        api_key=os.getenv('OLLAMA_API_KEY')
    )

    print_colored_message(COMMAND_COLOR, "Loading vault content...")
    minio_client = MinioClient()
    rag_path = minio_client.get_rag('tdl-BufferGeometry.pdf')
    vault_content = load_vault_content(rag_path)

    print_colored_message(COMMAND_COLOR, "Generating embeddings for the vault content...")
    vault_embeddings = torch.tensor(generate_embeddings(vault_content))

    print_colored_message(COMMAND_COLOR, "Starting conversation loop...")
    conversation_history = []
    system_message = (
        "You are a helpful assistant with expertise in Three.js. "
        "Explain concepts clearly and provide relevant examples. "
    )

    while True:
        user_input = input(USER_CHAT_COLOR + "Ask a query about your documents (or type 'quit' to exit): " + RESET_COLOR)
        if user_input.lower() == 'quit':
            print_colored_message(COMMAND_COLOR, "Exiting the conversation loop.")
            break

        print_colored_message(COMMAND_COLOR, "Choose response mode: 1 for Non-RAG, 2 for RAG")
        mode = input(USER_CHAT_COLOR + "Enter mode (1 or 2): " + RESET_COLOR).strip()

        if mode == '1':
            print_colored_message(COMMAND_COLOR, "Generating response WITHOUT RAG...")
            messages = [{"role": "system", "content": system_message}, {"role": "user", "content": user_input}]
            try:
                response = client.chat.completions.create(
                    model=args.model,
                    messages=messages,
                    max_tokens=2000,
                    temperature=args.temperature,
                )
                assistant_response = response.choices[0].message.content
                print_colored_message(LLAMA_CHAT_COLOR, f"Response (Non-RAG): \n\n{assistant_response}")
            except Exception as e:
                print_colored_message(ERROR_COLOR, f"Error generating Non-RAG response: {e}")

        elif mode == '2':
            print_colored_message(COMMAND_COLOR, "Generating response WITH RAG...")
            response = ollama_chat(
                user_input=user_input,
                system_message=system_message,
                vault_embeddings=vault_embeddings,
                vault_content=vault_content,
                ollama_model=args.model,
                conversation_history=conversation_history
            )
            print_colored_message(LLAMA_CHAT_COLOR, f"Response (RAG): \n\n{response}")

        else:
            print_colored_message(ERROR_COLOR, "Invalid mode. Please choose either 1 or 2.")
