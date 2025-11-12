# Live-Data-Dashboard

This app allows users to **analyze and visualize real-time data** for:
- 💰 **Cryptocurrencies** (via the CoinGecko API)
- 🌤️ **Weather Forecasts** (via the Open-Meteo API)
- 📈 **Stock Prices** (mock-generated data for demo)

It features a **beautiful, responsive, and accessible UI** with dynamic updates, custom themes, and seamless transitions.

---

## 🚀 Features

- **Three Data Modes:** Cryptocurrency, Weather, and Stock Market
- **Live Data Fetching:** Real-time data via public APIs
- **Interactive UI Controls:** Dropdowns, sliders, and input fields
- **Auto Refresh:** Dashboard updates every 5 minutes
- **Dynamic Stats Cards:** Auto-calculated key metrics (price change, avg temperature, etc.)

---

## Tech Stack

| Component | Description |
|------------|-------------|
| **Dash** | Web framework for building data dashboards |
| **Plotly** | For interactive charting (line, area, bar) |
| **Pandas** | For data processing and manipulation |
| **Requests** | For fetching data from APIs |
| **NumPy** | For generating mock stock data |

---

## Installation 

### **1. Clone the repository**
```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
```

### **2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate   
venv\Scripts\activate
```

### **3. Install dependencies**
```bash
pip install -r requirements.txt
```

### **4. Run the app**
```bash
python Multi-data-dashboard.py
```
