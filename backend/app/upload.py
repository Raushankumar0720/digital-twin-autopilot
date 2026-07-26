from fastapi import FastAPI, UploadFile, File, HTTPException
import json
import pandas as pd
import os
from typing import List, Dict

app = FastAPI()

# Folder to store relationship data
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
RELATIONSHIPS_FILE = os.path.join(DATA_DIR, "relationships.json")

def parse_messages(file_content: bytes, filename: str) -> List[Dict]:
    """Parse uploaded file (JSON, CSV, or TXT) into list of messages."""
    if filename.endswith(".json"):
        data = json.loads(file_content.decode("utf-8"))
        # Assume format: list of {"sender": "Name", "text": "...", "timestamp": "..."}
        return data
    elif filename.endswith(".csv"):
        df = pd.read_csv(pd.io.common.BytesIO(file_content))
        # Expect columns: sender, text, timestamp
        return df.to_dict(orient="records")
    elif filename.endswith(".txt"):
        lines = file_content.decode("utf-8").splitlines()
        messages = []
        for line in lines:
            if ":" in line:
                sender, text = line.split(":", 1)
                messages.append({"sender": sender.strip(), "text": text.strip(), "timestamp": ""})
        return messages
    else:
        raise ValueError("Unsupported file format")

def extract_relationships(messages: List[Dict]) -> Dict:
    """Analyze messages and assign relationship score (1-5)."""
    # Count messages per sender
    sender_counts = {}
    for msg in messages:
        sender = msg.get("sender", "Unknown")
        sender_counts[sender] = sender_counts.get(sender, 0) + 1

    # Calculate average message length per sender
    sender_lengths = {}
    for msg in messages:
        sender = msg.get("sender", "Unknown")
        length = len(msg.get("text", ""))
        sender_lengths.setdefault(sender, []).append(length)

    # Assign scores (simple heuristic)
    relationships = {}
    for sender, count in sender_counts.items():
        # If more than 100 messages, likely close contact
        if count > 100:
            score = 5
        elif count > 50:
            score = 4
        elif count > 20:
            score = 3
        elif count > 5:
            score = 2
        else:
            score = 1

        # If average length is very short, might be casual (increase score)
        avg_len = sum(sender_lengths.get(sender, [0])) / max(1, len(sender_lengths.get(sender, [0])))
        if avg_len < 10 and score < 4:
            score += 1  # very short messages = close friend?

        relationships[sender] = {
            "score": min(5, max(1, score)),
            "message_count": count,
            "avg_length": round(avg_len, 1)
        }
    return relationships

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload chat history and extract relationships."""
    try:
        content = await file.read()
        messages = parse_messages(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if not messages:
        raise HTTPException(status_code=400, detail="No messages found in file.")

    # Extract relationships
    relationships = extract_relationships(messages)

    # Save to file
    with open(RELATIONSHIPS_FILE, "w") as f:
        json.dump(relationships, f, indent=2)

    return {
        "success": True,
        "message_count": len(messages),
        "relationships": relationships,
        "preview": messages[:5]  # First 5 messages for preview
    }
