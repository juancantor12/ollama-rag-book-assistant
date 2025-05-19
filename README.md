# Ollama local AI app

[![CI Build](https://github.com/juancantor12/ollama-rag-book-assistant/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/juancantor12/ollama-rag-book-assistant/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

**Ollama RAG book assistant** This application allows the user to provide a large book in PDF (text based) and to query the contents of the book using natural language and a local LLM, the generated responses will feature precise, sourced and cited information from the book, including the relation from the retrieved parts of the book with the question and reference to chapters, sections and pages of the book.  
This is achieved by construction a embeddings vector database with the book information and then enhancing the LLM context with related documents fromt he book using RAG.

---

## Features

- **Fully Local** — No external API calls. All processing happens locally and offline.
- **Privacy-First** — Protects your data from third-party services.
- **Open source and LLM-Driven** — Implements local open source models for both user conversations and embeddings generation.
- **DevSecOps Friendly** — Includes CI/CD pipelines, formating, linting, testing, and security scanning.
- **Low hardware requirements** — This app aims to work with models that fit in low end GPUS, it was developed using a RTX2060 12GB, of course more cappable GPUS can be used with bigger models.

---


## Setup

### 1. Clone the repository

```
git clone https://github.com/juancantor12/ollama-rag-book-assistant.git
cd {repo}
```
### 2. Seup environment, either with run.sh on linux or run.ps1 on windows  
For linux soyboys it's advised to setup a virtual environment and activate it first.  
then  

```
./run.sh -setup
```
or well
```
./run.ps1 -setup	# For windows dev gigachads, no venv, test on production
```

## You can optionally run each steps by your own

```
./run.sh -install
```
or
```
./run.ps1 -test
```

This linux bash script uses a make file underneath, steps could also be called using make directly. The github actions CI uses make rather than the run.sh script.  
Both windows and linux run files provide a -help option for more details on available steps.

---

## Usage

### App usage steps

The app works by sourcing a PDF large book (tested with books of about 1200 pages) and generating a vector database with the book embeddings, then this database will be used to enhance the context of a regular LLM chat, using RAG.  
For this, the user has to copy the pdf book to the `data/` folder and then tell the app run script to start the process.

1. Go to the `data/` folder.
2. Paste the book in PDF (text, no scanned images of text) with a recognizable name and make sure the PDF is readable and not locked.
3. Make sure the name of the book doesnt contain spaces or characters that will break the command line parsing, ideally it should be just alphanumeric in lowercase, maybe with underscores
4. The `ask` action won't work until the `generatedb` action has been completed.

After setting up the book, you can use one of the provided scripts for linux or windows respectively:

```
./run.sh -book name_of_my_book.pdf -actions generatedb-ask
```
or well 
```
.\run.ps1 -book name_of_my_book.pdf -actions ask
```

Or run the CLI directly:
```
python -m src.app.cli --book name_of_my_book.pdf --actions generatedb-ask
```

### Output Structure

Each time you run the app, a **new folder** will be automatically created inside the `output/` directory with the name of the book provided.

Inside each book-specific output folder, you will find:

`embeddings.db` | The embeddings vector database generated using chromadb  

`chatlog.json` | A json log of conversations with the LLM  


The embeddings database is overwritten if the `generatedb` action is called again, the `chatlog.json` only appends but doesnt overrite any information
---

## Local LLM Requirements

This app assumes you have:

- Ollama installed and running locally.
- A model of your choice pulled and available for the embeddings generation.
- A model of your choice pulled and available for the chat.

---

### Roadmap & changelog

In the future i plan to add a user interface and may be add a secondary embeddings database with the user interactions to further enchance querying.

---

## Contact

- juancantor.all@gmail.com
