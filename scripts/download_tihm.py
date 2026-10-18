from pathlib import Path
import urllib.request, zipfile, hashlib
URL="https://zenodo.org/records/7622128/files/TIHM_Dataset.zip?download=1"
EXPECTED_MD5="ccf913f38a7808bc366bf0e799b409e4"
out=Path("data/raw/tihm"); out.mkdir(parents=True,exist_ok=True); z=out/"TIHM_Dataset.zip"
print("Downloading official TIHM v1.0 research dataset from Zenodo...")
urllib.request.urlretrieve(URL,z)
md5=hashlib.md5(z.read_bytes()).hexdigest()
if md5 != EXPECTED_MD5: raise SystemExit(f"Checksum mismatch: {md5}")
with zipfile.ZipFile(z) as f: f.extractall(out)
print(f"Downloaded and extracted to {out}. Raw data are intentionally git-ignored.")
