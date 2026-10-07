"""One-time acquisition of licensed demo assets; the running app never hotlinks."""
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
root=Path(__file__).resolve().parents[1]
sources=json.loads((root/'frontend/public/demo/sources.json').read_text())
def download(source):
    target=root/'frontend/public'/source['local_file']
    if target.exists() and target.stat().st_size>1000: return source['id']+' exists'
    request=Request(source['download_url'],headers={'User-Agent':'SearchHintsDemo/1.0'})
    with urlopen(request,timeout=30) as response: data=response.read()
    if not data.startswith(b'\xff\xd8'): raise ValueError('Expected JPEG for '+source['id'])
    target.write_bytes(data)
    return f"{source['id']}: {len(data)} bytes"
with ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(download,sources): print(result)
