#!/bin/bash
set -e

show_help() {
    cat <<EOF
Usage:
  -api           Run the fastapi version of the app.
  -apissl        Run the fastapi version of the app with SSL certificates.
  -book <file>   Name of the book in /data/.
  -actions <a>   Dash-separated list of actions (default: all).
  -install       Install dependencies.
  -format        Format code with black.
  -lint          Lint code with ruff.
  -security      Run bandit.
  -audit         Run pip-audit.
  -test          Run pytest.
  -precommit     Run format, lint, security, audit, test.
  -setup         Run install + precommit.
  -help          Show this help.
EOF
}

execute_action() {
    case "$1" in
        api)        uvicorn --app-dir src api.main:run --reload ;;
        apissl)     uvicorn --app-dir src api.main:run --reload --host 0.0.0.0 --port 443 \
                            --ssl-keyfile=key.pem --ssl-certfile=cert.pem ;;
        install)    pip install -r requirements.txt ;;
        format)     black src/ tests/ ;;
        lint)       ruff check src/ tests/ ;;
        security)   bandit -r src/ ;;
        audit)      pip-audit -r requirements.txt ;;
        test)       pytest tests/ -vv ;;
        *)          echo "Unknown action: $1" && exit 1 ;;
    esac
}

# --------------------
# Defaults
# --------------------
BOOK=""
ACTIONS=""
RAN_ACTION=false

# --------------------
# Parse arguments
# --------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        -book)     BOOK="$2"; shift 2 ;;
        -actions)  ACTIONS="$2"; shift 2 ;;
        -api)      execute_action api; RAN_ACTION=true; shift ;;
        -apissl)   execute_action apissl; RAN_ACTION=true; shift ;;
        -install)  execute_action install; RAN_ACTION=true; shift ;;
        -format)   execute_action format; RAN_ACTION=true; shift ;;
        -lint)     execute_action lint; RAN_ACTION=true; shift ;;
        -security) execute_action security; RAN_ACTION=true; shift ;;
        -audit)    execute_action audit; RAN_ACTION=true; shift ;;
        -test)     execute_action test; RAN_ACTION=true; shift ;;
        -precommit)
            for a in format lint security audit test; do execute_action "$a"; done
            RAN_ACTION=true
            shift
            ;;
        -setup)
            for a in install format lint security audit test; do execute_action "$a"; done
            RAN_ACTION=true
            shift
            ;;
        -help) show_help; exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# --------------------
# Interactive prompts
# --------------------
if [[ "$RAN_ACTION" = false ]]; then
    if [[ -z "$BOOK" ]]; then
        read -rp "Enter book name (leave empty to skip): " BOOK
    fi

    if [[ -n "$BOOK" && -z "$ACTIONS" ]]; then
        read -rp "Enter actions (default: all): " ACTIONS
    fi

    ACTIONS=${ACTIONS:-all}

    if [[ -n "$BOOK" ]]; then
        echo "Running the app..."
        python -m src.app.cli --book "$BOOK" --actions "$ACTIONS"
    else
        echo "Nothing to do. Use -help for usage."
    fi
fi
