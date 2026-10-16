# Integrate with a Linguistics / Leipzig Glossing API

The IPA Atlas API can run as a separate service, or can be mounted into the existing LinguaGloss FastAPI app without changing either API's source data.

```python
from fastapi import FastAPI
from ipa_atlas.main import app as ipa_app

main_app = FastAPI(title="Linguistics Student Toolkit")
main_app.mount("/ipa", ipa_app)
```

Example endpoints under this mount:

- `/ipa/` — IPA browser reference
- `/ipa/v1/sounds/describe?symbol=ɳ` — phonetic sound explanation
- `/ipa/v1/analyze` — IPA segmentation and diacritics
- `/ipa/v1/resources` — references

This API does *not* automatically gloss morphology. A future workflow can first store transcribed lexical items in a student corpus, inspect phone sequences through IPA Atlas, and then manually choose morpheme boundaries and glosses in LinguaGloss.

If mounting a sub-app, static assets remain within its mount path. Build client-side paths relative to the mount if deploying the included standalone browser interface under a sub-path; the supplied HTML currently uses root-relative URLs for standalone use.
