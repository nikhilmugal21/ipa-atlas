# Deploy IPA Atlas on Streamlit Community Cloud

This project contains **two separate entry points**:
- `streamlit_app.py`: interactive student website for Streamlit Community Cloud.
- `ipa_atlas/main.py`: original FastAPI REST service for platforms that support web APIs.

**Important:** A Streamlit app hosted on Streamlit Community Cloud is not a public REST API. This adaptation invokes the same analysis code from the Python package directly; it does not start a second server, and does not expose the FastAPI endpoints to external callers.

## 1. Test on your computer

From the unzipped repository folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

On Windows, activate with `.venv\Scripts\activate`. A browser will usually open at `http://localhost:8501`.

## 2. Upload to GitHub

Option A: In GitHub, click **New repository**, name it `ipa-atlas`, make it public or private as you prefer, then **Add file → Upload files** and upload the **contents of the extracted project folder**, keeping the directory structure. Commit the files. Do not upload the `.zip` as your sole repository file.

Option B: From the extracted folder:

```bash
git init
git add .
git commit -m "Add IPA Atlas Streamlit explorer"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ipa-atlas.git
git push -u origin main
```

Make sure `streamlit_app.py`, `requirements.txt`, `ipa_atlas/`, and `.streamlit/config.toml` are at the repository root in the same hierarchy shown below. Do not commit `.venv`.

## 3. Deploy on Streamlit

1. Visit <https://share.streamlit.io> and sign in with GitHub.
2. Click **Create app**, then **Yup, I have an app**.
3. Set **Repository** to `YOUR-USERNAME/ipa-atlas` and **Branch** to `main`.
4. Set **Main file path** to `streamlit_app.py`.
5. Optional: choose an app URL such as `ipa-atlas-linguistics`.
6. In Advanced Settings you can choose Python 3.12, which is a suitable target for this code.
7. Click **Deploy**. You will receive a shareable `.streamlit.app` URL.

Streamlit reads the root-level `requirements.txt` automatically. The app needs no API tokens, external services or secrets for the core sound explorer.

## Repository layout

```text
ipa-atlas/
├── streamlit_app.py        # Cloud entry point
├── requirements.txt        # Streamlit + original API dependencies
├── .streamlit/
│   └── config.toml
├── ipa_atlas/
│   ├── __init__.py
│   ├── catalog.py
│   ├── analyze.py
│   ├── english.py
│   ├── inventories.py
│   ├── main.py            # FastAPI, NOT the Cloud entry point
│   └── static/
│       └── index.html
├── scripts/
├── tests/
├── README.md
├── STREAMLIT_DEPLOY.md
└── THIRD_PARTY.md
```

## Features in the Streamlit app

- Browse and filter all core IPA segment entries and example affricates.
- Read articulatory descriptions and feature fields.
- Explore lexical illustrations in Hindi, Marathi, Bangla, Malayalam, Gujarati, Tamil and English, and clearly labeled constructed sound drills.
- Analyse `[phonetic]` or `/phonemic/` IPA strings, including common diacritics.
- Compare two phones' articulatory features.
- Browse diacritics, stress and tone.
- Optionally query CMUdict or an imported local PHOIBLE database.
- Export results as JSON files.

## Optional databases

To add CMUdict lookup, add `cmudict>=1.0,<2` to `requirements.txt` and redeploy, after checking the licensing terms described in `THIRD_PARTY.md`.

To add PHOIBLE inventories, follow `README.md` and import a *licensed, pinned-version* PHOIBLE CSV into `data/phoible.sqlite`. The app uses the local read-only SQLite database if present. **Do not commit that database until you have verified its redistribution licence, attribution requirements and the visibility of your repository.** On Streamlit Community Cloud, databases written to the app instance at runtime are not suitable for persistent shared storage.

## If you need an actual internet-accessible REST API

Deploy FastAPI on a Python web hosting service that supports long-running ASGI processes, using a command such as:

```bash
uvicorn ipa_atlas.main:app --host 0.0.0.0 --port $PORT
```

Then its endpoints such as `/v1/chart`, `/v1/sounds/describe` and `/docs` will be accessible at your API service's URL. Your Streamlit frontend does **not** require that service when hosted by itself because it shares the local Python code.

## Troubleshooting

- **ModuleNotFoundError: ipa_atlas:** Keep the `ipa_atlas/` folder at the root beside `streamlit_app.py`.
- **No module named streamlit:** Install root-level dependencies with `pip install -r requirements.txt`.
- **Repository shows only a ZIP:** Extract the ZIP and upload the uncompressed files and folders.
- **No PHOIBLE inventories:** The optional database is not bundled by default.
- **Dictionary unavailable:** `cmudict` is deliberately optional; normal IPA exploration works without it.
- **GitHub permission errors:** Connect the correct GitHub account and select a repository you can access.
- **App fails to start:** Open Streamlit's deployment logs and inspect dependency or import errors.

Official resources:
- <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>
- <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies>
- <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization>
