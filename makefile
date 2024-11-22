# Variables
PROJECT_NAME = ThreeDocLocal
PYTHON = python3
PIP = pip
API_DIR = api
VENV_DIR = $(API_DIR)/venv
REQUIREMENTS_FILE = $(API_DIR)/requirements.txt
MAIN_FILE = app.py

# Règles
.PHONY: help setup install run clean

help:
	@echo "Utilisation du Makefile pour $(PROJECT_NAME):"
	@echo "  make setup    - Initialiser le projet (crée un environnement virtuel, installe les dépendances)"
	@echo "  make install  - Installer les dépendances à partir de $(REQUIREMENTS_FILE)"
	@echo "  make run      - Démarrer l'application"
	@echo "  make clean    - Nettoyer les fichiers temporaires et l'environnement virtuel"

setup: $(VENV_DIR)

$(VENV_DIR):
	@echo "Création de l'environnement virtuel dans $(API_DIR)..."
	cd $(API_DIR) && $(PYTHON) -m venv venv
	@echo "Activation de l'environnement virtuel et installation des dépendances..."
	cd $(API_DIR) && . venv/bin/activate && $(PIP) install --upgrade pip && $(PIP) install -r requirements.txt

install:
	@echo "Installation des dépendances dans $(API_DIR)..."
	cd $(API_DIR) && venv/bin/$(PIP) install -r $(REQUIREMENTS_FILE)

run:
	@echo "Démarrage de l'application dans $(API_DIR)..."
	cd $(API_DIR) && venv/bin/$(PYTHON) $(MAIN_FILE)

clean:
	@echo "Nettoyage des fichiers temporaires dans $(API_DIR)..."
	rm -rf $(VENV_DIR)
	find $(API_DIR) -type d -name "__pycache__" -exec rm -rf {} +
	find $(API_DIR) -type f -name "*.pyc" -delete
	find $(API_DIR) -type f -name "*.pyo" -delete
	@echo "Nettoyage terminé."
