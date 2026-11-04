# Progress

Commit after every class. Tag every Friday: `git tag week-N && git push origin week-N`.

## Week 1 (tag week-1 by Fri 23 Oct)
- [x] Repo created from the Examate template and registered on the form
- [x] README top section filled from my project card
- [x] /health runs locally
- [x] docs/QUESTIONS.md: 10 real questions (3 multi-page, 1 unanswerable)
- [x] 50+ pages collected, DATASET.md filled, sample in data/sample/
- [x] Tag week-1 pushed

## Week 2 (tag week-2 by Fri 30 Oct)
- [x] POST /chat calls an LLM and returns structured JSON
- [x] Streaming, timeouts, retry and a fallback model
- [x] Cost log + GET /usage
- [x] Docker Compose (API + Postgres/pgvector) runs
- [x] CI green, live link in README
- [x] Tag week-2 pushed

## Week 3 (tag week-3 by Fri 6 Nov)
- [ ] Parser keeps page numbers and headings
- [ ] 500+ pages chunked, embedded and stored in pgvector
- [ ] POST /ask answers with [document, page] citations
- [ ] docs/EVAL_v0.md with my 10 questions scored
- [ ] Tag week-3 pushed

## Daily log
| Date | What I did today | Commit |
|---|---|---|
| 23 Oct 2026 | Created the UzhavarVoice repository and started collecting agricultural data from the TNAU Agritech Portal. | Initial commit |
| 24 Oct 2026 | Collected agricultural HTML and PDF resources and prepared the dataset structure. | Completed collecting data |
| 25 Oct 2026 | Prepared 10 real-world agricultural questions in Tamil for project evaluation. | updated questions |
| 26 Oct 2026 | Organized banana and paddy sample data and finalized Week 1 dataset documentation. | Finalize Week 1 data collection and samples |
| 27 Oct 2026 | Implemented the LLM-powered chat API and Docker Compose configuration. | feat: add reliable LLM chat and Docker Compose setup |
| 28 Oct 2026 | Configured CI workflow and added automated health-check diagnostics. | ci: add detailed health check diagnostics |
| 29 Oct 2026 | Implemented modular LLM providers, token usage tracking and API tests. | feat: add modular LLM providers and usage tracking |
| 30 Oct 2026 | Integrated PostgreSQL usage tracking and fixed usage persistence. | fix: restore PostgreSQL usage tracking |
| 1 Nov 2026 | Deployed the API using Render and connected Supabase PostgreSQL. Verified the deployed endpoints. | Week 2 documentation and deployment updates |
| 3 Nov 2026 | Updated Week 1 and Week 2 documentation, verified GitHub Actions and pushed the `week-2` tag. | Update Week 1 and Week 2 project documentation |
