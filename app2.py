import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import pandas as pd
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

class PostAnalyzer:
    def __init__(self):
        try:
            # Load data
            self.df = pd.read_csv("mockGeneratedData/raw/social_media_engagement.csv")
        except FileNotFoundError:
            st.error("Could not find social_media_engagement.csv in the current directory.")
            st.stop()

        # Initialize LLM
        self.setup_llm()

    def setup_llm(self):
        """Setup the Groq LLM."""
        try:
            load_dotenv()  # Load environment variables
            groq_api_key = os.getenv('GROQ_API_KEY')

            if not groq_api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables.")

            self.llm = ChatGroq(
                temperature=0.2,
                groq_api_key=os.getenv('GROQ_API_KEY'),
                model_name="mixtral-8x7b-32768"
            )
        except Exception as e:
            st.error(f"Error initializing Groq LLM: {str(e)}")
            st.stop()

    def get_available_posts(self, post_type=None):
        """Get list of available post IDs filtered by type if specified."""
        if post_type:
            filtered_df = self.df[self.df['post_type'] == post_type]
            return [f"{pid} ({row['topic']})" for pid, row in zip(filtered_df['post_id'], filtered_df.to_dict('records'))]
        return [f"{pid} ({row['topic']})" for pid, row in zip(self.df['post_id'], self.df.to_dict('records'))]

    def get_post_metrics(self, post_id, post_type):
        """Calculate post metrics and visualizations."""
        # Extract actual post_id from the display string
        actual_post_id = post_id.split(" (")[0]

        # Filter data
        type_stats = self.df[self.df['post_type'] == post_type]
        post = type_stats[type_stats['post_id'] == actual_post_id]

        if post.empty:
            return None, None, None

        post = post.iloc[0]

        # Calculate metrics
        numeric_columns = ['likes', 'comments', 'shares', 'saves', 'reach', 'engagement_rate']
        stats = type_stats[numeric_columns].agg(['mean', 'median', 'min', 'max']).to_dict()

        # Calculate performance vs average
        performance = {
            f"{col}_vs_avg": round((post[col] / stats[col]['mean'] - 1) * 100, 2)
            for col in numeric_columns
        }

        return post, stats, performance

    def create_performance_chart(self, performance_data):
        """Create performance visualization."""
        metrics = list(performance_data.keys())
        values = list(performance_data.values())

        # Clean metric names
        display_metrics = [m.replace('_vs_avg', '').replace('_', ' ').title() for m in metrics]

        # Create color scale
        colors = ['#e74c3c' if v < -20 else '#f39c12' if v < 0 else '#2ecc71' if v > 20 else '#27ae60' for v in values]

        fig = go.Figure(data=[
            go.Bar(
                x=display_metrics,
                y=values,
                marker_color=colors,
                text=[f"{v:+.1f}%" for v in values],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title={
                'text': "Performance vs Average",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Metrics",
            yaxis_title="% Difference from Average",
            template="plotly_white",
            height=400,
            margin=dict(t=50, l=0, r=0, b=0),
            yaxis=dict(
                gridcolor='rgba(0,0,0,0.1)',
                zerolinecolor='rgba(0,0,0,0.2)'
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    def generate_analysis(self, post, stats, performance):
        """Generate AI analysis of the post performance."""
        analysis_data = {
            'post_details': post.to_dict(),
            'type_statistics': stats,
            'performance': performance
        }

        prompt = PromptTemplate.from_template("""
            ### POST DATA:
            {data}

            ### INSTRUCTION:
            Analyze the performance of the post based on all available metrics in the dataset.
            Structure your analysis as follows:

            1. OVERALL PERFORMANCE:
            - Compare key metrics to average, median, min, and max values
            - Highlight standout metrics (both positive and negative)

            2. STRENGTHS:
            - List the top performing areas
            - Explain what might have contributed to success

            3. AREAS FOR IMPROVEMENT:
            - Identify underperforming metrics
            - Suggest specific actions for improvement

            4. CONTENT ANALYSIS:
            - Evaluate hashtag effectiveness
            - Assess topic relevance and timing
            - Analyze audio type impact

            5. ACTIONABLE RECOMMENDATIONS:
            - Provide 3-5 specific, data-driven recommendations
            - Include timing, content type, and engagement strategies

            Format the analysis using clear markdown headings and bullet points.

            ### ANALYSIS:
        """)

        try:
            chain = prompt | self.llm
            return chain.invoke({"data": str(analysis_data)}).content
        except Exception as e:
            st.error(f"Error generating analysis: {str(e)}")
            return None

def main():
    # Page config
    st.set_page_config(
        page_title="Social Media Post Analyzer",
        page_icon="📊",
        layout="wide"
    )

    # Styling
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton > button {
            width: 100%;
            background-color: #2ecc71 !important;
        }
        div[data-testid="stMarkdownContainer"] > h3 {
            padding-top: 1rem;
            padding-bottom: 0.5rem;
            color: #2c3e50;
        }
        .stAlert {
            background-color: #f8f9fa;
            border: none;
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Navigation bar
    menu = st.sidebar.radio("Navigation", ["Home", "Analyzer"])

    if menu == "Home":
        # Landing Page
        st.image("assets/Logo/team_logo_lumos.png", width=200)  # Placeholder for the team logo
        st.title("Welcome to Lumos Social Media Analyzer!")
        st.markdown(
            """
            Explore our AI-powered tool to analyze and optimize your social media performance.
            Use the navigation bar to access the Analyzer.
            """
        )

    elif menu == "Analyzer":
        # Main Analyzer Page
        st.title("📊 Social Media Post Analyzer")
        st.markdown("Analyze and optimize your social media performance with AI-powered insights")
        st.markdown("---")

        # Initialize analyzer
        analyzer = PostAnalyzer()

        # Input columns
        col1, col2 = st.columns(2)

        with col1:
            post_type = st.selectbox(
                "Select Content Type",
                options=['carousel', 'video', 'reel', 'static_image'],
                help="Choose the type of content you want to analyze"
            )

        with col2:
            available_posts = analyzer.get_available_posts(post_type)
            post_id = st.selectbox(
                "Select Post",
                options=available_posts,
                help="Choose a specific post to analyze"
            )

        # Analysis button
        if st.button("📈 Generate Analysis"):
            if post_id and post_type:
                with st.spinner("🤖 Analyzing post performance..."):
                    # Get post metrics
                    post, stats, performance = analyzer.get_post_metrics(post_id, post_type)

                    if post is not None:
                        # Create tabs
                        tab1, tab2 = st.tabs(["📊 Analysis", "📑 Raw Data"])

                        with tab1:
                            # Post details
                            st.markdown("### 📌 Post Details")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Topic", post['topic'])
                            with col2:
                                st.metric("Content Type", post['post_type'])
                            with col3:
                                st.metric("Audio Type", post['audio_type'])

                            st.markdown(f"**Hashtags:** `{post['hashtags_used']}`")

                            # Performance chart
                            st.markdown("### 📈 Performance Metrics")
                            analyzer.create_performance_chart(performance)

                            # AI Analysis
                            st.markdown("### 🤖 AI Analysis")
                            analysis = analyzer.generate_analysis(post, stats, performance)
                            if analysis:
                                st.markdown(analysis)

                        with tab2:
                            st.markdown("### 📊 Raw Metrics")
                            st.dataframe(
                                analyzer.df[analyzer.df['post_id'] == post_id.split(" (")[0]],
                                use_container_width=True
                            )
                    else:
                        st.error("Could not find post data.")

        # Footer
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col2:
            st.markdown("Built with ❤️ by Lumos")

if __name__ == "__main__":
    main()


    