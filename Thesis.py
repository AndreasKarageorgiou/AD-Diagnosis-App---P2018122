import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import time
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier


# ***** PART 1: Data Loading and Exploration *****
# Load dataset
df = pd.read_csv("AIBL.csv")
print(df.describe()) 
print(df.info())
print(df.isna().sum())

# Create "Label" column
df["Label"] = df["DXAD"].apply(lambda x: 1 if x == "Alzheimer" else 0)

# Calculate age
df["AgeAtExamination"] = df["Examyear"] - df["PTDOBYear"]

# Define your updated feature list
desired_features = ['CDGLOBAL', 'MMSCORE', 'DXMCI', 'LDELTOTAL', 'LIMMTOTAL', 
'AgeAtExamination', 'PTGENDER']

# Extract features and labels
X = df[desired_features]
y = df['DXAD']

# Statistics for each diagnosis
alzheimer_df = df[df["Label"] == 1]
non_alzheimer_df = df[df["Label"] == 0]

# Compare examination age
age_t_test = stats.ttest_ind(alzheimer_df["AgeAtExamination"], non_alzheimer_df["AgeAtExamination"])

# Compare MMSE
mmse_t_test = stats.ttest_ind(alzheimer_df["MMSCORE"], non_alzheimer_df["MMSCORE"])

# Correlation between age and MMSE
correlation_pearson = stats.pearsonr(df["AgeAtExamination"], df["MMSCORE"])

# Calculate probabilities
probabilities = df["Label"].value_counts(normalize=True)
print(probabilities)

# Create dataframe with statistics
df_statistics = pd.DataFrame({
"Feature": ["Age at Examination", "MMSE"],
"Mean Alzheimer": [alzheimer_df["AgeAtExamination"].mean(), alzheimer_df["MMSCORE"].mean()],
"Mean Non-Alzheimer": [non_alzheimer_df["AgeAtExamination"].mean(), non_alzheimer_df["MMSCORE"].mean()],
"t-test p-value": [age_t_test.pvalue, mmse_t_test.pvalue],
"Pearson Correlation Coefficient": correlation_pearson[0],
"Probability Alzheimer": probabilities.get(1, 0),
"Probability Non-Alzheimer": probabilities.get(0, 0),
})

# Save statistics
df_statistics.to_csv("AIBL_statistics.csv")

# Visualize data
plt.scatter(df["AgeAtExamination"], df["MMSCORE"], c=df["Label"])
plt.xlabel("Age at Examination")
plt.ylabel("MMSE")
plt.show()

# Display message
print("Statistics saved to AIBL_statistics.csv")

# ***** PART 2: Preprocessing *****
def preprocess_data(df, target_column):
    df.dropna(inplace=True)  
    X = df.drop(target_column, axis=1)
    y = df[target_column]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, y_train, y_test, X, y

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Create models
model_regularized = LogisticRegression(max_iter=10000, C=0.1)
svm_model = SVC()
random_forest_model = RandomForestClassifier()
gradient_boosting_model = GradientBoostingClassifier()
decision_tree_model = DecisionTreeClassifier()
naive_bayes_model = GaussianNB()

# Training and Evaluation Loop
models = [
    ("Regularized Logistic Regression", LogisticRegression(max_iter=10000, C=0.1)),
    ("SVM", SVC()),
    ("Random Forest", RandomForestClassifier()),
    ("Gradient Boosting", GradientBoostingClassifier()),
    ("Decision Tree", DecisionTreeClassifier()),
    ("Naive Bayes", GaussianNB()),
    ("KNN", KNeighborsClassifier(n_neighbors=10)),
]

# Define 10-fold stratified cross-validation
cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

# Loop through models and perform cross-validation
for name, model in models:
    start_time = time.time()

    # Calculate cross-validation scores
    cv_results = cross_val_score(model, X, y, cv=cv, scoring='accuracy') 

    end_time = time.time()

    # Print results for the model
    print(f"\nModel: {name}")
    print(f"Training Time: {end_time - start_time:.4f} seconds (Overall)")
    print("Cross-Validation Accuracy Scores:", cv_results)
    print(f"Mean Accuracy: {cv_results.mean():.4f}")
    print(f"Standard Deviation: {cv_results.std():.4f}")