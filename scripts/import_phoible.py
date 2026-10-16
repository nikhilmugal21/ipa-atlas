#!/usr/bin/env python3
"""Import downloaded PHOIBLE development CSV into local queryable SQLite.

Usage: python scripts/import_phoible.py /path/to/phoible.csv
No remote network calls; preserves per-source inventory distinctions.
Data is downloaded separately by the user under PHOIBLE's applicable license.
"""
from __future__ import annotations
import argparse,csv,sqlite3
from pathlib import Path

def import_csv(source:Path,out:Path):
 if not source.is_file():raise FileNotFoundError(source)
 out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.unlink()
 total=0
 try:
  with sqlite3.connect(str(out)) as conn,source.open(encoding='utf-8-sig',newline='') as f:
   reader=csv.DictReader(f)
   required={'InventoryID','LanguageName','Phoneme','SegmentClass'}
   if not required.issubset(set(reader.fieldnames or [])):
    raise ValueError('Expected PHOIBLE dev/data/phoible.csv columns: '+','.join(sorted(required)))
   conn.execute('''CREATE TABLE phonemes(inventory_id TEXT,language_name TEXT,iso6393 TEXT,glottocode TEXT,
         dialect TEXT,phoneme TEXT,segment_class TEXT,marginal TEXT,source TEXT)''')
   batch=[]
   for r in reader:
    batch.append((r.get('InventoryID','').strip(),r.get('LanguageName','').strip(),r.get('ISO6393','').strip(),r.get('Glottocode','').strip(),r.get('SpecificDialect','').strip(),r.get('Phoneme','').strip(),r.get('SegmentClass','').strip(),r.get('Marginal','').strip(),r.get('Source','').strip()))
    if len(batch)>=2000:
     conn.executemany('insert into phonemes values (?,?,?,?,?,?,?,?,?)',batch);total+=len(batch);batch=[]
   if batch:conn.executemany('insert into phonemes values (?,?,?,?,?,?,?,?,?)',batch);total+=len(batch)
   conn.execute('create index idx_phoible_lang on phonemes(iso6393,language_name)')
   conn.execute('create index idx_phoible_inv on phonemes(inventory_id)')
   conn.execute('create index idx_phoible_phon on phonemes(phoneme)')
 except Exception:
  out.unlink(missing_ok=True)
  raise
 return total
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('csv_file',type=Path);ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parent.parent/'data'/'phoible.sqlite');args=ap.parse_args()
 n=import_csv(args.csv_file,args.out);print(f'Imported {n} rows to {args.out}. Preserve source attribution and PHOIBLE license.')
