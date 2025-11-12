import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import requests
from datetime import datetime, timedelta
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Interactive Data Dashboard"

# Color scheme for accessibility (WCAG AA compliant)
COLORS = {
    'background': '#0f172a',
    'surface': '#1e293b',
    'primary': '#3b82f6',
    'secondary': '#8b5cf6',
    'accent': '#10b981',
    'text': '#f1f5f9',
    'text_secondary': '#94a3b8'
}

# API endpoints (free tier, no API key required for demo)
CRYPTO_API = "https://api.coingecko.com/api/v3"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

# ==================== DATA FETCHING FUNCTIONS ====================

def fetch_crypto_data(coins=['bitcoin', 'ethereum', 'cardano'], days=7):
    """Fetch cryptocurrency price data"""
    data = []
    for coin in coins:
        try:
            url = f"{CRYPTO_API}/coins/{coin}/market_chart"
            params = {'vs_currency': 'usd', 'days': days}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                prices = response.json()['prices']
                df = pd.DataFrame(prices, columns=['timestamp', 'price'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['coin'] = coin.capitalize()
                data.append(df)
        except Exception as e:
            print(f"Error fetching {coin}: {e}")
    
    return pd.concat(data) if data else pd.DataFrame()

def get_coordinates(location_name):
    """Get coordinates from location name using geocoding"""
    try:
        # Using Open-Meteo's geocoding API
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {'name': location_name, 'count': 1, 'language': 'en', 'format': 'json'}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                return result['latitude'], result['longitude'], result['name']
    except Exception as e:
        print(f"Error geocoding location: {e}")
    
    # Default to New York if geocoding fails
    return 40.7128, -74.0060, "New York"

def fetch_weather_data(location_name="New York", days=7):
    """Fetch weather forecast data"""
    latitude, longitude, resolved_name = get_coordinates(location_name)
    
    try:
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation',
            'forecast_days': days,
            'timezone': 'auto'
        }
        response = requests.get(WEATHER_API, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()['hourly']
            df = pd.DataFrame({
                'time': pd.to_datetime(data['time']),
                'temperature': data['temperature_2m'],
                'humidity': data['relative_humidity_2m'],
                'precipitation': data['precipitation']
            })
            df['location'] = resolved_name
            return df
    except Exception as e:
        print(f"Error fetching weather: {e}")
    
    return pd.DataFrame()

def generate_mock_stock_data(symbols=['AAPL', 'GOOGL', 'MSFT'], days=30):
    """Generate mock stock data (replace with real API in production)"""
    import numpy as np
    
    data = []
    base_prices = {'AAPL': 180, 'GOOGL': 140, 'MSFT': 380}
    
    for symbol in symbols:
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base = base_prices.get(symbol, 100)
        prices = base + np.cumsum(np.random.randn(days) * 5)
        
        df = pd.DataFrame({
            'date': dates,
            'price': prices,
            'symbol': symbol
        })
        data.append(df)
    
    return pd.concat(data)

# ==================== LAYOUT ====================

app.layout = html.Div([
    # Header
    html.Header([
        html.H1("📊 Interactive Data Dashboard", 
                className="dashboard-title",
                **{'aria-label': 'Interactive Data Dashboard'}),
        html.P("Real-time Crypto, Weather & Stock Data", 
               className="dashboard-subtitle")
    ], className="header"),
    
    # Control Panel
    html.Div([
        html.Div([
            html.Label("Select Data Type:", htmlFor="data-type-selector"),
            dcc.Dropdown(
                id='data-type-selector',
                options=[
                    {'label': '₿ Cryptocurrency Prices', 'value': 'crypto'},
                    {'label': '🌤️ Weather Forecast', 'value': 'weather'},
                    {'label': '📈 Stock Prices', 'value': 'stocks'}
                ],
                value='crypto',
                clearable=False,
                className="dropdown"
            )
        ], className="control-item"),
        
        html.Div([
            html.Label("Time Range (Days):", htmlFor="time-range-slider"),
            dcc.Slider(
                id='time-range-slider',
                min=1,
                max=30,
                value=7,
                marks={1: '1d', 7: '7d', 14: '14d', 30: '30d'},
                tooltip={"placement": "bottom", "always_visible": True},
                className="slider"
            )
        ], className="control-item"),
        
        html.Div([
            html.Label("Weather Location:", htmlFor="location-input"),
            dcc.Input(
                id='location-input',
                type='text',
                placeholder='e.g., New York, London, Tokyo',
                value='New York',
                className="location-input"
            )
        ], id='location-container', className="control-item", style={'display': 'none'}),
        
        html.Button("🔄 Refresh Data", 
                   id='refresh-button', 
                   n_clicks=0,
                   className="refresh-button",
                   **{'aria-label': 'Refresh dashboard data'})
    ], className="control-panel"),
    
    # Main Content Area
    html.Div([
        # Stats Cards
        html.Div(id='stats-cards', className="stats-container"),
        
        # Main Chart
        html.Div([
            dcc.Loading(
                id="loading-main-chart",
                type="circle",
                children=[
                    dcc.Graph(id='main-chart', 
                             config={'displayModeBar': True, 'displaylogo': False},
                             className="chart")
                ]
            )
        ], className="chart-container"),
        
        # Secondary Charts
        html.Div([
            html.Div([
                dcc.Loading(
                    id="loading-secondary-1",
                    type="circle",
                    children=[
                        dcc.Graph(id='secondary-chart-1', 
                                 config={'displayModeBar': False},
                                 className="chart")
                    ]
                )
            ], className="chart-half"),
            
            html.Div([
                dcc.Loading(
                    id="loading-secondary-2",
                    type="circle",
                    children=[
                        dcc.Graph(id='secondary-chart-2', 
                                 config={'displayModeBar': False},
                                 className="chart")
                    ]
                )
            ], className="chart-half")
        ], className="secondary-charts"),
    ], className="content"),
    
    # Footer
    html.Footer([
        html.P("Last updated: ", style={'display': 'inline'}),
        html.Span(id='last-update', children=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        html.P(" | Data sources: CoinGecko, Open-Meteo", 
               style={'marginLeft': '20px', 'display': 'inline'})
    ], className="footer"),
    
    # Interval component for auto-refresh (every 5 minutes)
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # 5 minutes in milliseconds
        n_intervals=0
    )
    
], className="dashboard-container")

# ==================== CALLBACKS ====================

@app.callback(
    Output('location-container', 'style'),
    Input('data-type-selector', 'value')
)
def toggle_location_input(data_type):
    """Show location input only when weather is selected"""
    if data_type == 'weather':
        return {'display': 'block'}
    return {'display': 'none'}

@app.callback(
    [Output('stats-cards', 'children'),
     Output('main-chart', 'figure'),
     Output('secondary-chart-1', 'figure'),
     Output('secondary-chart-2', 'figure'),
     Output('last-update', 'children')],
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals'),
     Input('data-type-selector', 'value'),
     Input('time-range-slider', 'value'),
     Input('location-input', 'value')]
)
def update_dashboard(n_clicks, n_intervals, data_type, time_range, location):
    """Main callback to update all dashboard components"""
    
    if data_type == 'crypto':
        return update_crypto_dashboard(time_range)
    elif data_type == 'weather':
        return update_weather_dashboard(time_range, location or "New York")
    else:
        return update_stocks_dashboard(time_range)

def update_crypto_dashboard(days):
    """Update dashboard with crypto data"""
    df = fetch_crypto_data(days=days)
    
    if df.empty:
        return create_empty_dashboard("No crypto data available")
    
    # Stats Cards
    latest_prices = df.groupby('coin')['price'].last()
    cards = []
    colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['accent']]
    
    for i, (coin, price) in enumerate(latest_prices.items()):
        price_change = df[df['coin'] == coin]['price'].pct_change().iloc[-1] * 100
        cards.append(
            html.Div([
                html.H3(coin, className="card-title"),
                html.P(f"${price:,.2f}", className="card-value"),
                html.P(f"{price_change:+.2f}%", 
                      className="card-change positive" if price_change > 0 else "card-change negative")
            ], className="stat-card", style={'borderColor': colors_list[i % 3]})
        )
    
    # Main Chart - Line chart
    fig_main = px.line(df, x='timestamp', y='price', color='coin',
                       title=f'Cryptocurrency Prices - Last {days} Days',
                       labels={'price': 'Price (USD)', 'timestamp': 'Date'})
    fig_main = style_figure(fig_main)
    
    # Secondary Chart 1 - Area chart
    fig_sec1 = go.Figure()
    for coin in df['coin'].unique():
        coin_data = df[df['coin'] == coin]
        fig_sec1.add_trace(go.Scatter(
            x=coin_data['timestamp'], 
            y=coin_data['price'],
            name=coin,
            fill='tonexty',
            mode='lines'
        ))
    fig_sec1.update_layout(title='Price Distribution')
    fig_sec1 = style_figure(fig_sec1)
    
    # Secondary Chart 2 - Bar chart (daily change)
    latest_data = df.groupby('coin').last().reset_index()
    latest_data['change'] = df.groupby('coin')['price'].apply(
        lambda x: ((x.iloc[-1] - x.iloc[0]) / x.iloc[0] * 100)
    ).values
    
    fig_sec2 = px.bar(latest_data, x='coin', y='change',
                      title='Total Change (%)',
                      labels={'change': 'Change (%)', 'coin': 'Cryptocurrency'})
    fig_sec2 = style_figure(fig_sec2)
    
    return cards, fig_main, fig_sec1, fig_sec2, datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def update_weather_dashboard(days, location):
    """Update dashboard with weather data"""
    df = fetch_weather_data(location_name=location, days=days)
    
    if df.empty:
        return create_empty_dashboard("No weather data available")
    
    location_name = df['location'].iloc[0] if 'location' in df.columns else location
    
    # Stats Cards
    avg_temp = df['temperature'].mean()
    avg_humidity = df['humidity'].mean()
    total_precip = df['precipitation'].sum()
    
    cards = [
        html.Div([
            html.H3("Avg Temperature", className="card-title"),
            html.P(f"{avg_temp:.1f}°C", className="card-value"),
            html.P(location_name, className="card-subtitle")
        ], className="stat-card", style={'borderColor': COLORS['primary']}),
        
        html.Div([
            html.H3("Avg Humidity", className="card-title"),
            html.P(f"{avg_humidity:.1f}%", className="card-value"),
            html.P(f"Next {days} days", className="card-subtitle")
        ], className="stat-card", style={'borderColor': COLORS['secondary']}),
        
        html.Div([
            html.H3("Total Precipitation", className="card-title"),
            html.P(f"{total_precip:.1f}mm", className="card-value"),
            html.P(f"Next {days} days", className="card-subtitle")
        ], className="stat-card", style={'borderColor': COLORS['accent']})
    ]
    
    # Main Chart - Temperature
    fig_main = px.line(df, x='time', y='temperature',
                       title=f'Temperature Forecast - {location_name} ({days} Days)',
                       labels={'temperature': 'Temperature (°C)', 'time': 'Date'})
    fig_main = style_figure(fig_main)
    
    # Secondary Chart 1 - Humidity
    fig_sec1 = px.area(df, x='time', y='humidity',
                       title='Humidity Levels',
                       labels={'humidity': 'Humidity (%)', 'time': 'Date'})
    fig_sec1 = style_figure(fig_sec1)
    
    # Secondary Chart 2 - Precipitation
    fig_sec2 = px.bar(df, x='time', y='precipitation',
                      title='Precipitation',
                      labels={'precipitation': 'Precipitation (mm)', 'time': 'Date'})
    fig_sec2 = style_figure(fig_sec2)
    
    return cards, fig_main, fig_sec1, fig_sec2, datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def update_stocks_dashboard(days):
    """Update dashboard with stock data"""
    df = generate_mock_stock_data(days=days)
    
    # Stats Cards
    latest_prices = df.groupby('symbol')['price'].last()
    cards = []
    colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['accent']]
    
    for i, (symbol, price) in enumerate(latest_prices.items()):
        price_change = df[df['symbol'] == symbol]['price'].pct_change().iloc[-1] * 100
        cards.append(
            html.Div([
                html.H3(symbol, className="card-title"),
                html.P(f"${price:,.2f}", className="card-value"),
                html.P(f"{price_change:+.2f}%", 
                      className="card-change positive" if price_change > 0 else "card-change negative")
            ], className="stat-card", style={'borderColor': colors_list[i % 3]})
        )
    
    # Main Chart
    fig_main = px.line(df, x='date', y='price', color='symbol',
                       title=f'Stock Prices - Last {days} Days',
                       labels={'price': 'Price (USD)', 'date': 'Date'})
    fig_main = style_figure(fig_main)
    
    # Secondary Chart 1
    fig_sec1 = px.area(df, x='date', y='price', color='symbol',
                       title='Price Distribution')
    fig_sec1 = style_figure(fig_sec1)
    
    # Secondary Chart 2
    latest_data = df.groupby('symbol').last().reset_index()
    latest_data['change'] = df.groupby('symbol')['price'].apply(
        lambda x: ((x.iloc[-1] - x.iloc[0]) / x.iloc[0] * 100)
    ).values
    
    fig_sec2 = px.bar(latest_data, x='symbol', y='change',
                      title='Total Change (%)',
                      labels={'change': 'Change (%)', 'symbol': 'Stock'})
    fig_sec2 = style_figure(fig_sec2)
    
    return cards, fig_main, fig_sec1, fig_sec2, datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def style_figure(fig):
    """Apply consistent styling to figures for accessibility"""
    fig.update_layout(
        paper_bgcolor=COLORS['surface'],
        plot_bgcolor=COLORS['surface'],
        font=dict(color=COLORS['text'], family="Inter, sans-serif"),
        title_font=dict(size=18, color=COLORS['text']),
        hovermode='x unified',
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            bgcolor=COLORS['background'],
            bordercolor=COLORS['text_secondary'],
            borderwidth=1
        )
    )
    fig.update_xaxes(gridcolor=COLORS['text_secondary'], gridwidth=0.5)
    fig.update_yaxes(gridcolor=COLORS['text_secondary'], gridwidth=0.5)
    return fig

