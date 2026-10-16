#!/usr/bin/env python3
"""Idempotently enable Marathi examples and REST routes in an existing IPA Atlas clone."""
from pathlib import Path
import argparse,shutil

def patch(root:Path):
    catalog=root/'ipa_atlas/catalog.py'
    api=root/'ipa_atlas/main.py'
    if not catalog.is_file() or not api.is_file():
        raise ValueError('Run this from a copy of your IPA Atlas repository (main.py/catalog.py missing).')
    source=catalog.read_text(encoding='utf8')
    marker='# MARATHI DATASET INTEGRATION v1'
    if marker not in source:
        # Modify LAST definition of examples_for, without replacing its entire function.
        head,sep,tail=source.rpartition('def examples_for(symbol,language=None):')
        if not sep:raise RuntimeError('examples_for() signature not found; merge manually.')
        needle=' if language:\n  items=[e for e in items if e[\'language\'].casefold()==language.casefold() or e[\'language\']==\'not language-specific\']'
        if needle not in tail:raise RuntimeError('Unsupported catalog formatting; no files changed.')
        injection=''' # MARATHI DATASET INTEGRATION v1\n try:\n  from .marathi_lexicon import examples_for_sound\n  items.extend(examples_for_sound(symbol, language))\n except (ImportError, OSError):\n  pass\n'''
        shutil.copy2(catalog,str(catalog)+'.before_marathi.bak')
        catalog.write_text(head+sep+tail.replace(needle,injection+needle,1),encoding='utf8')
        print('Patched catalog.examples_for(); backup saved.')
    else:print('Catalog already patched.')
    source=api.read_text(encoding='utf8')
    marker2='# MARATHI API ROUTER v1'
    if marker2 not in source:
        shutil.copy2(api,str(api)+'.before_marathi.bak')
        api.write_text(source+'''\n\n# MARATHI API ROUTER v1\nfrom .marathi_api import router as marathi_router\napp.include_router(marathi_router)\n''',encoding='utf8')
        print('Installed REST API routes. Original backed up.')
    else:print('API router already installed.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path.cwd())
    a=p.parse_args();patch(a.repo)
