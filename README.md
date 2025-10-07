# AI Interview Caller

An intelligent automated interview screening system that leverages AI to call candidates, conduct phone interviews, and evaluate their responses. This FastAPI-based application integrates with Twilio for telephony services and Google's Gemini AI for question generation and candidate assessment.

## 🚀 Features

- **Automated Question Generation**: AI-powered interview questions based on job descriptions
- **Resume Parsing**: Extract candidate information from PDF/DOCX resumes
- **Telephony Integration**: Automated phone calls via Twilio
- **Real-time Interview Conduct**: Interactive voice interviews with transcription
- **AI-Powered Scoring**: Automated candidate evaluation and recommendations
- **RESTful API**: Complete API for managing job descriptions, candidates, and interviews
- **Database Management**: PostgreSQL integration with SQLAlchemy ORM

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   FastAPI API    │───▶│   PostgreSQL    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   External APIs  │
                       │                  │
                       │ • Twilio (Calls) │
                       │ • Gemini AI (LLM)│
                       └──────────────────┘
```

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL database
- Twilio account with phone number
- Google Cloud account with Gemini API access
- Newman (for API testing)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai_interview_caller
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
# Or if using UV:
uv sync
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# Application Settings
API_KEY=your_secure_api_key_here
ENV_SETTING=development
BASE_URL=http://localhost:8000

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ai_interview_db

# AI/LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-1.5-flash

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=+1234567890
TWILIO_RECOVERY_CODE=your_recovery_code
```

#### Environment Variables Explanation

| Variable | Description | Example |
|----------|-------------|---------||
| `API_KEY` | Secure API key for authentication | `N4pe/zSQxDdJ/1o3lMUyw8hxfanmUWrylLJXXdo5ytc=` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/dbname` |
| `GEMINI_API_KEY` | Google Gemini AI API key | `AIzaSyC...` |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | `AC...` |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | `...` |
| `TWILIO_FROM_NUMBER` | Twilio phone number (E.164 format) | `+1234567890` |
| `BASE_URL` | Application base URL for webhooks | `https://yourdomain.com` |

### 5. Database Setup

Ensure PostgreSQL is running and create the database:

```bash
# Create database (if not exists)
createdb ai_interview_db

# The application will automatically create tables on startup
```

### 6. Start the Application

#### Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Job Description Management

#### Generate Interview Questions
```http
POST /jd/generate-questions
```

**Headers:**
```
X-API-KEY: your_api_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Software Engineer",
  "content": "Join us as a Software Engineer..."
}
```

**Response:**
```json
{
  "jd_id": "uuid-here",
  "questions": [
    "What is your experience with Python?",
    "Describe a challenging project you worked on...",
    "..."
  ]
}
```

### Candidate Management

#### Create Candidate
```http
POST /candidate/create
```

**Headers:**
```
X-API-KEY: your_api_key
```

**Form Data:**
- `name`: Candidate's full name
- `e164_phone`: Phone number in E.164 format (+1234567890)
- `jd_id`: UUID of the job description
- `file`: Resume file (PDF or DOCX)

**Response:**
```json
{
  "id": "candidate-uuid",
  "name": "John Doe",
  "e164_phone": "+1234567890",
  "resume_summary": {
    "name": "John Doe",
    "email": "john@example.com",
    "years_experience": 5,
    "top_skills": ["Python", "JavaScript"],
    "education_summary": "BS Computer Science"
  },
  "jd_id": "jd-uuid"
}
```

### Interview Management

#### Trigger Interview Call
```http
POST /interview/trigger/{candidate_id}
```
**Note**: Twilio only calls whitelist numbers which are verified by OTP on a trial account please contact before running and reviewing.

**Headers:**
```
X-API-KEY: your_api_key
```

**Response:**
```json
{
  "call_sid": "twilio-call-sid",
  "status": "Call initiated"
}
```

### Webhook Endpoints (Twilio Integration)

- `POST /twilio/interview/start/{candidate_id}` - Start interview
- `POST /twilio/interview/question/{candidate_id}/{question_index}` - Handle questions
- `POST /twilio/interview/record_data/{candidate_id}/{question_index}` - Record responses
- `POST /twilio/interview/finish/{candidate_id}` - Complete interview and scoring

