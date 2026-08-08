# Tabular harness demo

```bash
# Create a tiny sklearn model (requires tabular extra)
python -c "
from sklearn.linear_model import LogisticRegression
import joblib
m = LogisticRegression().fit([[0,0],[1,0],[0,1],[1,1]], [0,0,1,1])
joblib.dump(m, 'demo-tabular.joblib')
"

everyharness add demo-tabular.joblib --trust-pickle
everyharness list

# --input accepts a file path or inline JSON
everyharness run --trust-pickle <id> predict --input '[[1.5, 0.5]]'
everyharness run --trust-pickle <id> predict --input '{"features":[[1.5, 0.5]]}'
```

The repo fixture `fixtures/sklearn.pkl` is a 2-feature LogisticRegression — use rows shaped like `[x1, x2]`.
