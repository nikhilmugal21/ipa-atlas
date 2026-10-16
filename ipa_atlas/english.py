"""Optional CMUdict integration: lexical American English, not narrow phonetics.

External CMUdict package intentionally is NOT redistributed here. GPL wrapper is
an optional separately installed dependency; original CMU project maintains its
own licensing terms. Verify requirements before shipping a product.
"""
import re
try:import cmudict
except ImportError:cmudict=None

ARPABET={
 'AA':'ɑ','AE':'æ','AH':'ʌ','AO':'ɔ','AW':'aʊ','AY':'aɪ','B':'b','CH':'t͡ʃ','D':'d',
 'DH':'ð','EH':'ɛ','ER':'ɝ','EY':'eɪ','F':'f','G':'ɡ','HH':'h','IH':'ɪ','IY':'i','JH':'d͡ʒ',
 'K':'k','L':'l','M':'m','N':'n','NG':'ŋ','OW':'oʊ','OY':'ɔɪ','P':'p','R':'ɹ','S':'s',
 'SH':'ʃ','T':'t','TH':'θ','UH':'ʊ','UW':'u','V':'v','W':'w','Y':'j','Z':'z','ZH':'ʒ'
}

def lookup_english(word:str):
 if not re.fullmatch(r"[A-Za-z][A-Za-z'\-]{0,69}",word):raise ValueError("Use one ordinary English dictionary word, up to 70 characters")
 if not cmudict:return {"word":word,"available":False,"message":"Install optional dependency: pip install cmudict"}
 entries=cmudict.dict().get(word.lower(),[])
 variants=[]
 for arp in entries[:12]:
  forms=[];stresses=[]
  for phone in arp:
   base=re.sub(r'[012]$', '',phone)
   if base not in ARPABET:continue
   digits=re.findall(r'[012]$',phone)
   ipa='ə' if base=='AH' and digits==['0'] else 'ɚ' if base=='ER' and digits==['0'] else ARPABET[base]
   forms.append(ipa)
   if digits:stresses.append({"vowel_index":sum(1 for p in arp[:len(forms)] if re.search(r'[012]$',p)),"value":digits[0]})
  variants.append({"arpabet":arp,"ipa_broad_no_stress_markers":"/"+''.join(forms)+"/","lexical_vowel_stresses":[(p[-1] if p[-1].isdigit() else None) for p in arp if re.search(r'[012]$',p)],"caveat":"CMUdict transcription converted approximately to broad IPA; no syllabification, contextual allophony, or detailed stress positioning. Pronunciation is US English oriented."})
 return {"word":word,"available":True,"found":bool(entries),"variants":variants,"resource":"CMU Pronouncing Dictionary via separately installed cmudict package","source_url":"https://github.com/cmusphinx/cmudict"}
