# TikTok Ads AI Agent

An intelligent conversational AI agent for creating TikTok ad campaigns through natural language interaction. Powered by Groq's LLM with function calling capabilities.

## 🎯 Overview

This agent allows users to create TikTok ad campaigns by simply chatting naturally. Instead of filling out forms, users describe what they want, and the AI extracts the necessary information, validates it, and submits the campaign.

### Key Features

- **Natural Language Processing**: Extract campaign details from conversational input
- **Intelligent Validation**: Validates music IDs and enforces business rules
- **Function Calling**: Uses tools to interact with TikTok Ads API
- **Error Handling**: Gracefully handles API errors with clear guidance
- **Conversational Flow**: Asks follow-up questions only when needed

---

## 🔐 Authentication & OAuth

### Current Implementation (Mock)

This demo uses **mock authentication** for demonstration purposes:

```python
VALID_TOKENS = ["mock_token_12345", "act.demo.token.tiktok.ads.2024"]
```

The agent validates tokens against this list and simulates TikTok's token validation response.

### Production OAuth Flow

In production, you would implement TikTok's OAuth 2.0 flow:

1. **Authorization Request**
   ```
   https://business-api.tiktok.com/open_api/v1.3/oauth2/authorize/
   ?app_id={APP_ID}
   &state={STATE}
   &redirect_uri={REDIRECT_URI}
   &scope=ad.create,ad.read,campaign.create
   ```

2. **Token Exchange**
   ```python
   # After user authorizes, exchange auth code for access token
   response = requests.post(
       "https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/",
       json={
           "app_id": APP_ID,
           "secret": APP_SECRET,
           "auth_code": auth_code
       }
   )
   access_token = response.json()["data"]["access_token"]
   ```

3. **Token Refresh**
   ```python
   # Refresh expired tokens
   response = requests.post(
       "https://business-api.tiktok.com/open_api/v1.3/oauth2/refresh_token/",
       json={
           "app_id": APP_ID,
           "secret": APP_SECRET,
           "refresh_token": refresh_token
       }
   )
   ```

### Token Storage

For production:
- Store tokens securely (encrypted database, secret manager)
- Implement token refresh logic
- Handle token expiration gracefully
- Use environment variables for sensitive credentials

---

## 🧠 Prompt Design Explanation

### System Prompt Architecture

The agent uses a comprehensive system prompt with several key components:

#### 1. **Personality Definition**
```
- Friendly, professional, and helpful
- Patient and understanding
- Conversational (not robotic)
- Proactive in guiding users
```

This ensures consistent, human-like interactions.

#### 2. **Information Extraction Schema**

The prompt explicitly defines what information to collect:

```
1. Campaign Name (min 3 chars)
2. Objective (Traffic/Conversions)
3. Ad Text (max 100 chars)
4. CTA (Call to Action)
5. Music (conditional on objective)
```

#### 3. **Business Rules**

Critical rules are embedded in the prompt:

```
- Music is REQUIRED for "Conversions"
- Music is OPTIONAL for "Traffic"
- Campaign name minimum 3 characters
- Ad text maximum 100 characters
```

This prevents invalid submissions.

#### 4. **Intelligent Extraction**

The prompt instructs the AI to:
- Extract information from natural language
- Avoid asking for information already provided
- Understand variations ("I want traffic" → "Traffic")
- Be contextually aware

#### 5. **Tool Usage Guidelines**

```
- validate_music_id: Check if music exists
- upload_custom_music: Upload custom tracks
- submit_tiktok_ad: Submit ONLY when all info is validated
```

The prompt emphasizes calling `submit_tiktok_ad` only when requirements are met.

#### 6. **Example Conversations**

Includes real conversation examples to guide the AI's behavior:

```
User: "I want to create a campaign called SoluLab for conversions"
AI: "Great! I'll create a 'SoluLab' campaign with Conversions objective. 
     What ad text would you like to use?"
```

This teaches the AI proper conversation flow.

### Why This Design Works

1. **Stateful Conversation**: Maintains context across multiple turns
2. **Prevents Premature Submission**: Won't submit until all requirements met
3. **Handles Ambiguity**: Understands variations in user input
4. **Error Prevention**: Validates before calling expensive API operations
5. **User-Friendly**: Guides users without being annoying

---

## 🔧 API Assumptions & Mocks

