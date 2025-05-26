from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime, date
import secrets
import re
import json
import aiohttp
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Basic authentication
security = HTTPBasic()

# Simple auth function
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "admin")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Custom JSON encoder for dates
def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Admin Configuration Models
class OllamaConfig(BaseModel):
    enabled: bool = False
    host: str = "http://localhost:11434"
    model: str = "llama2"
    timeout: int = 60
    temperature: float = 0.7

class NPCExtractionPrompt(BaseModel):
    prompt_text: str = """
You are an expert D&D game master assistant. Analyze the following game session text and extract ALL Non-Player Characters (NPCs) mentioned.

For each NPC found, provide a JSON object with these fields:
- name: The NPC's full name
- description: Physical description if mentioned
- race: Race/species if mentioned
- class_role: Class, profession, or role if mentioned
- location: Where they were encountered
- personality_traits: Personality, quirks, or mannerisms observed
- interactions: What happened with this NPC in this session
- relationships: Relationships to other NPCs or party members mentioned
- loot_given: Any items, rewards, or loot provided by this NPC
- status: alive/deceased/unknown
- significance: How important this NPC seems to the story
- additional_notes: Any other relevant information

Return ONLY a JSON array of NPC objects. If no NPCs are found, return an empty array [].

Session Text:
{session_text}
"""

class AdminConfig(BaseModel):
    ollama_config: OllamaConfig = Field(default_factory=OllamaConfig)
    npc_extraction_prompt: NPCExtractionPrompt = Field(default_factory=NPCExtractionPrompt)

# Enhanced Pydantic Models for Structured Sessions
class CombatEncounter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    enemies: str = ""
    outcome: str = ""
    notable_events: str = ""

class RoleplayEncounter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    npcs_involved: List[str] = Field(default_factory=list)
    outcome: str = ""
    importance: str = ""

class LootItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item_name: str = ""
    description: str = ""
    value: str = ""
    recipient: str = ""

class OverarchingMission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mission_name: str = ""
    status: str = "In Progress"  # In Progress, Completed, Failed, On Hold
    description: str = ""
    notes: str = ""

