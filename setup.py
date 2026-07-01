import os

# Folders to create
folders = [
    "backend",
    "frontend",
    "scripts",
    "vocabulary_data"
]

# Files to create
files = [
    "backend/main.py",
    "backend/requirements.txt",
    "frontend/index.html",
    "scripts/build_vocabulary.py",
    "scripts/upload_to_github.py",
    "README.md"
]

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"✅ Created folder: {folder}")

# Create files
for file in files:
    with open(file, 'w') as f:
        pass  # Creates empty file
    print(f"✅ Created file: {file}")

print("\n🎉 All folders and files created successfully!")