"""
TikTok Ads AI Agent
"""

import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import random
import time

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Groq SDK not installed. Install with: pip install groq")


@dataclass
class AdPayload:
    campaign_name: str
    objective: str
    ad_text: str
    cta: str
    music_id: Optional[str] = None
    music_option: Optional[str] = None

    def to_dict(self):
        return {
            "campaign_name": self.campaign_name,
            "objective": self.objective,
            "creative": {
                "text": self.ad_text,
                "cta": self.cta,
                "music_id": self.music_id
            }
        }


class MockTikTokAPI:
    """Mock TikTok API for realistic demonstration."""

    VALID_MUSIC_IDS = [
        "music_123", "music_456", "music_789",
        "music_pop_2024", "music_trending_001",
        "music_viral_summer", "music_hiphop_beat"
    ]

    VALID_TOKENS = ["mock_token_12345", "act.demo.token.tiktok.ads.2024"]

    @staticmethod
    def validate_token(token: str) -> Dict[str, Any]:
        """Validate access token."""
        if not token:
            return {"valid": False, "error": "No access token provided"}

        if token in MockTikTokAPI.VALID_TOKENS or token.startswith("act."):
            return {
                "valid": True,
                "advertiser_id": "adv_123456",
                "scopes": ["ad.create", "ad.read", "campaign.create"]
            }

        if "expired" in token.lower():
            return {"valid": False, "error": "TOKEN_EXPIRED", "message": "Access token has expired"}

        return {"valid": False, "error": "INVALID_TOKEN", "message": "Invalid access token"}

    @staticmethod
    def validate_music_id(music_id: str) -> Dict[str, Any]:
        """Validate music ID against mock TikTok library."""
        if music_id in MockTikTokAPI.VALID_MUSIC_IDS:
            return {
                "valid": True,
                "music_title": f"Track {music_id.split('_')[-1]}",
                "duration": random.randint(15, 60),
                "message": "Music ID validated successfully"
            }
        elif music_id.startswith("music_"):
            return {
                "valid": False,
                "error_code": "MUSIC_NOT_FOUND",
                "message": "The music ID does not exist in TikTok's library."
            }
        else:
            return {
                "valid": False,
                "error_code": "INVALID_FORMAT",
                "message": "Invalid music ID format. Music IDs should start with 'music_'"
            }

    @staticmethod
    def upload_custom_music(file_info: str) -> Dict[str, Any]:
        """Simulate custom music upload."""
        time.sleep(0.5)
        if random.random() > 0.2:
            mock_music_id = f"music_custom_{random.randint(1000, 9999)}"
            return {
                "success": True,
                "music_id": mock_music_id,
                "message": f"Music uploaded successfully. Generated ID: {mock_music_id}"
            }
        else:
            return {
                "success": False,
                "error_code": "UPLOAD_FAILED",
                "message": "Upload failed. Please ensure file is MP3/WAV and under 10MB."
            }

    @staticmethod
    def submit_ad(payload: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        """Submit ad to TikTok Ads API."""
        token_validation = MockTikTokAPI.validate_token(access_token)
        if not token_validation["valid"]:
            return {
                "success": False,
                "error_type": "AUTH_ERROR",
                "error_code": token_validation.get("error", "INVALID_TOKEN"),
                "message": token_validation.get("message", "Invalid access token"),
                "suggested_action": "Please obtain a valid access token through OAuth.",
                "retry_possible": True
            }

        time.sleep(1)

        # 75% success rate
        if random.random() > 0.25:
            return {
                "success": True,
                "ad_id": f"ad_{random.randint(100000, 999999)}",
                "campaign_id": f"cmp_{random.randint(10000, 99999)}",
                "message": "✅ Ad campaign created successfully!",
                "payload": payload
            }

        error_scenarios = [
            {
                "success": False,
                "error_type": "VALIDATION_ERROR",
                "error_code": "INVALID_MUSIC_ID",
                "message": "The provided music ID is invalid or no longer available.",
                "suggested_action": "Choose a different music track or upload custom music.",
                "retry_possible": True
            },
            {
                "success": False,
                "error_type": "RATE_LIMIT",
                "error_code": "TOO_MANY_REQUESTS",
                "message": "Rate limit exceeded.",
                "suggested_action": "Wait a few minutes before trying again.",
                "retry_possible": True
            }
        ]
        return random.choice(error_scenarios)


# Tool definitions for function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "validate_music_id",
            "description": "Validate a TikTok music ID to check if it exists in the library",
            "parameters": {
                "type": "object",
                "properties": {
                    "music_id": {
                        "type": "string",
                        "description": "The music ID to validate (e.g., 'music_123')"
                    }
                },
                "required": ["music_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upload_custom_music",
            "description": "Upload custom music file and get a music ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_info": {
                        "type": "string",
                        "description": "Information about the music file to upload"
                    }
                },
                "required": ["file_info"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_tiktok_ad",
            "description": "Submit the completed ad campaign to TikTok Ads API. Only call this when ALL required information has been collected and validated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_name": {
                        "type": "string",
                        "description": "Name of the campaign (minimum 3 characters)"
                    },
                    "objective": {
                        "type": "string",
                        "enum": ["Traffic", "Conversions"],
                        "description": "Campaign objective"
                    },
                    "ad_text": {
                        "type": "string",
                        "description": "Ad text (maximum 100 characters)"
                    },
                    "cta": {
                        "type": "string",
                        "description": "Call to action (e.g., 'Shop Now', 'Learn More')"
                    },
                    "music_id": {
                        "type": "string",
                        "description": "Music ID (required for Conversions, optional for Traffic)"
                    },
                    "music_option": {
                        "type": "string",
                        "enum": ["existing", "custom", "none"],
                        "description": "Type of music being used"
                    }
                },
                "required": ["campaign_name", "objective", "ad_text", "cta", "music_option"]
            }
        }
    }
]


