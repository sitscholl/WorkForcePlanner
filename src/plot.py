import plotly.graph_objects as go
import pandas as pd
import datetime

def create_timeline_chart(schedule_df: pd.DataFrame, current_date: datetime.date = None) -> go.Figure:
    """
    Create an interactive timeline chart showing field work schedules

    Args:
        schedule_df: DataFrame with schedule information
        current_date: Current date to show as vertical line

    Returns:
        plotly.graph_objects.Figure: Timeline chart
    """
    if schedule_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No schedule data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig

    fig = go.Figure()

    # Create timeline bars
    for idx, (i, row) in enumerate(schedule_df.iterrows()):
        # Calculate bar position using sequential index, not DataFrame index
        y_pos = len(schedule_df) - idx - 1

        # Create hover text
        hover_text = (
            f"<b>{row['Field']}</b><br>"
            f"Start: {row['start_date']}<br>"
            f"End: {row['end_date']}<br>"
            f"Required Hours: {row['total_hours']}<br>"
            #f"Days Needed: {row['days_needed']}<br>"
            #f"Utilization: {row['worker_utilization']:.1f}%"
        )

        # Add timeline bar
        fig.add_trace(go.Scatter(
            x=[row['start_date'], row['end_date']],
            y=[y_pos, y_pos],
            mode='lines',
            line=dict(width=20),
            hovertemplate=hover_text + "<extra></extra>",
            name=row['Field'],
            showlegend=False
        ))

        # Add field name annotation
        fig.add_annotation(
            x=row['start_date'] + (row['end_date'] - row['start_date']) / 2,
            y=y_pos,
            text=row['Field'],
            showarrow=False,
            font=dict(color='white', size=10),
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='white',
            borderwidth=1
        )

    # Add current date line
    if current_date:
        fig.add_shape(
            type="line",
            x0=current_date,
            y0=0,
            x1=current_date,
            y1=len(schedule_df),
            line=dict(
                color="red",
                width=2,
                dash="dash",
            )
        )

        # Add "Today" annotation
        fig.add_annotation(
            x=current_date,
            y=len(schedule_df),
            text="Today",
            showarrow=False,
            yshift=10
        )

    # Update layout
    fig.update_layout(
        title="Field Work Timeline",
        xaxis_title="Date",
        yaxis_title="Fields",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(schedule_df))),
            ticktext=schedule_df['Field'].tolist()[::-1],  # Reverse order
            showgrid=True
        ),
        xaxis=dict(showgrid=True),
        height=max(400, len(schedule_df) * 50),
        hovermode='closest',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig

def create_predictions_scatterplot(
        df, 
        obs_col='Observed', 
        pred_col='Predicted', 
        field_col='Field', 
        year_col='Year'
    ):
    """
    Plots observed vs predicted values using Plotly, with a 1:1 reference line.
    Hovering over points shows Field and Year.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing the data.
        obs_col (str): Name of the observed values column.
        pred_col (str): Name of the predicted values column.
        field_col (str): Name of the field column.
        year_col (str): Name of the year column.
    """
    # Scatter plot
    scatter = go.Scatter(
        x=df[obs_col],
        y=df[pred_col],
        mode='markers',
        marker=dict(size=8, color='blue', opacity=0.7),
        text=[f"Field: {f}<br>Year: {y}" for f, y in zip(df[field_col], df[year_col])],
        hovertemplate=(
            f"{obs_col}: %{{x}}<br>"
            f"{pred_col}: %{{y}}<br>"
            "%{text}<extra></extra>"
        ),
        name='Data'
    )
    
    # 1:1 line
    min_val = min(df[obs_col].min(), df[pred_col].min())
    max_val = max(df[obs_col].max(), df[pred_col].max())
    line = go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        line=dict(color='red', dash='dash'),
        name='1:1 Line'
    )
    
    layout = go.Layout(
        title='Observed vs Predicted',
        xaxis=dict(title=obs_col),
        yaxis=dict(title=pred_col),
        showlegend=True
    )
    
    fig = go.Figure(data=[scatter, line], layout=layout)
    return fig