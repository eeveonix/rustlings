import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATE_FILE = os.path.join(REPO_ROOT, ".rustlings-state.txt")
EXERCISES_DIR = os.path.join(REPO_ROOT, "exercises")
QUIZZES_DIR = os.path.join(EXERCISES_DIR, "quizzes")
README_FILE = os.path.join(REPO_ROOT, "README.md")

EXERCISE_RE = re.compile(r"^(?P<name>[a-zA-Z_]+?)(?P<num>\d+)$")
QUIZ_RE = re.compile(r"^quiz(?P<num>\d+)$")

def read_completed(path):
    completed = set()

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line == "DON'T EDIT THIS FILE!":
                continue
            completed.add(line)

    return completed

def exercise_sort_key(entry):
    folder_num, name = entry

    match = EXERCISE_RE.match(name)
    if match:
        base = match.group("name")
        num = int(match.group("num"))
    else:
        base = name
        num = 0

    return (folder_num, base, num)

def find_all_exercises(root):
    exercises = []

    for folder in os.listdir(root):
        folder_path = os.path.join(root, folder)
        if not os.path.isdir(folder_path):
            continue

        if folder == "quizzes":
            continue

        try:
            folder_num = int(folder.split("_", 1)[0])
        except ValueError:
            continue

        for file in os.listdir(folder_path):
            if file.endswith(".rs"):
                name = file[:-3]
                exercises.append((folder_num, name))

    exercises.sort(key=exercise_sort_key)
    return [name for _, name in exercises]

def find_quizzes(root):
    quizzes = []

    if not os.path.isdir(root):
        return quizzes

    for file in os.listdir(root):
        if file.endswith(".rs"):
            name = file[:-3]
            match = QUIZ_RE.match(name)
            if match:
                quizzes.append((int(match.group("num")), name))

    quizzes.sort()
    return [name for _, name in quizzes]

def build_table(names, completed, mark_current=False):
    rows = []
    current = None

    for name in names:
        if name in completed:
            status = "completed"
        elif mark_current and current is None:
            status = "current"
            current = name
        else:
            status = "not started"

        rows.append(f"| {name} | {status} |")

    return "\n".join(rows), current

def build_readme(exercises, quizzes, completed):
    exercise_table, current = build_table(exercises, completed, mark_current=True)
    quiz_table, _ = build_table(quizzes, completed, mark_current=False)

    current_text = current if current else "All exercises completed"

    return f"""# Rustlings Progress

Tracking my progress through
[Rustlings](https://github.com/rust-lang/rustlings).

**Current exercise:** `{current_text}`

## Exercises

| Exercise | Status |
|----------|--------|
{exercise_table}

## Quizzes

| Quiz | Status |
|------|--------|
{quiz_table}
"""

def main():
    if not os.path.exists(STATE_FILE):
        print("Error: .rustlings-state.txt not found")
        return

    completed = read_completed(STATE_FILE)
    exercises = find_all_exercises(EXERCISES_DIR)
    quizzes = find_quizzes(QUIZZES_DIR)

    content = build_readme(exercises, quizzes, completed)

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("README.md updated")

if __name__ == "__main__":
    main()
