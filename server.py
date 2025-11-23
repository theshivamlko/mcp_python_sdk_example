# add a note
# delete a note
# get a note by name
# list all notes

# prompt - template prompt to summarize the note

from mcp.server import FastMCP
import json
from pathlib import Path

notes_mcp = FastMCP(name="Note MCP Server")


# create a file my_notes.json that contains a list of notes

NOTES_FILE="my_notes.json"

def load_notes()-> dict:
    notes_path = Path(NOTES_FILE)
    if notes_path.exists():
        with open(notes_path, "r") as f:
            return json.load(f)
    return {}

def save_notes(notes: dict):
    notes_path = Path(NOTES_FILE)
    with open(notes_path, "r") as f:
        f.write(json.dumps(notes, indent=2))
        # NOTES_FILE.write_text(json.dump(notes,indent=2))

@notes_mcp.tool()
def add_note(name: str, content: str) -> str:
    notes=load_notes()
    print( notes)
    notes[name]=content
    save_notes(notes)
    return f"Note '{name}' added!"

@notes_mcp.tool()
def delete_note(name: str) -> str:
    notes=load_notes()
    if name in notes:
        del notes[name]
        save_notes(notes)
        return f"Note '{name}' deleted!"
    else:
        return f"Note '{name}' does not exist."
    
@notes_mcp.tool()
def get_note(name: str) -> str:
    notes=load_notes()
    if name in notes:
        return notes[name]
    else:
        return f"Note '{name}' does not exist."
    
    
@notes_mcp.tool()
def list_notes() -> str:
    notes=load_notes()
    if notes:
        return "\n".join(notes.keys())
    else:
        return "No notes available."



@notes_mcp.resource("resource://{name}")
def get_note(name: str) -> str:
    notes=load_notes()
    if name in notes:
        return notes[name]
    else:
        return f"Note '{name}' does not exist."

@notes_mcp.prompt()
def summarize_note(name: str) -> str:
    notes=load_notes()
    if name in notes:
        return f"Here is the note summarize it in 10 words or less:\n\n{notes[name]}"
    return f"Note '{name}' nto found."