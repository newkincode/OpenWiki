# OpenWiki Document Structure

OpenWiki uses a special file structure to manage wiki documents.

## File Structure

Each wiki document has a `.opwi` extension and consists of the following structure:

### Document Header
```
DOC:[UUID v7]
```
- Each document is identified by a unique UUID v7
- Example: `DOC:067b6e84-fdbe-73a1-8000-85d847465a72`

### Revision Information
```
REVUSER:[Username]:[IP Address]
REV:[SHA256 Hash]
```
- `REVUSER`: Records the username and IP address of the user who made the modification
- `REV`: SHA256 hash value of the document data including timestamp
- Example:
  - `REVUSER:Sinoka:61.72.114.110`
  - `REV:db7a3c5284dc93ddec1c8e3e426478eec5889b2673ade6144059de594e876a01`

### Document Content Changes
```
[Change Type][Line Number]|[Start Index]|[End Index]:[Content]
```
- Change Types:
  - `+`: Addition
  - `-`: Deletion
  - `=`: Modification
- Line Number: The line where the change occurred
- Start Index: The character position where the change begins
- End Index: The character position where the change ends
- Content: The actual text content of the document

Example:
```
+0|0|10:오픈위키 대문입니다.
=0|0|10:안녕이친구야우리같이놀자
```

## Sample Document
```
DOC:067b6e84-fdbe-73a1-8000-85d847465a72
REVUSER:Sinoka:61.72.114.110
REV:db7a3c5284dc93ddec1c8e3e426478eec5889b2673ade6144059de594e876a01
+0|0|10:오픈위키 대문입니다.
REVUSER:Sinoka:61.72.114.110
REV:-----
=0|0|10:안녕이친구야우리같이놀자
```

This structure allows for accurate tracking and management of document revision history. 