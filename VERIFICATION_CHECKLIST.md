# Post-Rebuild Verification Checklist

After rebuilding your Codespace, verify everything is working:

## ✅ Verification Steps

### 1. Check Mount Points
\`\`\`bash
mount | grep copilot
\`\`\`
**Expected:** Should show `.copilot-data` mounted to `/home/codespace/.vscode-remote/data/User/globalStorage/github.copilot-chat`

### 2. Verify Copilot Data Directory
\`\`\`bash
ls -la /home/codespace/.vscode-remote/data/User/globalStorage/github.copilot-chat/
\`\`\`
**Expected:** Should show files like `commandEmbeddings.json`, `plan-agent/`, etc.

### 3. Check Settings Applied
\`\`\`bash
code --list-extensions | grep copilot
\`\`\`
**Expected:** Should show `github.copilot` and `github.copilot-chat`

### 4. Test Chat Persistence
1. Open GitHub Copilot Chat
2. Start a conversation
3. Ask Copilot a question
4. **Stop and restart the Codespace**
5. Open Copilot Chat again
6. **Expected:** Your previous conversation should still be there!

### 5. Verify Plan Agent
1. Open Copilot Chat
2. Type `@plan` and see if it autocompletes
3. **Expected:** Plan agent should be available

### 6. Check Workspace Settings
In VS Code:
1. Open Settings (Cmd/Ctrl + ,)
2. Search for "copilot persist"
3. **Expected:** `GitHub > Copilot > Chat: Persist History` should be checked

## 🔍 Troubleshooting

### If mounts don't show:
\`\`\`bash
# Check if devcontainer.json is valid
cat .devcontainer/devcontainer.json | jq .
\`\`\`
If error, rebuild again.

### If chat history doesn't persist:
1. Check `.vscode/settings.json` exists and has `persistHistory: true`
2. Verify `.copilot-data/` is populated: `du -sh .copilot-data/`
3. Check permissions: `ls -la .copilot-data/`

### If Plan agent missing:
\`\`\`bash
# Verify Plan.agent.md exists
cat .copilot-data/plan-agent/Plan.agent.md
\`\`\`

## 📊 Storage Usage
Check how much data is being persisted:
\`\`\`bash
du -sh .copilot-data/
du -sh .copilot-chat-history/
\`\`\`

## 🎯 Success Criteria
- ✅ Mounts are active
- ✅ Chat sessions survive Codespace restarts
- ✅ Plan agent is available
- ✅ No errors in Copilot chat
- ✅ Settings show persist history enabled

## 📝 Notes
- First rebuild may take 2-3 minutes
- Existing chat data was migrated on: $(date)
- If you encounter issues, see [CHAT_PERSISTENCE_FIX.md](CHAT_PERSISTENCE_FIX.md)