def create_empty_dashboard(message):
    """Create empty dashboard when data is unavailable"""
    empty_fig = go.Figure()
    empty_fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color=COLORS['text_secondary'])
    )
    empty_fig = style_figure(empty_fig)
    
    return [], empty_fig, empty_fig, empty_fig, datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==================== CSS STYLING ====================

app.index_string = '''
<!DOCTYPE html>
<html lang="en">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                min-height: 100vh;
            }
            
            .dashboard-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                padding: 40px 20px;
                background: rgba(30, 41, 59, 0.5);
                border-radius: 16px;
                margin-bottom: 30px;
                backdrop-filter: blur(10px);
            }
            
            .dashboard-title {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 10px;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .dashboard-subtitle {
                color: #94a3b8;
                font-size: 1.1rem;
            }
            
            .control-panel {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                padding: 25px;
                background: rgba(30, 41, 59, 0.5);
                border-radius: 12px;
                margin-bottom: 30px;
                backdrop-filter: blur(10px);
                position: relative;
                z-index: 100;
            }
            
            .control-item label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #cbd5e1;
                z-index: 1;
                position: relative;
            }
            
            .dropdown {
                width: 100%;
                z-index: 1000 !important;
            }
            
            /* Fix for Dash dropdown */
            .Select-menu-outer {
                z-index: 1000 !important;
            }
            
            .slider {
                width: 100%;
                z-index: 1;
            }
            
            .refresh-button {
                padding: 12px 24px;
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                align-self: end;
            }
            
            .refresh-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
            }
            
            .refresh-button:active {
                transform: translateY(0);
            }
            
            .stats-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                padding: 24px;
                background: rgba(30, 41, 59, 0.6);
                border-radius: 12px;
                border-left: 4px solid #3b82f6;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
            }
            
            .card-title {
                font-size: 0.9rem;
                color: #94a3b8;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .card-value {
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 6px;
            }
            
            .card-change {
                font-size: 0.9rem;
                font-weight: 600;
            }
            
            .card-change.positive {
                color: #10b981;
            }
            
            .card-change.negative {
                color: #ef4444;
            }
            
            .card-subtitle {
                font-size: 0.85rem;
                color: #64748b;
            }
            
            .chart-container {
                margin-bottom: 30px;
            }
            
            .chart {
                background: rgba(30, 41, 59, 0.5);
                border-radius: 12px;
                padding: 10px;
                backdrop-filter: blur(10px);
                position: relative;
                z-index: 1;
            }
            
            .secondary-charts {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .chart-half {
                min-height: 300px;
            }
            
            .footer {
                text-align: center;
                padding: 20px;
                color: #64748b;
                font-size: 0.9rem;
                background: rgba(30, 41, 59, 0.3);
                border-radius: 12px;
                margin-top: 30px;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }
            
            .footer p {
                margin: 5px 0;
            }
            
            .location-input {
                width: 100%;
                padding: 10px 14px;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid #475569;
                border-radius: 8px;
                color: #f1f5f9;
                font-size: 1rem;
                transition: all 0.3s ease;
            }
            
            .location-input:focus {
                border-color: #3b82f6;
                background: rgba(15, 23, 42, 0.8);
                outline: 2px solid #3b82f6;
                outline-offset: 2px;
            }
            
            .location-input::placeholder {
                color: #64748b;
            }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .dashboard-title {
                    font-size: 1.8rem;
                }
                
                .control-panel {
                    grid-template-columns: 1fr;
                }
                
                .secondary-charts {
                    grid-template-columns: 1fr;
                }
                
                .stats-container {
                    grid-template-columns: 1fr;
                }
            }
            
            /* Loading spinner styling */
            ._dash-loading-callback {
                color: #3b82f6 !important;
            }
            
            /* Accessibility - Focus states */
            button:focus, select:focus, input:focus {
                outline: 2px solid #3b82f6;
                outline-offset: 2px;
            }
            
            /* High contrast support */
            @media (prefers-contrast: high) {
                .stat-card {
                    border-width: 2px;
                }
                
                .card-change.positive {
                    color: #22c55e;
                }
                
                .card-change.negative {
                    color: #f87171;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.112', port=8050)