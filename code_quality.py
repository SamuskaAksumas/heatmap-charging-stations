"""Code Quality Dashboard - Test Coverage & Pylint Stats."""
import subprocess
import sys
import re


def run_command(cmd: list[str]) -> str:
    """Run command and return output."""
    import os
    env = os.environ.copy()
    
    # FIX: Use the current directory on your Mac instead of a hardcoded path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env["PYTHONPATH"] = current_dir
    
    # FIX: Changed cwd from "/workspace/work" to current_dir
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        cwd=current_dir, 
        env=env
    )
    return result.stdout + result.stderr


def get_test_coverage() -> dict:
    """Run pytest with coverage and extract stats."""
    print("Running tests with coverage...")
    output = run_command([
        sys.executable, "-m", "pytest", "tests/",
        "--cov=src", "--cov-report=term-missing", "-q"
    ])

    # Parse coverage percentage
    match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
    coverage_pct = int(match.group(1)) if match else 0

    # Parse test results
    test_match = re.search(r"(\d+) passed", output)
    tests_passed = int(test_match.group(1)) if test_match else 0

    # Parse coverage per layer
    layers = {
        "Domain": {"files": [], "total_stmts": 0, "covered_stmts": 0},
        "Application": {"files": [], "total_stmts": 0, "covered_stmts": 0},
        "Infrastructure": {"files": [], "total_stmts": 0, "covered_stmts": 0},
        "Presentation": {"files": [], "total_stmts": 0, "covered_stmts": 0},
    }

    for line in output.split("\n"):
        match = re.match(r"(src/\S+\.py)\s+(\d+)\s+(\d+)\s+(\d+)%", line)
        if match:
            filepath, stmts, miss, pct = match.groups()
            stmts, miss = int(stmts), int(miss)
            covered = stmts - miss

            if "/domain/" in filepath:
                layer = "Domain"
            elif "/application/" in filepath:
                layer = "Application"
            elif "/infrastructure/" in filepath:
                layer = "Infrastructure"
            elif "/presentation/" in filepath:
                layer = "Presentation"
            else:
                continue

            layers[layer]["total_stmts"] += stmts
            layers[layer]["covered_stmts"] += covered

    # Calculate percentages
    for layer in layers.values():
        if layer["total_stmts"] > 0:
            layer["percent"] = int(100 * layer["covered_stmts"] / layer["total_stmts"])
        else:
            layer["percent"] = 0

    return {
        "coverage_percent": coverage_pct,
        "tests_passed": tests_passed,
        "layers": layers,
        "raw_output": output
    }


def get_pylint_score() -> dict:
    """Run pylint and extract score."""
    print("Running pylint...")
    output = run_command([
        sys.executable, "-m", "pylint", "src/",
        "--disable=C0114,C0115,C0116",  # Disable missing docstring warnings
        "--max-line-length=120",
        "--exit-zero"
    ])

    # Parse score
    match = re.search(r"Your code has been rated at ([\d.]+)/10", output)
    score = float(match.group(1)) if match else 0.0

    # Count issues by type
    errors = len(re.findall(r"^E\d{4}:", output, re.MULTILINE))
    warnings = len(re.findall(r"^W\d{4}:", output, re.MULTILINE))
    conventions = len(re.findall(r"^C\d{4}:", output, re.MULTILINE))
    refactors = len(re.findall(r"^R\d{4}:", output, re.MULTILINE))

    return {
        "score": score,
        "errors": errors,
        "warnings": warnings,
        "conventions": conventions,
        "refactors": refactors,
        "raw_output": output
    }


def count_lines() -> dict:
    """Count lines of code."""
    import glob

    total_lines = 0
    total_files = 0

    for pattern in ["src/**/*.py", "tests/**/*.py"]:
        for filepath in glob.glob(pattern, recursive=True):
            with open(filepath, "r") as f:
                lines = len([l for l in f.readlines() if l.strip() and not l.strip().startswith("#")])
                total_lines += lines
                total_files += 1

    return {"files": total_files, "lines": total_lines}


def print_dashboard():
    """Print the code quality dashboard."""
    print("\n" + "=" * 60)
    print("           CODE QUALITY DASHBOARD")
    print("=" * 60 + "\n")

    # Lines of code
    loc = count_lines()
    print(f"Lines of Code:     {loc['lines']} lines in {loc['files']} files\n")

    # Test Coverage
    coverage = get_test_coverage()
    print("-" * 40)
    print("TEST COVERAGE")
    print("-" * 40)
    bar_filled = int(coverage["coverage_percent"] / 5)
    bar = "[" + "#" * bar_filled + "." * (20 - bar_filled) + "]"
    print(f"Total:             {bar} {coverage['coverage_percent']}%")
    print(f"Tests Passed:      {coverage['tests_passed']}")
    print()

    # Coverage per DDD Layer
    print("Coverage per Layer (DDD):")
    for layer_name, layer_data in coverage["layers"].items():
        pct = layer_data["percent"]
        bar_filled = int(pct / 5)
        bar = "[" + "#" * bar_filled + "." * (20 - bar_filled) + "]"
        status = "OK" if pct >= 80 else "  "
        print(f"  {layer_name:15}  {bar} {pct:3}%  {status}")
    print()

    # Pylint
    pylint = get_pylint_score()
    print("-" * 40)
    print("PYLINT SCORE")
    print("-" * 40)
    bar_filled = int(pylint["score"])
    bar = "[" + "#" * bar_filled + "." * (10 - bar_filled) + "]"
    print(f"Score:             {bar} {pylint['score']}/10")
    print(f"Errors:            {pylint['errors']}")
    print(f"Warnings:          {pylint['warnings']}")
    print(f"Refactor hints:    {pylint['refactors']}")
    print()
    print("Pylint checks:")
    print("  - Code style (PEP8 naming, line length)")
    print("  - Errors (undefined variables, bad imports)")
    print("  - Refactoring (duplicate code, complexity)")
    print("  - Design (too many arguments, deep nesting)")
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    domain_ok = coverage["layers"]["Domain"]["percent"] >= 80
    app_ok = coverage["layers"]["Application"]["percent"] >= 80
    pylint_ok = pylint["score"] >= 7

    print(f"Domain Layer:      {'WELL TESTED' if domain_ok else 'NEEDS TESTS'}")
    print(f"Application Layer: {'WELL TESTED' if app_ok else 'NEEDS TESTS'}")
    print(f"Code Quality:      {'GOOD' if pylint_ok else 'NEEDS WORK'}")
    print()

    if domain_ok and app_ok:
        print("Business logic is well tested - Presentation/Infrastructure")
        print("have lower coverage which is acceptable for a DDD demo.")
    print()


if __name__ == "__main__":
    print_dashboard()
