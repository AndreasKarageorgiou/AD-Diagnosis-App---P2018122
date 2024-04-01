import pandas as pd
import numpy as np
import time
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, HistGradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("AIBL.csv")

# Define diagnosis features
diagnosis_features = ['DXNORM', 'DXMCI', 'DXAD']


def create_DXTYPE(DXNORM, DXMCI, DXAD):
    if DXNORM == 1:
        return 0  # Represent "normal" 
    elif DXMCI == 1:
        return 1  # Represent "MCI"
    elif DXAD == 1:
        return 2  # Represent "AD"
    else:
        return -1  # Handle the case where none of the conditions are satisfied

# Create DXPOS before removing other diagnosis features
df['DXTYPE'] = df.apply(lambda row: create_DXTYPE(row['DXNORM'], row['DXMCI'], row['DXAD']), axis=1)



# Get value counts for 'DXTYPE'
dxtypes_counts = df['DXTYPE'].value_counts()

# Print the result
print("Value Counts for DXTYPE:")
print(dxtypes_counts)

# Now remove the unnecessary diagnosis features:
df.drop(diagnosis_features, axis=1, inplace=True)

# Calculate age
df["ExamAge"] = df["Examyear"] - df["PTDOBYear"]

# Data Preprocessing
df.dropna(inplace=True)

# Define your updated feature list
desired_features = ['APGEN1','APGEN2','CDGLOBAL','AXT117','BAT126','HMT3','HMT7' ,
'HMT13','HMT40','HMT100','HMT102','RCT6','RCT11','RCT20','RCT392', 'MHPSYCH',
'MH2NEURL','MH4CARD','MH6HEPAT','MH8MUSCL','MH9ENDO',
'MH10GAST','MH12RENA','MH16SMOK','MH17MALI','MMSCORE','LIMMTOTAL', 
'LDELTOTAL' ,'PTGENDER',"ExamAge", 'APTyear']

# Extract features and labels
X = df[desired_features]
y = df['DXTYPE']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Create classifiers
classifiers = {
    "Random Forest": RandomForestClassifier(),
    "Gradient Boosting": GradientBoostingClassifier(),
    "AdaBoost": AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=3)), 
    "HistGradientBoosting": HistGradientBoostingClassifier(), # Relatively new model
    "KNN": KNeighborsClassifier(),
    "Logistic Regression": LogisticRegression()
}

# Perform 10-fold cross-validation for each classifier
cv_results = {}
for name, clf in classifiers.items():
    start_time = time.time()
    scores = cross_val_score(clf, X_train_scaled, y_train, cv=10)
    end_time = time.time()
    cv_results[name] = {
        "Mean Accuracy": scores.mean(),
        "Standard Deviation": scores.std(),
        "Cross-Validation Time": end_time - start_time
    }

# Print cross-validation results
for name, result in cv_results.items():
    print(f"{name} Cross-Validation Results:")
    print(f"Mean Accuracy: {result['Mean Accuracy']:.3f}")
    print(f"Standard Deviation: {result['Standard Deviation']:.3f}")
    print(f"Cross-Validation Time: {result['Cross-Validation Time']:.4f} seconds")
    print("=" * 50)