class NPCMention(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    npc_name: str = ""
    role: str = ""
    notes: str = ""
    first_encounter: bool = False

class SessionStructuredData(BaseModel):
    session_number: Optional[int] = None
    session_date: Optional[Union[str, date]] = None  # Accept both string and date
    players_present: List[str] = Field(default_factory=list)
    session_goal: str = ""
    combat_encounters: List[CombatEncounter] = Field(default_factory=list)
    roleplay_encounters: List[RoleplayEncounter] = Field(default_factory=list)
    npcs_encountered: List[NPCMention] = Field(default_factory=list)
    loot: List[LootItem] = Field(default_factory=list)
    notes: str = ""
    notable_roleplay_moments: List[str] = Field(default_factory=list)
    next_session_goals: str = ""
    overarching_missions: List[OverarchingMission] = Field(default_factory=list)

class SessionCreate(BaseModel):
    title: str
    content: str = ""  # Free-form content for backward compatibility
    structured_data: Optional[SessionStructuredData] = None
    session_type: str = "free_form"  # "free_form" or "structured"

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    structured_data: Optional[SessionStructuredData] = None
    session_type: Optional[str] = None

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str = ""
    structured_data: Optional[SessionStructuredData] = None
    session_type: str = "free_form"
    npcs_mentioned: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Enhanced NPC Models
class NPCCreate(BaseModel):
    name: str
    status: str = "Unknown"
    race: str = ""
    class_role: str = ""
    appearance: str = ""
    quirks_mannerisms: str = ""
    background: str = ""
    notes: str = ""
    location: str = ""
    personality_traits: str = ""
    relationships: str = ""
    significance: str = ""

class NPCUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    race: Optional[str] = None
    class_role: Optional[str] = None
    appearance: Optional[str] = None
    quirks_mannerisms: Optional[str] = None
    background: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    personality_traits: Optional[str] = None
    relationships: Optional[str] = None
    significance: Optional[str] = None

class NPC(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: str = "Unknown"
    race: str = ""
    class_role: str = ""
    appearance: str = ""
    quirks_mannerisms: str = ""
    background: str = ""
    notes: str = ""
    location: str = ""
    personality_traits: str = ""
    relationships: str = ""
    significance: str = ""
    history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NPCExtraction(BaseModel):
    session_id: str
    extracted_text: str
    npc_name: str

# Enhanced NPC Extraction Models
class NPCExtractionRequest(BaseModel):
    session_text: str
    session_id: str
    use_ollama: bool = False

class ExtractedNPCData(BaseModel):
    name: str
    description: str = ""
    race: str = ""
    class_role: str = ""
    location: str = ""
    personality_traits: str = ""
    interactions: str = ""
    relationships: str = ""
    loot_given: str = ""
    status: str = "alive"
    significance: str = ""
    additional_notes: str = ""

# Player Management Models
class PlayerCreate(BaseModel):
    name: str
    character_name: str = ""
    character_class: str = ""
    character_level: int = 1
    notes: str = ""
    active: bool = True

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    character_name: Optional[str] = None
    character_class: Optional[str] = None
    character_level: Optional[int] = None
    notes: Optional[str] = None
    active: Optional[bool] = None

class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    character_name: str = ""
    character_class: str = ""
    character_level: int = 1
    notes: str = ""
    active: bool = True
    total_sessions: int = 0
    sessions_attended: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Loot Management Models
class LootItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item_name: str
    description: str = ""
    type: str = ""  # Weapon, Armor, Consumable, Misc, etc.
    rarity: str = "Common"  # Common, Uncommon, Rare, Very Rare, Legendary
    value: str = ""
    magical_properties: str = ""
    session_found: str = ""
    location_found: str = ""
    current_owner: str = ""  # Player ID or "Party" or "NPC"
    ownership_history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LootCreate(BaseModel):
    item_name: str
    description: str = ""
    type: str = ""
    rarity: str = "Common"
    value: str = ""
    magical_properties: str = ""
    session_found: str = ""
    location_found: str = ""
    current_owner: str = ""

class LootUpdate(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    rarity: Optional[str] = None
    value: Optional[str] = None
    magical_properties: Optional[str] = None
    current_owner: Optional[str] = None

class ExtractedLootData(BaseModel):
    item_name: str
    description: str = ""
    type: str = ""
    rarity: str = "Common"
    value: str = ""
    magical_properties: str = ""
    location_found: str = ""
    recipient: str = ""  # Who got the item
    circumstances: str = ""  # How it was obtained

# Enhanced Session Models with Attendance and Loot
class SessionAttendance(BaseModel):
    player_id: str
    player_name: str
    character_name: str = ""
    present: bool = True
    notes: str = ""

class SessionStructuredData(BaseModel):
    session_number: Optional[int] = None
    session_date: Optional[Union[str, date]] = None
    session_duration: str = ""  # e.g., "3 hours"
    dm_name: str = ""
    
    # Player attendance
    players_invited: List[str] = Field(default_factory=list)  # Player IDs
    attendance: List[SessionAttendance] = Field(default_factory=list)
    
    # Session content
    session_goal: str = ""
    session_summary: str = ""
    
    # Encounters
    combat_encounters: List[CombatEncounter] = Field(default_factory=list)
    roleplay_encounters: List[RoleplayEncounter] = Field(default_factory=list)
    
    # NPCs and Loot (extracted automatically)
    npcs_encountered: List[NPCMention] = Field(default_factory=list)
    loot_found: List[str] = Field(default_factory=list)  # Loot item IDs
    
    # Notes and planning
    notes: str = ""
    notable_roleplay_moments: List[str] = Field(default_factory=list)
    next_session_goals: str = ""
    overarching_missions: List[OverarchingMission] = Field(default_factory=list)
    
    # Session outcomes
    experience_awarded: str = ""
    gold_awarded: str = ""
    story_progress: str = ""

# Loot Extraction Request
class LootExtractionRequest(BaseModel):
    session_text: str
    session_id: str
    players: List[Dict[str, str]] = Field(default_factory=list)  # [{"id": "...", "name": "..."}]
    use_ollama: bool = False

# Enhanced Prompt Templates
class LootExtractionPrompt(BaseModel):
    prompt_text: str = """
You are an expert D&D game master assistant. Analyze the following game session text and extract ALL loot, treasure, and items found or acquired.

For each item found, provide a JSON object with these fields:
- item_name: The item's name (be specific)
- description: Physical description and any details mentioned
- type: Category (Weapon, Armor, Consumable, Jewelry, Coin, Misc, etc.)
- rarity: Rarity level if mentioned (Common, Uncommon, Rare, Very Rare, Legendary)
- value: Monetary value if mentioned (gold pieces, coins, etc.)
- magical_properties: Any magical effects or properties described
- location_found: Where the item was discovered
- recipient: Which player character received the item (use exact names from session)
- circumstances: How the item was obtained (found, rewarded, purchased, looted, etc.)

Players in this session: {player_list}

Return ONLY a JSON array of loot objects. If no loot is found, return an empty array [].

Session Text:
{session_text}
"""

class NPCExtractionPrompt(BaseModel):
    prompt_text: str = """
You are an expert D&D game master assistant. Analyze the following game session text and extract ALL Non-Player Characters (NPCs) mentioned.

For each NPC found, provide a JSON object with these fields:
- name: The NPC's full name
- description: Physical description if mentioned
- race: Race/species if mentioned
- class_role: Class, profession, or role if mentioned
- location: Where they were encountered
- personality_traits: Personality, quirks, or mannerisms observed
- interactions: What happened with this NPC in this session
- relationships: Relationships to other NPCs or party members mentioned
- loot_given: Any items, rewards, or loot provided by this NPC
- status: alive/deceased/unknown
- significance: How important this NPC seems to the story
- additional_notes: Any other relevant information

Return ONLY a JSON array of NPC objects. If no NPCs are found, return an empty array [].

Session Text:
{session_text}
"""

class AdminConfig(BaseModel):
    ollama_config: OllamaConfig = Field(default_factory=OllamaConfig)
    npc_extraction_prompt: NPCExtractionPrompt = Field(default_factory=NPCExtractionPrompt)
    loot_extraction_prompt: LootExtractionPrompt = Field(default_factory=LootExtractionPrompt)

# Enhanced Ollama LLM Service
class OllamaLLMService:
    """
    Enhanced Ollama LLM integration for advanced NPC extraction and management.
    """
    
    def __init__(self):
        self.enabled = os.environ.get('OLLAMA_ENABLED', 'false').lower() == 'true'
        self.host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        self.model = os.environ.get('OLLAMA_MODEL', 'llama2')
        self.timeout = int(os.environ.get('OLLAMA_TIMEOUT', 60))
        self.temperature = float(os.environ.get('OLLAMA_TEMPERATURE', 0.7))
        
    async def get_config(self) -> OllamaConfig:
        """Get current Ollama configuration"""
        return OllamaConfig(
            enabled=self.enabled,
            host=self.host,
            model=self.model,
            timeout=self.timeout,
            temperature=self.temperature
        )
    
    async def update_config(self, config: OllamaConfig):
        """Update Ollama configuration"""
        self.enabled = config.enabled
        self.host = config.host
        self.model = config.model
        self.timeout = config.timeout
        self.temperature = config.temperature
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Ollama service"""
        if not self.enabled:
            return {"status": "disabled", "message": "Ollama is disabled"}
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{self.host}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model['name'] for model in data.get('models', [])]
                        return {
                            "status": "connected",
                            "message": "Successfully connected to Ollama",
                            "available_models": models
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"Ollama responded with status {response.status}"
                        }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to connect to Ollama: {str(e)}"
            }
    
    async def extract_npcs_advanced(self, session_text: str, custom_prompt: str = None) -> List[ExtractedNPCData]:
        """
        Advanced NPC extraction using Ollama LLM with custom prompts
        """
        if not self.enabled:
            # Fallback to rule-based extraction
            return await self.extract_npcs_fallback(session_text)
        
        try:
            # Get admin config for prompt
            admin_config = await self.get_admin_config()
            prompt_template = custom_prompt or admin_config.npc_extraction_prompt.prompt_text
            
            # Format prompt with session text
            formatted_prompt = prompt_template.format(session_text=session_text)
            
            # Call Ollama API
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                payload = {
                    "model": self.model,
                    "prompt": formatted_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature
                    }
                }
                
                async with session.post(f"{self.host}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get('response', '')
                        
                        # Parse JSON response
                        try:
                            npcs_data = json.loads(response_text)
                            if isinstance(npcs_data, list):
                                return [ExtractedNPCData(**npc) for npc in npcs_data if isinstance(npc, dict)]
                            else:
                                logger.warning(f"Unexpected response format from Ollama: {response_text}")
                                return []
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON from Ollama response: {response_text}")
                            return []
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            # Fallback to rule-based extraction
            return await self.extract_npcs_fallback(session_text)
    
    async def extract_npcs_fallback(self, session_text: str) -> List[ExtractedNPCData]:
        """
        Fallback rule-based NPC extraction when Ollama is unavailable
        """
        patterns = [
            r'\b([A-Z][a-z]+ (?:the )?[A-Z][a-z]+)\b',  # "Thorin the Blacksmith"
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',           # "John Smith"
            r'NPC:\s*([A-Za-z\s]+)',                     # "NPC: Character Name"
        ]
        
        extracted_names = []
        for pattern in patterns:
            matches = re.findall(pattern, session_text)
            extracted_names.extend(matches)
        
        # Remove duplicates and common words
        common_words = {'The Game', 'The Party', 'The Group', 'Game Master', 'Dungeon Master'}
        unique_names = [name.strip() for name in set(extracted_names) if name.strip() not in common_words]
        
        # Convert to ExtractedNPCData format
        return [
            ExtractedNPCData(
                name=name,
                interactions=f"Mentioned in session text",
                additional_notes="Extracted using rule-based detection"
            ) for name in unique_names
        ]
    
    async def get_admin_config(self) -> AdminConfig:
        """Get admin configuration from database"""
        config_doc = await db.admin_config.find_one({"config_type": "admin"})
        if config_doc:
            return AdminConfig(**config_doc.get('config_data', {}))
        else:
            # Return default config
            return AdminConfig()
    
    async def extract_loot_advanced(self, session_text: str, players: List[Dict[str, str]], custom_prompt: str = None) -> List[ExtractedLootData]:
        """
        Advanced loot extraction using Ollama LLM with custom prompts
        """
        if not self.enabled:
            # Fallback to rule-based extraction
            return await self.extract_loot_fallback(session_text, players)
        
        try:
            # Get admin config for prompt
            admin_config = await self.get_admin_config()
            prompt_template = custom_prompt or admin_config.loot_extraction_prompt.prompt_text
            
            # Format player list for prompt
            player_names = [f"{p.get('name', '')} ({p.get('character_name', '')})" for p in players if p.get('name')]
            player_list = ", ".join(player_names) if player_names else "No specific players mentioned"
            
            # Format prompt with session text and players
            formatted_prompt = prompt_template.format(
                session_text=session_text,
                player_list=player_list
            )
            
            # Call Ollama API
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                payload = {
                    "model": self.model,
                    "prompt": formatted_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature
                    }
                }
                
                async with session.post(f"{self.host}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get('response', '')
                        
                        # Parse JSON response
                        try:
                            loot_data = json.loads(response_text)
                            if isinstance(loot_data, list):
                                return [ExtractedLootData(**item) for item in loot_data if isinstance(item, dict)]
                            else:
                                logger.warning(f"Unexpected loot response format from Ollama: {response_text}")
                                return []
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON from Ollama loot response: {response_text}")
                            return []
                    else:
                        logger.error(f"Ollama API error in loot extraction: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error calling Ollama API for loot extraction: {str(e)}")
            # Fallback to rule-based extraction
            return await self.extract_loot_fallback(session_text, players)
    
    async def extract_loot_fallback(self, session_text: str, players: List[Dict[str, str]]) -> List[ExtractedLootData]:
        """
        Fallback rule-based loot extraction when Ollama is unavailable
        """
        loot_patterns = [
            r'found\s+(?:a\s+)?([^.!?\n]+?)(?:\s+worth\s+([^.!?\n]+))?',
            r'gained\s+(?:a\s+)?([^.!?\n]+)',
            r'received\s+(?:a\s+)?([^.!?\n]+)',
            r'looted\s+(?:a\s+)?([^.!?\n]+)',
            r'treasure.*?([^.!?\n]+)',
            r'(\d+\s+gold\s+pieces?)',
            r'(\d+\s+gp)',
        ]
        
        extracted_loot = []
        for pattern in loot_patterns:
            matches = re.finditer(pattern, session_text, re.IGNORECASE)
            for match in matches:
                item_name = match.group(1).strip()
                if len(item_name) > 3 and len(item_name) < 100:  # Basic validation
                    extracted_loot.append(
                        ExtractedLootData(
                            item_name=item_name,
                            description="Found in session",
                            circumstances="Extracted using rule-based detection"
                        )
                    )
        
        return extracted_loot[:10]  # Limit to 10 items to avoid spam
    
    async def extract_npcs_from_text(self, text: str) -> List[str]:
        """
        Legacy method for backward compatibility
        """
        extracted_npcs = await self.extract_npcs_advanced(text)
        return [npc.name for npc in extracted_npcs]
    
    async def summarize_interaction(self, interaction_text: str) -> str:
        """
        Placeholder for interaction summarization using LLM.
        """
        if self.enabled:
            # TODO: Implement actual Ollama summarization
            pass
        
        # Simple summarization for now
        if len(interaction_text) > 100:
            return interaction_text[:97] + "..."
        return interaction_text

# Initialize LLM service
llm_service = OllamaLLMService()

# Helper function to convert session data for MongoDB storage
def prepare_session_for_storage(session_data: dict) -> dict:
    """Convert session data to MongoDB-compatible format"""
    if session_data.get('structured_data') and session_data['structured_data'].get('session_date'):
        session_date = session_data['structured_data']['session_date']
        if isinstance(session_date, str) and session_date:
            try:
                # Convert string date to ISO format for consistent storage
                parsed_date = datetime.fromisoformat(session_date.replace('Z', '+00:00')).date()
                session_data['structured_data']['session_date'] = parsed_date.isoformat()
            except:
                # If parsing fails, keep as string
                pass
    return session_data

# NPC merging utility
async def merge_npc_data(existing_npc: NPC, extracted_data: ExtractedNPCData, session_id: str) -> NPC:
    """
    Intelligently merge extracted NPC data with existing NPC data
    """
    # Update fields only if new data is more detailed
    updates = {}
    
    if extracted_data.description and len(extracted_data.description) > len(existing_npc.appearance):
        updates['appearance'] = extracted_data.description
    
    if extracted_data.race and not existing_npc.race:
        updates['race'] = extracted_data.race
    
    if extracted_data.class_role and not existing_npc.class_role:
        updates['class_role'] = extracted_data.class_role
    
    if extracted_data.location and not existing_npc.location:
        updates['location'] = extracted_data.location
    
    if extracted_data.personality_traits:
        if existing_npc.personality_traits:
            updates['personality_traits'] = f"{existing_npc.personality_traits}\n{extracted_data.personality_traits}"
        else:
            updates['personality_traits'] = extracted_data.personality_traits
    
    if extracted_data.relationships:
        if existing_npc.relationships:
            updates['relationships'] = f"{existing_npc.relationships}\n{extracted_data.relationships}"
        else:
            updates['relationships'] = extracted_data.relationships
    
    if extracted_data.status != "alive" and existing_npc.status == "Unknown":
        updates['status'] = extracted_data.status
    
    if extracted_data.significance and not existing_npc.significance:
        updates['significance'] = extracted_data.significance
    
    # Add new interaction to history
    new_interaction = {
        "session_id": session_id,
        "interaction": extracted_data.interactions,
        "location": extracted_data.location,
        "loot_given": extracted_data.loot_given,
        "timestamp": datetime.utcnow(),
        "extraction_method": "ollama_advanced" if llm_service.enabled else "rule_based"
    }
    
    # Update notes with additional information
    if extracted_data.additional_notes:
        if existing_npc.notes:
            updates['notes'] = f"{existing_npc.notes}\n{extracted_data.additional_notes}"
        else:
            updates['notes'] = extracted_data.additional_notes
    
    # Apply updates
    for field, value in updates.items():
        setattr(existing_npc, field, value)
    
    existing_npc.history.append(new_interaction)
    existing_npc.updated_at = datetime.utcnow()
    
    return existing_npc

# API Routes
@api_router.get("/")
async def root():
    return {"message": "D&D Note-Taking Tool API"}

@api_router.get("/auth/check")
async def check_auth(username: str = Depends(authenticate)):
    return {"authenticated": True, "username": username}

# Admin Configuration Routes
@api_router.get("/admin/config", response_model=AdminConfig)
async def get_admin_config(username: str = Depends(authenticate)):
    """Get admin configuration"""
    return await llm_service.get_admin_config()

@api_router.post("/admin/config")
async def update_admin_config(config: AdminConfig, username: str = Depends(authenticate)):
    """Update admin configuration"""
    try:
        # Update Ollama config in service
        await llm_service.update_config(config.ollama_config)
        
        # Save to database
        config_doc = {
            "config_type": "admin",
            "config_data": config.dict(),
            "updated_at": datetime.utcnow(),
            "updated_by": username
        }
        
        await db.admin_config.update_one(
            {"config_type": "admin"},
            {"$set": config_doc},
            upsert=True
        )
        
        return {"message": "Admin configuration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating admin config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {str(e)}")

@api_router.get("/admin/ollama/test")
async def test_ollama_connection(username: str = Depends(authenticate)):
    """Test Ollama connection"""
    return await llm_service.test_connection()

@api_router.get("/admin/ollama/config", response_model=OllamaConfig)
async def get_ollama_config(username: str = Depends(authenticate)):
    """Get current Ollama configuration"""
    return await llm_service.get_config()

# Enhanced NPC Extraction Routes
@api_router.post("/extract-npcs-advanced")
async def extract_npcs_advanced(request: NPCExtractionRequest, username: str = Depends(authenticate)):
    """Advanced NPC extraction using Ollama LLM or fallback methods"""
    try:
        # Extract NPCs using advanced method
        extracted_npcs = await llm_service.extract_npcs_advanced(request.session_text)
        
        results = []
        
        for extracted_npc in extracted_npcs:
            # Check if NPC already exists
            existing_npc = await db.npcs.find_one({"name": extracted_npc.name})
            
            if existing_npc:
                # Merge with existing NPC
                existing_npc_obj = NPC(**existing_npc)
                merged_npc = await merge_npc_data(existing_npc_obj, extracted_npc, request.session_id)
                
                # Update in database
                await db.npcs.update_one(
                    {"id": merged_npc.id},
                    {"$set": merged_npc.dict()}
                )
                
                results.append({
                    "action": "updated",
                    "npc": merged_npc,
                    "extraction_method": "ollama_advanced" if llm_service.enabled else "rule_based"
                })
            else:
                # Create new NPC
                new_npc = NPC(
                    name=extracted_npc.name,
                    race=extracted_npc.race,
                    class_role=extracted_npc.class_role,
                    appearance=extracted_npc.description,
                    personality_traits=extracted_npc.personality_traits,
                    location=extracted_npc.location,
                    relationships=extracted_npc.relationships,
                    significance=extracted_npc.significance,
                    status=extracted_npc.status,
                    notes=extracted_npc.additional_notes,
                    history=[{
                        "session_id": request.session_id,
                        "interaction": extracted_npc.interactions,
                        "location": extracted_npc.location,
                        "loot_given": extracted_npc.loot_given,
                        "timestamp": datetime.utcnow(),
                        "extraction_method": "ollama_advanced" if llm_service.enabled else "rule_based"
                    }]
                )
                
                await db.npcs.insert_one(new_npc.dict())
                
                results.append({
                    "action": "created",
                    "npc": new_npc,
                    "extraction_method": "ollama_advanced" if llm_service.enabled else "rule_based"
                })
        
        return {
            "npcs_processed": len(results),
            "results": results,
            "ollama_enabled": llm_service.enabled
        }
        
    except Exception as e:
        logger.error(f"Error in advanced NPC extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting NPCs: {str(e)}")

# Player Management Routes
@api_router.post("/players", response_model=Player)
async def create_player(player_data: PlayerCreate, username: str = Depends(authenticate)):
    """Create a new player"""
    try:
        player_dict = player_data.dict()
        player_obj = Player(**player_dict)
        await db.players.insert_one(player_obj.dict())
        return player_obj
    except Exception as e:
        logger.error(f"Error creating player: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating player: {str(e)}")

@api_router.get("/players", response_model=List[Player])
async def get_players(username: str = Depends(authenticate)):
    """Get all players"""
    players = await db.players.find().sort("name", 1).to_list(1000)
    return [Player(**player) for player in players]

@api_router.get("/players/{player_id}", response_model=Player)
async def get_player(player_id: str, username: str = Depends(authenticate)):
    """Get a specific player"""
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return Player(**player)

@api_router.put("/players/{player_id}", response_model=Player)
async def update_player(player_id: str, player_data: PlayerUpdate, username: str = Depends(authenticate)):
    """Update a player"""
    try:
        update_data = {k: v for k, v in player_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.players.update_one(
            {"id": player_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Player not found")
        
        updated_player = await db.players.find_one({"id": player_id})
        return Player(**updated_player)
    except Exception as e:
        logger.error(f"Error updating player: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating player: {str(e)}")

@api_router.delete("/players/{player_id}")
async def delete_player(player_id: str, username: str = Depends(authenticate)):
    """Delete a player"""
    result = await db.players.delete_one({"id": player_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Player not found")
    return {"message": "Player deleted successfully"}

@api_router.get("/players/{player_id}/loot", response_model=List[LootItem])
async def get_player_loot(player_id: str, username: str = Depends(authenticate)):
    """Get all loot owned by a specific player"""
    loot_items = await db.loot.find({"current_owner": player_id}).sort("created_at", -1).to_list(1000)
    return [LootItem(**item) for item in loot_items]

@api_router.get("/players/{player_id}/attendance")
async def get_player_attendance(player_id: str, username: str = Depends(authenticate)):
    """Get attendance statistics for a player"""
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Get sessions where player was invited
    sessions_invited = await db.sessions.find(
        {"structured_data.players_invited": player_id}
    ).to_list(1000)
    
    # Calculate attendance stats
    total_invited = len(sessions_invited)
    attended_sessions = player.get("sessions_attended", [])
    attendance_rate = (len(attended_sessions) / total_invited * 100) if total_invited > 0 else 0
    
    return {
        "player_id": player_id,
        "player_name": player["name"],
        "total_sessions_invited": total_invited,
        "sessions_attended": len(attended_sessions),
        "attendance_rate": round(attendance_rate, 1),
        "attended_session_ids": attended_sessions
    }

# Loot Management Routes
@api_router.post("/loot", response_model=LootItem)
async def create_loot_item(loot_data: LootCreate, username: str = Depends(authenticate)):
    """Create a new loot item"""
    try:
        loot_dict = loot_data.dict()
        
        # Add to ownership history if there's an owner
        if loot_dict.get("current_owner"):
            loot_dict["ownership_history"] = [{
                "owner": loot_dict["current_owner"],
                "acquired_date": datetime.utcnow(),
                "method": "Manual creation"
            }]
        
        loot_obj = LootItem(**loot_dict)
        await db.loot.insert_one(loot_obj.dict())
        return loot_obj
    except Exception as e:
        logger.error(f"Error creating loot item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating loot item: {str(e)}")

@api_router.get("/loot", response_model=List[LootItem])
async def get_loot_items(username: str = Depends(authenticate)):
    """Get all loot items"""
    loot_items = await db.loot.find().sort("created_at", -1).to_list(1000)
    return [LootItem(**item) for item in loot_items]

@api_router.get("/loot/{loot_id}", response_model=LootItem)
async def get_loot_item(loot_id: str, username: str = Depends(authenticate)):
    """Get a specific loot item"""
    loot_item = await db.loot.find_one({"id": loot_id})
    if not loot_item:
        raise HTTPException(status_code=404, detail="Loot item not found")
    return LootItem(**loot_item)

@api_router.put("/loot/{loot_id}", response_model=LootItem)
async def update_loot_item(loot_id: str, loot_data: LootUpdate, username: str = Depends(authenticate)):
    """Update a loot item"""
    try:
        # Get current item to check for owner changes
        current_item = await db.loot.find_one({"id": loot_id})
        if not current_item:
            raise HTTPException(status_code=404, detail="Loot item not found")
        
        update_data = {k: v for k, v in loot_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # If owner is changing, add to ownership history
        if "current_owner" in update_data and update_data["current_owner"] != current_item.get("current_owner"):
            ownership_history = current_item.get("ownership_history", [])
            ownership_history.append({
                "owner": update_data["current_owner"],
                "acquired_date": datetime.utcnow(),
                "method": "Manual transfer"
            })
            update_data["ownership_history"] = ownership_history
        
        result = await db.loot.update_one(
            {"id": loot_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Loot item not found")
        
        updated_item = await db.loot.find_one({"id": loot_id})
        return LootItem(**updated_item)
    except Exception as e:
        logger.error(f"Error updating loot item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating loot item: {str(e)}")

@api_router.delete("/loot/{loot_id}")
async def delete_loot_item(loot_id: str, username: str = Depends(authenticate)):
    """Delete a loot item"""
    result = await db.loot.delete_one({"id": loot_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Loot item not found")
    return {"message": "Loot item deleted successfully"}

@api_router.post("/extract-loot-advanced")
async def extract_loot_advanced(request: LootExtractionRequest, username: str = Depends(authenticate)):
    """Advanced loot extraction using Ollama LLM or fallback methods"""
    try:
        # Extract loot using advanced method
        extracted_loot = await llm_service.extract_loot_advanced(request.session_text, request.players)
        
        results = []
        
        for extracted_item in extracted_loot:
            # Create new loot item
            loot_data = {
                "item_name": extracted_item.item_name,
                "description": extracted_item.description,
                "type": extracted_item.type,
                "rarity": extracted_item.rarity,
                "value": extracted_item.value,
                "magical_properties": extracted_item.magical_properties,
                "session_found": request.session_id,
                "location_found": extracted_item.location_found,
                "current_owner": "",  # Will be set based on recipient
            }
            
            # Find player by name/character name
            if extracted_item.recipient:
                for player in request.players:
                    if (player.get("name", "").lower() in extracted_item.recipient.lower() or
                        player.get("character_name", "").lower() in extracted_item.recipient.lower()):
                        loot_data["current_owner"] = player.get("id", "")
                        break
            
            # Add ownership history
            ownership_history = []
            if loot_data["current_owner"]:
                ownership_history.append({
                    "owner": loot_data["current_owner"],
                    "acquired_date": datetime.utcnow(),
                    "method": f"Extracted from session: {extracted_item.circumstances}",
                    "session_id": request.session_id
                })
            
            loot_data["ownership_history"] = ownership_history
            
            # Create loot item
            new_loot = LootItem(**loot_data)
            await db.loot.insert_one(new_loot.dict())
            
            results.append({
                "action": "created",
                "loot": new_loot,
                "extraction_method": "ollama_advanced" if llm_service.enabled else "rule_based"
            })
        
        return {
            "loot_processed": len(results),
            "results": results,
            "ollama_enabled": llm_service.enabled
        }
        
    except Exception as e:
        logger.error(f"Error in advanced loot extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting loot: {str(e)}")

# Enhanced session routes with attendance tracking
@api_router.post("/sessions", response_model=Session)
async def create_session(session_data: SessionCreate, username: str = Depends(authenticate)):
    try:
        session_dict = session_data.dict()
        session_dict = prepare_session_for_storage(session_dict)
        session_obj = Session(**session_dict)
        
        # Convert to dict for MongoDB storage
        storage_dict = session_obj.dict()
        
        await db.sessions.insert_one(storage_dict)
        return session_obj
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@api_router.get("/sessions", response_model=List[Session])
async def get_sessions(username: str = Depends(authenticate)):
    sessions = await db.sessions.find().sort("created_at", -1).to_list(1000)
    return [Session(**session) for session in sessions]

@api_router.get("/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str, username: str = Depends(authenticate)):
    session = await db.sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return Session(**session)

@api_router.put("/sessions/{session_id}", response_model=Session)
async def update_session(session_id: str, session_data: SessionUpdate, username: str = Depends(authenticate)):
    try:
        update_data = {k: v for k, v in session_data.dict().items() if v is not None}
        update_data = prepare_session_for_storage(update_data)
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.sessions.update_one(
            {"id": session_id}, 
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        updated_session = await db.sessions.find_one({"id": session_id})
        return Session(**updated_session)
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")

@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, username: str = Depends(authenticate)):
    result = await db.sessions.delete_one({"id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}

# Session template route
@api_router.get("/sessions/template/structured")
async def get_structured_template(username: str = Depends(authenticate)):
    """Return an empty structured session template"""
    template = SessionStructuredData()
    return template

# Export session route
@api_router.get("/sessions/{session_id}/export")
async def export_session(session_id: str, username: str = Depends(authenticate)):
    """Export session data in a formatted structure"""
    session = await db.sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_obj = Session(**session)
    
    # Create formatted export data
    export_data = {
        "session_info": {
            "title": session_obj.title,
            "created_at": session_obj.created_at.isoformat(),
            "session_type": session_obj.session_type
        },
        "content": session_obj.content,
        "structured_data": session_obj.structured_data.dict() if session_obj.structured_data else None
    }
    
    return export_data

# Enhanced NPC routes
@api_router.post("/npcs", response_model=NPC)
async def create_npc(npc_data: NPCCreate, username: str = Depends(authenticate)):
    npc_dict = npc_data.dict()
    npc_obj = NPC(**npc_dict)
    await db.npcs.insert_one(npc_obj.dict())
    return npc_obj

@api_router.get("/npcs", response_model=List[NPC])
async def get_npcs(username: str = Depends(authenticate)):
    npcs = await db.npcs.find().sort("name", 1).to_list(1000)
    return [NPC(**npc) for npc in npcs]

@api_router.get("/npcs/{npc_id}", response_model=NPC)
async def get_npc(npc_id: str, username: str = Depends(authenticate)):
    npc = await db.npcs.find_one({"id": npc_id})
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")
    return NPC(**npc)

@api_router.put("/npcs/{npc_id}", response_model=NPC)
async def update_npc(npc_id: str, npc_data: NPCUpdate, username: str = Depends(authenticate)):
    update_data = {k: v for k, v in npc_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.npcs.update_one(
        {"id": npc_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="NPC not found")
    
    updated_npc = await db.npcs.find_one({"id": npc_id})
    return NPC(**updated_npc)

@api_router.delete("/npcs/{npc_id}")
async def delete_npc(npc_id: str, username: str = Depends(authenticate)):
    result = await db.npcs.delete_one({"id": npc_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="NPC not found")
    return {"message": "NPC deleted successfully"}

# Legacy NPC extraction route (for backward compatibility)
@api_router.post("/extract-npc")
async def extract_npc(extraction_data: NPCExtraction, username: str = Depends(authenticate)):
    # Check if NPC already exists
    existing_npc = await db.npcs.find_one({"name": extraction_data.npc_name})
    
    if existing_npc:
        # Add interaction to existing NPC
        interaction_entry = {
            "session_id": extraction_data.session_id,
            "interaction": extraction_data.extracted_text,
            "timestamp": datetime.utcnow(),
            "extraction_method": "manual"
        }
        
        await db.npcs.update_one(
            {"name": extraction_data.npc_name},
            {"$push": {"history": interaction_entry}, "$set": {"updated_at": datetime.utcnow()}}
        )
        
        updated_npc = await db.npcs.find_one({"name": extraction_data.npc_name})
        return {"action": "updated", "npc": NPC(**updated_npc)}
    else:
        # Create new NPC
        new_npc = NPC(
            name=extraction_data.npc_name,
            notes=f"First mentioned: {extraction_data.extracted_text}",
            history=[{
                "session_id": extraction_data.session_id,
                "interaction": extraction_data.extracted_text,
                "timestamp": datetime.utcnow(),
                "extraction_method": "manual"
            }]
        )
        
        await db.npcs.insert_one(new_npc.dict())
        return {"action": "created", "npc": new_npc}

# Auto-suggest NPCs from text
@api_router.post("/suggest-npcs")
async def suggest_npcs(text_data: dict, username: str = Depends(authenticate)):
    text = text_data.get("text", "")
    suggested_names = await llm_service.extract_npcs_from_text(text)
    return {"suggested_npcs": suggested_names}

# Include the router in the main app
app.include_router(api_router)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
