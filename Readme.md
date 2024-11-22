# TODO : OLLAMA
# TODO : RAG NO RAG
# TODO : MAKEFILE (DOWLOAD OLLAMA EMBED & LLAMA) PUSH FIRST FILE IN MINIO FOR TEST
# TODO : README

```bash
docker-compose -p threedoccontainer up --build
```

```bash 
ollama pull mxbai-embed-large
```

```bash
ollama run llama3.2:1b
```

```bash
cd api
```

```bash
python3.12 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
python3 app.py
```