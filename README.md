# 🍎 Nutrition Backend  
**Backend service for the Nutritions-AI platform**

---

## 🧩 Overview
`nutrition_backend` is the backend API powering the **Nutritions-AI** platform — a system that helps users analyze, validate, and plan their nutrition data intelligently using AI.  
It provides endpoints for interacting with OpenAI models, validating health data, and executing nutrition-related tool functions.

---

## 🚀 Features
- ✅ **Health data validation** (height, weight, BMI, etc.)  
- 🧠 **Integration with OpenAI** for nutrition and health planning  
- ⚙️ **Tool functions** for domain-specific operations  

---

## 🏗 Architecture
```
nutrition_backend/
│
├── main.py              # App entry point (FastAPI/Flask)
├── models.py            # Data models (Pydantic)
├── openai_client.py     # Handles OpenAI API calls
├── tool_functions.py    # Nutrition/health-specific functions
├── test_main.http       # Example API tests
└── .idea/, __pycache__/ # IDE & compiled files (ignore)
```

---

## ⚙️ Getting Started

### 1️⃣ Prerequisites
- Python **3.9+**
- (Optional) Virtual environment tool (`venv`, `pipenv`, or `poetry`)
- OpenAI API key  
- (Optional) Any additional API keys or DB connections

---

### 2️⃣ Installation
```bash
git clone https://github.com/nutritions-ai/nutrition_backend.git
cd nutrition_backend
python -m venv .venv
source .venv/bin/activate      # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, create one:
```bash
pip freeze > requirements.txt
```

---

### 3️⃣ Configuration
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
# Add more variables as needed
```

---

### 4️⃣ Running the Server
If using **FastAPI + Uvicorn**:
```bash
uvicorn main:app --reload
```
Then open your browser at  
👉 `http://localhost:8000`  
👉 or check interactive docs at `http://localhost:8000/docs`

---

