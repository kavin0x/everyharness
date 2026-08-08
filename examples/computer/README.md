# Computer-use harness demo

```bash
everyharness add computer:demo-agent --type computer

# Dry-run (default) — logs action without executing
everyharness run <id> plan '{"type":"click","x":100,"y":200}'

# Opt-in control (requires EVERYHARNESS_ALLOW_COMPUTER=1)
EVERYHARNESS_ALLOW_COMPUTER=1 everyharness run <id> plan '{"type":"echo","message":"hi"}' --allow-control
```
