import os
from pathlib import Path

import pathspec

MAX_FILE_SIZE_KB = 150  
MAX_TOTAL_CHARS = 400_000

# Extended to cover all major ecosystems, not just Python
PRIORITY_FILES = {
    # Python
    "main.py", "cli.py", "app.py", "index.py",
    "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
    # JavaScript / TypeScript
    "package.json", "tsconfig.json", "index.ts", "index.js",
    "index.tsx", "index.jsx", "vite.config.ts", "vite.config.js",
    "next.config.js", "next.config.ts",
    # Rust
    "Cargo.toml",
    # Go
    "go.mod",
    # Java / Kotlin / Scala
    "pom.xml", "build.gradle", "build.gradle.kts",
    # Ruby
    "Gemfile",
    # Infra / Config
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "Makefile", ".env.example", "config.yml", "config.yaml",
    ".gitignore",
}

# Extension whitelist: only text-based, LLM-useful file types
TEXT_EXTENSIONS = {
    # Source code
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".rs", ".go", ".java", ".kt", ".scala", ".rb", ".php",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".swift", ".m",
    ".lua", ".r", ".jl", ".ex", ".exs", ".erl", ".hs",
    ".sh", ".bash", ".zsh", ".fish", ".ps1",
    # Config / data
    ".toml", ".yaml", ".yml", ".json", ".xml", ".ini",
    ".cfg", ".conf", ".env", ".properties",
    # Docs / markup
    ".md", ".mdx", ".rst", ".txt", ".tex",
    # Web
    ".html", ".htm", ".css", ".scss", ".sass", ".less", ".vue", ".svelte",
    # SQL
    ".sql",
}

# Hardcoded ignores that must always apply, regardless of .gitignore
ALWAYS_IGNORE = [
    # Version control
    ".git/",
    # Python
    ".venv/", "venv/", "env/", "__pycache__/", "*.egg-info/",
    ".python-version", ".env", ".env.*",
    # Node
    "node_modules/", ".npm/", ".yarn/",
    # Build outputs
    "dist/", "build/", "out/", ".next/", ".nuxt/", ".output/",
    "target/",          # Rust / Maven
    "bin/", "obj/",     # .NET
    # Lock files (rarely useful for README generation)
    "*.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    # Compiled / binary artifacts
    "*.pyc", "*.pyo", "*.class", "*.o", "*.a", "*.so", "*.dll", "*.exe",
    # Media / fonts (unreadable as text)
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.ico",
    "*.woff", "*.woff2", "*.ttf", "*.eot",
    # Data files
    "*.csv", "*.db", "*.sqlite", "*.sqlite3",
    # Misc
    ".DS_Store", "Thumbs.db", "*.min.js", "*.min.css", "*.map",
    "coverage/", ".coverage", ".pytest_cache/", ".mypy_cache/",
]


def get_ignore_spec(root_path: Path) -> pathspec.PathSpec:
    ignore_lines = list(ALWAYS_IGNORE)

    gitignore_path = root_path / ".gitignore"
    if gitignore_path.exists():
        with gitignore_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                # Skip blank lines and comments
                if stripped and not stripped.startswith("#"):
                    ignore_lines.append(stripped)

    return pathspec.GitIgnoreSpec.from_lines(ignore_lines)


def is_binary_file(filepath: Path) -> bool:
    """
    Quick binary sniff: read the first 8KB and look for null bytes.
    This catches compiled files, images, archives, etc. that slipped
    past the extension whitelist (e.g. extensionless executables).
    """
    try:
        with filepath.open("rb") as f:
            chunk = f.read(8192)
        return b"\x00" in chunk
    except OSError:
        return True


def scan_codebase(root: str = ".") -> dict:
    tree = []
    files = {}
    priority_files = {}   # collected separately to guarantee budget priority
    other_files = {}

    root_path = Path(root).resolve()
    spec = get_ignore_spec(root_path)

    for dirpath, dirnames, filenames in os.walk(root_path):
        rel_dir = Path(dirpath).relative_to(root_path)

        # Prune ignored directories in-place so os.walk won't descend into them
        dirnames[:] = [
            d for d in dirnames
            if not spec.match_file((rel_dir / d).as_posix() + "/")
        ]

        for filename in filenames:
            filepath = Path(dirpath) / filename
            rel_path = filepath.relative_to(root_path).as_posix()

            # 1. Ignore-spec check
            if spec.match_file(rel_path):
                continue

            # 2. Add to the structural map (The LLM MUST see the whole architecture)
            tree.append(rel_path)

            is_priority = filepath.name in PRIORITY_FILES

            # 3. Whitelist & Binary checks (Fixed Security Gate)
            has_extension = filepath.suffix != ""
            if has_extension and filepath.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            
            # Unconditional safety net for all files
            if is_binary_file(filepath):  
                continue

            # 4. File size cap (Fixed Reporting)
            if filepath.stat().st_size > MAX_FILE_SIZE_KB * 1024:
                skip_msg = f"[SKIPPED: Exceeds {MAX_FILE_SIZE_KB}KB limit]"
                if is_priority:
                    priority_files[rel_path] = skip_msg
                else:
                    other_files[rel_path] = skip_msg
                continue

            # 5. Read contents
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                content = "[unreadable]"

            # 6. Bucket into priority vs other
            if is_priority:
                priority_files[rel_path] = content
            else:
                other_files[rel_path] = content

    # Priority files first, then the rest (both sorted alphabetically within group)
    files = {
        **dict(sorted(priority_files.items())),
        **dict(sorted(other_files.items())),
    }

    return {"tree": tree, "files": files}


def format_codebase_for_prompt(scan_result: dict) -> str:
    limit = max(0, MAX_TOTAL_CHARS)
    result = ""
    truncation_marker = "\n...[TRUNCATED AT BUDGET LIMIT]"

    def append_section(section: str) -> bool:
        nonlocal result
        separator = "\n" if result else ""
        remaining = limit - len(result)
        addition = separator + section
        if len(addition) <= remaining:
            result += addition
            return True

        available = max(0, remaining - len(separator))
        if available:
            if available > len(truncation_marker):
                result += separator + section[: available - len(truncation_marker)]
                result += truncation_marker
            else:
                result += separator + section[:available]
        return False

    append_section("=== PROJECT FILE TREE ===")
    for path in sorted(scan_result["tree"]):
        if not append_section(f"  {path}"):
            return result

    if not append_section("=== FILE CONTENTS ==="):
        return result

    for path, content in scan_result["files"].items():
        if not append_section(f"--- {path} ---\n{content}"):
            return result

    return result
