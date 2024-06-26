import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, classification_report, make_scorer, precision_score, recall_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, make_scorer



def get_clean_data():
    df = pd.read_csv("AIBL.csv")
  
    # Define diagnosis features and create a target variable
    diagnosis_features = ['DXNORM', 'DXMCI', 'DXAD']
    def create_DXTYPE(DXNORM, DXMCI, DXAD):
        if DXNORM == 1:
            return 0
        elif DXMCI == 1:
            return 1
        elif DXAD == 1:
            return 2
        else:
            return -1

    # Apply the function to create a target variable 'DXTYPE'
    df['DXTYPE'] = df.apply(lambda row: create_DXTYPE(row['DXNORM'], row['DXMCI'], row['DXAD']), axis=1)

    # Calculate age before dropping 'Examyear' and 'PTDOBYear'
    if 'Examyear' in df.columns and 'PTDOBYear' in df.columns:
        df["ExamAge"] = df["Examyear"] - df["PTDOBYear"]    

    # Columns to drop including the 'APTyear', 'Examyear', 'PTDOBYear', and 'DXCURREN'
    columns_to_drop = diagnosis_features + ['APTyear', 'Examyear', 'PTDOBYear', 'DXCURREN']
    df.drop(columns_to_drop, axis=1, inplace=True)
    
    return df

df = get_clean_data()

# Handling missing values
imputer = SimpleImputer(strategy='median')
df[df.columns] = imputer.fit_transform(df[df.columns])

# Define features and labels
desired_features = [
    'APGEN1', 'APGEN2', 'CDGLOBAL', 'AXT117', 'BAT126', 'HMT3', 'HMT7', 'HMT13', 'HMT40', 'HMT100', 'HMT102',
    'RCT6', 'RCT11', 'RCT20', 'RCT392', 'MHPSYCH', 'MH2NEURL', 'MH4CARD', 'MH6HEPAT', 'MH8MUSCL', 'MH9ENDO',
    'MH10GAST', 'MH12RENA', 'MH16SMOK', 'MH17MALI', 'MMSCORE', 'LIMMTOTAL', 'LDELTOTAL', 'PTGENDER', "ExamAge", 
]
X = df[desired_features]
y = df['DXTYPE']

# Data split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

# Ensure y_train and y_test are 1D arrays
y_train = y_train.ravel()
y_test = y_test.ravel()

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Label encoding
encoder = LabelEncoder()
y_train_encoded = encoder.fit_transform(y_train.ravel())  # Converts to 1D array if not already
y_test_encoded = encoder.transform(y_test.ravel())        # Now y_test should be 1D

# Model setup
model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', learning_rate=0.24056620429189268, max_depth=3, n_estimators=95)

# Pipeline creation
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', model)
])

# Cross-validation setup
cv = StratifiedKFold(n_splits=10, random_state=42, shuffle=True)
auc_scores = cross_val_score(pipeline, X_train_scaled, y_train_encoded, cv=cv, scoring=make_scorer(roc_auc_score, needs_proba=True, multi_class='ovo', average='macro'))

# Model training
pipeline.fit(X_train_scaled, y_train_encoded)

# Save the scaler, model, and encoder
joblib.dump(scaler, 'scaler.joblib')
joblib.dump(pipeline, 'model.joblib')
joblib.dump(encoder, 'label_encoder.joblib')

# Model prediction
y_pred = pipeline.predict(X_test_scaled)

# Evaluation
auc_score = roc_auc_score(y_test_encoded, pipeline.predict_proba(X_test_scaled), multi_class='ovo', average='macro')
accuracy = accuracy_score(y_test_encoded, y_pred)
f1 = f1_score(y_test_encoded, y_pred, average='weighted')
precision = precision_score(y_test_encoded, y_pred, average='weighted')
recall = recall_score(y_test_encoded, y_pred, average='weighted')
class_report = classification_report(y_test_encoded, y_pred, target_names=['Normal', 'MCI', 'AD'])

print(f"Average AUC Score (CV): {np.mean(auc_scores):.3f}")
print(f"AUC Score: {auc_score:.3f}")
print(f"Accuracy: {accuracy:.3f}")
print(f"F1 Score: {f1:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print("\nClassification Report:\n", class_report)



# Save the updated dataframe to a new CSV file
df.to_csv("Updated_AIBL1.csv", index=False)