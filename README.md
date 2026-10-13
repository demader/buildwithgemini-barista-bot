# ☕ BaristaBot — Specialty Coffee Concierge & Dial-in Brewing Guide

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Cloud%20Run-blue?style=for-the-badge&logo=googlecloud)](https://barista-bot-frontend-10926667655.us-central1.run.app)
[![Built with Gemini](https://img.shields.io/badge/Built%20with-Gemini%203.8%20Flash-orange?style=for-the-badge&logo=googlegemini)](https://deepmind.google/technologies/gemini/)
[![Powered by ADK](https://img.shields.io/badge/Google-ADK-green?style=for-the-badge)](https://google.github.io/adk-docs/)

> An autonomous AI concierge that remembers your home brewing gear and taste preferences, queries a live specialty coffee bean catalog, calculates precision brew recipes, and generates custom latte art and brewing diagrams.

---

## 🌐 Live Application

- **Live Web Chat (Cloud Run)**: [https://barista-bot-frontend-10926667655.us-central1.run.app](https://barista-bot-frontend-10926667655.us-central1.run.app)
- **Deployed Agent Card (A2A)**: [Agent Card](https://us-central1-aiplatform.googleapis.com/reasoningEngines/v1/projects/10926667655/locations/us-central1/reasoningEngines/474786987937628160/api/a2a/app/.well-known/agent-card.json)

---

## ✨ Features & Capabilities

- 🧠 **Gemini 3.8 Flash Core Engine**: Deep coffee extraction reasoning, dial-in troubleshooting, and conversational brewing advice.
- 🗄️ **Persistent Firestore Roastery Catalog**: Real-time lookups and filters by roast level, origin, and tasting notes.
- 💾 **Vertex AI Memory Bank**: Persistent cross-session recall of user grinders, kettle models, and taste preferences.
- 🎨 **AI Image Generation**: Generates latte art patterns and brewing diagrams using `gemini-3.1-flash-lite-image`, automatically hosted on Google Cloud Storage.
- 🎴 **A2UI Rich Visuals**: Formatted UI cards and recipe tables rendered dynamically in the chat UI.
- ⚡ **A2A Protocol & Cloud Run**: High-performance FastAPI proxy interfacing directly with Vertex AI Agent Runtime over the Agent2Agent protocol.

---

## 🏗️ Architecture

```
[ Web Browser ]
      │ (HTTPS / Chat UI + Native A2UI Renderer)
      ▼
[ Cloud Run Proxy (FastAPI) ]
      │ (A2A Protocol / IAM Authenticated)
      ▼
[ Vertex AI Agent Engine (`gemini-3.8-flash`) ]
 ├── 🗄️ Cloud Firestore (Specialty bean roastery database)
 ├── 💾 Vertex AI Memory Bank (Long-term user preferences)
 ├── 🖼️ Gemini 3.1 Flash-Lite Image -> Cloud Storage Bucket
 └── 🎴 A2UI Schema Manager v0.8
```

---

## 🚀 Running Locally

### 1. Install Dependencies
```bash
agents-cli install
```

### 2. Launch Local Dev Playground
```bash
agents-cli playground
```
Then visit `http://127.0.0.1:8080/dev-ui/?app=app` to interact with BaristaBot locally.

---

## 🤝 Project Submission
Built for the **Build with Gemini** workshop.
- **Repository**: [https://github.com/demader/buildwithgemini-barista-bot](https://github.com/demader/buildwithgemini-barista-bot)
- **Author**: Abhishek Govind ([@demader](https://github.com/demader))
