# Chat_BotPy — Run & Test Guide

## Run locally
1) Install deps
```
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) Environment (.env in backend/)
```
MONGODB_URI=mongodb://localhost:27017/japanese_learning
AI_PROVIDER=openai              # or myai
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
COURSE_SERVICE_BASE_URL=http://course-service/storefront/courses
HOST=0.0.0.0
PORT=5001
DEBUG=true
```

3) Start service
```
cd backend
python run.py
```
Swagger: http://localhost:5001/apidocs

## Core API test (Postman/Swagger)

### 1) Create conversation
POST `/api/conversation`
```
{
  "user_id": "user-123",
  "topic": "travel",
  "level": "N4"
}
```
→ 201 with `conversation_id`

### 2) Send message (chat & persist)
POST `/api/conversation/{conversation_id}/messages`
```
{
  "message": "昨日、日本へ行きます。",
  "response_time": 2300
}
```
→ 200 with `user_message`, `ai_message`

### 3) Evaluate conversation (persist analysis)
POST `/api/v1/ai/evaluate`
```
{
  "conversation_id": "<id>",
  "jlpt_target": "N4"
}
```
→ 200 with `jlpt_estimation`, `scores`, `errors`
→ Also writes to `conversation_analyses` and updates conversation cache

### 4) AI chat (testing only, requires conversation_id, no persistence)
POST `/api/v1/ai/chat`
```
{
  "conversation_id": "<id>",
  "user_id": "user-123",
  "role": "student",
  "language": "ja",
  "jlpt_target": "N4",
  "conversation_mode": "speaking_practice",
  "message": "週末は何をしますか？"
}
```
→ 200 with `reply`, no DB changes

### 5) Correct sentence
POST `/api/v1/ai/correct-sentence`
```
{ "sentence": "日本へ行きたいですから勉強します" }
```
→ 200 with `original`, `corrected`, `explanation_vi`

### 6) Recommendations
GET `/api/conversation/{conversation_id}/recommendations`
→ 200 list of courses by JLPT target (uses `COURSE_SERVICE_BASE_URL`)

## Expected responses (examples)
- `/conversation/{id}/messages`: `{"user_message": {...}, "ai_message": {...}, "overall_score": {"grammar":0,"vocabulary":0,"fluency":0,"naturalness":0,"total":0}}`
- `/api/v1/ai/evaluate`: `{"jlpt_estimation":"N4","scores":{"grammar":78,"vocabulary":75,"fluency":90,"naturalness":76},"errors":{"grammar":["..."],"particles":["..."]}}`
- Error non-ja language: `{"error":"Language not supported yet"}`, HTTP 400
- Missing conversation_id for `/api/v1/ai/chat`: `{"error":"conversation_id is required"}`, HTTP 400



