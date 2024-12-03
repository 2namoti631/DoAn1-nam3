import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import plotly.graph_objs as go
import plotly.io as pio

# Đọc dữ liệu từ file CSV
df = pd.read_csv('c:/doan/all_aposts.csv')

# Xử lý dữ liệu
df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
df['Created_str'] = df['Created'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(x) else '')

# Chuẩn bị dữ liệu đầu vào và đầu ra
X = df[['Score', 'Subreddit', 'Created_str']]
y = df['Num Comments']

# Chuyển đổi các cột văn bản về dạng số (One-Hot Encoding)
X = pd.get_dummies(X, columns=['Subreddit', 'Created_str'], drop_first=True)

# Chia dữ liệu thành tập huấn luyện và kiểm tra
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Khởi tạo mô hình và grid search
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2],
    'max_features': ['auto', 'sqrt']
}
rf = RandomForestRegressor(random_state=42)
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, scoring='neg_mean_squared_error', verbose=2, n_jobs=-1)
grid_search.fit(X_train, y_train)

# Lấy ra mô hình tốt nhất từ GridSearchCV và dự đoán
best_rf = grid_search.best_estimator_
y_pred = best_rf.predict(X_test)

# Tính toán RMSE
mse_optimized = mean_squared_error(y_test, y_pred)
rmse_optimized = np.sqrt(mse_optimized)

# Tạo biểu đồ Plotly
trace_actual = go.Scatter(x=list(range(len(y_test))), y=y_test, mode='lines', name='Actual Comments')
trace_pred = go.Scatter(x=list(range(len(y_pred))), y=y_pred, mode='lines', name='Predicted Comments')
layout = go.Layout(title=f"Prediction of Information Spread (RMSE: {rmse_optimized:.2f})",
                   xaxis=dict(title='Post Index'),
                   yaxis=dict(title='Number of Comments'))
fig = go.Figure(data=[trace_actual, trace_pred], layout=layout)

# Lưu biểu đồ dưới dạng file HTML
pio.write_html(fig, file='prediction_results.html', auto_open=True)
