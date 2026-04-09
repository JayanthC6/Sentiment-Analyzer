import streamlit as st
import pandas as pd
from transformers import pipeline

# 1. Page Configuration
st.set_page_config(page_title="Sentiment Analyzer", page_icon="🧠")
st.title("Text Sentiment Analysis")
st.write("Enter a sentence below to determine if the sentiment is Positive, Negative, or Neutral.")

# 2. Load the Model 
@st.cache_resource
def load_sentiment_model():
    return pipeline(
        task="sentiment-analysis", 
        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
        top_k=None # CRITICAL ADDITION: This tells the model to return scores for ALL categories, not just the top one
    )

analyzer = load_sentiment_model()

# 3. User Input (Added a character limit to prevent abuse/crashing)
user_text = st.text_area("Your text:", placeholder="Type your sentence or review here...", max_chars=1000)

# 4. Execution & Prediction
if st.button("Analyze Sentiment"):
    
    # EDGE CASE HANDLING: Check for empty strings or gibberish
    if not user_text.strip():
        st.warning("⚠️ Please enter some text before analyzing.")
    elif len(user_text.split()) < 3:
        st.warning("⚠️ Please enter a slightly longer sentence (at least 3 words) for a meaningful analysis.")
    else:
        with st.spinner("Analyzing..."):
            # Get the results
            results = analyzer(user_text)[0]
            
            # Find the primary prediction
            top_prediction = max(results, key=lambda x: x['score'])
            sentiment = top_prediction['label'].capitalize()
            confidence = top_prediction['score'] * 100
            
            # Display primary result
            st.success(f"**Predicted Sentiment:** {sentiment} ({confidence:.1f}% Confidence)")
            
            st.divider() # Adds a clean visual break
            
            # VISUALIZING PROBABILITY
            st.subheader("🧠 Model Confidence Breakdown")
            st.write("Machine learning models deal in probabilities. Here is exactly how the AI evaluated your text:")
            
            # Format the output into a Pandas DataFrame for Streamlit's native charting
            chart_data = pd.DataFrame({
                "Sentiment": [res['label'].capitalize() for res in results],
                "Confidence Score": [res['score'] for res in results]
            }).set_index("Sentiment")
            
            # Display a clean bar chart
            st.bar_chart(chart_data)