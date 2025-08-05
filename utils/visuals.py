
import plotly.graph_objects as go
import pandas as pd

def create_enhanced_radar_chart(scores: dict) -> go.Figure:
    categories_list = list(scores.keys())
    values = [scores[cat][0] for cat in categories_list]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories_list,
        fill='toself',
        name='Your Score',
        line=dict(color='#667eea', width=3),
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))

    benchmark = [7] * len(categories_list)
    fig.add_trace(go.Scatterpolar(
        r=benchmark,
        theta=categories_list,
        name='Target Score',
        line=dict(color='#28a745', width=2, dash='dash'),
        fill=None
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickfont=dict(size=10),
                gridcolor='lightgray'
            ),
            angularaxis=dict(
                tickfont=dict(size=11)
            )
        ),
        showlegend=True,
        title=dict(
            text="Performance Radar",
            x=0.5,
            font=dict(size=16)
        ),
        font=dict(size=12),
        height=500
    )

    return fig

def create_score_history_chart(score_history: list) -> go.Figure:
    if not score_history:
        return None

    df = pd.DataFrame(score_history)

    fig = go.Figure()

    for column in df.columns:
        if column != 'timestamp':
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[column],
                mode='lines+markers',
                name=column,
                line=dict(width=2)
            ))

    fig.update_layout(
        title="Score Progress Over Time",
        xaxis_title="Submission Number",
        yaxis_title="Score",
        yaxis=dict(range=[0, 10]),
        hovermode='x unified',
        height=400
    )

    return fig
