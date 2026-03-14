import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download necessary NLTK data
nltk.download('vader_lexicon')

# Set global dark theme for plots
plt.style.use('dark_background')
sns.set_palette('Set2')

# Set dark mode friendly Streamlit config
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

st.sidebar.title("📊 Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat file (.txt)", type=['txt'])

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    try:
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

        if df.empty:
            st.warning("The uploaded file seems to be empty or not properly formatted.")
        else:
            user_list = df['User'].unique().tolist()
            if "Notifications" in user_list:
                user_list.remove("Notifications")
            user_list.sort()
            user_list.insert(0, "Overall")

            selected_user = st.sidebar.selectbox("Analyze chat for:", user_list)

            if st.sidebar.button("Show Analysis"):
                st.title('📈 Chat Statistics Overview')
                col1, col2, col3, col4 = st.columns(4)

                num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

                with col1:
                    st.metric("Total Messages", num_messages)
                with col2:
                    st.metric("Total Words", words)
                with col3:
                    st.metric("Media Shared", num_media_messages)
                with col4:
                    st.metric("Links Shared", num_links)

                st.divider()

                if selected_user == 'Overall':
                    st.header('👥 Most Active Users')
                    x, new_df = helper.most_busy_user(df)
                    col1, col2 = st.columns([2,1])

                    with col1:
                        fig, ax = plt.subplots(figsize=(8,5))
                        ax.bar(x.index, x.values, color='#4F8BF9', edgecolor='white')
                        ax.set_ylabel('Message Count', color='white')
                        plt.xticks(rotation=45, ha='right', color='white')
                        ax.yaxis.label.set_color('white')
                        ax.tick_params(axis='y', colors='white')
                        st.pyplot(fig)
                        plt.close(fig)

                    with col2:
                        st.dataframe(new_df)

                st.divider()

                st.header("📅 Monthly Timeline")
                timeline = helper.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots(figsize=(10,4))
                ax.plot(timeline['time'], timeline['Message'], marker='o', color='#4F8BF9')
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45, color='white')
                ax.yaxis.label.set_color('white')
                ax.tick_params(axis='y', colors='white')
                st.pyplot(fig)
                plt.close(fig)

                st.header('📆 Daily Timeline')
                daily_timeline = helper.daily_timeline(selected_user, df)
                fig, ax = plt.subplots(figsize=(10,4))
                ax.plot(daily_timeline['only_date'], daily_timeline['Message'], marker='o', color='#1E40AF')
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45, color='white')
                ax.yaxis.label.set_color('white')
                ax.tick_params(axis='y', colors='white')
                st.pyplot(fig)
                plt.close(fig)

                st.divider()

                st.header('🗺️ Activity Map')
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader('Most Active Day')
                    busy_day = helper.week_activity_map(selected_user, df)
                    fig, ax = plt.subplots(figsize=(8,4))
                    ax.bar(busy_day.index, busy_day.values, color='#6366F1', edgecolor='white')
                    ax.set_ylabel('Messages', color='white')
                    plt.xticks(rotation=45, color='white')
                    ax.tick_params(axis='y', colors='white')
                    st.pyplot(fig)
                    plt.close(fig)

                with col2:
                    st.subheader("Most Active Month")
                    busy_month = helper.month_activity_map(selected_user, df)
                    fig, ax = plt.subplots(figsize=(8,4))
                    ax.bar(busy_month.index, busy_month.values, color='#F97316', edgecolor='white')
                    ax.set_ylabel('Messages', color='white')
                    plt.xticks(rotation=45, color='white')
                    ax.tick_params(axis='y', colors='white')
                    st.pyplot(fig)
                    plt.close(fig)

                st.divider()

                st.header("🧭 Weekly Heatmap")
                user_heatmap = helper.activity_heatmap(selected_user, df)
                fig, ax = plt.subplots(figsize=(8,5))
                sns.heatmap(user_heatmap, ax=ax, cmap='coolwarm', linewidths=0.3, linecolor='white')
                st.pyplot(fig)
                plt.close(fig)

                st.divider()

                st.header("☁️ Word Cloud")
                df_wc = helper.create_wordcloud(selected_user, df)
                fig, ax = plt.subplots(figsize=(8,5))
                ax.imshow(df_wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
                plt.close(fig)

                st.divider()

                st.header("💬 Sentiment Analysis")
                filtered_df = df if selected_user == 'Overall' else df[df['User'] == selected_user]

                if not filtered_df.empty:
                    sentiments = SentimentIntensityAnalyzer()
                    filtered_df['po'] = [sentiments.polarity_scores(i)["pos"] for i in filtered_df['Message']]
                    filtered_df['ne'] = [sentiments.polarity_scores(i)["neg"] for i in filtered_df['Message']]
                    filtered_df['nu'] = [sentiments.polarity_scores(i)["neu"] for i in filtered_df['Message']]

                    def sentiment(d):
                        if d['po'] >= d['ne'] and d['po'] >= d['nu']:
                            return 1  # Positive
                        if d['ne'] >= d['po'] and d['ne'] >= d['nu']:
                            return -1  # Negative
                        return 0  # Neutral

                    filtered_df['value'] = filtered_df.apply(lambda row: sentiment(row), axis=1)

                    sentiment_counts = filtered_df['value'].value_counts().sort_index()
                    sentiment_labels = ['Negative', 'Neutral', 'Positive']

                    fig, ax = plt.subplots(figsize=(6,4))
                    ax.bar(sentiment_labels, [
                        sentiment_counts.get(-1, 0),
                        sentiment_counts.get(0, 0),
                        sentiment_counts.get(1, 0)
                    ], color=['#EF4444', '#9CA3AF', '#22C55E'], edgecolor='white')
                    ax.set_ylabel('Number of Messages', color='white')
                    ax.tick_params(axis='x', colors='white')
                    ax.tick_params(axis='y', colors='white')
                    st.pyplot(fig)
                    plt.close(fig)

                    if selected_user == 'Overall':
                        col1, col2, col3 = st.columns(3)
                        x = filtered_df['User'][filtered_df['value'] == 1].value_counts().head(10)
                        y = filtered_df['User'][filtered_df['value'] == -1].value_counts().head(10)
                        z = filtered_df['User'][filtered_df['value'] == 0].value_counts().head(10)

                        for col, title, data, color in zip(
                            [col1, col2, col3],
                            ["Most Positive Users", "Most Neutral Users", "Most Negative Users"],
                            [x, z, y],
                            ['#22C55E', '#9CA3AF', '#EF4444']
                        ):
                            with col:
                                st.markdown(f"<h4 style='text-align: center; color: white;'>{title}</h4>", unsafe_allow_html=True)
                                fig, ax = plt.subplots(figsize=(6,4))
                                ax.bar(data.index, data.values, color=color, edgecolor='white')
                                plt.xticks(rotation=45, color='white')
                                ax.tick_params(axis='y', colors='white')
                                st.pyplot(fig)
                                plt.close(fig)

                else:
                    st.warning("No messages available for sentiment analysis for the selected user.")

                st.divider()

                st.header("🔤 Most Common Words")
                most_common_df = helper.most_common_words(selected_user, df)
                fig, ax = plt.subplots(figsize=(8,5))
                ax.barh(most_common_df[0], most_common_df[1], color='#4F8BF9', edgecolor='white')
                ax.invert_yaxis()
                ax.tick_params(axis='x', colors='white')
                ax.tick_params(axis='y', colors='white')
                st.pyplot(fig)
                plt.close(fig)

                st.divider()

                st.header("😀 Emoji Analysis")
                emoji_df = helper.emoji_helper(selected_user, df)
                col1, col2 = st.columns(2)

                with col1:
                    st.dataframe(emoji_df)

                with col2:
                    if not emoji_df.empty:
                        fig, ax = plt.subplots()
                        ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f", shadow=True, startangle=90, textprops={'color':'white'})
                        ax.axis('equal')
                        st.pyplot(fig)
                        plt.close(fig)
                    else:
                        st.write("No emojis found in the conversation!")

    except UnicodeDecodeError:
        st.error("Error reading the file. Make sure it's a valid WhatsApp .txt chat export.")
