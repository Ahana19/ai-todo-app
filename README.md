
To‑Do List Streamlit App with HuggingFace AI
===========================================


Features
--------
- Simple To‑Do app with SQLite persistence.
- AI-powered priority suggestion using HuggingFace zero-shot classification (facebook/bart-large-mnli).
- Works without API key (for light use); set HUGGINGFACEHUB_API_TOKEN for reliability.


Files
-----
- app.py 
- requirements.txt


requirements.txt
----------------
streamlit
requests


Quick run locally
-----------------
1. python -m venv venv && source venv/bin/activate
2. pip install -r requirements.txt
3. streamlit run app.py


Deploy to Streamlit Community Cloud
----------------------------------
1. Push app.py + requirements.txt to a GitHub repo.
2. Go to https://share.streamlit.io and deploy.
3. Get your public URL.


Deploy to Replit

1. Create a new Python Repl, upload files.
2. pip install -r requirements.txt
3. Run: streamlit run app.py --server.port=$PORT
4. Replit will give you a public URL.


'''
