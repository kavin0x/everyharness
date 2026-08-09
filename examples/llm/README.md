# LLM harness demo

everyharness is a thin wrapper: Ollama must already be running for the Ollama path.

```bash
# Ollama backend (requires running ollama daemon)
everyharness add ollama:llama3
everyharness run <id> repl
everyharness serve <id> --port 8000
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'

# GGUF local file (requires: pip install 'everyharness[llm,llm-gguf]')
everyharness add ./model.gguf --type llm
everyharness run <id> complete "Say hi in one sentence"
```
