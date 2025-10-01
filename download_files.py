import urllib.request
import os

files = [
    (".gitignore", "https://raw.githubusercontent.com/sumuko98/InSilico_Genome/8a11909629e9e73eff3e4d7d087404f3920c6b80/.gitignore"),
    ("EXAMPLES.md", "https://raw.githubusercontent.com/sumuko98/InSilico_Genome/8a11909629e9e73eff3e4d7d087404f3920c6b80/EXAMPLES.md"),
    ("QUICKSTART.md", "https://raw.githubusercontent.com/sumuko98/InSilico_Genome/8a11909629e9e73eff3e4d7d087404f3920c6b80/QUICKSTART.md"),
    ("README.md", "https://raw.githubusercontent.com/sumuko98/InSilico_Genome/8a11909629e9e73eff3e4d7d087404f3920c6b80/README.md"),
    ("WORKFLOW.md", "https://raw.githubusercontent.com/sumuko98/InSilico_Genome/8a11909629e9e73eff3e4d7d087404f3920c6b80/WORKFLOW.md"),
    ("example_regions.txt", "https://raw.githubusercontent.com/sumuko98/InSilico_Genome/8a11909629e9e73eff3e4d7d087404f3920c6b80/example_regions.txt"),
    ("remove_genomic_regions.py", "https://raw.githubusercontent.com/sumuko98/InSilico_Genome/8a11909629e9e73eff3e4d7d087404f3920c6b80/remove_genomic_regions.py"),
    ("remove_regions.sh", "https://raw.githubusercontent.com/sumuko98/InSilico_Genome/8a11909629e9e73eff3e4d7d087404f3920c6b80/remove_regions.sh"),
    ("test_removal.py", "https://raw.githubusercontent.com/sumuko98/InSilico_Genome/8a11909629e9e73eff3e4d7d087404f3920c6b80/test_removal.py"),
]

for filename, url in files:
    try:
        print(f"Downloading {filename}...")
        with urllib.request.urlopen(url) as response:
            content = response.read()
        with open(filename, 'wb') as f:
            f.write(content)
        if filename.endswith('.sh') or filename.endswith('.py'):
            os.chmod(filename, 0o755)
        print(f"  ✓ {filename} downloaded")
    except Exception as e:
        print(f"  ✗ Failed to download {filename}: {e}")

print("Done!")
