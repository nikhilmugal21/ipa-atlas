from fastapi.testclient import TestClient
from ipa_atlas.main import app
from ipa_atlas.catalog import SOUNDS, DIACRITIC_DATA, TONES

c=TestClient(app)
def test_chart_complete():
 d=c.get('/v1/chart').json()
 assert len([x for x in SOUNDS.values() if x.category!='composite_consonant'])==107
 assert len(DIACRITIC_DATA)==31
 assert len(TONES)>=19
 assert len(d['categories']['vowel'])==28
 assert len(d['categories']['pulmonic_consonant'])==59

def test_home_and_docs():
 assert c.get('/').status_code==200
 assert 'IPA Atlas' in c.get('/').text
 assert c.get('/openapi.json').status_code==200

def test_chart_sound_features():
 for sym,place,manner,voicing in [('p','bilabial','plosive','voiceless'),('ɲ','palatal','nasal','voiced'),('ʈ','retroflex','plosive','voiceless'),('ŋ','velar','nasal','voiced')]:
  x=c.get('/v1/sounds/describe',params={'symbol':sym}).json()
  assert x['place']==place and x['manner']==manner and x['voicing']==voicing
  assert 'description' in x and 'examples' in x

def test_all_basic_sounds_have_description_and_drill():
 for sound in SOUNDS.values():
  if sound.category=='composite_consonant':continue
  x=c.get('/v1/sounds/describe',params={'symbol':sound.symbol})
  assert x.status_code==200,(sound.symbol,x.text)
  d=x.json()
  assert len(d['description'])>75,(sound.symbol,d['description'])
  assert any(e['type']=='constructed_articulatory_drill' for e in d['examples'])

def test_modifiers():
 x=c.get('/v1/sounds/describe',params={'symbol':'t̪ʰ'}).json()
 assert x['base_symbol']=='t' and x['aspirated'] and x['place_modified']=='dentalized'
 assert len(x['modifiers'])==2

def test_affricate():
 x=c.get('/v1/sounds/describe',params={'symbol':'d͡ʒ'}).json()
 assert x['manner']=='affricate' and x['voicing']=='voiced'

def test_parse_tamil():
 x=c.post('/v1/analyze',json={'transcription':'[t̪ʰaːmiɻ]'}).json()
 assert x['notation']=='phonetic' and x['sound_count']==5
 assert x['unknown_count']==0
 assert x['tokens'][0]['text']=='t̪ʰ'

def test_parse_stress():
 x=c.post('/v1/analyze',json={'transcription':'/ˈkæt/'}).json()
 assert x['notation']=='phonemic' and x['sound_count']==3 and x['unknown_count']==0

def test_parse_unknown_safe():
 x=c.post('/v1/analyze',json={'transcription':'[abc🤖]'}).json()
 assert x['unknown_count']==1
 assert x['warnings']

def test_compare():
 d=c.post('/v1/compare',json={'a':'p','b':'b'}).json()
 assert d['contrasts']['voicing']=={'a':'voiceless','b':'voiced'}

def test_filters():
 d=c.get('/v1/sounds',params={'category':'vowel','height':'close'})
 # unsupported filter is ignored by FastAPI (not a failure)
 assert d.status_code==200
 assert all(s['category']=='vowel' for s in d.json()['items'])

def test_examples_and_not_attested():
 d=c.get('/v1/examples',params={'symbol':'ʘ'}).json()
 assert len(d['examples'])==1
 assert d['examples'][0]['verification']=='not an attested word'

def test_invalid():
 assert c.get('/v1/sounds/describe',params={'symbol':'🤖'}).status_code==404
 assert c.post('/v1/analyze',json={'transcription':''}).status_code==422
 assert c.post('/v1/analyze',json={'transcription':'a'*4001}).status_code==422

def test_no_internal_error_on_resources():
 assert len(c.get('/v1/resources').json()['resources'])>=5

def test_dictionary_with_optional_dependency():
 r=c.get('/v1/transcribe/english/language')
 assert r.status_code==200
 if r.json()['available']:
  assert r.json()['found']
  assert r.json()['variants'][0]['ipa_broad_no_stress_markers'].startswith('/')

def test_diacritic_reference_by_symbol():
 assert c.get('/v1/sounds/describe',params={'symbol':'◌̪'}).json()['name']=='dental'
 assert c.get('/v1/sounds/describe',params={'symbol':'ˈ'}).json()['name']=='primary stress'

def test_nfd_tones_and_rhotic_vowels():
 x=c.post('/v1/analyze',json={'transcription':'[mǎ]'}).json()
 assert x['unknown_count']==0 and x['sound_count']==2
 assert any(m['name']=='rising (diacritic)' for m in x['tokens'][-1]['detail']['modifiers'])
 y=c.post('/v1/analyze',json={'transcription':'[ɚ]'}).json()
 assert y['unknown_count']==0 and y['sound_count']==1

def test_aspirated_and_non_chart_examples():
 x=c.get('/v1/examples',params={'symbol':'pʰ','language':'Hindi'}).json()
 assert any(ex.get('word')=='फल' for ex in x['examples'])
 assert any(ex['type']=='constructed_articulatory_drill' for ex in x['examples'])

def test_prior_languages_have_examples():
 from ipa_atlas.catalog import EXAMPLES
 languages={e['language'] for ex in EXAMPLES.values() for e in ex}
 assert {'Hindi','Marathi','Bangla','Malayalam','Gujarati','Tamil','English'}<=languages

def test_phoible_import(tmp_path,monkeypatch):
 from scripts.import_phoible import import_csv
 csv=tmp_path/'phoible.csv';db=tmp_path/'test.sqlite'
 csv.write_text('InventoryID,LanguageName,ISO6393,Glottocode,SpecificDialect,Phoneme,SegmentClass,Marginal,Source\n12,Testlang,tst,abcd1234,Urban,p,consonant,FALSE,Smith2020\n12,Testlang,tst,abcd1234,Urban,a,vowel,FALSE,Smith2020\n13,Testlang,tst,abcd1234,Rural,ɓ,consonant,FALSE,Smith2021\n',encoding='utf-8')
 assert import_csv(csv,db)==3
 monkeypatch.setenv('IPA_ATLAS_PHOIBLE_DB',str(db))
 status=c.get('/v1/inventories/status').json()
 assert status['available'] and status['rows']==3
 assert len(c.get('/v1/inventories',params={'iso6393':'tst'}).json()['items'])==2
 assert len(c.get('/v1/inventories/12').json()['items'])==2
 assert len(c.get('/v1/attestations',params={'symbol':'ɓ'}).json()['items'])==1
