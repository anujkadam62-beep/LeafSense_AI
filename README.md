# LeafSense AI

**AI-powered Leaf Disease Detection and Severity Analysis**

LeafSense AI is a full-stack web application that analyzes plant leaf images to detect whether a leaf is healthy or unhealthy, estimate the affected area, and visualize the complete image-processing pipeline. The project combines a **Next.js frontend** with a **FastAPI backend** running an EfficientNet-B0 model for classification and OpenCV-based image processing for disease visualization.

## Features

* Upload leaf images for instant analysis.
* Detect **Healthy** or **Unhealthy** leaves using EfficientNet-B0.
* Estimate disease severity based on affected leaf area.
* Visualize each processing stage:

  * Original Image
  * Segmented Leaf
  * Affected Region
* Built-in model evaluation dashboard.
* Modern responsive UI with a dark green agricultural theme.
* Demo login flow for portfolio presentation.

## Demo Preview

* Login screen
* Interactive dashboard
* Image upload and analysis
* HSV segmentation visualization
* Model evaluation metrics

> Add screenshots inside `public/screenshots/` and update this section later.

## Tech Stack

| Layer            | Technology                 |
| ---------------- | -------------------------- |
| Frontend         | Next.js, React, TypeScript |
| Styling          | Tailwind CSS               |
| Backend          | FastAPI                    |
| AI Model         | EfficientNet-B0 (PyTorch)  |
| Image Processing | OpenCV                     |
| Evaluation       | Scikit-learn, Matplotlib   |
| Deployment       | GitHub Codespaces          |

## Project Structure

```text
LeafSense-AI/
├── backend/
│   ├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── uploads/
│   └── validation_dataset/
├── public/
├── src/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   └── lib/
├── package.json
└── README.md
```

## Image Processing Pipeline

The application follows a complete computer vision workflow.

1. Image Upload
2. Preprocessing
3. HSV Color Conversion
4. Leaf Segmentation
5. Disease Region Detection
6. Feature Extraction
7. AI Classification
8. Severity Estimation
9. Result Visualization

## Model Evaluation

The dashboard includes an evaluation section that displays:

* Accuracy
* Precision
* Recall
* F1 Score
* Per-class metrics
* Confusion Matrix
* Validation dataset statistics

The backend automatically evaluates the bundled validation dataset or a user-uploaded ZIP dataset.

## Installation

### Clone the repository

```bash
git clone https://github.com/anujkadam62-beep/practice.git
cd practice
```

### Frontend

```bash
npm install
npm run dev
```

Runs on:

```text
http://localhost:3000
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Runs on:

```text
http://localhost:8000
```

## How It Works

1. User uploads a leaf image.
2. Backend preprocesses the image.
3. HSV segmentation isolates the leaf.
4. Disease regions are highlighted.
5. EfficientNet-B0 predicts the leaf health.
6. Severity is estimated from the affected area.
7. Dashboard displays predictions, confidence score, and processing visuals.

## Current Status

### Completed

* Full Next.js frontend
* FastAPI backend
* Leaf upload workflow
* HSV segmentation
* Disease highlighting
* Severity estimation
* Model evaluation dashboard
* Responsive UI
* GitHub deployment

### Future Improvements

* Multi-species leaf support
* Multiple disease categories
* Real authentication
* History of previous analyses
* Mobile application
* Farmer dashboard

## License

This project is for educational, research, and portfolio purposes.

## Author

**Anuj Kadam**

* GitHub: https://github.com/anujkadam62-beep
* Data Science Student
* Interested in AI, Computer Vision, and Agriculture Technology
