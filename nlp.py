import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

# Bước 1: Phân tích cảm xúc sơ bộ bằng VADER
def analyze_vader(df, text_column):
    analyzer = SentimentIntensityAnalyzer()
    results = []

    for text in df[text_column]:
        score = analyzer.polarity_scores(text)
        compound = score['compound']  # Điểm tổng hợp cảm xúc
        if compound > 0.5:
            sentiment = "Positive"
        elif compound < -0.5:
            sentiment = "Negative"
        else:
            sentiment = "Unclear"  # Cần xử lý sâu hơn bằng Transformers
        results.append(sentiment)
    
    df.loc[:, 'VADER Sentiment'] = results  # Sử dụng loc để tránh cảnh báo
    return df

# Bước 2: Phân tích sâu hơn bằng Transformers
def analyze_transformers(df, text_column):
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    transformer_results = []

    for text in df[text_column]:
        try:
            result = classifier(text)[0]
            label = result['label']  # Nhãn cảm xúc (POSITIVE/NEGATIVE)
            transformer_results.append(label)
        except Exception as e:
            transformer_results.append("Error")  # Xử lý lỗi nếu có
    
    df.loc[:, 'Transformers Sentiment'] = transformer_results  # Sử dụng loc để tránh cảnh báo
    return df

# Đọc dữ liệu
df = pd.read_csv("c:/doan/all_aposts.csv")

# Xử lý sơ bộ bằng VADER
df = analyze_vader(df, text_column='Title')

# Chọn bài viết "không rõ ràng" để phân tích bằng Transformers
unclear_posts = df[df['VADER Sentiment'] == "Unclear"].copy()  # Thêm copy() để đảm bảo không cảnh báo
if not unclear_posts.empty:
    unclear_posts = analyze_transformers(unclear_posts, text_column='Title')

# Gộp lại kết quả
df.update(unclear_posts)

# Tùy chỉnh giao diện bảng bằng pandas Styler
def highlight_sentiment(row):
    """Hàm tùy chỉnh màu sắc dựa trên cảm xúc"""
    if row['VADER Sentiment'] == "Positive" or row.get('Transformers Sentiment', '') == "POSITIVE":
        return ['background-color: #d4edda'] * len(row)  # Màu xanh lá
    elif row['VADER Sentiment'] == "Negative" or row.get('Transformers Sentiment', '') == "NEGATIVE":
        return ['background-color: #f8d7da'] * len(row)  # Màu đỏ
    else:
        return ['background-color: #fff3cd'] * len(row)  # Màu vàng nhạt

# Áp dụng style
styled_df = df.style.apply(highlight_sentiment, axis=1).set_table_styles(
    [
        {"selector": "thead", "props": [("background-color", "#343a40"), ("color", "white"), ("font-weight", "bold")]},
        {"selector": "tbody tr:hover", "props": [("background-color", "#f1f1f1")]}
    ]
).set_properties(**{"text-align": "center"})

# Xuất ra file HTML với giao diện đẹp hơn
styled_df.to_html("sentiment_analysis_styled.html", index=False)
print("Phân tích cảm xúc hoàn tất. File kết quả: sentiment_analysis_styled.html")