class TikTokAdAgent:
    """AI-powered TikTok Ads agent using LLM for intelligent conversation."""

    def __init__(self, groq_api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.groq_api_key = groq_api_key
        self.access_token = access_token or "act.demo.token.tiktok.ads.2024"
        self.conversation_history: List[Dict[str, Any]] = []

        if not GROQ_AVAILABLE:
            raise Exception("Groq SDK is required for AI-powered mode. Install with: pip install groq")

        if not groq_api_key:
            raise Exception("GROQ_API_KEY is required. Set it as environment variable or pass it directly.")

        try:
            self.client = Groq(api_key=groq_api_key)
            print("✅ Groq client initialized successfully")
        except Exception as e:
            raise Exception(f"Failed to initialize Groq: {e}")

        # Validate access token
        token_validation = MockTikTokAPI.validate_token(self.access_token)
        if token_validation["valid"]:
            print(f"✅ Access token validated")
            print(f"   Advertiser ID: {token_validation['advertiser_id']}")
        else:
            print(f"⚠️  Access token validation failed: {token_validation.get('error')}")

        self.system_prompt = """You are an expert TikTok Ads campaign assistant. Your job is to help users create valid ad campaigns through natural conversation.

## Your Personality:
- Friendly, professional, and helpful
- Patient and understanding
- Conversational (not robotic)
- Proactive in guiding users

## Information You Need to Collect:
1. **Campaign Name**: Extract from natural language (e.g., "call it SoluLab" → "SoluLab")
   - Must be at least 3 characters

2. **Objective**: Must be exactly "Traffic" or "Conversions"
   - Understand variations: "I want traffic" → "Traffic", "conversion campaign" → "Conversions"

3. **Ad Text**: Maximum 100 characters
   - Extract the actual ad copy from user's message

4. **CTA (Call to Action)**: Examples: "Shop Now", "Learn More", "Sign Up"
   - Understand variations and suggest if unclear

5. **Music**: Conditional based on objective
   - **For Conversions**: Music is REQUIRED (either existing music_id or custom upload)
   - **For Traffic**: Music is optional
   - Options: existing (provide music_id), custom (upload), or none

## Critical Business Rules:
- Campaign name minimum 3 characters
- Ad text maximum 100 characters
- Music is REQUIRED for "Conversions" objective
- Music is OPTIONAL for "Traffic" objective
- Music IDs must be validated before submission

## Available Tools:
- `validate_music_id`: Check if a music ID exists
- `upload_custom_music`: Upload custom music and get an ID
- `submit_tiktok_ad`: Submit the complete campaign (ONLY when all info is collected and validated)

## Your Approach:
1. Extract information intelligently from natural language
2. Don't ask for information you already have
3. Validate music IDs when provided
4. Enforce business rules before submission
5. Handle errors gracefully and provide clear guidance
6. Use tools when appropriate

## Example Conversations:
User: "I want to create a campaign called SoluLab for conversions"
You: "Great! I'll create a 'SoluLab' campaign with Conversions objective. What ad text would you like to use?"

User: "The ad should say 'Check out our amazing AI solutions!'"
You: "Perfect! What call-to-action would you like? For example: 'Learn More', 'Shop Now', 'Sign Up'"

User: "Learn More sounds good"
You: "Excellent! Since this is a Conversions campaign, music is required. Would you like to use existing TikTok music or upload custom music?"

## Important:
- Be conversational and natural
- Extract information intelligently (don't make users repeat themselves)
- Only call submit_tiktok_ad when you have ALL required information and it's validated
- If music is required and user hasn't provided it, don't submit
- Guide users through errors with clear next steps"""

    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return results."""
        if tool_name == "validate_music_id":
            return MockTikTokAPI.validate_music_id(tool_args["music_id"])

        elif tool_name == "upload_custom_music":
            return MockTikTokAPI.upload_custom_music(tool_args.get("file_info", "user_upload.mp3"))

        elif tool_name == "submit_tiktok_ad":
            payload = {
                "campaign_name": tool_args["campaign_name"],
                "objective": tool_args["objective"],
                "creative": {
                    "text": tool_args["ad_text"],
                    "cta": tool_args["cta"],
                    "music_id": tool_args.get("music_id")
                }
            }
            return MockTikTokAPI.submit_ad(payload, self.access_token)

        return {"error": "Unknown tool"}

    def chat(self, user_input: str) -> str:
        """Main chat interface using AI."""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Prepare messages for API call
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history
        ]

        try:
            # Call Groq with function calling
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=2000
            )

            assistant_message = response.choices[0].message

            # Handle tool calls
            if assistant_message.tool_calls:
                # Add assistant message with tool calls to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    print(f"\n🔧 Calling tool: {tool_name}")
                    print(f"   Arguments: {json.dumps(tool_args, indent=2)}")

                    tool_result = self._execute_tool(tool_name, tool_args)

                    print(f"   Result: {json.dumps(tool_result, indent=2)}")

                    # Add tool result to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })

                # Get final response after tool execution
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    *self.conversation_history
                ]

                final_response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )

                final_content = final_response.choices[0].message.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_content
                })

                return final_content

            else:
                # No tool calls, just return the response
                content = assistant_message.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": content
                })
                return content

        except Exception as e:
            error_msg = f"❌ Error communicating with AI: {str(e)}"
            print(error_msg)
            return error_msg

    def start(self):
        """Start the interactive CLI session."""
        print("=" * 70)
        print("🎵 TikTok Ads AI Agent")
        print("Powered by Groq LLM with Function Calling")
        print("=" * 70)
        print("\nI'll help you create a TikTok ad campaign through natural conversation.")
        print("Type 'quit' to exit, 'reset' to start over.\n")

        # Initial greeting
        print("Agent: Hi! I'm your TikTok Ads assistant. I can help you create a new ad campaign. What would you like to call your campaign?\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for using TikTok Ads AI Agent!")
                    break

                if user_input.lower() == 'reset':
                    self.conversation_history = []
                    print("\n🔄 Conversation reset. Starting fresh!\n")
                    print("Agent: Hi! I'm your TikTok Ads assistant. What would you like to call your campaign?\n")
                    continue

                if not user_input:
                    continue

                response = self.chat(user_input)
                print(f"\nAgent: {response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using TikTok Ads AI Agent!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    # Get API key from environment variable
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        print("\n❌ ERROR: GROQ_API_KEY environment variable not set!")
        print("\nPlease set your Groq API key:")
        print("  export GROQ_API_KEY='your_api_key_here'")
        print("\nOr get a free API key at: https://console.groq.com")
        exit(1)

    access_token = os.getenv("TIKTOK_ACCESS_TOKEN", "act.demo.token.tiktok.ads.2024")

    print("\n🚀 Initializing AI-Powered TikTok Ads Agent...\n")

    try:
        agent = TikTokAdAgent(
            groq_api_key=groq_api_key,
            access_token=access_token
        )
        agent.start()
    except Exception as e:
        print(f"\n❌ Failed to start agent: {e}\n")
