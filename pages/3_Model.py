import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Page configuration
st.set_page_config(
    page_title="Model Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stMetric > label {
        font-size: 14px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Model Performance Dashboard")
st.markdown("---")

# Get metrics and feature importance
metrics = st.session_state.predictor.get_metrics()
feature_importance = st.session_state.predictor.get_feature_importance()

# Main dashboard layout
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    st.subheader("🎯 Model Performance Metrics")

    # Key metrics in a nice layout
    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.metric(
            label="Overall R²",
            value=f"{metrics['overall_r2']:.4f}",
            help="Coefficient of determination on the full dataset"
        )

    with metric_col2:
        st.metric(
            label="Cross-Validation R²",
            value=f"{metrics['cv_r2_mean']:.4f}",
            help="Mean R² score from cross-validation"
        )

    # Additional metrics if available
    if 'cv_r2_std' in metrics:
        st.metric(
            label="CV R² Std Dev",
            value=f"{metrics['cv_r2_std']:.4f}",
            help="Standard deviation of cross-validation R² scores"
        )

with col2:
    st.subheader("📈 Feature Importance")

    if feature_importance is not None and len(feature_importance) > 0:
        # Create feature importance chart
        if isinstance(feature_importance, dict):
            importance_df = pd.DataFrame(
                list(feature_importance.items()), 
                columns=['Feature', 'Importance']
            )
        else:
            importance_df = feature_importance

        importance_df = importance_df.sort_values('Importance', ascending=True)

        fig = px.bar(
            importance_df, 
            x='Importance', 
            y='Feature',
            orientation='h',
            title="Feature Importance Ranking",
            color='Importance',
            color_continuous_scale='viridis'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Feature importance not available for this model type")

with col3:
    st.subheader("ℹ️ Model Info")

    # Model configuration details
    st.markdown(f"**Target Variable:** {st.session_state.config['model']['target']}")
    st.markdown(f"**CV Method:** {st.session_state.config['model']['cv_method']}")
    st.markdown(f"**Features:** {len(st.session_state.config['model']['predictors'])}")
    st.markdown(f"**Data Points:** {len(st.session_state.data)}")

# Data overview section
st.markdown("---")
st.subheader("📋 Data Overview")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("**Dataset Summary**")
    st.dataframe(st.session_state.data.describe(), use_container_width=True)

with col2:
    st.markdown("**Target Variable Distribution**")
    fig = px.histogram(
        st.session_state.data, 
        x=st.session_state.config['model']['target'],
        nbins=30,
        title=f"Distribution of {st.session_state.config['model']['target']}"
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# Model performance visualization
if 'cv_scores' in metrics:
    st.markdown("---")
    st.subheader("🔄 Cross-Validation Performance")

    cv_scores = metrics['cv_scores']
    cv_df = pd.DataFrame({
        'Fold': range(1, len(cv_scores) + 1),
        'R² Score': cv_scores
    })

    fig = px.line(
        cv_df, 
        x='Fold', 
        y='R² Score',
        markers=True,
        title="Cross-Validation R² Scores by Fold"
    )
    fig.add_hline(
        y=metrics['cv_r2_mean'], 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Mean: {metrics['cv_r2_mean']:.4f}"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
