import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import streamlit as st
import matplotlib.pyplot as plt  # Thêm thư viện matplotlib

# Giao diện Streamlit
st.title("Phân tích dữ liệu và dự đoán tương tác bài viết")

# Upload dữ liệu
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    # Đọc dữ liệu từ file tải lên
    df = pd.read_csv(uploaded_file)

    # Hiển thị thông tin dữ liệu
    st.write("### Data Preview", df.head())

    # Xử lý dữ liệu
    df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
    df['Hour'] = df['Created'].dt.hour  # Thêm đặc trưng giờ trong ngày
    df['DayOfWeek'] = df['Created'].dt.dayofweek  # Thêm đặc trưng ngày trong tuần
    df['IsWeekend'] = df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)  # Xác định cuối tuần

    df = df.dropna(subset=['Score', 'Subreddit', 'Num Comments', 'Hour', 'DayOfWeek'])
    X = df[['Score', 'Subreddit', 'Hour', 'DayOfWeek', 'IsWeekend']]
    y = df['Num Comments']
    X = pd.get_dummies(X, columns=['Subreddit'], drop_first=True)

    # Chia dữ liệu thành tập huấn luyện và kiểm tra
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Chọn mô hình
    model_option = st.selectbox("Select Model", ["Random Forest", "Gradient Boosting", "XGBoost"])

    models = {
        'Random Forest': RandomForestRegressor(random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(random_state=42),
        'XGBoost': XGBRegressor(random_state=42, verbosity=0)
    }

    model = models[model_option]

    # Huấn luyện mô hình
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Đánh giá mô hình
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Hiển thị kết quả
    st.write(f"### Model: {model_option}")
    st.write(f"RMSE: {np.sqrt(mse):.2f}")
    st.write(f"R2 Score: {r2:.2f}")

    # Vẽ biểu đồ với matplotlib
    plt.figure(figsize=(10, 6))

    # Vẽ đường màu đỏ cho Actual Comments
    plt.plot(y_test.values, label="Lượng bình luận thực tế", color='red')

    # Vẽ đường màu xanh dương cho Predicted Comments
    plt.plot(y_pred, label="Lượng bình luận dự đoán", color='blue')

    # Thêm nhãn cho các trục và tiêu đề
    plt.xlabel("Chỉ số")
    plt.ylabel("Số lượng bình luận")
    plt.title(f"Lượng bình luận thực tế so với dự đoán {model_option}")

    # Hiển thị legend
    plt.legend()

    # Hiển thị biểu đồ trong Streamlit
    st.pyplot(plt)
