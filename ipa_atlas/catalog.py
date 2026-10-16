"""Original educational descriptions of IPA chart symbols.

The International Phonetic Association is the authority on the chart.
This module is an authored, machine-readable representation, not an
inclusion of the IPA's copyrighted chart artwork or audio recordings.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
import unicodedata

SOURCE = {"name":"International Phonetic Association – official IPA chart", "url":"https://www.internationalphoneticassociation.org/content/ipa-chart", "scope":"IPA symbols and chart classification"}

PLACE = {
 "bilabial":"Bring both lips together (or close to one another).",
 "labiodental":"Bring the lower lip against or near the upper front teeth.",
 "dental":"Bring the tongue tip or blade to or near the upper teeth.",
 "alveolar":"Use the tongue tip or blade at the ridge just behind the upper teeth.",
 "postalveolar":"Raise the tongue blade toward the area just behind the alveolar ridge.",
 "alveolo-palatal":"Bring the tongue blade toward the area behind the alveolar ridge while also raising the tongue body toward the palate.",
 "retroflex":"Curl or retract the tongue tip toward the postalveolar region; exact tongue configuration differs across languages.",
 "palatal":"Raise the front of the tongue toward the hard palate.",
 "velar":"Raise the back of the tongue toward the soft palate (velum).",
 "uvular":"Move the back of the tongue toward the uvula.",
 "pharyngeal":"Constrict the pharynx using the tongue root and/or epiglottic area.",
 "epiglottal":"Bring the epiglottis and surrounding tissues into a constriction near the aryepiglottic folds.",
 "glottal":"Produce the constriction at the vocal folds (glottis).",
 "labial-velar":"Use the lips and the back of the tongue together, forming a double articulation.",
 "labial-palatal":"Round the lips while raising the front of the tongue toward the hard palate.",
 "alveolar lateral":"Use the tongue at the alveolar ridge, with air passing along one or both sides.",
 "palatoalveolar":"Make a tongue-body contact near the hard palate and an additional posterior closure for click release.",
 "linguolabial":"Touch the upper lip with the tongue tip or blade.",
 "multiple":"Use a complex constriction whose exact mechanics vary across speakers and descriptions.",
}
MANNER = {
 "plosive":"Make a complete oral closure, build pressure behind it, then release the closure.",
 "nasal":"Make an oral closure while lowering the velum so air flows through the nose.",
 "trill":"Position an articulator so airflow makes it vibrate repeatedly.",
 "tap or flap":"Make one very brief contact by a quick movement of the active articulator.",
 "fricative":"Constrict the airstream through a narrow passage, creating turbulent friction.",
 "lateral fricative":"Obstruct central airflow and force turbulent air along the sides of the tongue.",
 "approximant":"Bring articulators close without sufficient narrowing to make substantial turbulence.",
 "lateral approximant":"Block airflow down the middle of the mouth while permitting relatively free flow along the tongue's sides.",
 "lateral flap":"Make one brief tongue contact while allowing air around the side of the tongue.",
 "click":"Make two oral closures, rarefy air between them, then release the anterior closure with an ingressive click.",
 "implosive":"Make an oral closure with a downward larynx movement, typically with voicing; the pressure mechanism varies among languages.",
 "ejective":"Close the glottis while producing an oral constriction, raise the larynx to compress air, and release with an outward burst.",
 "affricate":"Begin with an oral stop closure and release into frication at a nearby place of articulation.",
}
VOICE={"voiceless":"Keep the vocal folds apart enough that regular periodic voicing does not occur during the main constriction.", "voiced":"Allow the vocal folds to vibrate during at least part of the sound.","variable":"Voicing may vary, so examine the particular sound and language description."}

@dataclass(frozen=True)
class Sound:
 symbol: str
 name: str
 category: str
 place: Optional[str] = None
 manner: Optional[str] = None
 voicing: Optional[str] = None
 airstream: Optional[str] = None
 height: Optional[str] = None
 backness: Optional[str] = None
 rounding: Optional[str] = None
 notes: str = ""
 def to_dict(self):
  d=asdict(self)
  if self.category=="vowel":
   d["description"]=(f"A {self.height} {self.backness} {self.rounding} vowel. "
      f"Keep the oral tract relatively open and let voiced air flow without a consonantal constriction. "
      f"Adjust tongue height to the {self.height.replace('-', ' ')} region and tongue position toward the {self.backness}; "
      f"{'round/protrude the lips' if self.rounding=='rounded' else 'leave the lips unrounded'}. "
      f"Exact vowel quality depends on language and speaker.")
   d["articulation"]={"tongue_height":self.height,"tongue_backness":self.backness,"lip_rounding":self.rounding,"airflow":"pulmonic egressive, ordinarily voiced"}
  else:
   steps=[]
   if self.place:steps.append(PLACE.get(self.place,""))
   if self.manner:steps.append(MANNER.get(self.manner,""))
   if self.voicing:steps.append(VOICE.get(self.voicing,""))
   if self.airstream and self.airstream!="pulmonic egressive":
    steps.append(f"Airstream mechanism: {self.airstream}.")
   if self.notes:steps.append(self.notes)
   d["description"]=" ".join(s for s in steps if s)
   d["articulation"]={"active_region":self.place,"constriction":self.manner,"vocal_folds":self.voicing,"airstream":self.airstream}
  d["source"]="official IPA chart (classification); authored articulatory explanation"
  return d

SOUNDS: dict[str, Sound]={}
def add(sym,name,category,place=None,manner=None,voicing=None,airstream="pulmonic egressive",notes="",**kwargs):
 if sym in SOUNDS:raise ValueError("duplicate:"+sym)
 SOUNDS[sym]=Sound(sym,name,category,place,manner,voicing,airstream,notes=notes,**kwargs)

# All basic pulmonic consonant letters displayed in the main chart (including paired rows).
ROWS=[
 ("plosive",[("bilabial","p","b"),("alveolar","t","d"),("retroflex","ʈ","ɖ"),("palatal","c","ɟ"),("velar","k","ɡ"),("uvular","q","ɢ"),("glottal","ʔ",None)]),
 ("nasal",[("bilabial",None,"m"),("labiodental",None,"ɱ"),("alveolar",None,"n"),("retroflex",None,"ɳ"),("palatal",None,"ɲ"),("velar",None,"ŋ"),("uvular",None,"ɴ")]),
 ("trill",[("bilabial",None,"ʙ"),("alveolar",None,"r"),("uvular",None,"ʀ")]),
 ("tap or flap",[("labiodental",None,"ⱱ"),("alveolar",None,"ɾ"),("retroflex",None,"ɽ")]),
 ("fricative",[("bilabial","ɸ","β"),("labiodental","f","v"),("dental","θ","ð"),("alveolar","s","z"),("postalveolar","ʃ","ʒ"),("retroflex","ʂ","ʐ"),("palatal","ç","ʝ"),("velar","x","ɣ"),("uvular","χ","ʁ"),("pharyngeal","ħ","ʕ"),("glottal","h","ɦ")]),
 ("lateral fricative",[("alveolar","ɬ","ɮ")]),
 ("approximant",[("labiodental",None,"ʋ"),("alveolar",None,"ɹ"),("retroflex",None,"ɻ"),("palatal",None,"j"),("velar",None,"ɰ")]),
 ("lateral approximant",[("alveolar",None,"l"),("retroflex",None,"ɭ"),("palatal",None,"ʎ"),("velar",None,"ʟ")]),
]
for manner,cells in ROWS:
 for place,unvoiced,voiced in cells:
  for sym,voice in ((unvoiced,"voiceless"),(voiced,"voiced")):
   if sym:
    label=f"{voice} {place} {manner}"
    if sym=="ʔ": label="glottal stop";voice="voiceless"
    if sym=="h": label="voiceless glottal fricative" 
    if sym=="ɦ":label="voiced glottal fricative (breathy phonation common)"
    add(sym,label,"pulmonic_consonant",place,manner,voice,
        notes=("Although traditionally placed among glottal fricatives, this may behave as a laryngeal approximant or a type of phonation in particular languages." if sym in ("h","ɦ") else ""))

for sym,place,label in [("ʘ","bilabial","bilabial click"),("ǀ","dental","dental click"),("ǃ","alveolar","(post)alveolar click"),("ǂ","palatoalveolar","palatoalveolar click"),("ǁ","alveolar lateral","alveolar lateral click")]:
 add(sym,label,"nonpulmonic_consonant",place,"click","variable","lingual ingressive",notes="The symbol specifies the click type; accompanying symbols may be needed to specify voicing or other details.")
for sym,place in [("ɓ","bilabial"),("ɗ","alveolar"),("ʄ","palatal"),("ɠ","velar"),("ʛ","uvular")]:
 add(sym,"voiced "+place+" implosive","nonpulmonic_consonant",place,"implosive","voiced","glottalic ingressive")
for sym,place,manner in [("ʍ","labial-velar","fricative"),("w","labial-velar","approximant"),("ɥ","labial-palatal","approximant"),("ʜ","epiglottal","fricative"),("ʢ","epiglottal","fricative"),("ʡ","epiglottal","plosive"),("ɕ","alveolo-palatal","fricative"),("ʑ","alveolo-palatal","fricative"),("ɺ","alveolar","lateral flap"),("ɧ","multiple","fricative")]:
 voice={"ʍ":"voiceless","w":"voiced","ɥ":"voiced","ʜ":"voiceless","ʢ":"voiced","ʡ":"voiceless","ɕ":"voiceless","ʑ":"voiced","ɺ":"voiced","ɧ":"voiceless"}[sym]
 notes={"ɧ":"Often called the Swedish 'sj' sound; this is a conventional symbol whose articulation varies considerably between speakers and dialects.","ʍ":"Traditionally called a voiceless labial-velar fricative; commonly realised as a voiceless labial-velar approximant in English varieties.","ʡ":"Complete constriction at the epiglottic/laryngeal region."}.get(sym,"")
 add(sym,f"{voice} {place} {manner}","other_consonant",place,manner,voice,notes=notes)

# Chart vowel symbols: tuple = (unrounded, rounded, height, backness).
VOWEL_PAIRS=[
 ("i","y","close","front"),("ɨ","ʉ","close","central"),("ɯ","u","close","back"),
 ("ɪ","ʏ","near-close","near-front"),(None,"ʊ","near-close","near-back"),
 ("e","ø","close-mid","front"),("ɘ","ɵ","close-mid","central"),("ɤ","o","close-mid","back"),
 (None,"ə","mid","central"),
 ("ɛ","œ","open-mid","front"),("ɜ","ɞ","open-mid","central"),("ʌ","ɔ","open-mid","back"),
 ("æ",None,"near-open","front"),("ɐ",None,"near-open","central"),
 ("a","ɶ","open","front"),(None,None,"open","central"),("ɑ","ɒ","open","back"),
]
for un,rd,height,backness in VOWEL_PAIRS:
 for sym,rounding in ((un,"unrounded"),(rd,"rounded")):
  if sym:add(sym,f"{height} {backness} {rounding} vowel","vowel",height=height,backness=backness,rounding=rounding)

# Generalised pedagogical features for independent IPA modifiers.
DIACRITICS=[
 ("◌̥","voiceless","No vocal fold vibration in a segment that would otherwise be voiced."),
 ("◌̬","voiced","Add voicing to a segment commonly represented as voiceless."),
 ("◌ʰ","aspirated","Release the segment with a noticeable period of breathy airflow."),
 ("◌̤","breathy voiced","Produce voicing with greater glottal opening and breathiness."),
 ("◌̰","creaky voiced","Use irregular/creaky vocal fold vibration."),
 ("◌̼","linguolabial","Articulate with the tongue touching the upper lip."),
 ("◌̪","dental","Move tongue contact towards the teeth."),
 ("◌̺","apical","Use the tongue tip as the active articulator."),
 ("◌̻","laminal","Use the tongue blade as the active articulator."),
 ("◌ʷ","labialized","Add lip rounding to the main articulation."),
 ("◌ʲ","palatalized","Add a secondary raising of the tongue front toward the palate."),
 ("◌ˠ","velarized","Add secondary raising of the tongue back toward the velum."),
 ("◌ˁ","pharyngealized","Add secondary pharyngeal constriction."),
 ("◌̴","velarized or pharyngealized","Use a secondary posterior articulation; the convention depends on context."),
 ("◌̹","more rounded","Increase lip rounding."),
 ("◌̜","less rounded","Reduce lip rounding."),
 ("◌̟","advanced","Move the articulation further forward."),
 ("◌̠","retracted","Move the articulation further backward."),
 ("◌̈","centralized","Move a vowel quality toward the central region."),
 ("◌̽","mid-centralized","Move the vowel toward the mid-central schwa-like area."),
 ("◌̝","raised","Raise the tongue relative to the base symbol."),
 ("◌̞","lowered","Lower the tongue relative to the base symbol."),
 ("◌̩","syllabic","Allow the segment to form a syllable nucleus."),
 ("◌̯","non-syllabic","Produce a vowel-like segment without a syllable nucleus."),
 ("◌˞","rhoticity","Add an r-colouring/rhotic articulation to a vowel."),
 ("◌̘","advanced tongue root","Advance the tongue root."),
 ("◌̙","retracted tongue root","Retract the tongue root."),
 ("◌̃","nasalized","Lower the velum to let some air escape through the nose during the segment."),
 ("◌ⁿ","nasal release","Release a consonant into the nasal cavity."),
 ("◌ˡ","lateral release","Release a consonant laterally along the tongue."),
 ("◌̚","no audible release","Maintain the closure without an audible release burst."),
]
DIACRITIC_DATA={s.replace("◌",""):{"symbol":s,"name":n,"description":d,"category":"diacritic"} for s,n,d in DIACRITICS}
SUPRASEGMENTALS=[
 ("ˈ","primary stress","Mark the following stressed syllable (before its onset)."),
 ("ˌ","secondary stress","Mark a following syllable with secondary stress."),
 ("ː","long","Indicate extended duration of the preceding segment."),
 ("ˑ","half-long","Indicate moderately increased duration."),
 ("̆","extra-short","Indicate an especially brief segment."),
 (".","syllable break","Mark a syllable boundary."),
 ("|","minor prosodic group","Mark a minor foot/prosodic boundary."),
 ("‖","major intonation group","Mark a major prosodic boundary."),
 ("‿","linking","Mark absence of a break across a boundary."),
 ("͡","tie bar above","Connect two letters representing one complex segment or double articulation."),
 ("͜","tie bar below","Connect two letters representing one complex segment or double articulation."),
]
SUPRA_DATA={sym:{"symbol":sym,"name":name,"description":desc,"category":"suprasegmental"} for sym,name,desc in SUPRASEGMENTALS}
TONE_LEVEL=[("˥","extra-high"),("˦","high"),("˧","mid"),("˨","low"),("˩","extra-low"),
 ("̋","extra-high (diacritic)"),("́","high (diacritic)"),("̄","mid (diacritic)"),("̀","low (diacritic)"),("̏","extra-low (diacritic)")]
TONE_CONTOUR=[("̌","rising (diacritic)"),("̂","falling (diacritic)"),("᷄","high rising"),("᷅","low rising"),("᷈","rising–falling"),("ꜛ","upstep"),("ꜜ","downstep"),("↗","global rise"),("↘","global fall")]
TONES={sym:{"symbol":sym,"name":name,"category":"tone","description":(f"Mark {name} pitch or pitch movement relative to the language's tonal or intonational system. Numeric interpretation is language-specific.")} for sym,name in TONE_LEVEL+TONE_CONTOUR}
# Ejectives are formed with a modifier letter in the official chart, rather than a separate base-series of letter glyphs.
EJECTIVE_MARKER={"symbol":"ʼ","name":"ejective marker","category":"modifier","description":"After a consonant (e.g. pʼ, tʼ, kʼ, sʼ) indicates glottalic egressive airstream with raised-larynx compression."}

# At least one illustrative pronunciation exercise for EVERY basic chart consonant and vowel;
# these are explicitly constructed exercises, NOT lexical evidence of attestation.
EXAMPLES={}
def lexical(sym,lang,word,ipa,meaning,notes=""):
 EXAMPLES.setdefault(sym,[]).append({"language":lang,"word":word,"ipa":ipa,"meaning":meaning,"type":"illustrative_lexical_example","verification":"pedagogical example; pronunciation can vary by accent","notes":notes})
# Broad, illustrative transcriptions. Avoid overclaiming narrow phones or exact language inventories.
for sym,items in {
 "p":[("English","spin","/spɪn/","turn rapidly")],
 "b":[("English","bat","/bæt/","a flying mammal")],
 "t":[("English","stop","/stɑp/","cease")],
 "d":[("English","dog","/dɔɡ/","domestic animal")],
 "k":[("English","skill","/skɪl/","ability")],
 "ɡ":[("English","go","/ɡoʊ/","move")],
 "m":[("English","map","/mæp/","diagram")],
 "n":[("English","no","/noʊ/","negative response")],
 "ŋ":[("English","sing","/sɪŋ/","make music with the voice")],
 "f":[("English","fine","/faɪn/","good")],
 "v":[("English","vine","/vaɪn/","climbing plant")],
 "θ":[("English","thin","/θɪn/","not thick")],
 "ð":[("English","this","/ðɪs/","demonstrative")],
 "s":[("English","sip","/sɪp/","drink slowly")],
 "z":[("English","zip","/zɪp/","fastener")],
 "ʃ":[("English","ship","/ʃɪp/","large boat")],
 "ʒ":[("English","measure","/ˈmɛʒɚ/","determine an amount")],
 "h":[("English","hat","/hæt/","headwear")],
 "l":[("English","leaf","/lif/","part of a plant")],
 "ɹ":[("English","red","/ɹɛd/","colour")],
 "j":[("English","yes","/jɛs/","affirmative")],
 "w":[("English","wet","/wɛt/","not dry")],
 "ʔ":[("English (many accents)","uh-oh","[ʌʔoʊ]","hesitation/interjection")],
 "ʈ":[("Hindi","टाल","[ʈaːl]","put off")],
 "ɖ":[("Hindi","डाल","[ɖaːl]","put/place")],
 "ɳ":[("Marathi","बाण","[baːɳ]","arrow")],
 "ɭ":[("Malayalam","വെള്ളം","[ʋeɭːam]","water")],
 "ɾ":[("Marathi","राम","[ɾaːm]","proper name")],
 "ɻ":[("Tamil","தமிழ்","[t̪amiɻ]","Tamil")],
 "ɲ":[("Spanish","año","/ˈaɲo/","year")],
 "x":[("Spanish","jota","/ˈxota/","letter name")],
 "β":[("Spanish","lobo","[ˈloβo]","wolf",)],
 "ʎ":[("Italian","famiglia","/faˈmiʎʎa/","family")],
 "r":[("Spanish","perro","/ˈpero/","dog")],
 "i":[("Spanish","sí","/si/","yes")],
 "u":[("Spanish","tú","/tu/","you")],
 "e":[("Spanish","mesa","/ˈmesa/","table")],
 "o":[("Spanish","lobo","/ˈlobo/","wolf")],
 "a":[("Spanish","casa","/ˈkasa/","house")],
 "ɪ":[("English","sit","/sɪt/","be seated")],
 "ʊ":[("English","foot","/fʊt/","body part")],
 "ɛ":[("English","bed","/bɛd/","furniture")],
 "æ":[("English","cat","/kæt/","animal")],
 "ə":[("English","about","/əˈbaʊt/","concerning")],
 "ʌ":[("English","cut","/kʌt/","divide with blade")],
 "ɑ":[("English (US)","father","/ˈfɑðɚ/","male parent")],
 "ɔ":[("English (many accents)","thought","/θɔt/","idea")],
 "y":[("French","tu","/ty/","you")],
 "ø":[("French","deux","/dø/","two")],
 "œ":[("French","sœur","/sœʁ/","sister")],
 "ɛ̃":[("French","vin","/vɛ̃/","wine")],
 "ɯ":[("Turkish","kız","/kɯz/","girl")],
 "ʃ":[("Hindi","शेर","[ʃeːɾ]","lion")],
 }.items():
 for item in items:
  if len(item)==4:lexical(sym,*item)
  else:lexical(sym,*item[:4],notes=item[4])

# Accented common compounds, as optional entries for quick lookup.
COMPOSITES={
 "t͡ʃ": ("voiceless postalveolar affricate","postalveolar","affricate","voiceless","English 'church' /t͡ʃɝt͡ʃ/"),
 "d͡ʒ": ("voiced postalveolar affricate","postalveolar","affricate","voiced","English 'judge' /d͡ʒʌd͡ʒ/"),
 "t͡s": ("voiceless alveolar affricate","alveolar","affricate","voiceless","German 'Zeit' /t͡saɪt/"),
 "d͡z": ("voiced alveolar affricate","alveolar","affricate","voiced","Italian 'zero' /ˈd͡zɛro/ (in one pronunciation)"),
 "t͡ɕ": ("voiceless alveolo-palatal affricate","alveolo-palatal","affricate","voiceless","Polish 'ci' /t͡ɕi/ (illustrative)"),
 "d͡ʑ": ("voiced alveolo-palatal affricate","alveolo-palatal","affricate","voiced","Japanese 'ji' [d͡ʑi] in some contexts"),
 "t͡ʂ": ("voiceless retroflex affricate","retroflex","affricate","voiceless","Mandarin zh (in conventional broad transcription)"),
 "d͡ʐ": ("voiced retroflex affricate","retroflex","affricate","voiced","Polish dż (dialect-dependent)"),
}
for symbol,(name,place,manner,voice,example) in COMPOSITES.items():
 add(symbol,name,"composite_consonant",place,manner,voice,notes="Conventional two-symbol transcription joined with a tie bar; some phonetic descriptions use alternatives.")
 EXAMPLES[symbol]=[{"language":"illustrative","word":example,"ipa":symbol,"meaning":None,"type":"illustrative_reference","verification":"review specific pronunciation with a language reference","notes":"A guide to a commonly cited sound, not an independently verified lexical recording."}]

# Add drill for all symbols, clearly marked constructed, not an attested lexical example.
def examples_for(symbol,language=None):
 items=list(EXAMPLES.get(symbol,[]))
 if symbol in SOUNDS:
  info=SOUNDS[symbol]
  if info.category=="vowel":drill=f"[{symbol}]"
  elif info.manner=="click":drill=f"[{symbol}] (isolated click)"
  else:drill=f"[a{symbol}a]"
  items.append({"language":"not language-specific","word":None,"ipa":drill,"meaning":None,"type":"constructed_articulatory_drill","verification":"not an attested word","notes":"Pronounce the target in isolation or between [a] vowels; this is a constructed exercise."})
 if language:
  return [x for x in items if x["language"].casefold()==language.casefold() or x["language"]=="not language-specific"]
 return items

# Distinguish IPA <g> from the official phonetic glyph <ɡ> in strict output.
ALIASES={"g":"ɡ", "ɫ":"l̴", "ɚ":"ə˞", "ɝ":"ɜ˞"}

def get_sound(symbol):
 if symbol in SOUNDS:return SOUNDS[symbol].to_dict()
 if symbol in ALIASES:return {**get_sound(ALIASES[symbol]),"queried_symbol":symbol,"alias_notice":f"{symbol} is a recognised IPA-compatible glyph or derived form; canonical base shown as {ALIASES[symbol]}."}
 return None

# Examples in the seven South Asian / English languages requested for the prior
# LinguaGloss project. All are BROAD illustrative references, not dialect proofs.
for sym,items in {
 "p":[("Gujarati","પાણી","/paːɳi/","water"),("Tamil","பால்","/paːl/","milk")],
 "b":[("Bangla","বাংলা","/baŋla/","Bangla language")],
 "m":[("Tamil","அம்மா","/amːaː/","mother")],
 "ɳ":[("Gujarati","પાણી","/paːɳi/","water")],
 "ŋ":[("Bangla","বাংলা","/baŋla/","Bangla language")],
 "ɭ":[("Malayalam","വെള്ളം","/ʋeɭːam/","water")],
 "a":[("Bangla","বাংলা","/baŋla/","Bangla language"),("Hindi","राम","[ɾaːm]","personal name")],
 "ʋ":[("Malayalam","വെള്ളം","/ʋeɭːam/","water")],
 "t͡ʃ":[("Hindi","चाय","/t͡ʃaːj/","tea")],
 "ɾ":[("Hindi","राम","[ɾaːm]","personal name; in a tap realisation")],
 "i":[("Gujarati","પાણી","/paːɳi/","water")],
}.items():
 for entry in items:lexical(sym,*entry)

# Some phonetic combinations are conventional non-chart exemplars.
lexical("pʰ","Hindi","फल","[pʰəl]","fruit","Illustrative initial aspirated stop")
lexical("t̪","Hindi","तुम","[t̪ʊm]","you (informal)","Dental stop")

def examples_for(symbol,language=None):
 """Lexical examples where curated; otherwise explicitly synthetic phonetic drill."""
 items=list(EXAMPLES.get(symbol,[]))
 info=SOUNDS.get(symbol)
 if info is None:
  try:
   from .analyze import describe_sequence
   info=describe_sequence(symbol)
  except ValueError:
   info=None
 if info:
  category=info.category if isinstance(info,Sound) else info.get('category')
  manner=info.manner if isinstance(info,Sound) else info.get('manner')
  drill=f"[{symbol}]" if category=='vowel' else f"[{symbol}] (isolated click)" if manner=='click' else f"[a{symbol}a]"
  items.append({"language":"not language-specific","word":None,"ipa":drill,"meaning":None,"type":"constructed_articulatory_drill","verification":"not an attested word","notes":"Constructed IPA sequence for practising the target phone; not a linguistic lexical attestation."})
 if language:
  items=[e for e in items if e['language'].casefold()==language.casefold() or e['language']=='not language-specific']
 return items
