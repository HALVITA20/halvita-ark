#!/usr/bin/env python3
import json, pandas as pd, numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from pathlib import Path

data = []
for f in Path('sessions/raw').glob('*.json'):
    with open(f) as file:
        s = json.load(file)
        fin = s.get('final_metrics', {})
        data.append({
            'IVP': fin.get('IVP',0), 'IP': fin.get('IP',0),
            'INS': fin.get('INS',0), 'alpha': fin.get('alpha',0),
            'beta': fin.get('beta',0), 'gamma': fin.get('gamma',0),
            'success': 1 if fin.get('IVP',0)>=30 else 0
        })
df = pd.DataFrame(data)
if df.empty: exit()

X = df.drop('success', axis=1)
y = df['success']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

clf = RandomForestClassifier()
clf.fit(X_train, y_train)
print(f"Точность: {accuracy_score(y_test, clf.predict(X_test)):.2%}")
importance = pd.Series(clf.feature_importances_, index=X.columns).sort_values(ascending=False)
print("Важность признаков:\n", importance)
importance.to_csv('analysis/FEATURE_IMPORTANCE.csv')
