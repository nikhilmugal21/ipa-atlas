from __future__ import annotations
from collections import Counter
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .catalog import SOUNDS, DIACRITIC_DATA, SUPRA_DATA, TONES, SOURCE, EJECTIVE_MARKER, examples_for
from .analyze import tokenize, describe_sequence, compare
from .english import lookup_english
from .bangla_lexicon import stats as bangla_stats, search as bangla_search, examples_for_sound as bangla_phone_examples

app=FastAPI(title="IPA Atlas API",version="1.0.0",description="Educational IPA chart reference, articulatory explanation, IPA structural parser, example catalog, and optional CMUdict lookup. Not a phoneme inventory inference model.")
STATIC=Path(__file__).parent/'static'
app.mount('/static',StaticFiles(directory=str(STATIC)),name='static')

class AnalysisRequest(BaseModel):
 transcription:str=Field(min_length=1,max_length=4000,examples=['[t̪ʰaːmiɻ]'])
class CompareRequest(BaseModel):
 a:str=Field(min_length=1,max_length=15)
 b:str=Field(min_length=1,max_length=15)

def combined_examples(symbol: str, language: str | None = None):
    """Pedagogical examples plus individually attributed Bangla WikiPron records."""
    output = list(examples_for(symbol, language))
    if language is None or language.casefold() in ("bangla", "bengali"):
        output.extend(bangla_phone_examples(symbol, limit=8))
    return output


@app.get('/',include_in_schema=False)
def home():return FileResponse(str(STATIC/'index.html'))
@app.get('/health')
def health():return {'status':'ok','catalogue':{'basic_segment_symbols':len([x for x in SOUNDS.values() if x.category!='composite_consonant']),'sample_complex_segments':len([x for x in SOUNDS.values() if x.category=='composite_consonant']),'diacritics':len(DIACRITIC_DATA),'tone_marks':len(TONES)}}
@app.get('/v1/chart')
def chart():
 return {'source':SOURCE,'description':'A symbolic feature-based index of the official chart sections (not a reproduction of chart artwork).','chart_revision':'IPA chart last formally revised in 2015/2005; later editions largely update year and copyright','categories':{category:[x.to_dict() for x in SOUNDS.values() if x.category==category] for category in ['pulmonic_consonant','nonpulmonic_consonant','other_consonant','vowel','composite_consonant']},'diacritics':list(DIACRITIC_DATA.values()),'suprasegmentals':list(SUPRA_DATA.values()),'tones':list(TONES.values()),'ejective_marker':EJECTIVE_MARKER}
@app.get('/v1/sounds')
def list_sounds(category:str|None=None,place:str|None=None,manner:str|None=None,voicing:str|None=None,q:str|None=None,limit:int=Query(150,ge=1,le=200),offset:int=Query(0,ge=0)):
 vals=[s for s in SOUNDS.values() if (not category or s.category==category) and (not place or s.place==place) and (not manner or s.manner==manner) and (not voicing or s.voicing==voicing) and (not q or q.casefold() in (s.symbol+' '+s.name+' '+(s.notes or '')).casefold())]
 return {'total':len(vals),'offset':offset,'limit':limit,'items':[v.to_dict() for v in vals[offset:offset+limit]]}
@app.get('/v1/sounds/describe')
def describe(symbol:str=Query(min_length=1,max_length=32)):
 try:return {**describe_sequence(symbol),'examples':combined_examples(symbol)}
 except ValueError as e:raise HTTPException(404,str(e))
@app.get('/v1/sounds/{symbol}')
def describe_path(symbol:str):
 try:return {**describe_sequence(symbol),'examples':combined_examples(symbol)}
 except ValueError as e:raise HTTPException(404,str(e))
@app.get('/v1/examples')
def examples(symbol:str=Query(min_length=1,max_length=32),language:str|None=None):
 try:desc=describe_sequence(symbol)
 except ValueError as e:raise HTTPException(404,str(e))
 return {'symbol':symbol,'name':desc['name'],'examples':combined_examples(symbol,language),'example_policy':'Constructed drills are labelled, not represented as real words; lexical examples are illustrative broad transcriptions that require dialect-specific verification.'}
@app.get('/v1/diacritics')
def diacritics():return {'items':list(DIACRITIC_DATA.values()),'count':len(DIACRITIC_DATA)}
@app.get('/v1/prosody')
def prosody():return {'suprasegmentals':list(SUPRA_DATA.values()),'tones':list(TONES.values()),'ejective_marker':EJECTIVE_MARKER}
@app.post('/v1/analyze')
def analyze(body:AnalysisRequest):
 try:return tokenize(body.transcription)
 except ValueError as e:raise HTTPException(422,str(e))
