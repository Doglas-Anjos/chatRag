# ChatRAG - RAG-powered Chat Application

This is a full-stack application that implements a ChatGPT-like interface using RAG (Retrieval Augmented Generation). The project is built with Django (backend) and React (frontend).

## Project Structure

```
chatRAG/
├── backend/         # Django backend application
└── frontend/        # React frontend application
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Features

- RAG-powered chat interface
- Document upload and processing
- Real-time chat responses
- Modern and responsive UI

## Technologies Used

- Backend:
  - Django
  - Django REST Framework
  - LangChain
  - Vector Database (FAISS/Chroma)
  - OpenAI API

- Frontend:
  - React
  - TypeScript
  - Tailwind CSS
  - Axios 