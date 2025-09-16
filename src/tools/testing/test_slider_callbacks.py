#!/usr/bin/env python3
"""
Minimal Test Script for Slider → Chart Callbacks
Isolates the callback functionality to test if sliders update the chart
"""

import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Simple projection calculation for testing
def calculate_test_projections(income, housing, utilities, time_months):
    """Simple projection calculation for testing"""
    monthly_surplus = income - housing - utilities
    
    projections = {
        'net_worth': [i * monthly_surplus for i in range(1, time_months + 1)],
        'total_assets': [i * income * 0.8 for i in range(1, time_months + 1)],
        'total_liabilities': [max(0, 50000 - i * 500) for i in range(1, time_months + 1)],
        'cumulative_cash_flow': [i * monthly_surplus for i in range(1, time_months + 1)]
    }
    return projections

def create_test_chart(projections, time_months):
    """Create test chart"""
    months = list(range(1, time_months + 1))
    years = [month / 12 for month in months]
    
    fig = go.Figure()
    
    # Net Worth Trace
    fig.add_trace(go.Scatter(
        x=years,
        y=projections['net_worth'],
        mode='lines',
        name='Net Worth',
        line=dict(color='#28a745', width=3)
    ))
    
    # Total Assets Trace  
    fig.add_trace(go.Scatter(
        x=years,
        y=projections['total_assets'],
        mode='lines',
        name='Total Assets',
        line=dict(color='#007bff', width=2)
    ))
    
    # Total Liabilities Trace
    fig.add_trace(go.Scatter(
        x=years,
        y=projections['total_liabilities'],
        mode='lines',
        name='Total Liabilities',
        line=dict(color='#dc3545', width=2)
    ))
    
    # Cumulative Cash Flow Trace
    fig.add_trace(go.Scatter(
        x=years,
        y=projections['cumulative_cash_flow'],
        mode='lines',
        name='Cash Flow',
        line=dict(color='#20c997', width=2)
    ))
    
    fig.update_layout(
        title=f"Test Financial Projection ({time_months//12}-Year Outlook)",
        xaxis_title="Years",
        yaxis_title="Value (£)",
        height=500,
        showlegend=True
    )
    
    return fig

# App Layout
app.layout = dbc.Container([
    html.H1("🧪 Slider → Chart Callback Test", className="mb-4"),
    
    dbc.Alert([
        "Test the real-time connection between sliders and chart. Move any slider to see if the chart updates instantly."
    ], color="info", className="mb-4"),
    
    dbc.Row([
        # Control Panel (4 columns)
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🎛️ Test Control Panel"),
                dbc.CardBody([
                    # Income Slider
                    html.Label("Monthly Income:", className="fw-bold mb-2"),
                    dcc.Slider(
                        id="income-slider",
                        min=1000, max=8000, step=100, value=3500,
                        marks={1000: '£1K', 3000: '£3K', 5000: '£5K', 8000: '£8K'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Hr(),
                    
                    # Housing Slider
                    html.Label("Monthly Housing:", className="fw-bold mb-2 mt-3"),
                    dcc.Slider(
                        id="mortgage-slider",
                        min=500, max=3000, step=50, value=1200,
                        marks={500: '£500', 1500: '£1.5K', 3000: '£3K'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Hr(),
                    
                    # Utilities Slider
                    html.Label("Monthly Utilities:", className="fw-bold mb-2 mt-3"),
                    dcc.Slider(
                        id="utilities-slider",
                        min=50, max=400, step=10, value=150,
                        marks={50: '£50', 150: '£150', 300: '£300', 400: '£400'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Hr(),
                    
                    # Time Range Slider
                    html.Label("Time Range:", className="fw-bold mb-2 mt-3"),
                    dcc.Slider(
                        id="chart-time-range-slider",
                        min=12, max=360, step=12, value=60,
                        marks={12: '1Y', 60: '5Y', 120: '10Y', 360: '30Y'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ])
            ])
        ], width=4),
        
        # Chart (8 columns)
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📈 Test Financial Chart"),
                dbc.CardBody([
                    dcc.Graph(
                        id="enhanced-financial-projection-chart",
                        config={'displayModeBar': False},
                        style={"height": "500px"}
                    )
                ])
            ])
        ], width=8)
    ], className="mb-4"),
    
    # Status Display
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Test Status", className="card-title"),
                    html.Div([
                        html.Span("Chart Updates: ", className="fw-bold"),
                        html.Span(id="update-status", children="Not tested yet", className="text-muted")
                    ]),
                    html.Hr(),
                    html.Div([
                        html.Span("Last Update: ", className="fw-bold"),
                        html.Span(id="last-update-time", children="Never", className="text-muted")
                    ])
                ])
            ])
        ], width=12)
    ])
], fluid=True)

# TEST CALLBACK - This should update the chart when sliders move
@callback(
    [
        Output('enhanced-financial-projection-chart', 'figure'),
        Output('update-status', 'children'),
        Output('last-update-time', 'children')
    ],
    [
        Input('income-slider', 'value'),
        Input('mortgage-slider', 'value'),
        Input('utilities-slider', 'value'),
        Input('chart-time-range-slider', 'value')
    ]
)
def update_test_chart(income, housing, utilities, time_range):
    """
    TEST CALLBACK: Update chart when any slider moves
    """
    import datetime
    
    # Calculate projections
    projections = calculate_test_projections(income, housing, utilities, time_range)
    
    # Create chart
    chart_figure = create_test_chart(projections, time_range)
    
    # Status updates
    update_time = datetime.datetime.now().strftime("%H:%M:%S")
    status = f"✅ Working! Income: £{income}, Housing: £{housing}, Utilities: £{utilities}"
    
    return chart_figure, status, update_time

if __name__ == '__main__':
    print("🧪 Starting Slider → Chart Test App")
    print("📊 Test Instructions:")
    print("   1. Move any slider")
    print("   2. Check if chart updates immediately")
    print("   3. Check if status shows '✅ Working!'")
    print("🌐 App running at: http://127.0.0.1:8052/")
    print("=" * 50)
    
    app.run_server(debug=True, host='0.0.0.0', port=8052)
