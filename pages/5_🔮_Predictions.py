"""
Page 5: Climate Trend Prediction
Displays Random Forest Regressor forecasts, model accuracy metrics (R2, MAE, RMSE), and Actual vs Predicted comparison curves.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.mongodb import get_db

st.set_page_config(page_title="Climate Predictions | EarthScape", page_icon="🔮", layout="wide")

if not st.session_state.get('authenticated', False):
    st.warning("Please sign in from the main portal.")
    st.stop()

db = get_db()
if db is None:
    st.error("Cannot connect to MongoDB.")
    st.stop()

st.title("🔮 Predictive Climate Event Forecasting")
st.markdown("Forecasting macro-level weather event volumes using a **Scikit-learn Random Forest Regressor** trained on historical lag features.")

# Fetch Predictions & Model Metrics from MongoDB
pred_doc = db['predictions'].find_one() or {}
metrics = pred_doc.get('metrics', {})
series = pred_doc.get('series', [])

if not series:
    st.warning("No prediction records found in database. Run the pipeline first.")
    st.stop()

pred_df = pd.DataFrame(series)
pred_df['DateLabel'] = pred_df['Year'].astype(str) + '-' + pred_df['Month'].astype(str).str.zfill(2)

# Metric Scorecards
st.markdown("### 🏆 Model Performance Scorecards")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Model Architecture", "Random Forest Regressor")
with c2:
    st.metric("Coefficient of Determination (R²)", f"{metrics.get('R2', 0.0):.4f}")
with c3:
    st.metric("Mean Absolute Error (MAE)", f"{metrics.get('MAE', 0.0):,.2f}")
with c4:
    st.metric("Root Mean Squared Error (RMSE)", f"{metrics.get('RMSE', 0.0):,.2f}")

st.markdown("---")

# Main Forecast Chart: Actual vs Predicted
st.subheader("📈 Historical vs Predicted Weather Event Trajectory")

fig_pred = go.Figure()

# Actual historical line
fig_pred.add_trace(go.Scatter(
    x=pred_df['DateLabel'],
    y=pred_df['EventCount'],
    mode='lines+markers',
    name='Actual Events',
    line=dict(color='#0284C7', width=2.5),
    marker=dict(size=6)
))

# Predicted line
fig_pred.add_trace(go.Scatter(
    x=pred_df['DateLabel'],
    y=pred_df['PredictedCount'],
    mode='lines+markers',
    name='Predicted Events (RF)',
    line=dict(color='#DC2626', width=2, dash='dash'),
    marker=dict(size=6, symbol='x')
))

# Split line for test period if available
if 'IsTestPeriod' in pred_df.columns:
    test_start = pred_df[pred_df['IsTestPeriod'] == True]['DateLabel'].iloc[0] if (pred_df['IsTestPeriod'] == True).any() else None
    if test_start:
        fig_pred.add_vline(x=test_start, line_dash="dot", line_color="green", annotation_text="Test Period Evaluation Boundary")

fig_pred.update_layout(
    height=500,
    xaxis_title="Time Horizon (Year-Month)",
    yaxis_title="Monthly Event Volume",
    legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)'),
    template='plotly_white'
)
st.plotly_chart(fig_pred, use_container_width=True)

# Comparison Data Table
st.markdown("---")
st.subheader("📊 Model Output & Residuals Table")
pred_df['Residual_Error'] = pred_df['EventCount'] - pred_df['PredictedCount']
pred_df['Error_Pct'] = (abs(pred_df['Residual_Error']) / pred_df['EventCount']) * 100

st.dataframe(
    pred_df[['Year', 'Month', 'DateLabel', 'EventCount', 'PredictedCount', 'Residual_Error', 'Error_Pct', 'IsTestPeriod']],
    use_container_width=True
)
