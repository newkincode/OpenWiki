# OpenWiki

OpenWiki is a wiki engine based on Python and Flask.

## Features

- Markdown syntax support
- Document revision history
- Inter-document links (`[[document name]]`)
- Document search (title, content, tags)
- User contribution tracking
- Namespace support

## Project Structure

```
OpenWiki/
├── main.py                 # Flask application main file
├── parser/                 # Document parsing modules
│   ├── __init__.py
│   └── parser.py          # OPWI file parser
├── rev_system/            # Document management system
│   ├── __init__.py
│   └── document.py        # Document and DocumentManager classes
├── static/                # Static files
│   ├── css/
│   │   └── style.css     # Stylesheet
│   └── js/
│       └── search.js     # Search functionality script
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── edit.html         # Document edit page
│   ├── create.html       # Document creation page
│   ├── history.html      # Revision history page
│   ├── search.html       # Search results page
│   └── 404.html          # 404 error page
├── pages/                # Wiki document storage
│   └── main/            # Main namespace
│       └── *.opwi       # Wiki document files
└── index/               # Document index
    └── document_index.json  # Document metadata index
```

## OPWI File Structure

OpenWiki uses a special file format with the `.opwi` extension:

```
DOC:[UUID]                # Document unique ID (UUID v4)
META:[JSON metadata]      # Document metadata (title, creation date, tags, etc.)
REVUSER:[user]:[IP]      # User who made the modification
REVBLOCK:START           # Start of change block
CHANGES:[changes JSON]    # Changes (additions/deletions/modifications)
REVBLOCK:END             # End of change block
```

### Change Format

Changes are recorded in the following format:
- `+line|start|end:content` : Content addition
- `-line|start|end:content` : Content deletion
- `=line|start|end:content` : Content modification

## Installation

1. Clone repository:
```bash
git clone https://github.com/FamilyMink5/OpenWiki.git
cd OpenWiki
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run server:
```bash
python main.py
```

## Usage

1. Create document:
   - Click "New Document" button
   - Enter title and content
   - Markdown syntax supported

2. Edit document:
   - Click "Edit" button on document page
   - Modify content and save

3. Link documents:
   - Use `[[document name]]` format to link to other documents
   - Automatically redirects to creation page for non-existent documents

4. Search documents:
   - Enter search term in top search bar
   - Supports search by title, content, and tags

5. View history:
   - Click "History" button on document page
   - View all changes and contributors