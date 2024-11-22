# TODO : RAG NO RAG
# TODO : MAKEFILE (DOWLOAD OLLAMA EMBED & LLAMA) PUSH FIRST FILE IN MINIO FOR TEST
# TODO : README

```bash
docker-compose -p threedoccontainer up --build
```

OLLAMA :

```bash 
ollama pull mxbai-embed-large
```

```bash
ollama run llama3.2:1b
```

MINIO:
Créer un bucket
Mettre le fichier disponible dans `./assets` dans le bucket

API:
```bash
cd api
```

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

normal :
```bash
python3 app.py
```

with temp :
```bash
python3 app.py --temperature 0.7
```