# Review Code & Upgrade Plan - Chat_BotPy Core AI

## 1. Code Review - Mapping với BRD/SRS

### 1.1 Điểm mạnh hiện tại ✅

- ✅ Có structure rõ ràng: models, services, controllers, repositories
- ✅ Đã có AI service với OpenAI integration
- ✅ Đã có scoring service với 4 tiêu chí (grammar, vocabulary, fluency, naturalness)
- ✅ Đã có analysis modules (grammar, vocabulary, fluency)
- ✅ Đã có authentication với Keycloak
- ✅ Đã có recommendation service

### 1.2 Gaps so với BRD/SRS ❌

#### Data Models
- ❌ Thiếu `conversation_mode` (speaking_practice, role_play, jlpt_exam, free_conversation)
- ❌ Thiếu `language` field (mặc định "ja")
- ❌ Thiếu `jlpt_estimation` trong analysis
- ❌ Thiếu `grammar_errors`, `particle_errors` trong MessageAnalysis
- ❌ Thiếu `keigo` analysis
- ❌ Thiếu `ConversationAnalysis` model riêng (tách khỏi Conversation)
- ❌ Thiếu `summary` field trong Conversation

#### API Endpoints
- ❌ Thiếu `/api/v1/ai/chat` (theo spec)
- ❌ Thiếu `/api/v1/ai/evaluate` (theo spec)
- ❌ Thiếu `/api/v1/ai/correct-sentence` (theo spec)
- ⚠️ Routes hiện tại không match với spec (thiếu `/api/v1/ai/` prefix)

#### Analysis Services
- ❌ Thiếu `keigo_analyzer`
- ❌ Thiếu `jlpt_level_estimator`
- ❌ Thiếu `particle_analyzer`
- ⚠️ Grammar analyzer chưa track `grammar_errors` và `particle_errors` chi tiết

#### Response Format
- ❌ Response chưa match với spec (thiếu `jlpt_estimation`, `errors` structure)

---

## 2. Upgrade Plan

### Phase 1: Data Models & Schema (Priority: HIGH)

#### 2.1 New Models
1. **ConversationMode** (Enum)
   - speaking_practice
   - role_play
   - jlpt_exam
   - free_conversation

2. **Enhanced MessageAnalysis**
   - Add: `grammar_errors: List[str]`
   - Add: `particle_errors: List[str]`
   - Add: `keigo_score: Optional[float]`
   - Add: `jlpt_estimation: Optional[str]`

3. **ConversationAnalysis** (New Model)
   - conversation_id
   - jlpt_estimation
   - scores (grammar, vocabulary, fluency, naturalness)
   - errors (grammar, particles)
   - common_mistakes
   - created_at

4. **Enhanced Conversation**
   - Add: `conversation_mode: ConversationMode`
   - Add: `language: str` (default: "ja")
   - Add: `jlpt_target: str` (alias for level)
   - Add: `summary: Optional[str]`

#### 2.2 Database Schema Updates
- Indexes: `user_id`, `conversation_mode`, `jlpt_target`
- Collection: `conversation_analyses` (separate from conversations)

---

### Phase 2: Analysis Services (Priority: HIGH)

#### 2.1 New Analyzers
1. **keigo_analyzer.py**
   - Detect keigo usage
   - Score keigo correctness
   - Suggest keigo improvements

2. **jlpt_level_estimator.py**
   - Estimate JLPT level from conversation
   - Based on grammar, vocabulary complexity
   - Return: "N5", "N4", "N3", "N2", "N1"

3. **particle_analyzer.py**
   - Detect particle errors (は/が, に/で, etc.)
   - Return list of particle mistakes

#### 2.2 Enhanced Existing Analyzers
- **grammar_analyzer.py**: Add `grammar_errors` tracking
- **vocabulary_analyzer.py**: Enhance with JLPT level detection

---

### Phase 3: API Endpoints (Priority: HIGH)

#### 3.1 New Routes (`/api/v1/ai/`)
1. **POST /api/v1/ai/chat**
   - Match spec exactly
   - Input: user_id, role, language, jlpt_target, conversation_mode, message
   - Output: reply, conversation_id

2. **POST /api/v1/ai/evaluate**
   - Match spec exactly
   - Input: conversation_id, jlpt_target
   - Output: jlpt_estimation, scores, errors

3. **POST /api/v1/ai/correct-sentence**
   - Match spec exactly
   - Input: sentence
   - Output: original, corrected, explanation_vi

---

### Phase 4: Enhanced Features (Priority: MEDIUM)

1. **Conversation Summary Generation**
   - Auto-generate summary after conversation ends
   - Store in Conversation.summary

2. **Personalized Practice Generator**
   - Generate practice based on errors
   - Return practice exercises

3. **Teacher Content Assistant** (Future)
   - Generate speaking exercises
   - Generate role-play scenarios

---

## 3. Implementation Order

1. ✅ **Data Models** → Create new models
2. ✅ **Database Schema** → Update indexes, create collections
3. ✅ **Analysis Services** → Create keigo, jlpt, particle analyzers
4. ✅ **API Endpoints** → Create new routes matching spec
5. ✅ **Integration** → Update existing code to use new models
6. ✅ **Testing** → Test all new endpoints

---

## 4. Files to Create/Modify

### New Files
- `app/models/conversation_analysis.py`
- `app/models/enums.py` (ConversationMode, JLPTLevel)
- `app/services/analysis/keigo_analyzer.py`
- `app/services/analysis/jlpt_level_estimator.py`
- `app/services/analysis/particle_analyzer.py`
- `app/routes/ai_routes.py` (new AI endpoints)
- `app/controllers/ai_controller.py`
- `app/schemas/ai_schema.py`

### Modified Files
- `app/models/conversation.py` (add fields)
- `app/models/conversation.py` (MessageAnalysis enhancement)
- `app/services/analysis/grammar_analyzer.py` (add error tracking)
- `app/routes/__init__.py` (register new routes)

---

## 5. Database Schema

### Collections

#### conversations
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "conversation_mode": "speaking_practice|role_play|jlpt_exam|free_conversation",
  "language": "ja",
  "jlpt_target": "N5|N4|N3|N2|N1",
  "topic": "string",
  "summary": "string?",
  "messages": [...],
  "overall_score": {...},
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### conversation_analyses
```json
{
  "_id": "ObjectId",
  "conversation_id": "ObjectId",
  "jlpt_estimation": "N5|N4|N3|N2|N1",
  "scores": {
    "grammar": 6.0,
    "vocabulary": 6.5,
    "fluency": 5.5,
    "naturalness": 5.0
  },
  "errors": {
    "grammar": ["〜ます vs 〜ました"],
    "particles": ["は / が"]
  },
  "common_mistakes": ["は/が", "〜ている"],
  "created_at": "datetime"
}
```

### Indexes
```javascript
// conversations collection
db.conversations.createIndex({ "user_id": 1, "created_at": -1 })
db.conversations.createIndex({ "conversation_mode": 1 })
db.conversations.createIndex({ "jlpt_target": 1 })

// conversation_analyses collection
db.conversation_analyses.createIndex({ "conversation_id": 1 })
db.conversation_analyses.createIndex({ "user_id": 1, "created_at": -1 })
```

---

## 6. Next Steps

1. Create enums and enhanced models
2. Create new analysis services
3. Create new API endpoints
4. Update database schema
5. Test integration





