"""
Download Word Data Script
Downloads GloVe, WordNet, spaCy models, and other word embeddings
Run this script once to download all word data
"""

import os
import sys
import requests
import zipfile
import gzip
import shutil
from pathlib import Path
import nltk
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class WordDataDownloader:
    """Download all word data for AI Humanizer"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "backend" / "word_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        print("=" * 60)
        print("📦 WORD DATA DOWNLOADER")
        print("=" * 60)
        print(f"📁 Data directory: {self.data_dir}")
        print("=" * 60)
    
    def download_wordnet(self):
        """Download WordNet using NLTK"""
        print("\n📥 Downloading WordNet...")
        try:
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
            print("✅ WordNet downloaded successfully!")
            return True
        except Exception as e:
            print(f"❌ WordNet download failed: {e}")
            return False
    
    def download_spacy_model(self):
        """Download spaCy language model"""
        print("\n📥 Downloading spaCy model (en_core_web_sm)...")
        try:
            subprocess.run(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                check=True,
                capture_output=True
            )
            print("✅ spaCy model downloaded successfully!")
            return True
        except Exception as e:
            print(f"❌ spaCy model download failed: {e}")
            return False
    
    def download_glove(self):
        """Download GloVe embeddings (Optional - Large file)"""
        print("\n📥 Downloading GloVe embeddings (822 MB)...")
        print("⚠️ This is optional and may take several minutes.")
        
        response = input("Download GloVe? (y/n): ")
        if response.lower() != 'y':
            print("⏭️ Skipping GloVe download")
            return True
        
        url = "https://nlp.stanford.edu/data/glove.6B.zip"
        zip_path = self.data_dir / "glove.zip"
        glove_dir = self.data_dir / "glove"
        glove_dir.mkdir(exist_ok=True)
        
        try:
            # Download with progress
            print("📥 Downloading...")
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(zip_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Progress bar
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r   Progress: {percent:.1f}%", end="")
            
            print("\n📦 Extracting...")
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(glove_dir)
            
            os.remove(zip_path)
            print("✅ GloVe downloaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ GloVe download failed: {e}")
            return False
    
    def download_all(self):
        """Download all word data"""
        print("\n" + "=" * 60)
        print("🚀 STARTING DOWNLOADS")
        print("=" * 60)
        
        success = True
        
        # Download WordNet
        if not self.download_wordnet():
            success = False
        
        # Download spaCy model
        if not self.download_spacy_model():
            success = False
        
        # Download GloVe (optional)
        if not self.download_glove():
            success = False
        
        print("\n" + "=" * 60)
        if success:
            print("✅ All word data downloaded successfully!")
        else:
            print("⚠️ Some downloads failed. Check logs above.")
        print("=" * 60)
        
        # Show what was downloaded
        self.show_downloaded_files()
    
    def show_downloaded_files(self):
        """Show downloaded files"""
        print("\n📊 Downloaded Files:")
        print("-" * 40)
        
        # Check WordNet
        try:
            import nltk
            from nltk.corpus import wordnet
            wordnet.synsets('test')
            print("✅ WordNet: Installed")
        except:
            print("❌ WordNet: Not installed")
        
        # Check spaCy
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy: Installed")
        except:
            print("❌ spaCy: Not installed")
        
        # Check GloVe
        glove_dir = self.data_dir / "glove"
        if glove_dir.exists():
            files = list(glove_dir.glob("*.txt"))
            if files:
                print(f"✅ GloVe: {len(files)} files found")
                for f in files:
                    size = f.stat().st_size / (1024 * 1024)
                    print(f"   - {f.name} ({size:.1f} MB)")
            else:
                print("❌ GloVe: No files found")
        else:
            print("❌ GloVe: Directory not found")
        
        print("-" * 40)
        print(f"📁 Data directory: {self.data_dir}")


if __name__ == "__main__":
    downloader = WordDataDownloader()
    downloader.download_all()