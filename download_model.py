import os
import time
from huggingface_hub import snapshot_download
from requests.exceptions import RequestException

def download_with_retries(model_id, local_dir, max_retries=10, delay=5):
    """
    Downloads a HuggingFace model with aggressive retries and resume support.
    """
    print(f"🚀 Starting download of {model_id} to {local_dir}...")
    
    # Try to use a mirror if standard HF is blocked
    # os.environ["HF_ENDPOINT"] = "https://hf-mirror.com" 
    
    for attempt in range(1, max_retries + 1):
        try:
            snapshot_download(
                repo_id=model_id,
                local_dir=local_dir,
                local_dir_use_symlinks=False,
                resume_download=True,
                token=False # No token needed for public models
            )
            print(f"✅ Successfully downloaded {model_id} after {attempt} attempt(s)!")
            return True
        except Exception as e:
            print(f"⚠️ Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                print(f"🔄 Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("❌ Max retries reached. Please check your internet connection or VPN.")
                return False

if __name__ == "__main__":
    MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
    LOCAL_DIR = "./embedding_model"
    
    # Ensure directory exists
    os.makedirs(LOCAL_DIR, exist_ok=True)
    
    success = download_with_retries(MODEL_ID, LOCAL_DIR)
    
    if success:
        print("\n🎉 Model is ready!")
        print(f"You can now configure your RAG core to use this local path: {os.path.abspath(LOCAL_DIR)}")
    else:
        print("\n❌ Download failed. You might need to check your network or try a mirror.")
        print("Tip: Try setting $env:HF_ENDPOINT='https://hf-mirror.com' in PowerShell before running this.")
