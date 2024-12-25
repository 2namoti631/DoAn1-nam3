import pandas as pd
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

# Bước 1: Phân tích cảm xúc sơ bộ bằng VADER
def analyze_vader(df, text_column):
    analyzer = SentimentIntensityAnalyzer()
    results = []

    for text in df[text_column]:
        score = analyzer.polarity_scores(text)
        compound = score['compound']
        if compound > 0.5:
            sentiment = "Positive"
        elif compound < -0.5:
            sentiment = "Negative"
        else:
            sentiment = "Unclear"
        results.append(sentiment)
    
    df.loc[:, 'VADER Sentiment'] = results
    return df

# Bước 2: Phân tích sâu hơn bằng Transformers
def analyze_transformers(df, text_column):
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    transformer_results = []

    for text in df[text_column]:
        try:
            result = classifier(text)[0]
            label = result['label']
            transformer_results.append(label)
        except Exception as e:
            transformer_results.append("Error")
    
    df.loc[:, 'Transformers Sentiment'] = transformer_results
    return df

# Streamlit: Giao diện người dùng
st.title("Phân Tích Cảm Xúc Bài Viết")
st.sidebar.header("Tùy chọn")

# Tải dữ liệu
uploaded_file = st.sidebar.file_uploader("Tải lên file CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Dữ liệu gốc:")
    st.dataframe(df)

    # Phân tích cảm xúc bằng VADER
    if st.sidebar.checkbox("Phân tích cảm xúc bằng VADER"):
        df = analyze_vader(df, text_column="Title")
        st.write("Kết quả phân tích cảm xúc bằng VADER:")
        st.dataframe(df[["Title", "VADER Sentiment"]])

    # Phân tích cảm xúc nâng cao bằng Transformers
    if st.sidebar.checkbox("Phân tích cảm xúc nâng cao bằng Transformers"):
        df = analyze_transformers(df, text_column="Title")
        st.write("Kết quả phân tích cảm xúc nâng cao bằng Transformers:")
        st.dataframe(df[["Title", "VADER Sentiment", "Transformers Sentiment"]])

    # Tải xuống kết quả
    st.download_button(
        label="Tải xuống kết quả",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="sentiment_analysis_results.csv",
        mime="text/csv",
    )
