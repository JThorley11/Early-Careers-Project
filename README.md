# Early Careers Project

This project is a full-stack application with a **FastAPI backend** and a **React frontend**.

## Prerequisites

Make sure you have installed:

- Python 3.11–3.12
- Poetry (`pip install poetry`)
- Node.js 18+ and npm
- Git

---

# Setup & Running the Project

## Backend

### Step 1: Enter the backend
```bash
# Backend
cd backend
```

### Step 2: Install dependencies
```bash
poetry install
```

### Step 3: Create a .env file with your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

### Step 4: Run the server
```bash
poetry run uvicorn main:app --reload
```

# Frontend (in a new terminal)

### Step 1: Enter the frontend
```bash
cd frontend
```

### Step 2: Install the dependencies
```bash
npm install
```

### Step 3: Run the server
```bash 
npm start
```


# Create the vector database

### Step 1: Enter the backend
```bash
# Backend
cd backend
```

### Step 2: Create the database (ensure one does not already exist)
```bash
poetry run python build_chromadb.py
```



# Project Structure:

```bash
Early Careers Project/
├─ backend/   # FastAPI backend
│   main.py
│  ├─ build_chromadb.py
│  ├─ test_chromadb.py #for testing db built correctly
│  ├─ pyproject.toml
|  ├─ poetry.lock
|  ├─ data /
│  |   ├─ flood_risk /
│  |   ├─ sustainability_reports /
│  |   └─ urban_spaces /
│  └─ db/    
├─ frontend/  # React frontend
│  ├─ src/
│  |   ├─ App.jsx
│  |   ├─ globals.css
│  |   ├─ index.css
│  |   ├─ index.jsx
│  |   └─ layout.jsx
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ postcss.config.js
│  └─ tailwind.config.js
├─ .gitignore
└─ README.md