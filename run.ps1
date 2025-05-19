param (
    [string]$book,       # Name of the book in /data/, the same name will be used for the output/ folder where user generated files will reside
    [string]$actions,    # Which actions to perform, if empty, all are executed
    [switch]$install,
    [switch]$format,
    [switch]$lint,
    [switch]$security,
    [switch]$audit,
    [switch]$test,
    [switch]$precommit,
    [switch]$setup,
    [switch]$help
)
$ErrorActionPreference = "Stop"

function Execute-Action {
    param (
        [string]$action
    )
    Write-Host "$action..."
    switch ($action) {
        "install" { pip install -r requirements.txt }
        "format" { black src/ tests/ }
        "lint" { ruff check src/ tests/ }
        "security" { bandit -r src/ }
        "audit" { pip-audit -r requirements.txt }
        "test" { pytest tests/ -vv }
    }
}

if ($help){
    Write-Host (
        @(
            "Usage:",
            "-book          Name of the book in /data/, the same name will be used for the output/ folder where user generated files will reside",
            "-actions       List of actions to perform (dash-separated, no spaces). Defaults to 'all'.",
            "-install       Installs dependencies",
            "-format        Format the code with black.",
            "-lint          Lint the code with ruff.",
            "-security      Check code security with bandit.",
            "-audit         Check dependencies vulnerabilities with pip-audit.",
            "-test          Run unit tests with pytest",
            "-precommit     Run format, lint, security, audit and test"
            "-setup         Run install, format, lint, security, audit and test.",
            "-help          Show this help message."
            "",
            "Availabe actions: generatedb, ask. ask can only be called if generatedb has been completed.",
            "If no actions are provided, all will run",
            "",
            "Example: .\\run.ps1 -book my_book.pdf -actions generatedb-ask"
        ) -join [Environment]::NewLine
    )
    exit 0
}

if ($install) { Execute-Action -action "install"; exit }
if ($format) { Execute-Action -action "format"; exit }
if ($lint) { Execute-Action -action "lint"; exit }
if ($security) { Execute-Action -action "security"; exit }
if ($audit) { Execute-Action -action "audit"; exit }
if ($test) { Execute-Action -action "test"; exit }
if ($precommit) { 
    "format", "lint", "security", "audit", "test" | ForEach-Object { Execute-Action -action $_ }
    exit
}
if ($setup) { 
    "install", "format", "lint", "security", "audit", "test" | ForEach-Object { Execute-Action -action $_ }
    exit
}

if ($book) {
    Write-Host "Running the app"
    $script_action = "all"
    if($actions){
        $script_action = $actions
    }
    python -m src.app.cli --book $book --actions $script_action
    exit 0
}