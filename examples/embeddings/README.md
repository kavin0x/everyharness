# Embeddings harness demo

```bash
everyharness add embeddings:demo-model --type embeddings
everyharness run <id> embed --input '{"texts":["hello world","goodbye"]}'
everyharness run <id> similarity --input '{"a":"cat","b":"kitten"}'
```

Without `sentence-transformers`, the harness uses a deterministic hash fallback.
