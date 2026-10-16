"""Conservative IPA tokenisation: structural interpretation, not automatic phoneme discovery."""
import unicodedata
from .catalog import SOUNDS, DIACRITIC_DATA, SUPRA_DATA, TONES, EJECTIVE_MARKER, ALIASES

# A small set of recognisable IPA-derived alternatives and commonly combined phones.
MODIFIERS=set(DIACRITIC_DATA)|{EJECTIVE_MARKER['symbol']}
COMPOUND_SYMBOLS=sorted([s for s in SOUNDS if len(s)>1],key=len,reverse=True)
BARE_COMBINING=set(DIACRITIC_DATA)|{s for s in TONES if unicodedata.combining(s)}|{"̆"}
ENCLOSURES={'[':']','/':'/'}


def describe_sequence(symbol:str)->dict:
 if symbol in SOUNDS:return {**SOUNDS[symbol].to_dict(),"modifiers":[]}
 if symbol.startswith("◌") and symbol[1:] in DIACRITIC_DATA:return DIACRITIC_DATA[symbol[1:]]
 if symbol in DIACRITIC_DATA:return DIACRITIC_DATA[symbol]
 if symbol in SUPRA_DATA:return SUPRA_DATA[symbol]
 if symbol in TONES:return TONES[symbol]
 if symbol==EJECTIVE_MARKER['symbol']:return EJECTIVE_MARKER
 if symbol in ALIASES:
  canonical=ALIASES[symbol]
  return {**describe_sequence(canonical),"queried_symbol":symbol,"canonical_symbol":canonical,"note":"Normalised an IPA-compatible or commonly used alternative symbol."}
 result=tokenize(symbol)
 sounds=[t for t in result['tokens'] if t['type']=='sound']
 if len(sounds)!=1 or result['unknown_count'] or len([t for t in result['tokens'] if t['type']!='sound']):
  raise ValueError("Input is not one recognised IPA segment; use /v1/analyze for transcriptions")
 return sounds[0]['detail']


def tokenise_sound(base:str,suffixes:list[str]):
 info=SOUNDS[base].to_dict()
 info['base_symbol']=base
 info['symbol']=base+''.join(suffixes)
 info['modifiers']=[]
 extras=[]
 for mark in suffixes:
  entry=DIACRITIC_DATA.get(mark) or SUPRA_DATA.get(mark) or TONES.get(mark)
  if mark=='ʼ': entry=EJECTIVE_MARKER
  if entry:
   info['modifiers'].append(entry)
   extras.append(entry['description'])
   if mark=='ʰ':info['aspirated']=True
   if mark=='̥': info['voicing_modified']='voiceless'
   if mark=='̬': info['voicing_modified']='voiced'
   if mark=='̪':info['place_modified']='dentalized'
   if mark=='̃':info['nasalized']=True
   if mark=='ʼ':info['airstream_modified']='glottalic egressive'
 info['description']+=' '+ ' '.join(extras) if extras else ''
 return info


def tokenize(raw:str):
 if not raw or not raw.strip():raise ValueError("Supply a nonempty IPA transcription")
 if len(raw)>4000:raise ValueError("Transcription exceeds the 4000-character limit")
 original=raw.strip()
 raw=unicodedata.normalize('NFD',original)
 notation='plain'
 text=raw
 if len(raw)>=2 and raw[0] in ENCLOSURES and raw[-1]==ENCLOSURES[raw[0]]:
  notation='phonetic' if raw[0]=='[' else 'phonemic'
  text=raw[1:-1]
 # A complete input is never silently converted from orthography.
 tokens=[];i=0;unknown=0
 keys=sorted(SOUNDS,key=len,reverse=True)
 while i<len(text):
  c=text[i]
  if c.isspace() or c in '-‿.ˈˌ|‖':
   label=("space" if c.isspace() else "prosodic")
   entry=SUPRA_DATA.get(c)
   tokens.append({"text":c,"type":label,"offset":i,"detail":entry})
   i+=1;continue
  if c in ALIASES and c!='g':
   entry=describe_sequence(ALIASES[c]);entry['queried_symbol']=c;entry['symbol']=c;entry['normalisation_note']=f'Derived IPA symbol {c} analysed as {ALIASES[c]}.'
   tokens.append({'text':c,'type':'sound','offset':i,'detail':entry});i+=1;continue
  base=next((s for s in keys if text.startswith(s,i)),None)
  if not base and c=='g':base='ɡ' # common-looking IPA replacement
  if base:
   base_chars=1 if (c=='g' and base=='ɡ') else len(base)
   start=i;i+=base_chars
   mods=[]
   while i<len(text) and text[i] in MODIFIERS | {'ː','ˑ','̆'} | {t for t in TONES if unicodedata.combining(t)}:
    mods.append(text[i]);i+=1
   # Do not consume a tie bar as an ordinary modifier; affricates above are long-matched.
   entry=tokenise_sound(base,mods)
   if c=='g' and base=='ɡ':entry['normalisation_note']='Latin g treated as IPA ɡ (script g).'
   tokens.append({"text":text[start:i],"type":"sound","offset":start,"detail":entry})
   continue
  if c in SUPRA_DATA:
   tokens.append({"text":c,"type":"prosodic","offset":i,"detail":SUPRA_DATA[c]});i+=1;continue
  if c in TONES:
   tokens.append({"text":c,"type":"tone","offset":i,"detail":TONES[c]});i+=1;continue
  if c=="ʼ":
   tokens.append({"text":c,"type":"modifier_unattached","offset":i,"detail":EJECTIVE_MARKER});i+=1;continue
  if c in DIACRITIC_DATA:
   tokens.append({"text":c,"type":"modifier_unattached","offset":i,"detail":DIACRITIC_DATA[c]});i+=1;continue
  if c in {'(',')','{','}','[',']','/','‖', '͡','͜'}:
   tokens.append({"text":c,"type":"annotation_or_unattached_tie","offset":i,"detail":None});i+=1;continue
  tokens.append({"text":c,"type":"unknown","offset":i,"detail":None});unknown+=1;i+=1
 count=sum(1 for t in tokens if t['type']=='sound')
 warnings=[]
 if unknown:warnings.append("Unrecognised characters exist. This does not necessarily imply an invalid phonetic transcription; extended IPA and language-specific notation are not exhaustively supported.")
 if any(t['type']=='modifier_unattached' for t in tokens):warnings.append("A diacritic or modifier was not attached to a recognised base segment.")
 if any(t['type']=='annotation_or_unattached_tie' for t in tokens):warnings.append("Unmatched or non-canonical compound notation may need manual review.")
 if notation=='plain':warnings.append("Use [square brackets] for a phonetic transcription or /slashes/ for a phonemic transcription if the distinction matters.")
 return {"input":raw,"normalised":text,"unicode_normalisation":"NFD for decomposed diacritics","notation":notation,"tokens":tokens,"sound_count":count,"unknown_count":unknown,"warnings":warnings,"limitations":"This is a chart-oriented symbol parser, not an orthography-to-IPA or a complete phonological grammar. Multiple phones may represent one phoneme and vice versa."}


def compare(a,b):
 x=describe_sequence(a);y=describe_sequence(b)
 features=['category','place','manner','voicing','airstream','height','backness','rounding','aspirated','nasalized','voicing_modified','place_modified','airstream_modified']
 differences={f:{'a':x.get(f),'b':y.get(f)} for f in features if x.get(f)!=y.get(f)}
 return {"a":x,"b":y,"contrasts":differences,"note":"Articulatory differences shown are descriptive; do not assume the pair is phonemically contrastive in a particular language."}