@app.post('/v1/compare')
def compare_endpoint(body:CompareRequest):
 try:return compare(body.a,body.b)
 except ValueError as e:raise HTTPException(422,str(e))
@app.get('/v1/transcribe/english/{word}')
def english_dictionary(word:str):
 try:return lookup_english(word)
 except ValueError as e:raise HTTPException(422,str(e))
@app.get('/v1/resources')
def resources():
 return {'resources':[
  {'name':'International Phonetic Association chart','url':'https://www.internationalphoneticassociation.org/content/ipa-chart','role':'canonical inventory of chart symbols and classification','use':'Manually modelled in core, source attributed','licensing':'Official chart artwork under CC BY-SA 4.0; no artwork included in this project.'},
  {'name':'IPA Handbook recordings','url':'https://www.internationalphoneticassociation.org/node/125','role':'language-specific examples and audio','use':'Linked only, recordings not copied','licensing':'Do not bundle or redistribute recordings without permission.'},
  {'name':'CMU Pronouncing Dictionary','url':'https://github.com/cmusphinx/cmudict','role':'American English word pronunciations','use':'Optional separate cmudict installation; approximate ARPAbet-to-IPA conversion','licensing':'Respect original dictionary license and independent Python wrapper license.'},
  {'name':'PHOIBLE 2.0','url':'https://phoible.org/download','role':'language phoneme inventory data','use':'Potential future local CLDF/CSV import; not bundled or queried live','licensing':'CC BY-SA 3.0; required credit & share-alike if reused.'},
  {'name':'PanPhon','url':'https://github.com/dmort27/panphon','role':'phonological distinctive feature vectors for IPA segments','use':'Suggested optional future enrichment; not required or included','licensing':'Check package license before dependency or redistribution.'},
  {'name':'Wiktionary','url':'https://www.wiktionary.org/','role':'dictionary entries, some with IPA transcriptions and dialect notes','use':'Link-out reference; no scraping or automatic unverified synthesis in this release','licensing':'Reuse subject to applicable Wiktionary licensing and attribution requirements.'},
 ]}

from .inventories import status as inventories_status, list_inventories, inventory_items, attestations

@app.get('/v1/inventories/status')
def inventory_status():return inventories_status()
@app.get('/v1/inventories')
def inventories(language:str|None=None,iso6393:str|None=None,limit:int=Query(30,ge=1,le=100)):
 return list_inventories(language,iso6393,limit)
@app.get('/v1/inventories/{inventory_id}')
def inventory(inventory_id:str):return inventory_items(inventory_id)
@app.get('/v1/attestations')
def attest(symbol:str=Query(min_length=1,max_length=32),language:str|None=None,limit:int=Query(50,ge=1,le=100)):
 return attestations(symbol,language,limit)
@app.get('/v1/example-languages')
def example_languages():
 return {'curated_examples_for':['English','Hindi','Marathi','Bangla','Malayalam','Gujarati','Tamil','French','Spanish','Turkish','Italian','Hausa'],
         'note':'Examples are selected educational illustrations, not comprehensive language-wide lexicons or dialect verified phonetic recordings.'}

@app.get('/v1/datasets/bangla/stats')
def bangla_dataset_stats():
    """Coverage of WikiPron-derived Bangla data grouped by dialect filter and level."""
    return bangla_stats()


@app.get('/v1/datasets/bangla')
def bangla_dataset_entries(
    q: str = Query("", max_length=150),
    dialect: str | None = Query(None, pattern="^(Dhaka|Rarh)$"),
    level: str | None = Query(None, pattern="^(broad|narrow)$"),
    phone: str | None = Query(None, max_length=24),
    limit: int = Query(100, ge=1, le=250),
    offset: int = Query(0, ge=0),
):
    """Exact-segment search, with pagination and original Wiktionary source links."""
    items = bangla_search(q=q, dialect=dialect, level=level, phone=phone)
    return {
        "total": len(items),
        "offset": offset,
        "limit": limit,
        "items": items[offset:offset+limit],
        "provenance": "WikiPron-mined Wiktionary data, NOT speaker-verified",
        "dialect_caveat": "Unlabeled Wiktionary entries may occur in both dialect-filtered files.",
    }
