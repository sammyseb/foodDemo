"""Constants for the Restaurant Agent."""

# API
API_V1_PREFIX = "/api/v1"
API_TITLE = "Restaurant Agent API"
API_VERSION = "1.0.0"

# LLM Defaults
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000

# Chat
MAX_MESSAGE_LENGTH = 4000
MAX_SESSION_MESSAGES = 100

# Agent Defaults
DEFAULT_MAX_ITERATIONS = 10
ROUTER_MAX_ITERATIONS = 3

# Intent Mapping
INTENT_MAPPING = {
    "search": "search_agent",
    "recommend": "search_agent",
    "compare": "search_agent",
    "details": "search_agent",
    "reserve": "search_agent",
    "book": "search_agent",
    "chat": "generate_response",
}

# Entity Extraction Patterns
ENTITY_PATTERNS = {
    "location": ["in", "near", "around", "at"],
    "cuisine": ["italian", "mexican", "japanese", "chinese", "indian", "thai"],
    "price": ["$", "$$", "$$$", "$$$$", "cheap", "moderate", "expensive"],
    "rating": ["rating", "stars", "review"],
}
