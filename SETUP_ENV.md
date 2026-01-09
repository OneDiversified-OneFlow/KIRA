# KIRA Environment Setup Guide

## Required Environment Variables

### Minimum Required (for testing web chat UI)

For basic testing of the enhanced context injection and persona system, you need:

1. **ANTHROPIC_API_KEY** - Claude API key (required for full agent pipeline)
2. **SLACK_BOT_TOKEN** - Slack bot token (optional for web chat, required for Slack integration)
3. **SLACK_SIGNING_SECRET** - Slack signing secret (optional for web chat)

### Optional (for full KIRA functionality)

- **SLACK_APP_TOKEN** - For Socket Mode
- **BOT_NAME** - Bot display name
- **BOT_ORGANIZATION** - Organization name
- **FILESYSTEM_BASE_DIR** - Base directory for file storage
- Various MCP service API keys (Perplexity, DeepL, GitHub, etc.)

## Setup Steps

### 1. Create dev.env file

```bash
cd /tmp/KIRA
cp app/config/env/dev.env.example app/config/env/dev.env
```

### 2. Edit dev.env and set required variables

```bash
# Open in editor
nano app/config/env/dev.env
# or
code app/config/env/dev.env
```

### 3. Set minimum required variables

```bash
# Claude API Key (required for agent pipeline)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Slack (optional for web chat, required for Slack)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret

# Bot info (optional)
BOT_NAME=KIRA
BOT_ORGANIZATION=OneFlow
FILESYSTEM_BASE_DIR=/tmp/KIRA/data
```

### 4. Activate virtual environment

```bash
cd /tmp/KIRA
source venv/bin/activate
```

### 5. Verify installation

```bash
python3 -c "import claude_agent_sdk; print('✅ claude_agent_sdk installed')"
```

## Testing

After setup, test the web chat UI:

```bash
cd /tmp/KIRA
source venv/bin/activate
python3 start_chat_server.py
```

Then open http://127.0.0.1:8000/chat in your browser.

## Notes

- The web chat UI works without full KIRA environment, but responses will be limited
- Full agent pipeline requires ANTHROPIC_API_KEY
- Slack integration requires Slack tokens
- OneFlow data source is currently mocked (no API key needed yet)
