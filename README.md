# <Your product name>

> Fill this top section from your Examate project card on Day 1. Replace every line in angle brackets.

## Problem
TNAU's Agritech Portal has excellent advice on pests,varieties,fertiliser and schemes,but much of it is in English and spread across thousands of pages.Farmers rely on pesticide shop owners who may push products, while a Tamil question needs to find the right English or Tamil page.UzhavarVoice changes this by allowing farmers to ask crop questions in spoken Tamil and get answers from TNAU's expert pages.

## Who it is for
Paddy and banana farmer in Thanjavur district with a basic smartphone, who prefers speaking in Tamil over typing.

## Signature feature
The app must read the answer aloud in simple, conversational Tamil, provide a direct link to the TNAU page, and highlight key details—such as crop varieties, fertilizer doses, or timelines—in large, easy-to-read text.

## Hardest problem (my interview story)
To handle cross-language search—where questions come in Tamil while many source pages are in English—the system compares direct multilingual embeddings against translating the question into English first, measuring retrieval recall separately for Tamil-to-English and Tamil-to-Tamil pairs.

## Dataset
| Source | Link | Documents | Pages | Licence / terms |
|---|---|---|---|---|
|TNAU Agritech Portal |http://www.agritech.tnau.ac.in/|Crop production, protection, released varieties (2019-2025), post-harvest technology, schemes and services (English and Tamil) |Minimum 4,000 pages |Public educational portal content |

## 10 real questions
See [docs/QUESTIONS.md](docs/QUESTIONS.md).

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                 # Windows: copy .env.example .env
uvicorn app.main:app --reload
curl localhost:8000/health
```

## Live link
<Added in Week 2>
