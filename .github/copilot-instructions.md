# Copilot Instructions - Mergington High School Activities API

## Project Overview

FastAPI application for managing high school extracurricular activities with a vanilla JavaScript frontend. The app uses **in-memory storage** (data resets on server restart) and follows a simple REST API pattern.

## Architecture

- **Backend**: `src/app.py` - Single-file FastAPI server with static file serving
- **Frontend**: `src/static/` - Vanilla JS (no framework), fetches from API
- **Tests**: `tests/test_app.py` - pytest with FastAPI TestClient
- **Data Model**: Dictionary-based with activity names as keys, email addresses as participant identifiers

## Key Patterns

### Data Structure Convention
Activities use **name as identifier** (not IDs). Students identified by **email only** (no separate student objects in current implementation):

```python
activities = {
    "Chess Club": {
        "description": str,
        "schedule": str,
        "max_participants": int,
        "participants": [email, ...]
    }
}
```

### API Endpoint Pattern
- Activity names in URL paths: `/activities/{activity_name}/signup`
- Email passed as query parameter: `?email=student@mergington.edu`
- All URLs must be **URL-encoded** (spaces become `%20`)

### Error Handling
Use FastAPI's `HTTPException` with specific status codes:
- 404: Activity not found
- 400: Business logic errors (duplicate signup, not registered)

## Development Workflow

### Running the Server
```bash
python src/app.py
# Server runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Running Tests
```bash
pytest
# Uses pytest.ini configuration: pythonpath = .
```

**Critical**: Tests use `reset_activities()` fixture with `autouse=True` to reset state before each test. Always maintain this pattern when adding new tests.

### Frontend Development
Frontend at `src/static/` uses **event delegation** for dynamic delete buttons. When adding UI features:
- Use `fetch()` API (no axios/jQuery)
- Handle URL encoding with `encodeURIComponent()`
- Refresh activity list after mutations with `await fetchActivities()`

## Common Tasks

### Adding a New Activity Field
1. Update `activities` dict in `src/app.py`
2. Update `reset_activities()` fixture in `tests/test_app.py`
3. Modify frontend rendering in `src/static/app.js` (activity card HTML)

### Adding a New Endpoint
1. Define route in `src/app.py` with proper validation
2. Add corresponding tests in `tests/test_app.py`
3. Update frontend if UI integration needed

### Testing Strategy
- Use `client` fixture (TestClient instance)
- Access in-memory data via `activities` dict directly for assertions
- Test both success and error paths (404, 400 status codes)
- Example: `test_signup_duplicate_participant` shows error handling pattern

## Important Constraints

- **No database**: All data in memory, resets on restart
- **No authentication**: Email is trusted user identifier
- **No capacity enforcement**: `max_participants` is informational only (not enforced in code)
- **Single-file backend**: Keep all routes in `app.py` unless significant growth

## Dependencies

Minimal stack (see `requirements.txt`):
- `fastapi` + `uvicorn` for server
- `pytest` + `httpx` for testing

No ORM, no database drivers, no authentication libraries.
