# Computer harness demo (experimental)

v1 is a **dry-run action logger**, not real computer use. With `--allow-control`, only `echo` actions run.

```bash
everyharness add computer:demo-agent --type computer

# Dry-run (default) — logs action without executing
everyharness run <id> plan '{"type":"click","x":100,"y":200}'

# Opt-in echo only (requires EVERYHARNESS_ALLOW_COMPUTER=1)
EVERYHARNESS_ALLOW_COMPUTER=1 everyharness run <id> plan '{"type":"echo","message":"hi"}' --allow-control
```
