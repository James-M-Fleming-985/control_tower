#!/usr/bin/env python3
"""
SLIDER → CHART TEST SCRIPT
Simple test to isolate slider callback functionality

This minimal script tests ONLY:
1. Control panel sliders (16 inputs)
2. Financial chart updates  
3. Real-time responsiveness

No modal, no data input, no complex callbacks - just pure slider → chart testing
"""

import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# Simple projection calculation for testing
def calculate_test_projections(income, housing, utilities, transport, food, savings, investments, months):
    """Simple financial projections for testing slider responsiveness"""
    
    monthly_surplus = income - (housing + utilities + transport + food)
    monthly_total_savings = savings + investments
    
    # Create test data that changes based on slider values
    projections = {
        'net_worth': [i * monthly_surplus for i in range(1, months + 1)],
        'total_assets': [i * (monthly_surplus + monthly_total_savings) for i in range(1, months + 1)],
        'total_liabilities': [max(0, 50000 - i * 200) for i in range(1, months + 1)],
        'cumulative_cash_flow': [i * monthly_surplus for i in range(1, months + 1)]
    }
    return projections

def create_test_chart(projections, time_range_months):
    """Create test chart that should update when sliders change"""
    
    years = [month / 12 for month in range(1, time_range_months + 1)]
    
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
        title=f"Test Chart - {time_range_months//12} Year Projection",
        xaxis_title="Years",
        yaxis_title="Value (£)",
        height=500,
        hovermode='x unified'
    )
    
    return fig

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Simple layout with sliders and chart
app.layout = html.Div([
    html.H1("🧪 SLIDER → CHART TEST", className="text-center mb-4"),
    
    dbc.Alert("Move sliders and watch chart update in real-time", color="info", className="mb-4"),
    
    dbc.Row([
        # Sliders Column
        dbc.Col([
            html.H4("Control Panel Sliders"),
            
            # Income Slider
            html.Div([
                html.Label("Monthly Income:", className="fw-bold"),
                dcc.Slider(
                    id="income-slider",
                    min=1000, max=8000, step=100, value=3500,
                    marks={1000: '£1K', 3000: '£3K', 5000: '£5K', 8000: '£8K'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id="income-display", className="text-center mt-2")
            ], className="mb-4"),
            
            # Housing Slider
            html.Div([
                html.Label("Monthly Housing:", className="fw-bold"),
                dcc.Slider(
                    id="mortgage-slider",
                    min=500, max=3000, step=50, value=1200,
                    marks={500: '£500', 1500: '£1.5K', 3000: '£3K'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id="housing-display", className="text-center mt-2")
            ], className="mb-4"),
            
            # Utilities Slider
            html.Div([
                html.Label("Monthly Utilities:", className="fw-bold"),
                dcc.Slider(
                    id="utilities-slider",
                    min=50, max=400, step=10, value=150,
                    marks={50: '£50', 150: '£150', 300: '£300', 400: '£400'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id="utilities-display", className="text-center mt-2")
            ], className="mb-4"),
            
            # Transport Slider
            html.Div([
                html.Label("Monthly Transport:", className="fw-bold"),
                dcc.Slider(
                    id="transport-slider",
                    min=50, max=800, step=25, value=200,
                    marks={50: '£50', 200: '£200', 500: '£500', 800: '£800'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id="transport-display", className="text-center mt-2")
            ], className="mb-4"),
            
            # Food Slider
            html.Div([
                html.Label("Monthly Food:", className="fw-bold"),
                dcc.Slider(
                    id="food-slider",
                    min=100, max=800, step=25, value=300,
                    marks={100: '£100', 300: '£300', 500: '£500', 800: '£800'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id="food-display", className="text-center mt-2")
            ], className="mb-4"),
            
            # Savings Slider
            html.Div([
                html.Label("Monthly Savings:", className="fw-bold"),
                dcc.Slider(
                    id="total-savings-slider",
                    min=0, max=2000, step=50, value=500,
                    marks={0: '£0', 500: '£500', 1000: '£1K', 2000: '£2K'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id="savings-display", className="text-center mt-2")
            ], className="mb-4"),
            
            # Investments Slider
            html.Div([
                html.Label("Monthly Investments:", className="fw-bold"),
                dcc.Slider(
                    id="total-investments-slider",
                    min=0, max=2000, step=50, value=300,
                    marks={0: '£0', 500: '£500', 1000: '£1K', 2000: '£2K'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id="investments-display", className="text-center mt-2")
            ], className="mb-4"),
            
            # Time Range Slider
            html.Div([
                html.Label("Time Range:", className="fw-bold"),
                dcc.Slider(
                    id="chart-time-range-slider",
                    min=6, max=360, step=6, value=60,
                    marks={6: '6M', 12: '1Y', 60: '5Y', 120: '10Y', 360: '30Y'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id="timerange-display", className="text-center mt-2")
            ], className="mb-4")
            
        ], width=4),
        
        # Chart Column
        dbc.Col([
            html.H4("Financial Chart"),
            dcc.Graph(
                id="test-financial-chart",
                config={'displayModeBar': False},
                style={"height": "600px"}
            ),
            
            # Debug Info
            html.Div([
                html.H5("Debug Info:", className="mt-4"),
                html.Div(id="debug-info", className="bg-light p-3 rounded")
            ])
        ], width=8)
    ])
], className="container-fluid p-4")

# Main callback: Sliders → Chart Update
@callback(
    [
        Output('test-financial-chart', 'figure'),
        Output('income-display', 'children'),
        Output('housing-display', 'children'),
        Output('utilities-display', 'children'),
        Output('transport-display', 'children'),
        Output('food-display', 'children'),
        Output('savings-display', 'children'),
        Output('investments-display', 'children'),
        Output('timerange-display', 'children'),
        Output('debug-info', 'children')
    ],
    [
        Input('income-slider', 'value'),
        Input('mortgage-slider', 'value'),
        Input('utilities-slider', 'value'),
        Input('transport-slider', 'value'),
        Input('food-slider', 'value'),
        Input('total-savings-slider', 'value'),
        Input('total-investments-slider', 'value'),
        Input('chart-time-range-slider', 'value')
    ]
)
def update_test_chart(income, housing, utilities, transport, food, savings, investments, time_range):
    """
    🎯 TEST CALLBACK: All sliders → Chart update
    
    This should fire every time ANY slider moves and update the chart immediately
    """
    
    # Calculate projections based on slider values
    projections = calculate_test_projections(
        income, housing, utilities, transport, food, savings, investments, time_range
    )
    
    # Create updated chart
    chart_figure = create_test_chart(projections, time_range)
    
    # Calculate net cash flow for debug
    monthly_surplus = income - (housing + utilities + transport + food)
    
    # Debug information
    debug_info = [
        html.P(f"📊 Callback triggered successfully!", className="text-success fw-bold"),
        html.P(f"💰 Monthly Income: £{income:,}"),
        html.P(f"🏠 Monthly Expenses: £{housing + utilities + transport + food:,}"),
        html.P(f"💵 Monthly Surplus: £{monthly_surplus:,}"),
        html.P(f"💾 Monthly Savings+Investments: £{savings + investments:,}"),
        html.P(f"📅 Time Range: {time_range} months ({time_range//12} years)"),
        html.P(f"🔄 Net Worth at end: £{projections['net_worth'][-1]:,.0f}", className="text-primary fw-bold")
    ]
    
    return (
        chart_figure,
        f"£{income:,}",
        f"£{housing:,}",
        f"£{utilities:,}",
        f"£{transport:,}",
        f"£{food:,}",
        f"£{savings:,}",
        f"£{investments:,}",
        f"{time_range} months",
        debug_info
    )

if __name__ == '__main__':
    print("🧪 SLIDER → CHART TEST SCRIPT")
    print("=" * 50)
    print("✅ Starting test app...")
    print("🎯 Test: Move sliders and watch chart update")
    print("🌐 Opening: http://127.0.0.1:8051/")
    print("=" * 50)
    
    app.run_server(debug=True, port=8051, host='0.0.0.0')
