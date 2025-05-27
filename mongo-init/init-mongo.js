// MongoDB Initialization Script for D&D Notes Application
// This script runs when MongoDB container starts for the first time

// Switch to the application database
db = db.getSiblingDB('dnd_notes');

// The root user is already created by Docker Compose environment variables
// Create an application-specific user for the backend to use
db.createUser({
  user: 'dnd_app_user',
  pwd: 'dnd_app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'dnd_notes'
    },
    {
      role: 'dbAdmin',
      db: 'dnd_notes'
    }
  ]
});

// Create collections with initial indexes for better performance
db.createCollection('sessions');
db.createCollection('npcs');
db.createCollection('users'); // Add users collection for authentication

// Create indexes for sessions collection
db.sessions.createIndex({ "id": 1 }, { unique: true });
db.sessions.createIndex({ "created_at": -1 });
db.sessions.createIndex({ "session_type": 1 });
db.sessions.createIndex({ "title": "text", "content": "text" }); // Full-text search
db.sessions.createIndex({ "structured_data.session_number": 1 });
db.sessions.createIndex({ "updated_at": -1 }); // For recent sessions

// Create indexes for npcs collection  
db.npcs.createIndex({ "id": 1 }, { unique: true });
db.npcs.createIndex({ "name": 1 });
db.npcs.createIndex({ "created_at": -1 });
db.npcs.createIndex({ "status": 1 });
db.npcs.createIndex({ "name": "text", "background": "text", "notes": "text" }); // Full-text search

// Create indexes for users collection
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true, sparse: true });
db.users.createIndex({ "created_at": -1 });

// Insert default admin user (hashed password should be handled by backend)
db.users.insertOne({
  "id": "admin-user-1",
  "username": "admin",
  "email": "admin@dndnotes.local",
  "role": "admin",
  "created_at": new Date(),
  "updated_at": new Date(),
  "is_active": true
});

// Insert sample data (optional - remove if you don't want sample data)
db.sessions.insertOne({
  "id": "sample-session-1",
  "title": "Welcome to D&D Note Keeper!",
  "content": "This is a sample free-form session to get you started. You can delete this once you create your own sessions.",
  "session_type": "free_form",
  "npcs_mentioned": [],
  "created_at": new Date(),
  "updated_at": new Date()
});

db.npcs.insertOne({
  "id": "sample-npc-1", 
  "name": "Sample NPC",
  "status": "Unknown",
  "race": "Human",
  "class_role": "Guide",
  "appearance": "A helpful character to demonstrate the NPC system",
  "quirks_mannerisms": "Always ready to help new users",
  "background": "Created to showcase the NPC management features",
  "notes": "This is a sample NPC. Feel free to edit or delete once you're familiar with the system.",
  "history": [],
  "created_at": new Date(),
  "updated_at": new Date()
});

// Print initialization completion message
print('D&D Notes database initialized successfully!');
print('Created collections: sessions, npcs, users');
print('Created indexes for better performance');
print('Created application user: dnd_app_user');
print('Added sample data (delete when ready)');
print('Default admin user created (username: admin)');
