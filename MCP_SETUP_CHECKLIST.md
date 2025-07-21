# MCP System Setup Checklist

## 🚀 Pre-Setup
- [ ] Kill any existing processes on ports 5000, 5003, 5005
- [ ] Clear terminal and start fresh

## 📋 Step-by-Step Setup

### 1. Start Jarvis (API Server)
```bash
python3 api_server.py
```
**Expected Output:**
```
* Running on http://127.0.0.1:5000
* Debugger is active!
```

### 2. Start CEO Review System  
```bash
python3 proper_mcp_system.py
```
**Expected Output:**
```
* Running on http://127.0.0.1:5003
* Debugger is active!
```

### 3. Test Both Servers Are Running
```bash
curl http://localhost:5000/api/jarvis/chat -X POST -H "Content-Type: application/json" -d '{"message": "test"}'
curl http://localhost:5003/api/ceo/review -X POST -H "Content-Type: application/json" -d '{"message": "test"}'
```

### 4. Start Active MCP Coordinator
```bash
python3 active_mcp_coordinator.py
```
**Expected Output:**
```
🚀 ACTIVE MCP COORDINATOR
✅ Jarvis responded: [response]
📊 CEO Score: [score]/1.0
✅ Feedback sent to Cursor
✅ Applied [X] improvements
```

## 🔧 Troubleshooting

### Port Already in Use
```bash
lsof -ti:5000 | xargs kill -9
lsof -ti:5003 | xargs kill -9
lsof -ti:5005 | xargs kill -9
```

### Connection Refused
- Check if servers are actually running
- Verify ports are correct
- Restart servers in order

### No Improvement in Scores
- Check if improvements are being applied to api_server.py
- Verify CEO review is working
- Check feedback files are being generated

## 📊 Success Indicators

✅ **Jarvis responding** on port 5000  
✅ **CEO Review working** on port 5003  
✅ **Coordinator running** automatic cycles  
✅ **Scores improving** over cycles  
✅ **Files being modified** (api_server.py)  
✅ **Feedback generated** (ceo_feedback.md, cursor_feedback.md)  

## 🎯 Expected Cycle Flow
1. **Jarvis** → Responds to test message
2. **CEO Review** → Analyzes and scores response  
3. **Send to Cursor** → Generates improvement feedback
4. **Implement** → Modifies api_server.py with improvements
5. **Re-test** → Tests improved Jarvis
6. **Compare** → Shows before/after scores
7. **Repeat** → Every 30 seconds

## 📁 Key Files
- `api_server.py` - Jarvis's brain (port 5000)
- `proper_mcp_system.py` - CEO Review (port 5003)  
- `active_mcp_coordinator.py` - Orchestrator
- `ceo_feedback.md` - CEO feedback output
- `cursor_feedback.md` - Cursor improvement suggestions

## 🚨 Critical Notes
- **Both servers must run simultaneously**
- **Order matters**: Jarvis first, then CEO Review
- **Check logs** for connection errors
- **Monitor file changes** to verify improvements
- **Scores should improve** over multiple cycles 