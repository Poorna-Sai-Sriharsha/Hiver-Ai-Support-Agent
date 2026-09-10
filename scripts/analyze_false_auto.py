import io
import json

import pandas as pd

with open('artifacts/metrics.json', 'r') as f:
    data = json.load(f)

with open('evaluation/golden_set.csv', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    df = pd.read_csv(io.StringIO(content))

y_true = data['raw']['y_true_esc']
y_pred = data['raw']['y_pred_ai_esc']
texts = df['customer_message'].tolist()

failures = []
for i in range(len(y_true)):
    if y_true[i] == "Yes" and y_pred[i] == "No":
        failures.append(texts[i])

with open('artifacts/false_auto_handles.txt', 'w', encoding='utf-8') as f:
    f.write(f"Found {len(failures)} false auto-handles.\n\n")
    for i, text in enumerate(failures):
        f.write(f"Failure {i+1}: {text}\n")

print(f"Analyzed. Found {len(failures)} false auto-handles. Results saved to artifacts/false_auto_handles.txt")