## 🧪 Testing with Newman

Newman is a command-line runner for Postman collections. Use it to test the deployed API.

### Prerequisites

Install Newman globally:

```bash
npm install -g newman
```

### Available Test Files

The `postman/` directory contains:
- `My_Collection.postman_collection.json` - Complete API test collection
- `env.postman_environment.json` - Environment variables for testing
- `data.json` - Test data for data-driven testing

### Running Tests

#### Basic Collection Run
```bash
newman run postman/My_Collection.postman_collection.json \
  -e postman/env.postman_environment.json
```

#### With Data File
```bash
newman run postman/My_Collection.postman_collection.json \
  -e postman/env.postman_environment.json \
  -d postman/data.json
```

#### With Detailed Reporting
```bash
newman run postman/My_Collection.postman_collection.json \
  -e postman/env.postman_environment.json \
  -d postman/data.json \
  --reporters cli,html \
  --reporter-html-export newman-report.html
```

#### Against Deployed Server
Update the environment file or use environment variables:

```bash
newman run postman/My_Collection.postman_collection.json \
  -e postman/env.postman_environment.json \
  --env-var "baseURL=https://ai-interview-caller-1.onrender.com" \
  --env-var "api_key=your_production_api_key"
```

### Test Scenarios Covered

1. **Generate Questions** - Create job description and generate AI questions
2. **Create Candidate** - Upload resume and parse candidate data
3. **Trigger Interview** - Initiate automated phone interview
4. **End-to-End Flow** - Complete workflow from JD to interview completion

### Custom Newman Commands

#### Test Specific Environment
```bash
# Test local development
newman run postman/My_Collection.postman_collection.json \
  -e postman/env.postman_environment.json \
  --env-var "baseURL=http://localhost:8000"

# Test production
newman run postman/My_Collection.postman_collection.json \
  -e postman/env.postman_environment.json \
  --env-var "baseURL=https://your-production-url.com"
```

#### Performance Testing
```bash
newman run postman/My_Collection.postman_collection.json \
  -e postman/env.postman_environment.json \
  --iteration-count 10 \
  --delay-request 1000
```

## 🔧 Configuration

### Twilio Webhook Configuration

Configure your Twilio phone number to use your application's webhook endpoints:

1. Log in to Twilio Console
2. Go to Phone Numbers → Manage → Active numbers
3. Select your number
4. Set webhook URL: `https://yourdomain.com/twilio/interview/start/{candidate_id}`
5. Set HTTP method to `POST`

### Database Schema

The application uses the following main tables:

- `job_descriptions` - Stores job descriptions and generated questions
- `candidates` - Candidate information and parsed resume data
- `results` - Interview results, scores, and recommendations

## 🚀 Deployment

### Using Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Deploy to Render

1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Deploy with build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Environment-specific Configurations

#### Development
```bash
ENV_SETTING=development
BASE_URL=http://localhost:8000
```

#### Production
```bash
ENV_SETTING=production
BASE_URL=https://your-domain.com
```

## 🔍 Monitoring & Logging

The application includes built-in logging for:
- AI service interactions
- Twilio webhook events
- Database operations
- Error tracking

Monitor logs for:
- Failed calls (`FATAL SCORING ERROR`)
- API key validation issues
- Database connection problems
- External service failures

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check PostgreSQL is running
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux

# Verify connection
psql -h hostname -U username -d dbname
```

#### 2. Twilio Webhook Issues
- Ensure `BASE_URL` in `.env` matches your deployed URL
- Check Twilio webhook configuration
- Verify phone number format (E.164)

#### 3. AI Service Failures
- Validate `GEMINI_API_KEY`
- Check API quotas and limits
- Ensure model name is correct (`gemini-1.5-flash`)

#### 4. Resume Parsing Issues
- Supported formats: PDF, DOCX only
- Check file size limits
- Verify file is not corrupted

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check Endpoint

```bash
curl http://localhost:8000/
# Expected response: {"message": "AI Interview Screener Backend is running."}
```

## 👥 Support

For support and questions:
- Create an issue on GitHub
- Email: aaryan7068@gmail.com