### Mock TikTok API (`MockTikTokAPI`)

Since we don't have real TikTok API access, the code implements realistic mocks:

#### 1. **Token Validation**
```python
def validate_token(token: str) -> Dict[str, Any]:
    # Returns mock advertiser_id and scopes
    # Simulates expired tokens, invalid tokens
```

**Real API Equivalent**:
```
GET https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/
```

#### 2. **Music ID Validation**
```python
VALID_MUSIC_IDS = [
    "music_123", "music_456", "music_789",
    "music_pop_2024", "music_trending_001"
]

def validate_music_id(music_id: str) -> Dict[str, Any]:
    # Checks against mock library
    # Returns music details or error
```

**Real API Equivalent**:
```
GET https://business-api.tiktok.com/open_api/v1.3/music/search/
```

#### 3. **Custom Music Upload**
```python
def upload_custom_music(file_info: str) -> Dict[str, Any]:
    # Simulates upload with 80% success rate
    # Returns generated music_id
```

**Real API Equivalent**:
```
POST https://business-api.tiktok.com/open_api/v1.3/file/music/upload/
```

#### 4. **Ad Submission**
```python
def submit_ad(payload: Dict[str, Any], access_token: str) -> Dict[str, Any]:
    # 75% success rate
    # Simulates various error scenarios:
    #   - Invalid music ID
    #   - Rate limiting
    #   - Validation errors
```

**Real API Equivalent**:
```
POST https://business-api.tiktok.com/open_api/v1.3/ad/create/
POST https://business-api.tiktok.com/open_api/v1.3/campaign/create/
```

### API Response Structures

All mocks return realistic response structures:

**Success Response**:
```json
{
  "success": true,
  "ad_id": "ad_123456",
  "campaign_id": "cmp_12345",
  "message": "✅ Ad campaign created successfully!"
}
```

**Error Response**:
```json
{
  "success": false,
  "error_type": "VALIDATION_ERROR",
  "error_code": "INVALID_MUSIC_ID",
  "message": "The provided music ID is invalid",
  "suggested_action": "Choose a different music track",
  "retry_possible": true
}
```

### Assumptions Made

1. **Authentication**: Mock tokens are sufficient for demo
2. **Music Library**: Limited to predefined music IDs
3. **Rate Limiting**: Simulated with random delays
4. **Error Rates**: 75% success rate to demonstrate error handling
5. **Sync Operations**: Real API may have async operations
6. **Simplified Payload**: Real API requires more fields (targeting, budget, etc.)

---

## 🚀 How to Run the Agent

### Prerequisites

