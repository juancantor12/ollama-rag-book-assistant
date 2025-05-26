#!/bin/bash
set -e  # Exit immediately if any command exits with a non-zero status
function show_help() {
    echo "Usage:"
    echo "-book          Name of the book in /data/, the same name will be used for the output/ folder where user generated files will reside."
    echo "-actions       List of actions to perform (dash-separated, no spaces). Defaults to 'all'."
    echo "-install       Installs dependencies."
    echo "-format        Format the code with black."
    echo "-lint          Lint the code with ruff."
    echo "-security      Check code security with bandit."
    echo "-audit         Check dependencies vulnerabilities with pip-audit."
    echo "-test          Run unit tests with pytest."
    echo "-setup         Run install, format, lint, security, audit and test."
    echo "-precommit     Run format, lint, security, audit and test"
    echo "-help          Show this help message."
    echo ""
    echo "Availabe actions: generatedb, ask. ask can only be called if generatedb has been completed.",
    echo ""
    echo "Example: ./run.sh -book my_book.pdf -actions generatedb-ask"
    exit 0
}

execute_action() {
    precommit_steps=("-format" "-lint" "-security" "-audit" "-test")
    setup_steps=("-install" "-format" "-lint" "-security" "-audit" "-test")
    case $1 in
        "-api") make launch-api ;;
        "-install") make install-dependencies ;;
        "-format") make format-code ;;
        "-lint") make lint-code ;;
        "-security") make check-code-security ;;
        "-audit") make check-dependencies-vulnerabilities ;;
        "-test") make unit-testing ;;
    	"-precommit")
    	    for step in "${precommit_steps[@]}"; do
    		execute_action "$step"
    	    done
    	 ;;
         "-setup")
            for step in "${setup_steps[@]}"; do
            execute_action "$step"
            done
         ;;
    	"-help") show_help 
    esac
}

if [ "$1" = "-book" ]; then
    if [ -z "$2" ]; then
	   echo "-book parameter provided but no book value found."
    	exit 1
    elif [ -z "$3" -o "$3" != "-actions" ]; then
    	python -m src.app.cli --book "$2" --actions all
    	exit 0
    elif [ -n "$3" -a "$3" = "-actions" -a -n "$4" ]; then
    	python -m src.app.cli --book "$2" --actions "$4"
    	exit 0
    fi
fi

# Other params
for arg in "$@"; do
    case "$arg" in
        -*) 
            execute_action "$arg"
            exit 0
            ;;
    esac
done
