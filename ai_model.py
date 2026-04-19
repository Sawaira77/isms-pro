import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

data = pd.DataFrame({
    "likelihood": [1,1,2,2,3,3,3,4,4,4,5,5,5,2,3,4,1,5,3,2],
    "impact":     [1,2,2,3,2,3,4,3,4,5,4,5,5,5,1,2,4,3,5,1],
    "level": [
        "LOW","LOW","LOW","MEDIUM","MEDIUM","MEDIUM","HIGH",
        "HIGH","HIGH","CRITICAL","HIGH","CRITICAL","CRITICAL",
        "HIGH","LOW","MEDIUM","MEDIUM","HIGH","CRITICAL","LOW"
    ]
})

X = data[["likelihood", "impact"]]
y = data["level"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

joblib.dump(model, "ai_model.pkl")
print("AI model trained and saved successfully.")
print("Classes:", model.classes_)
