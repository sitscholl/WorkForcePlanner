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
    for i, row in schedule_df.iterrows():
        # Calculate bar position
        y_pos = len(schedule_df) - i - 1
        
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