1. **Python 3.8+**
2. **Groq API Key** (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# Install required packages
pip install groq
```

### Configuration

#### Option 1: Environment Variable (Recommended)

```bash
export GROQ_API_KEY='your_groq_api_key_here'
export TIKTOK_ACCESS_TOKEN='act.demo.token.tiktok.ads.2024'  # Optional (has default)
```

#### Option 2: Modify Code Directly

⚠️ **Warning: Hardcoding API keys is not recommended for production**

In the code, replace:
```python
groq_api_key = "gsk_YOUR_API_KEY_HERE"
```

### Running the Agent

```bash
python tiktok_ads_agent.py
```

### Usage Example

```
======================================================================
🎵 TikTok Ads AI Agent
Powered by Groq LLM with Function Calling
======================================================================

✅ Groq client initialized successfully
✅ Access token validated
   Advertiser ID: adv_123456

I'll help you create a TikTok ad campaign through natural conversation.
Type 'quit' to exit, 'reset' to start over.

Agent: Hi! I'm your TikTok Ads assistant. I can help you create a new ad 
       campaign. What would you like to call your campaign?

You: I want to create a campaign called SoluLab for conversions

Agent: Great! I'll create a "SoluLab" Conversions campaign. What ad text 
       would you like to use? (Keep it under 100 characters)

You: Check out our amazing AI solutions!

Agent: Perfect! What call-to-action button would you like? 
       For example: "Learn More", "Shop Now", "Sign Up"

You: Learn More

Agent: Excellent! Since this is a Conversions campaign, music is required. 
       Would you like to use an existing TikTok music track (provide music_id) 
       or upload custom music?

You: Use music_123

🔧 Calling tool: validate_music_id
   Arguments: {"music_id": "music_123"}
   Result: {"valid": true, "music_title": "Track 123", "duration": 30}

🔧 Calling tool: submit_tiktok_ad
   Arguments: {
     "campaign_name": "SoluLab",
     "objective": "Conversions",
     "ad_text": "Check out our amazing AI solutions!",
     "cta": "Learn More",
     "music_id": "music_123",
     "music_option": "existing"
   }
   Result: {
     "success": true,
     "ad_id": "ad_789012",
     "campaign_id": "cmp_34567",
     "message": "✅ Ad campaign created successfully!"
   }

Agent: 🎉 Success! Your "SoluLab" campaign has been created!
       
       Campaign ID: cmp_34567
       Ad ID: ad_789012
       
       Your ad is now ready to launch. Would you like to create another campaign?
```

### Commands

- `quit` / `exit` / `q` - Exit the agent
- `reset` - Start a new conversation
- `Ctrl+C` - Gracefully exit

---

## 📝 Code Structure

```
tiktok_ads_agent.py
│
├── MockTikTokAPI          # Simulates TikTok Ads API
│   ├── validate_token()
│   ├── validate_music_id()
│   ├── upload_custom_music()
│   └── submit_ad()
│
├── TikTokAdAgent          # Main AI agent class
│   ├── __init__()         # Initialize Groq client
│   ├── chat()             # Handle conversation turn
│   ├── _execute_tool()    # Execute function calls
│   └── start()            # CLI interface
│
└── TOOLS                  # Function calling definitions
    ├── validate_music_id
    ├── upload_custom_music
    └── submit_tiktok_ad
```

---

## 🎨 Conversation Examples

### Example 1: Complete Flow
```
You: Create a campaign called "Summer Sale" for traffic
Agent: Great! What ad text would you like?
You: Shop our summer collection now!
Agent: What CTA would you like?
You: Shop Now
Agent: Would you like to add music? (optional for Traffic campaigns)
You: No music needed
[Submits campaign]
```

### Example 2: With Music
```
You: I need a conversions campaign called "Product Launch"
Agent: What ad copy do you want?
You: Discover our revolutionary new product
Agent: What CTA?
You: Learn More
Agent: Music is required for Conversions. Music ID or custom upload?
You: music_trending_001
[Validates music, then submits]
```

### Example 3: Error Handling
```
You: Campaign called "X"
Agent: Campaign name must be at least 3 characters. Can you provide a longer name?
You: Campaign called "XYZ Product"
[Continues normally]
```

---

## 🛠️ Extending for Production

### 1. Implement Real OAuth

```python
class TikTokOAuthHandler:
    def get_authorization_url(self):
        # Generate OAuth URL
        
    def exchange_code_for_token(self, code):
        # Exchange auth code for access token
        
    def refresh_token(self, refresh_token):
        # Refresh expired token
```

### 2. Replace Mocks with Real API Calls

```python
import requests

class TikTokAPI:
    BASE_URL = "https://business-api.tiktok.com/open_api/v1.3"
    
    def submit_ad(self, payload, access_token):
        response = requests.post(
            f"{self.BASE_URL}/ad/create/",
            headers={"Access-Token": access_token},
            json=payload
        )
        return response.json()
```

### 3. Add Database for State Management

```python
# Store conversation state, tokens, campaign drafts
from sqlalchemy import create_engine, Column, String, JSON
```

### 4. Add More Campaign Options

- Targeting (age, gender, location, interests)
- Budget and bidding
- Schedule and duration
- Creative assets (video upload)
- A/B testing variants

### 5. Implement Logging & Monitoring

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Campaign created: {campaign_id}")
```

---

## 🐛 Troubleshooting

### Error: "Groq SDK not installed"
```bash
pip install groq
```

### Error: "GROQ_API_KEY not set"
```bash
export GROQ_API_KEY='your_key_here'
```

### Error: "Rate limit exceeded"
Wait a few minutes - the mock API simulates rate limiting.

### AI not calling tools correctly
Check that your Groq API key is valid and has credits.

---

## 📄 License

MIT License - feel free to use and modify for your needs.

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Add more conversation examples
- Improve error handling
- Add unit tests
- Implement real TikTok API integration
- Add web interface (Streamlit/Gradio)
- Support more ad formats

---

## 📧 Support

For issues or questions, please open a GitHub issue or contact the maintainer.

---

**Built with ❤️ using Groq LLM and Python**
