#!/usr/bin/env python3
"""Reproducible source-preserving import of WikiPron Marathi TSV files.

Usage:
python scripts/build_marathi_dataset.py --broad data/source_broad_seed.tsv --narrow data/source_narrow_seed.tsv
For a bigger dataset use original broad/narrow WikiPron TSV downloads instead of seeds.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, unicodedata
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://github.com/CUNY-CL/wikipron/blob/master/data/scrape/tsv/'
VERSION = {
 'broad': ('mar_deva_broad.tsv', 'ec0afc66ff7966bac5e4dffc20040e407b8e0ab9'),
 'narrow': ('mar_deva_narrow.tsv', 'e9bc77df49e99f7b1b35227f83356d714b67e0b2'),
}
# Editorial glosses for illustration only. WikiPron does not furnish translations.
# These are not labelled scholarly verified and may represent only one sense.
GLOSSES = {
 'अंक':'number; digit','अंग':'body part','अंगठा':'thumb','अंगठी':'ring','अंगण':'courtyard',
 'आंबा':'mango','आई':'mother','आकाश':'sky','आज':'today','आजी':'grandmother','आजोबा':'grandfather',
 'आठ':'eight','आपण':'we; oneself (context-dependent)','आरसा':'mirror','आवाज':'sound; voice',
 'ऊन':'sunshine; heat','एक':'one','औषध':'medicine','कडू':'bitter','कण':'particle; grain',
 'कधी':'when','कपडा':'cloth','कांदा':'onion','काकडी':'cucumber','कागद':'paper','काठी':'stick',
 'कापूस':'cotton','काम':'work','काळा':'black','काळे':'black (inflected)','कावळा':'crow',
 'कुठे':'where','कुत्रा':'dog','केळे':'banana','केस':'hair','कोळसा':'coal','खिडकी':'window',
 'खूप':'a lot; very','खेळणे':'to play; toy (depends on sense)','गवत':'grass','गाडी':'vehicle',
 'गाणे':'song; to sing (depends on sense)','गोड':'sweet','गोष्ट':'story; matter','घर':'house',
 'घाम':'sweat','चंद्र':'moon','चहा':'tea','चांगला':'good','चार':'four','चाल':'gait; tune; move',
 'चूक':'mistake','चेंडू':'ball','जड':'heavy','जमीन':'ground; land','जवळ':'near','जास्त':'more',
 'जेवण':'meal','झाड':'tree','झाडू':'broom','झोप':'sleep','टाकणे':'to put; throw',
 'डाळ':'lentils; dal','डोळा':'eye','ढग':'cloud','तांदूळ':'rice grain','ताट':'plate',
 'तारा':'star; wire','तीन':'three','तेल':'oil','थंड':'cold','थोडे':'a little; few',
 'दरवाजा':'door','दही':'curd; yogurt','दात':'tooth','दादा':'elder brother','दिवस':'day',
 'दिशा':'direction','दूध':'milk','दोन':'two','नऊ':'nine','नदी':'river','नवा':'new',
 'नाक':'nose','नाव':'name; boat (depends on sense)','नाही':'no; not','पत्र':'letter; leaf',
 'पहाट':'dawn','पांढरा':'white','पाऊस':'rain','पाच':'five','पाठ':'back; lesson',
 'पाणी':'water','पान':'leaf; page','पाय':'foot; leg','पालक':'spinach; guardian',
 'पुस्तक':'book','फळ':'fruit; result','फुगा':'balloon','फुले':'flowers',
 'फूल':'flower','बटाटा':'potato','बाई':'woman','बाण':'arrow','बाळ':'baby',
 'बाळे':'children (plural)','भाऊ':'brother','भाकरी':'flatbread','भात':'cooked rice',
 'भाषा':'language','माणूस':'person','माती':'soil; earth','माशी':'fly (insect)',
 'मासा':'fish','मिरची':'chilli','मुलगी':'girl','मुळा':'radish','मेघ':'cloud',
 'मोर':'peacock','यश':'success','रस्ता':'road','राजा':'king','रात्र':'night','राम':'personal name',
 'लहान':'small; young','लाल':'red','लिंबू':'lemon','वाघ':'tiger','वाचणे':'to read; to survive',
 'वारा':'wind','विहीर':'well','वीज':'electricity; lightning','वेळ':'time','शब्द':'word',
 'शाळा':'school','शिक्षक':'teacher','शिक्षण':'education','शुद्ध':'pure; correct',
 'शेत':'farm field','सकाळ':'morning','सगळे':'all','साखर':'sugar','साप':'snake',
 'सिंह':'lion','सुंदर':'beautiful','सूर्य':'sun','सोने':'gold',
 'हवा':'air; desire (context-dependent)','हसणे':'to laugh','हसू':'laughter',
 'हाड':'bone','हात':'hand'
}
HEADERS = ['id','language','iso6393','orthography','ipa','source_segmented_ipa','ipa_tokens',
           'transcription_level','source_name','source_file','source_blob_sha','source_file_url',
           'wiktionary_entry_url','dialect','meaning_en','meaning_provenance','verification_status',
           'speaker_audio_url','reviewer','review_date','notes']

def source_rows(path:Path, level:str):
    filename, blob_sha = VERSION[level]
    with path.open(encoding='utf-8-sig',newline='') as f:
        for line_number, line in enumerate(f,1):
            line=line.strip('\n\r')
            if not line:continue
            cells=line.split('\t')
            if len(cells)!=2:raise ValueError(f'{path}:{line_number} expected exactly 2 TSV columns')
            word, raw=cells
            word=unicodedata.normalize('NFC',word.strip())
            toks=raw.split()
            if not word or not toks:raise ValueError(f'{path}:{line_number} blank word / IPA')
            # Keep WikiPron segment tokens precisely as given, including diacritics.
            ipa_str=''.join(toks)
            wrapped=f'/{ipa_str}/' if level=='broad' else f'[{ipa_str}]'
            h=hashlib.sha256(f'{level}\t{word}\t{raw}'.encode('utf8')).hexdigest()[:12]
            yield dict(zip(HEADERS,[
                f'mr-{level}-{h}','Marathi','mar',word,wrapped,raw,'|'.join(toks),
                level,'WikiPron/Wiktionary',filename,blob_sha,BASE+filename,
                'https://en.wiktionary.org/wiki/'+quote(word, safe=''), 'unspecified',
                GLOSSES.get(word,''),'editorial_not_cross_checked' if word in GLOSSES else 'not_supplied',
                'source_extracted_not_expert_reviewed','','','',
                'WikiPron source-level notation; not a verified production by a named speaker.'
            ]))

def build(broad:Path,narrow:Path,out:Path):
    out.parent.mkdir(parents=True,exist_ok=True)
    seen=set();stats={};rows=[]
    for typ,fn in [('broad',broad),('narrow',narrow)]:
        if not fn.exists():raise FileNotFoundError(fn)
        for row in source_rows(fn,typ):
            if row['id'] in seen:continue
            seen.add(row['id']);rows.append(row);stats[typ]=stats.get(typ,0)+1
    rows.sort(key=lambda r:(r['orthography'],r['transcription_level'],r['ipa']))
    with out.open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.DictWriter(f,fieldnames=HEADERS);wr.writeheader();wr.writerows(rows)
    return {'rows':len(rows),'unique_words':len(set(r['orthography'] for r in rows)),**stats}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--broad',type=Path,default=ROOT/'data/source_broad_seed.tsv')
    p.add_argument('--narrow',type=Path,default=ROOT/'data/source_narrow_seed.tsv')
    p.add_argument('--out',type=Path,default=ROOT/'data/marathi_examples.csv')
    a=p.parse_args(); print(json.dumps(build(a.broad,a.narrow,a.out),ensure_ascii=False))
