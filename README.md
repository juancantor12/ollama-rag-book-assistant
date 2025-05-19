# Ollama local AI app

[![CI Build](https://github.com/juancantor12/ollama-python-skeleton/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/juancantor12/ollama-python-skeleton/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

**App** [Bried description of the app and main features]

---

## Features

- **Fully Local** — No external API calls. All processing happens locally.
- **Privacy-First** — Protects your data from third-party services.
- **LLM-Driven** — Implements local LLM models for specific tasks.
- **DevSecOps Friendly** — Includes CI/CD pipelines, formating, linting, testing, and security scanning.

---


## Setup

### 1. Clone the repository

```
git clone https://github.com/{user}/{repo}.git
cd {repo}
```
### 2. Seup environment, either with run.sh on linux or run.ps1 on windows  
For linux soyboys it's advised to setup a virtual environment and activate it first.  

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

This linux bash script uses a make file underneath, steps could also be called using make directly.
Both windows and linux run files provide a -help option for more details on available steps.

---

## Usage

### App usage steps

{Describe how to use the app from the terminal or from the UI if an UI is available}

1. Go to the `data/` folder.
2. Fill in required data for the app to run.

After setting up, you can use one of the provided scripts for linux or windows respectively:

```
./run.sh -output-folder test_folder -actions action1-action2
```
```
.\run.ps1 -output-folder test_folder -actions action1
```

Or run the CLI directly:
```
python -m src.app.cli --output-folder test_folder --actions action1-action2
```

### Output Structure

Each time you run the app, a **new folder** will be automatically created inside the `output/` directory with the folder name you provided.

Inside each job-specific output folder, you will find:

`any_generated_output.txt` | Any file the app is supposed to generate  


{Aditional info or notes about generated files}

---

## Local LLM Requirements

This app assumes you have:

- Ollama installed and running locally.
- A model of your choice pulled and available.

---

### Roadmap & changelog

{Additional roadmap and changelog info}

---

## Contact

- {user@email.com}
