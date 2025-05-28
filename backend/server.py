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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DATABASE_NAME', os.environ.get('DB_NAME', 'dnd_notes'))]

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

# Campaign Models
class CampaignPlayer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    character_name: Optional[str] = ""
    status: str = "Active"  # Active, Inactive, Left
    notes: str = ""
    joined_date: datetime = Field(default_factory=datetime.utcnow)

class CampaignCreate(BaseModel):
    name: str
    description: str = ""
    dm_name: str = ""
    players: List[CampaignPlayer] = Field(default_factory=list)

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    dm_name: Optional[str] = None
    players: Optional[List[CampaignPlayer]] = None
    is_active: Optional[bool] = None

class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    dm_name: str = ""
    players: List[CampaignPlayer] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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
    campaign_id: str  # Link session to a campaign
    content: str = ""  # Free-form content for backward compatibility
    structured_data: Optional[SessionStructuredData] = None
    session_type: str = "free_form"  # "free_form" or "structured"

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    campaign_id: Optional[str] = None
    content: Optional[str] = None
    structured_data: Optional[SessionStructuredData] = None
    session_type: Optional[str] = None

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    campaign_id: str  # Link session to a campaign
    content: str = ""
    structured_data: Optional[SessionStructuredData] = None
    session_type: str = "free_form"
    npcs_mentioned: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# NPC Models (keeping existing structure)
class NPCCreate(BaseModel):
    name: str
    status: str = "Unknown"
    race: str = ""
    class_role: str = ""
    appearance: str = ""
    quirks_mannerisms: str = ""
    background: str = ""
    notes: str = ""

class NPCUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    race: Optional[str] = None
    class_role: Optional[str] = None
    appearance: Optional[str] = None
    quirks_mannerisms: Optional[str] = None
    background: Optional[str] = None
    notes: Optional[str] = None

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
    history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NPCExtraction(BaseModel):
    session_id: str
    extracted_text: str
    npc_name: str

# Ollama LLM Placeholder Class
class OllamaLLMService:
    """
    Placeholder class for Ollama LLM integration.
    Currently uses rule-based logic, but designed to be easily replaced
    with actual Ollama API calls.
    """
    
    def __init__(self):
        self.enabled = False  # Set to True when Ollama is configured
        
    async def extract_npcs_from_text(self, text: str) -> List[str]:
        """
        Placeholder for NPC extraction using LLM.
        Currently uses simple pattern matching.
        """
        if self.enabled:
            # TODO: Implement actual Ollama API call
            pass
        
        # Simple rule-based extraction for now
        patterns = [
            r'\b([A-Z][a-z]+ (?:the )?[A-Z][a-z]+)\b',  # "Thorin the Blacksmith"
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',           # "John Smith"
            r'NPC:\s*([A-Za-z\s]+)',                     # "NPC: Character Name"
        ]
        
        extracted_names = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            extracted_names.extend(matches)
        
        # Remove duplicates and common words
        common_words = {'The Game', 'The Party', 'The Group', 'Game Master', 'Dungeon Master'}
        return [name.strip() for name in set(extracted_names) if name.strip() not in common_words]
    
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

# API Routes
@api_router.get("/")
async def root():
    return {"message": "D&D Note-Taking Tool API"}

@api_router.get("/auth/check")
async def check_auth(username: str = Depends(authenticate)):
    return {"authenticated": True, "username": username}

# Session routes
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

# NPC routes (keeping existing)
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

