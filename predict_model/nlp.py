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
    
    df['VADER Sentiment'] = results
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
    
    df.loc[:, 'Transformers Sentiment'] = transformer_results
    return df

# Đọc dữ liệu
df = pd.read_csv("c:/doan/all_aposts.csv")

# Xử lý sơ bộ bằng VADER
df = analyze_vader(df, text_column='Title')

# Chọn bài viết "không rõ ràng" để phân tích bằng Transformers
unclear_posts = df[df['VADER Sentiment'] == "Unclear"]
if not unclear_posts.empty:
    unclear_posts = analyze_transformers(unclear_posts, text_column='Title')

# Gộp lại kết quả
df.update(unclear_posts)

# Xuất kết quả ra HTML để trực quan hóa
df.to_html("sentiment_analysis_transformers.html", index=False)
print("Phân tích cảm xúc hoàn tất. File kết quả: sentiment_analysis_transformers.html")
