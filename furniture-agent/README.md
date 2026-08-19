# Furniture Lead Hunter 🪑

A lead generation agent that finds new buildings and offices with potential to sell furniture. Built with the same UI/UX pattern as Hunter Agent but customized for the furniture industry.

## Features

- 🔍 **Smart Search** - Uses Exa.ai to find relevant leads
- 📊 **Intent Scoring** - Scores leads based on furniture buying signals
- 🌐 **Streamlit Web UI** - Modern, interactive web interface
- 📱 **Telegram Bot** - Access leads from your phone
- 💾 **Supabase Storage** - Save leads to database
- 📥 **CSV Export** - Download leads for offline use

## Setup

### 1. Install Dependencies

```bash
cd furniture-agent
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file and add your API keys:

```env
# Get from https://exa.ai
EXA_API_KEY=your_exa_api_key

# Get from https://supabase.com
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Get from https://t.me/BotFather
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### 3. Create Supabase Table (Optional)

If using Supabase, create a table:

```sql
CREATE TABLE furniture_leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company TEXT,
    website TEXT,
    intent_signal TEXT,
    intent_score INTEGER,
    city TEXT,
    segment TEXT,
    decision_maker_role TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Usage

### Web Interface (Streamlit)

```bash
python app.py
```

Open http://localhost:8501 in your browser.

### Telegram Bot

```bash
python bot.py
```

Commands:
- `/start` - Welcome message
- `/help` - Help information
- `/segments` - View available segments
- `/hunt <City> <Segment>` - Search for leads

Examples:
```
/hunt Chennai Office
/hunt Mumbai Hotel
/hunt Bangalore Coworking
```

## Segments

| Segment | Description |
|---------|-------------|
| Office | Corporate offices, business parks |
| Coworking | Shared workspaces, incubators |
| Hotel | Hotels, resorts, hospitality |
| Restaurant | Restaurants, cafes, dining |
| Residential | Apartments, housing complexes |
| Retail | Stores, malls, showrooms |

## Intent Scoring

| Score | Signal | Keywords |
|-------|--------|----------|
| 9-10 | High | new opening, grand opening, fit-out, interior design |
| 7-8 | Medium | renovation, refurbishment, expansion |
| 4-6 | Low | planning, proposed, upcoming |

## Project Structure

```
furniture-agent/
├── .env                 # Environment variables
├── agent.py             # Core lead generation logic
├── app.py               # Streamlit web app
├── bot.py               # Telegram bot
├── supabase_client.py   # Database integration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## License

MIT License
