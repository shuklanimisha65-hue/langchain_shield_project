Deepfake Shield

  Deepfake Shield is a forensic web tool that helps you figure out whether a piece of media — an image, a video,
  or even just a claim — is real or synthetically manipulated. It combines live
  news verification with local AI-powered analysis to give you a structured,
  technical verdict.

  Built with Streamlit, LangChain, and Groq-hosted LLMs. No cloud black box — you
  control what gets analyzed.

  ---
  What it does

  Drop in a suspicious image, video, or text claim, and the app walks you through
  two steps:

  Step 1 — Check the news wire
  It searches NewsAPI to see if the media or claim already has a real-world
  digital footprint. If something is going viral and it's real, there's usually a
  paper trail.

  Step 2 — Run local AI forensics
  This is where it gets interesting. Depending on what you uploaded:

  - Image — the vision model inspects pixel-level artifacts, lighting
  inconsistencies, and edge anomalies.
  - Video (.mp4) — three key frames are extracted and fed to the model for
  temporal analysis.
  - Text only — a RAG pipeline retrieves relevant forensic knowledge from a local
  shield.txt knowledge base and reasons over your claim.

  Every report breaks down into four sections:
  1. Risk Rating — Low / Medium / High chance of manipulation
  2. Structural Artifacts — specific technical red flags found in the media
  3. Logical Consistency — does the claim even make sense in context?
  4. Verification Verdict — what you should do next

  ---
  Tech Stack

  The app is built on Streamlit for the UI, with Groq powering two LLMs —
  llama-3.3-70b-versatile for text reasoning and
  meta-llama/llama-4-scout-17b-16e-instruct for vision. Embeddings use
  HuggingFace's all-MiniLM-L6-v2, stored in a LangChain InMemoryVectorStore. Video
  processing runs through OpenCV, news lookups hit NewsAPI, and secrets are
  managed via python-dotenv.
