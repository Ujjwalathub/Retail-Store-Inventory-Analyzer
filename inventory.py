import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the Dataset
# Ensure 'retail_store_inventory.csv' is in the same directory as your script
df = pd.read_csv('retail_store_inventory.csv')

# 2. Preprocessing & Feature Engineering
print("Engineering new features...")
# Convert Date to datetime so we can extract useful info and sort it
df['Date'] = pd.to_datetime(df['Date'])

# Extract Month and Day of Week (helps the model learn time-based patterns)
df['Month'] = df['Date'].dt.month
df['DayOfWeek'] = df['Date'].dt.dayofweek

# Create a 'Price Difference' feature (Competitor Price vs Our Price)
df['Price_Difference'] = df['Competitor Pricing'] - df['Price']

# Sort data chronologically by store and product to create a "Lag" feature
df = df.sort_values(by=['Store ID', 'Product ID', 'Date'])

# Create a feature for "Previous Day's Units Sold" for the exact same store and product
df['Lag_1_Units_Sold'] = df.groupby(['Store ID', 'Product ID'])['Units Sold'].shift(1)

# Drop the first day's rows since they won't have a "previous day" value (NaNs)
df = df.dropna()

# 3. Define Features (X) and Target (y)
target = 'Units Sold'

# Drop the target, the leaky 'Demand Forecast', and 'Date' (since we extracted month/day)
features = df.drop(columns=[target, 'Demand Forecast', 'Date'])

# Convert text columns (Categorical) into numbers using One-Hot Encoding
categorical_cols = ['Store ID', 'Product ID', 'Category', 'Region', 'Weather Condition', 'Seasonality']
X = pd.get_dummies(features, columns=categorical_cols, drop_first=True)
y = df[target]

# 4. Train-Test Split
# Splitting 80% of data for training, 20% for testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Initialize and Train the Model
print("Training Random Forest Regressor (this may take a moment)...")
rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

# 6. Evaluate the Model
y_pred = rf_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n--- Improved Model Evaluation ---")
print(f"Mean Absolute Error (MAE): {mae:.2f} units")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f} units")
print(f"R-squared (R2) Score: {r2:.4f}")

# 7. Visualizations
plt.figure(figsize=(15, 6))

# Plot 1: Feature Importances
plt.subplot(1, 2, 1)
importances = rf_model.feature_importances_
# Get the top 10 most important features
indices = np.argsort(importances)[-10:]
plt.barh(range(len(indices)), importances[indices], align='center', color='skyblue')
plt.yticks(range(len(indices)), [X.columns[i] for i in indices])
plt.title('Top 10 Feature Importances')
plt.xlabel('Relative Importance (Contribution to Model)')

# Plot 2: Fixed Seaborn Boxplot
plt.subplot(1, 2, 2)
# FIX APPLIED: Added hue='Category' and legend=False to remove the warning
sns.boxplot(x='Category', y='Units Sold', data=df, hue='Category', palette='Set2', legend=False)
plt.title('Units Sold Distribution by Category')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()