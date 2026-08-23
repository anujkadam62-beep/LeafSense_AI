# Coffee Leaf AI — Backend

FastAPI backend with a PyTorch inference pipeline for coffee leaf
disease detection: upload an image, get back a prediction, confidence,
severity, and the full probability distribution.

## Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI app, CORS, model preload on startup
│   ├── routes/
│   │   ├── analyze.py          # POST /analyze — validate → preprocess → predict
│   │   └── health.py           # GET /health — liveness + model_loaded flag
│   ├── services/
│   │   ├── image_processing.py # bytes -> validated, normalized tensor
│   │   └── prediction.py       # inference, softmax, severity estimation
│   ├── models/
│   │   ├── model_loader.py     # singleton model load, device detection
│   │   ├── labels.json         # class index -> disease name
│   │   └── coffee_leaf_model.pth   # ⚠️ not included — see below
│   └── utils/
│       ├── exceptions.py       # InvalidImageError, ModelNotAvailableError
│       └── logger.py
├── scripts/
│   └── create_dummy_weights.py # throwaway weights for local testing
└── requirements.txt
```

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

`torch`/`torchvision` install a CPU build by default. For a CUDA GPU,
install PyTorch first following https://pytorch.org/get-started/locally/,
then run `pip install -r requirements.txt` for the rest.

## Placing your trained model

The architecture is **ResNet-18** (torchvision) with its final layer
replaced to output `len(labels.json)` classes — see
`app/models/model_loader.py::_build_architecture`. Train against this
same architecture so the saved weights load back in correctly.

1. Train against `app/models/labels.json`'s 4 classes (`Healthy`,
   `Coffee Leaf Rust`, `Cercospora Leaf Spot`, `Phoma`) — edit
   `labels.json` first if your classes differ.
2. Save weights with either:
   ```python
   torch.save(model.state_dict(), "coffee_leaf_model.pth")
   ```
   or a checkpoint dict with a `"state_dict"` / `"model_state_dict"`
   key — both are supported.
3. Copy the file to `backend/app/models/coffee_leaf_model.pth`.
4. Restart the server. Startup logs confirm `Model loaded successfully
   on cpu` (or `cuda`).

**No weights yet?** The server still starts. `/health` reports
`"model_loaded": false`, and `/analyze` returns a `500` with
`{"error": "Model weights not found..."}` until you add one. To
exercise the full pipeline in the meantime with a random-initialized
model:

```bash
python scripts/create_dummy_weights.py
```

Predictions from that file are meaningless — it's for wiring/testing
only.

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Testing with curl

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/analyze \
  -F "file=@/path/to/leaf.jpg;type=image/jpeg"
```

Success response (`200`):

```json
{
  "prediction": "Coffee Leaf Rust",
  "confidence": 97.8,
  "severity": "High",
  "probabilities": {
    "Healthy": 1.1,
    "Coffee Leaf Rust": 97.8,
    "Cercospora Leaf Spot": 0.6,
    "Phoma": 0.5
  },
  "processing_time_ms": 45
}
```

Error cases:

```bash
# Invalid / corrupted image -> 400
curl -X POST http://localhost:8000/analyze -F "file=@/path/to/not-an-image.txt;type=image/jpeg"

# Missing weights -> 500 with {"error": "..."}
```

## Severity thresholds

Defined in `app/services/prediction.py`:

| Confidence in predicted class | Severity   |
|---|---|
| Prediction is "Healthy"       | `None`     |
| ≥ 85%                         | `High`     |
| 60–85%                        | `Moderate` |
| < 60%                         | `Low`      |

This is a confidence-based proxy until a real affected-area
segmentation stage exists — tune `SEVERITY_HIGH_THRESHOLD` /
`SEVERITY_MODERATE_THRESHOLD` once you have validation data.

## Logging

Every request logs device selection, model load status, prediction
start, result + inference time, and any errors via the standard
`logging` module, printed to stdout with timestamps.
