"""Streamlit extra page. Upload to pages/ at your existing IPA Atlas repo root."""
import csv
import io
from collections import Counter
import streamlit as st
from ipa_atlas.marathi_lexicon import search, records

st.set_page_config(page_title='Marathi Lexicon · IPA Atlas',page_icon='📖',layout='wide')
st.title('मराठी · Marathi Phonetic Lexicon')
st.caption('WikiPron/Wiktionary-sourced transcriptions. Broad vs narrow readings are preserved. Not expert-validated or speaker-recorded.')
rows=records()
if not rows:
    st.error('Dataset missing. Put data/marathi_examples.csv in the repository root, next to streamlit_app.py.')
    st.stop()
c1,c2,c3=st.columns(3)
c1.metric('Pronunciation records',len(rows))
c2.metric('Distinct Marathi forms',len({r['orthography'] for r in rows}))
c3.metric('Narrow records',sum(r['transcription_level']=='narrow' for r in rows))
with st.container(border=True):
    q=st.text_input('Search Marathi word, English meaning or IPA',placeholder='पाणी, retroflex, /paɳi/ …')
    a,b=st.columns(2)
    with a:
        phonelist=sorted({t for r in rows for t in r['ipa_tokens'].split('|') if t})
        phone=st.selectbox('Filter by IPA phone', ['All phones']+phonelist)
    with b:
        level=st.radio('Transcription', ['Both','Broad (/ /)','Narrow ([ ])'],horizontal=True)
    kind={'Both':'','Broad (/ /)':'broad','Narrow ([ ])':'narrow'}[level]
    matches=search(q=q,phone='' if phone=='All phones' else phone,level=kind,limit=1000)
st.caption(f'{len(matches)} result(s) shown (up to 1,000). Source-extracted does not imply independent phonetic verification.')
show=[{'Word':r['orthography'],'IPA':r['ipa'],'Type':r['transcription_level'],
        'English gloss (editorial)':r['meaning_en'] or '—','Review':'Unreviewed'} for r in matches]
st.dataframe(show,use_container_width=True,hide_index=True)
if matches:
    entries=list(dict.fromkeys(x['orthography'] for x in matches))
    selected=st.selectbox('Inspect word and source',entries)
    for r in [a for a in matches if a['orthography']==selected]:
        with st.container(border=True):
            st.subheader(f"{r['orthography']} · {r['ipa']}")
            st.write('**Segment sequence:**',r['source_segmented_ipa'])
            st.write('**Transcription type:**',r['transcription_level'])
            st.write('**Dialect:**',r['dialect'])
            st.write('**Source:**',r['source_name'])
            st.markdown(f"[Original dictionary entry]({r['wiktionary_entry_url']}) · [WikiPron source file]({r['source_file_url']})")
            st.warning('Check the source IPA, syllabification, lexeme sense and regional pronunciation before citing this word as phonetic evidence.')
    out=io.StringIO();writer=csv.DictWriter(out,fieldnames=matches[0].keys());writer.writeheader();writer.writerows(matches)
    st.download_button('Download filtered CSV',out.getvalue().encode('utf-8-sig'),'marathi_ipa_filtered.csv','text/csv')
st.divider()
st.markdown('**Academic citation:** Lee et al. (2020), *Massively Multilingual Pronunciation Modeling with WikiPron*, LREC, pp. 4223–4228. Dataset transcriptions originate from Wiktionary. See project README for licenses.')
