#!/usr/bin/env python3
"""Download pinned WikiPron TSV assets, fail if content changes unexpectedly."""
from pathlib import Path
from urllib.request import urlopen, Request
import hashlib

ROOT=Path(__file__).resolve().parent.parent
SOURCES={
 'broad':('mar_deva_broad.tsv','ec0afc66ff7966bac5e4dffc20040e407b8e0ab9'),
 'narrow':('mar_deva_narrow.tsv','e9bc77df49e99f7b1b35227f83356d714b67e0b2'),
}

def git_blob_sha(content:bytes)->str:
    return hashlib.sha1(f'blob {len(content)}\0'.encode()+content).hexdigest()

if __name__=='__main__':
    dest=ROOT/'data/raw';dest.mkdir(parents=True,exist_ok=True)
    for kind,(name,expected) in SOURCES.items():
        url=f'https://raw.githubusercontent.com/CUNY-CL/wikipron/master/data/scrape/tsv/{name}'
        print('Downloading',url)
        req=Request(url,headers={'User-Agent':'IPAAtlas-Marathi-Dataset-Research/1.0'})
        with urlopen(req,timeout=45) as response: data=response.read()
        sha=git_blob_sha(data)
        if sha!=expected:raise ValueError(f'Source changed: {name} got {sha} expected {expected}. Review and update pinned provenance before importing.')
        out=dest/name;out.write_bytes(data)
        print(f'Verified {name}: {len(data)} bytes, Git blob {sha}; saved {out}')
    print('Now build full dataset:')
    print('python scripts/build_marathi_dataset.py --broad data/raw/mar_deva_broad.tsv --narrow data/raw/mar_deva_narrow.tsv')