# NPC extraction route
@api_router.post("/extract-npc")
async def extract_npc(extraction_data: NPCExtraction, username: str = Depends(authenticate)):
    # Check if NPC already exists
    existing_npc = await db.npcs.find_one({"name": extraction_data.npc_name})
    
    if existing_npc:
        # Add interaction to existing NPC
        interaction_entry = {
            "session_id": extraction_data.session_id,
            "interaction": extraction_data.extracted_text,
            "timestamp": datetime.utcnow()
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
                "timestamp": datetime.utcnow()
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

# Campaign routes
@api_router.post("/campaigns", response_model=Campaign)
async def create_campaign(campaign_data: CampaignCreate, username: str = Depends(authenticate)):
    """Create a new campaign (admin only)"""
    try:
        campaign_dict = campaign_data.dict()
        campaign_obj = Campaign(**campaign_dict)
        
        # Convert to dict for MongoDB storage
        storage_dict = campaign_obj.dict()
        
        await db.campaigns.insert_one(storage_dict)
        return campaign_obj
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating campaign: {str(e)}")

@api_router.get("/campaigns", response_model=List[Campaign])
async def get_campaigns(username: str = Depends(authenticate)):
    """Get all campaigns"""
    campaigns = await db.campaigns.find({"is_active": True}).sort("created_at", -1).to_list(1000)
    return [Campaign(**campaign) for campaign in campaigns]

@api_router.get("/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str, username: str = Depends(authenticate)):
    """Get a specific campaign"""
    campaign = await db.campaigns.find_one({"id": campaign_id})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return Campaign(**campaign)

@api_router.put("/campaigns/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, campaign_data: CampaignUpdate, username: str = Depends(authenticate)):
    """Update a campaign (admin only)"""
    try:
        update_data = {k: v for k, v in campaign_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.campaigns.update_one(
            {"id": campaign_id}, 
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        updated_campaign = await db.campaigns.find_one({"id": campaign_id})
        return Campaign(**updated_campaign)
    except Exception as e:
        logger.error(f"Error updating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating campaign: {str(e)}")

@api_router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, username: str = Depends(authenticate)):
    """Soft delete a campaign (admin only)"""
    result = await db.campaigns.update_one(
        {"id": campaign_id}, 
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted successfully"}

@api_router.get("/campaigns/{campaign_id}/sessions", response_model=List[Session])
async def get_campaign_sessions(campaign_id: str, username: str = Depends(authenticate)):
    """Get all sessions for a specific campaign"""
    sessions = await db.sessions.find({"campaign_id": campaign_id}).sort("created_at", -1).to_list(1000)
    return [Session(**session) for session in sessions]

@api_router.post("/campaigns/{campaign_id}/players")
async def add_campaign_player(campaign_id: str, player_data: CampaignPlayer, username: str = Depends(authenticate)):
    """Add a player to a campaign"""
    try:
        # Get the campaign
        campaign = await db.campaigns.find_one({"id": campaign_id})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign_obj = Campaign(**campaign)
        
        # Check if player name already exists
        existing_names = [p.name for p in campaign_obj.players]
        if player_data.name in existing_names:
            raise HTTPException(status_code=400, detail="Player name already exists in this campaign")
        
        # Add the new player
        campaign_obj.players.append(player_data)
        campaign_obj.updated_at = datetime.utcnow()
        
        # Update in database
        await db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": campaign_obj.dict()}
        )
        
        return {"message": "Player added successfully", "player": player_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding player: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding player: {str(e)}")

@api_router.put("/campaigns/{campaign_id}/players/{player_id}")
async def update_campaign_player(campaign_id: str, player_id: str, player_data: CampaignPlayer, username: str = Depends(authenticate)):
    """Update a player in a campaign"""
    try:
        campaign = await db.campaigns.find_one({"id": campaign_id})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign_obj = Campaign(**campaign)
        
        # Find and update the player
        player_found = False
        for i, player in enumerate(campaign_obj.players):
            if player.id == player_id:
                campaign_obj.players[i] = player_data
                player_found = True
                break
        
        if not player_found:
            raise HTTPException(status_code=404, detail="Player not found in campaign")
        
        campaign_obj.updated_at = datetime.utcnow()
        
        # Update in database
        await db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": campaign_obj.dict()}
        )
        
        return {"message": "Player updated successfully", "player": player_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating player: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating player: {str(e)}")

@api_router.delete("/campaigns/{campaign_id}/players/{player_id}")
async def remove_campaign_player(campaign_id: str, player_id: str, username: str = Depends(authenticate)):
    """Remove a player from a campaign"""
    try:
        campaign = await db.campaigns.find_one({"id": campaign_id})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign_obj = Campaign(**campaign)
        
        # Find and remove the player
        original_count = len(campaign_obj.players)
        campaign_obj.players = [p for p in campaign_obj.players if p.id != player_id]
        
        if len(campaign_obj.players) == original_count:
            raise HTTPException(status_code=404, detail="Player not found in campaign")
        
        campaign_obj.updated_at = datetime.utcnow()
        
        # Update in database
        await db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": campaign_obj.dict()}
        )
        
        return {"message": "Player removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing player: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error removing player: {str(e)}")

# Initialize default campaign for existing data
@api_router.post("/initialize-default-campaign")
async def initialize_default_campaign(username: str = Depends(authenticate)):
    """Initialize a default campaign for existing sessions (admin only)"""
    try:
        # Check if default campaign already exists
        existing_default = await db.campaigns.find_one({"name": "Default Campaign"})
        if existing_default:
            return {"message": "Default campaign already exists", "campaign_id": existing_default["id"]}
        
        # Create default campaign
        default_campaign = Campaign(
            name="Default Campaign",
            description="Default campaign for existing sessions",
            dm_name="Game Master",
            players=[]
        )
        
        await db.campaigns.insert_one(default_campaign.dict())
        
        # Update all existing sessions without campaign_id
        sessions_without_campaign = await db.sessions.find({"campaign_id": {"$exists": False}}).to_list(None)
        
        if sessions_without_campaign:
            await db.sessions.update_many(
                {"campaign_id": {"$exists": False}},
                {"$set": {"campaign_id": default_campaign.id}}
            )
        
        return {
            "message": "Default campaign created and existing sessions updated",
            "campaign_id": default_campaign.id,
            "sessions_updated": len(sessions_without_campaign)
        }
    except Exception as e:
        logger.error(f"Error initializing default campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initializing default campaign: {str(e)}")

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

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
