# Compileit RAG Chat

En svenskspråkig chat-applikation som svarar på frågor om innehållet på [compileit.com](https://compileit.com) med hjälp av RAG (Retrieval-Augmented Generation) och en LangGraph-agent med tool calling.

## Arkitektur

```
Next.js (chat UI, SSE)  ──▶  FastAPI  ──▶  LangGraph agent (gpt-4o-mini)
                                              │
                                              ├─ Tool: search_compileit  ──▶ Chroma (vektorindex)
                                              └─ Tool: fetch_page        ──▶ httpx + trafilatura
```

Indexering sker offline via ett separat CLI-script som crawlar `compileit.com` (sitemap.xml + BFS-fallback), rensar HTML med `trafilatura`, chunk:ar med `RecursiveCharacterTextSplitter` och bygger ett persistent Chroma-index.

## Why this design

1. **LangGraph + tool calling** – uppgiften kräver orchestration med tool calling. LangGraph ger en tydlig agent-loop, inbyggt konversationsminne (`MemorySaver`) per `thread_id` och förstklassigt streaming-stöd.
2. **Single agent, inte multi-agent** – scope:t (en webbplats, en domän) motiverar inte koordinationsoverhead. Multi-agent vore overengineering.
3. **Citat och "vet ej" före allt annat** – system-prompten tvingar modellen att svara endast utifrån hämtad kontext och alltid inkludera källor. Adresserar hallucinationskravet direkt.
4. **Chroma lokalt** – noll infrastruktur för granskaren att sätta upp. Retriever-lagret är abstraherat så det enkelt byts mot pgvector/Pinecone i produktion.
5. **SSE token-streaming** – upplevd snabbhet via Server-Sent Events utan WebSocket-komplexitet. Frontend parsar SSE-events och renderar tokens i realtid.


## Förutsättningar

- Python 3.11+
- Node.js 20+
- En OpenAI API-nyckel

## Viktigt om API-nycklar

- **Demo/PoC:** En egen OpenAI-nyckel används för att demonstrera lösningen.  
- **Produktion:** Byt ut `OPENAI_API_KEY` i `.env` mot er egna nyckel.  
- **Byta till lokal LLM:** Ersätt `ChatOpenAI` med `ChatOllama` i `backend/app/agent.py` – inga andra ändringar behövs.

> **OBS:** `.env` är i `.gitignore` och publiceras aldrig till GitHub.  
> Nyckeln kan skapas på https://platform.openai.com/api-keys

## Installation och körning

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
copy .env.example .env
# Öppna .env och lägg in din OPENAI_API_KEY
```

### 2. Bygg vektorindexet (görs en gång)

```powershell
python -m ingest.build_index
```

Detta crawlar `compileit.com`, rensar HTML och bygger ett Chroma-index i `./chroma_db/`.

### 3. Starta API:t

```powershell
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend

I en ny terminal:

```powershell
cd frontend
npm install
npm run dev
```

Öppna http://localhost:3000.

## Exempel på testfrågor

- "Vad erbjuder ni för typer av AI-tjänster?"
- "Vilka branscher jobbar ni med?"
- "Hur kontaktar man er, och var sitter ni?"
- "Har ni beskrivit hur ni jobbar med säkerhet/sekretess?"
- "Sammanfatta sidan 'Om oss' i tre punkter och länka källan."

Och en uppföljningsfråga inom samma session:
- "Kan du utveckla det första svaret?"

## Projektstruktur

```
backend/
  app/
    main.py        FastAPI + SSE-endpoint
    agent.py       LangGraph ReAct-agent
    tools.py       search_compileit, fetch_page
    retriever.py   Chroma-wrapper
    prompts.py     System prompt (svenska)
    config.py      Settings via pydantic
  ingest/
    crawl.py       sitemap.xml + BFS
    clean.py       trafilatura-rensning
    build_index.py CLI för att bygga indexet
  tests/
frontend/
  app/             Next.js App Router
  components/      ChatWindow, Message, SourceList
```
---

## Driftsättning (produktion)

> **För att köra och testa projektet lokalt** – använd installationsstegen ovan (Python + Node).  
> Docker och GCP är dokumenterat här för referens vid ev. produktionsdeploy.

### Lokalt med Docker Compose

```bash
# 1. Sätt OPENAI_API_KEY i backend/.env

# 2. Bygg Chroma-indexet lokalt först (kräver .env och OpenAI-nyckel)
#    Kör från backend/ med aktiverat venv:
python -m ingest.build_index

# 3. Gå tillbaka till roten och starta hela stacken med Docker
cd ..
docker-compose up --build
```

Öppna http://localhost:3000. Chroma-datan persisteras i en Docker-volym (`chroma_data`).

### Backend – GCP Cloud Run

```bash
# Bygg och publicera Docker-image
cd backend
gcloud builds submit --tag gcr.io/PROJECT_ID/compileit-rag-backend .

# Deploya till Cloud Run (--min-instances 1 eliminerar cold starts)
gcloud run deploy compileit-rag-backend \
  --image gcr.io/PROJECT_ID/compileit-rag-backend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --min-instances 1 \
  --set-env-vars OPENAI_API_KEY=sk-...
```

### Frontend – Vercel

```bash
npm i -g vercel
cd frontend
vercel --prod
# Sätt NEXT_PUBLIC_API_URL till Cloud Run-URL:en i Vercel dashboard
```

### Integration i Compileits webbplats

Chatten kan bäddas in som en **floating chat widget** direkt på compileit.com:

```html
<!-- Lägg till i <head> -->
<script>
  window.CompileitChat = { apiUrl: "https://chat-api.compileit.com" };
</script>
<script src="https://chat.compileit.com/widget.js" defer></script>
```

En blå chattbubbla nere i höger hörn öppnar chatten utan att navigera bort från sidan – likt Intercom men helt under er kontroll. Besökare får svar direkt, med källhänvisningar och utan risk för felaktig information.

---

## Leverans

1. Publicera repot på GitHub (publikt eller privat med @Compileit-case inbjuden)
2. Maila linda.svedin@compileit.com med länk till repot
3. Bjud in @Compileit-case som collaborator på GitHub

