# 📄 ThreeDocLocal by Benjamin SCHINKEL

## 🚀 Lancer le projet

### 🐳 Docker

**Démarrer tous les services nécessaires avec Docker :**
```bash
docker-compose -p threedoccontainer up --build
```

### 🐑 OLLAMA

**Télécharger les modules nécessaires :**
```bash
ollama pull mxbai-embed-large
```
**Télécharger le modèle llama :**
```bash
ollama run llama3.2:1b
```

### ☁️ MINIO

#### Étapes pour configurer MinIO :
1. Aller sur http://localhost:9001/login

2. Connectez-vous grâce aux informations du docker-compose (id: minioadmin, password: minioadmin)

3. Créer un bucket : **Administrator -> Create Bucket**.

4. Uploader un fichier : **Object Browser -> tdl-bucket -> Upload** donner le fichier disponible dans `./assets`.

### 🌐 API (avec makefile)
**Installer l'application :**
```bash
make setup
```

**Lancer l’API sans changer la température :**
```bash
make run
```

**Lancer l’API en changant la température :**
**Accédez au dossier api :**
```bash
cd api
```

**Lancer l’API en choissant sa température :**
```bash
python3 app.py --temperature 0.7
```

### 🌐 API (sans makefile)

**Accédez au dossier api :**
```bash
cd api
```

**Créez un environnement virtuel :**
```bash
python3 -m venv venv
```

**Activez l’environnement virtuel :**
```bash
source venv/bin/activate
```

**Installez les dépendances nécessaires :**
```bash
pip install -r requirements.txt
```

**Lancer l’API sans changer la température :**
```bash
python3 app.py
```

**Lancer l’API en changant la température :**
```bash
python3 app.py --temperature 0.7
```
