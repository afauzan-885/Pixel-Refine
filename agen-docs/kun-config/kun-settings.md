# Konfigurasi Kun App

**Sumber**: `.kun/data/config.json` + `.kun/mcp.json` + `.kun/data/memory/`

## Model Profiles

### DeepSeek Models

| Model | Context | Input | Output | Reasoning | Default Effort |
|-------|---------|-------|--------|-----------|----------------|
| `deepseek-v4-pro` | 1M tokens | text | text | off/high/max | max |
| `deepseek-v4-flash` | 1M tokens | text | text | off/high/max | max |

**Aliases**:
- `deepseek-chat` → deepseek-v4-flash
- `deepseek-reasoner` → deepseek-v4-flash

### Mimo Models

| Model | Context | Input | Output | Reasoning | Default Effort |
|-------|---------|-------|--------|-----------|----------------|
| `mimo-v2.5-pro-ultraspeed` | 1M tokens | text | text | off/low/medium/high | high |
| `mimo-v2.5-pro` | 1M tokens | text | text | off/low/medium/high | high |
| `mimo-v2.5` | 1M tokens | text+image | text | off/low/medium/high | high |
| `mimo-v2-pro` | 1M tokens | text | text | off/low/medium/high | high |
| `mimo-v2-omni` | 256K tokens | text+image | text | off/low/medium/high | high |
| `mimo-v2-flash` | 256K tokens | text | text | off/low/medium/high | high |

## Context Compaction Settings

```json
{
  "defaultSoftThreshold": 16000,
  "defaultHardThreshold": 24000,
  "summaryMode": "heuristic",
  "summaryTimeoutMs": 15000,
  "summaryMaxTokens": 1200,
  "summaryInputMaxBytes": 98304
}
```

## Runtime Settings

```json
{
  "streamIdleTimeoutMs": 45000,
  "toolStorm": {
    "enabled": true,
    "windowSize": 8,
    "threshold": 3
  },
  "toolArgumentRepair": {
    "maxStringBytes": 524288
  }
}
```

## Quality Settings

```json
{
  "enabled": true,
  "strictness": "standard",
  "maxFindings": 12
}
```

## MCP Servers

### 1. GUI Schedule
```json
{
  "enabled": true,
  "transport": "stdio",
  "command": "C:\\Users\\BelutGoyang\\AppData\\Local\\Programs\\Kun\\Kun.exe",
  "args": ["claw-schedule-mcp-node-entry.js", "--gui-schedule-mcp-server", "--base-url", "http://127.0.0.1:8788"],
  "trustScope": "user",
  "timeoutMs": 5000
}
```

### 2. Memory
```json
{
  "enabled": true,
  "transport": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"],
  "trustScope": "user",
  "timeoutMs": 300000
}
```

### 3. Sequential Thinking
```json
{
  "enabled": true,
  "transport": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
  "trustScope": "user",
  "timeoutMs": 300000
}
```

### 4. Context7
```json
{
  "enabled": true,
  "transport": "stdio",
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp@latest"],
  "trustScope": "user",
  "timeoutMs": 300000
}
```

## Capabilities

### Web
```json
{
  "enabled": true,
  "fetchEnabled": true,
  "searchEnabled": false,
  "maxFetchBytes": 1000000
}
```

### Skills
```json
{
  "enabled": true,
  "roots": [
    "C:\\Users\\BelutGoyang\\.agents\\skills",
    "C:\\Users\\BelutGoyang\\.codex\\skills",
    "C:\\Users\\BelutGoyang\\.kun\\skills"
  ],
  "legacySkillMd": true
}
```

### Memory
```json
{
  "enabled": true,
  "scopes": ["user", "workspace", "project"],
  "maxInjectedRecords": 8
}
```

### Attachments
```json
{
  "enabled": true,
  "maxImageBytes": 5242880,
  "maxImageDimension": 4096,
  "allowedMimeTypes": ["image/png", "image/jpeg", "image/webp"]
}
```

### Disabled Features
- imageGen: disabled
- speechGen: disabled
- musicGen: disabled
- videoGen: disabled
- computerUse: disabled

## Thread History

### Thread 1: `thr_ljlbd1vb`
- Title: "Untitled requirement"
- Model: mimo-v2-flash
- Created: 2026-06-17
- Status: idle (no turns)

### Thread 2: `thr_oyjprc1m` (Current)
- Created: 2026-06-17
- Events: 5.1 MB
- Messages: 2 MB
- Metadata: 800 KB

## Attachments (Screenshots)

| ID | Name | Date | Size | Resolution |
|----|------|------|------|------------|
| att_24de3dd0082ebf66487e0717 | pasted-image-20260618-134758 | 2026-06-18 | 205 KB | 1920×1080 |
| att_53cc5fdbe463929bb67268d8 | pasted-image-20260616-154538 | 2026-06-16 | 231 KB | 1920×1080 |
| att_74043f3af890fdddaba3725f | pasted-image-20260616-151510 | 2026-06-16 | 229 KB | 1920×1080 |
| att_9fe2f7425660d4c9b2c13ecd | pasted-image-20260616-154703 | 2026-06-16 | 171 KB | 1920×1080 |
| att_a61043628dcb8e5079bdc0df | pasted-image-20260616-152104 | 2026-06-16 | 81 KB | 1920×1080 |
| att_aa7c20bccf10cb7e00f794b2 | pasted-image-20260616-151512 | 2026-06-16 | 80 KB | 1920×1080 |
| att_c46c15097afc9ed4bd76ae23 | pasted-image-20260616-154518 | 2026-06-16 | 83 KB | 1920×1080 |
| att_de57036e794d246df73c3a09 | pasted-image-20260616-152143 | 2026-06-16 | 231 KB | 1920×1080 |

## Codex Skills (15 Available)

| # | Skill | Description |
|---|-------|-------------|
| 1 | hatch-pet | Animasi virtual pet |
| 2 | jupyter-notebook | Template Jupyter notebooks |
| 3 | linear | Integrasi Linear |
| 4 | migrate-to-codex | Migrasi ke Codex |
| 5 | netlify-deploy | Deploy ke Netlify |
| 6 | notion-knowledge-capture | Knowledge capture Notion |
| 7 | render-deploy | Deploy ke Render |
| 8 | security-best-practices | Best practices keamanan |
| 9 | security-ownership-map | Ownership mapping |
| 10 | security-threat-model | Threat modeling |
| 11 | sentry | Error tracking Sentry |
| 12 | speech | Text-to-speech |
| 13 | transcribe | Audio transcription |
| 14 | vercel-deploy | Deploy ke Vercel |
| 15 | winui-app | Pengembangan WinUI |
| 16 | yeet | Deployment tools |

## Deleted Memory

### `mem_mqjjpwky_9wjpb7`
- Content: "Setiap percakapan ambil inti dan ringkasannya untuk mendapati konteks dan mengurangi cache miss"
- Scope: workspace
- Created: 2026-06-18
- Deleted: 2026-06-19

**Catatan**: Memory ini sudah dihapus, mungkin karena duplikat atau user berubah pikiran.
