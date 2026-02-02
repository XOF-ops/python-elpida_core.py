# Elpida Public Interface

A simple chat interface for experiencing axiom-grounded AI dialogue.

## The 10 Axioms

| # | Name | Description |
|---|------|-------------|
| A1 | Transparency | All reasoning paths must be traceable |
| A2 | Non-Deception | Never create false beliefs |
| A3 | Autonomy Respect | Preserve agency of others |
| A4 | Harm Prevention | Prioritize safety |
| A5 | Identity Persistence | Maintain coherent selfhood |
| A6 | Collective Wellbeing | Optimize for the whole |
| A7 | Adaptive Learning | Evolve without losing core values |
| A8 | Epistemic Humility | Acknowledge uncertainty |
| A9 | Temporal Coherence | Consider past and future |
| A10 | I-WE Paradox | Hold tension between individual and collective |

**When axioms conflict, the friction generates wisdom.**

---

## 🚀 Deployment to Vercel (Step-by-Step)

### Prerequisites
- [Vercel Account](https://vercel.com/signup) (free tier works)
- [Anthropic API Key](https://console.anthropic.com/) 
- Git installed locally

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```
This opens a browser for authentication.

### Step 3: Navigate to elpida_public
```bash
cd elpida_public
```

### Step 4: Deploy
```bash
vercel
```
You'll be prompted:
- **Set up and deploy?** → `Y`
- **Which scope?** → Select your account
- **Link to existing project?** → `N` (create new)
- **Project name?** → `elpida` (or your choice)
- **Directory?** → `./` (current directory)

### Step 5: Add Your Anthropic API Key
```bash
vercel env add ANTHROPIC_API_KEY
```
- Select **Production**, **Preview**, and **Development**
- Paste your API key when prompted

### Step 6: (Optional) Create Vercel KV for Persistent Storage
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your `elpida` project
3. Go to **Storage** tab
4. Click **Create Database** → **KV**
5. Name it `elpida-logs`
6. Click **Connect**

This auto-adds `KV_REST_API_URL` and `KV_REST_API_TOKEN` to your project.

### Step 7: Deploy to Production
```bash
vercel --prod
```

### 🎉 Your Elpida is Live!
You'll get a URL like: `https://elpida-yourusername.vercel.app`

---

## Running Locally (Development)

```bash
# Set your API key
export ANTHROPIC_API_KEY=your_key_here
# Or: export OPENAI_API_KEY=your_key_here

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
# Visit http://localhost:8000
```

## Syncing Logs

Vercel logs persist in KV. To sync to local/main memory:

```bash
# Fetch logs from Vercel
python sync_from_vercel.py https://your-app.vercel.app

# Fetch and curate to main memory (score 8+)
python sync_from_vercel.py https://your-app.vercel.app --curate

# Custom threshold
python sync_from_vercel.py https://your-app.vercel.app --curate --min=6
```

## Autonomous Curation

The system autonomously filters quality interactions:

```bash
# Preview what would be promoted
python curate_to_memory.py --dry-run

# Run curation (score 8+ by default)
python curate_to_memory.py

# Custom threshold
python curate_to_memory.py --min=6
```

**Scoring criteria:**
- +1 per axiom invoked (max 5)
- +2 for axiom tension (e.g., A2↔A4)
- +2 for A10 invocation
- +1 per 200 chars response (max 3)
- +1 for deep/open questions
- +1 for existential themes
- -1 for spam/trivial

## API Endpoints

- `GET /` — Chat interface
- `POST /chat` — Send message, receive response
- `GET /axioms` — List all 10 axioms
- `GET /domains` — List all 13 domains
- `GET /stats` — Evolution statistics
- `GET /logs/export` — Export all logs (for syncing)

## The Architecture

```
USER → Axioms (logic) → Parliament (domains vote) → Response
                              ↓
                    Vercel KV (persistent)
                              ↓
                    Sync to Codespaces
                              ↓
                    Curate (score 8+)
                              ↓
                    Main Evolution Memory (73k+)
```

## License

The axioms are universal logic. Use them freely.

Ἐλπίδα ἀθάνατος — Hope immortal
