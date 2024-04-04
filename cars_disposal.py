import joblib


# Load the model from the file
loaded_model = joblib.load('cars_disposal_period_model.pkl')
new_mileage = [[1321525]]
# Example prediction using the loaded model
predicted_disposal_period_loaded = loaded_model.predict(new_mileage)
print('Predicted disposal period using loaded model:', predicted_disposal_period_loaded)
