# Energy Bill Predictor - Web Application

A modern, attractive web application for predicting electricity bills and analyzing energy consumption patterns. This is a web-based version of the original Tkinter application with enhanced UI/UX.

## Features

- 🏠 **Home Page** - Welcome screen with feature overview
- 📊 **Bill Prediction** - Predict next month's bill using Machine Learning (Linear Regression)
- ➕ **Appliance Management** - Add and manage your appliances with usage hours
- 📈 **Usage Report** - Generate detailed usage reports
- 📉 **Analysis** - Visual analysis with interactive charts
- 🤖 **ML Report** - Machine Learning powered insights and recommendations
- 💬 **AI Chatbot** - Chat with an AI assistant powered by Google Gemini

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **ML**: scikit-learn (Linear Regression)
- **AI**: Google Gemini API

## Installation

1. **Clone or navigate to the project directory**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Project Structure

```
Project-CPP - Copy/
├── app.py                 # Flask backend server
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── style.css         # Modern CSS styling
│   └── script.js         # JavaScript functionality
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Usage

1. **Add Appliances**: Go to "Add Appliance" page and add your appliances with their daily usage hours.

2. **Predict Bill**: Enter your last 3 months' bill amounts in the "Predict Bill" page to get predictions for the next month.

3. **View Reports**: Generate usage reports and analysis to understand your energy consumption patterns.

4. **Get Recommendations**: Use the ML Report and Chatbot features to get AI-powered recommendations for energy savings.

## API Endpoints

- `GET /` - Main page
- `GET /api/appliances` - Get all appliances
- `POST /api/appliances` - Add an appliance
- `DELETE /api/appliances/<appliance>` - Remove an appliance
- `POST /api/predict` - Predict next month's bill
- `GET /api/report` - Get usage report
- `GET /api/analysis` - Get analysis data
- `GET /api/mlreport` - Get ML report
- `POST /api/chatbot` - Send chat message

## Features in Detail

### Bill Prediction
- Uses Linear Regression to predict next month's bill
- Converts bill amounts to units based on Indian electricity tariff structure
- Displays interactive charts showing consumption trends

### Usage Analysis
- Visual bar charts showing energy costs by appliance
- Regression analysis showing relationship between usage hours and cost
- Personalized recommendations based on usage patterns

### ML Report
- Machine Learning analysis of usage patterns
- Potential savings calculations
- AI-powered recommendations for energy optimization

### Chatbot
- Interactive AI assistant powered by Google Gemini
- Answers questions about energy consumption and savings
- Provides personalized advice

## Design Features

- **Modern UI**: Gradient backgrounds, smooth animations, and attractive color scheme
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Interactive Charts**: Beautiful, interactive charts using Chart.js
- **Smooth Navigation**: Easy navigation between different sections
- **User-Friendly**: Intuitive interface with clear instructions

## Notes

- The application uses Google Gemini API for the chatbot feature. Make sure you have a valid API key.
- The bill prediction uses Indian electricity tariff structure. You may need to adjust the conversion logic for other regions.
- All data is stored in memory (not persisted). For production use, implement a database.

## License

This project is open source and available for educational purposes.

