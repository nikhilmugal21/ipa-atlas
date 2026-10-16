"""Optional FastAPI router; include with app.include_router(marathi_router)."""
from fastapi import APIRouter, Query
from .marathi_lexicon import records, search, examples_for_sound

router=APIRouter(prefix='/v1/marathi',tags=['Marathi phonetic lexicon'])

@router.get('/summary')
def summary():
    r=records()
    return {'language':'Marathi','rows':len(r),
            'unique_orthographies':len({x['orthography'] for x in r}),
            'broad':sum(x['transcription_level']=='broad' for x in r),
            'narrow':sum(x['transcription_level']=='narrow' for x in r),
            'verification':'source-extracted, not expert-reviewed'}

@router.get('/words')
def words(q:str='',phone:str='',level:str='',limit:int=Query(50,ge=1,le=1000)):
    if level and level not in ('broad','narrow'):
        return {'error':'level must be broad or narrow','items':[]}
    return {'items':search(q,phone,level,limit)}

@router.get('/phone/{symbol}')
def phone_examples(symbol:str,limit:int=Query(12,ge=1,le=100)):
    return {'phone':symbol,'examples':examples_for_sound(symbol,limit=limit)}
