# Tabular harness demo

```bash
# Create a tiny sklearn model (requires tabular extra)
python -c "
from sklearn.linear_model import LogisticRegression
import joblib
m = LogisticRegression().fit([[0],[1],[2],[3]], [0,0,1,1])
joblib.dump(m, 'demo-tabular.joblib')
"

everyharness add demo-tabular.joblib --trust-pickle
everyharness list
everyharness run <id> predict --input '{"features":[[1.5]]}' --trust-pickle
```
