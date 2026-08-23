# Coffee Leaf AI

Upload a coffee leaf photo, get back a disease prediction, confidence
score, and severity. Next.js frontend, FastAPI + PyTorch backend.

```
coffee-leaf-ai/
├── src/
│   ├── app/
│   │   ├── page.tsx           # landing: hero, upload, how it works
│   │   └── dashboard/page.tsx # full workspace + session history
│   ├── components/            # UploadCard, PredictionResult, InsightPanel, ...
│   ├── hooks/useLeafAnalysis.ts
│   └── lib/                   # api.ts, types.ts
├── backend/
│   └── app/
│       ├── main.py
│       ├── routes/            # health.py, analyze.py
│       ├── services/          # image_processing.py, prediction.py
│       └── models/            # model_loader.py, labels.json, coffee_leaf_model.pth
└── package.json
```

## Run the backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

See `backend/README.md` for how to place a trained
`coffee_leaf_model.pth`, curl examples, and severity thresholds.

## Run the frontend

```bash
cp .env.local.example .env.local   # points the frontend at localhost:8000
npm install
npm run dev
```

Opens at http://localhost:3000. Both the landing page and `/dashboard`
call the real `/analyze` endpoint — no mock data.

## Design

Dark theme, one accent color (green), minimal motion. Tokens live in
`src/app/globals.css`.
