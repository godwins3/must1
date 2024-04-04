import pandas as pd
import joblib

# Load the dataset
data = {
    'make': ['Ford', 'Honda', 'BMW', 'Ford', 'Toyota'],
    'model': ['3 Series', 'Fusion', 'Camry', 'Fusion', 'Camry'],
    'year': [2020, 2023, 2024, 2001, 2013],
    'last_maintenance_date': ['2020-12-27', '2022-03-08', '2021-11-26', '2023-12-07', '2019-09-04'],
    'insurance_due': [True, True, True, True, False]
}
df = pd.DataFrame(data)

# Convert last_maintenance_date to datetime
df['last_maintenance_date'] = pd.to_datetime(df['last_maintenance_date'])

# Load the trained Random Forest classifier model
loaded_model = joblib.load('insurance.pkl')

# Select features for prediction
X_pred = df[['make', 'model', 'year', 'last_maintenance_date']]

# Predict whether insurance is due
predictions = loaded_model.predict(X_pred)

# Add predicted insurance due to the DataFrame
df['predicted_insurance_due'] = predictions

# Print the new DataFrame with predicted insurance due
print(df)

# Save the trained model
# joblib.dump(loaded_model, 'random_forest_model_trained.pkl')
