# add a note
# delete a note
# get a note by name
# list all notes

# prompt - template prompt to summarize the note

from mcp.server import FastMCP
import json
from pathlib import Path

notes_mcp = FastMCP(name="Note MCP Server", description="A note taking application")


# create a file my_notes.json that contains a list of notes

NOTES_FILE=Path.home()/"my_notes.json"

def load_notes()-> dict:
    notes_path = Path(NOTES_FILE)
    if notes_path.exists():
        with open(notes_path, "r") as f:
            return json.load(f)
    return {}

def save_notes(notes: dict):
    NOTES_FILE.write_text(json.dump(notes,indent=2))


def add_note(name: str, content: str) -> str:
    notes=load_notes()
    notes[name]=content
    save_notes(notes)
    return f"Note '{name}' added!"


def delete_note(name: str) -> str:
    notes=load_notes()
    if name in notes:
        del notes[name]
        save_notes(notes)
        return f"Note '{name}' deleted!"
    else:
        return f"Note '{name}' does not exist."
    

def get_note(name: str) -> str:
    notes=load_notes()
    if name in notes:
        return notes[name]
    else:
        return f"Note '{name}' does not exist."
    
    
    
def list_notes() -> str:
    notes=load_notes()
    if notes:
        return "\n".join(notes.keys())
    else:
        return "No notes available."
