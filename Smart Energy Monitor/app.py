from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import google.generativeai as genai
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key="AIzaSyDJvJq4J8Jv4dKCLkylfEWm1N91qWrIxLQ")
model = genai.GenerativeModel("gemini-2.5-flash")
chat_session = model.start_chat(history=[])

# Store user appliances (in production, use a database)
user_appliances = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/appliances', methods=['GET'])
def get_appliances():
    return jsonify(user_appliances)

@app.route('/api/appliances', methods=['POST'])
def add_appliance():
    data = request.json
    appliance = data.get('appliance')
    hours = data.get('hours')
    
    if not appliance or hours is None:
        return jsonify({'error': 'Missing appliance or hours'}), 400
    
    try:
        hours = int(hours)
        if hours < 0 or hours > 24:
            return jsonify({'error': 'Hours must be between 0 and 24'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid hours value'}), 400
    
    user_appliances[appliance] = hours
    return jsonify({'success': True, 'appliances': user_appliances})

@app.route('/api/appliances/<appliance>', methods=['DELETE'])
def remove_appliance(appliance):
    if appliance in user_appliances:
        del user_appliances[appliance]
        return jsonify({'success': True, 'appliances': user_appliances})
    return jsonify({'error': 'Appliance not found'}), 404

@app.route('/api/predict', methods=['POST'])
def predict_bill():
    data = request.json
    bills = data.get('bills', [])
    
    if len(bills) != 3:
        return jsonify({'error': 'Please provide exactly 3 months of bill data'}), 400
    
    try:
        bills = np.array([float(b) for b in bills])
        
        # Convert bills to units
        prev_units = []
        for bill in bills:
            if bill <= 471:
                units = bill / 4.71
            elif bill <= 3087:
                s = bill - 471
                v = s / 10.29
                units = v + 100
            elif bill <= 7275:
                s = bill - 3087
                v = s / 14.55
                units = v + 200
            else:
                s = bill - 7275
                v = s / 16.64
                units = v + 500
            prev_units.append(units)
        
        # Predict next month
        months = np.array([1, 2, 3]).reshape(-1, 1)
        bill_model = LinearRegression().fit(months, bills)
        predicted_bill = bill_model.predict(np.array([[4]]))[0]
        predicted_bill = abs(predicted_bill)
        rounded_predicted_bill = (predicted_bill + 5) // 10 * 10
        
        # Convert predicted bill to units
        if predicted_bill <= 471:
            predicted_units = predicted_bill / 4.71
        elif predicted_bill <= 3087:
            s = predicted_bill - 471
            v = s / 10.29
            predicted_units = v + 100
        elif predicted_bill <= 7275:
            s = predicted_bill - 3087
            v = s / 14.55
            predicted_units = v + 200
        else:
            s = predicted_bill - 7275
            v = s / 16.64
            predicted_units = v + 500
        
        # Get month names
        today = datetime.today()
        month_names = []
        for i in range(1, 4):
            prev_month = today.replace(day=1) - timedelta(days=1)
            month_names.append(prev_month.strftime("%B"))
            today = prev_month
        month_names.reverse()
        month_names.append(datetime.today().strftime("%B"))
        
        return jsonify({
            'success': True,
            'predicted_bill': round(predicted_bill, 2),
            'predicted_units': round(predicted_units, 2),
            'rounded_bill': round(rounded_predicted_bill, 2),
            'previous_bills': bills.tolist(),
            'previous_units': [round(u, 2) for u in prev_units],
            'month_names': month_names
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/report', methods=['GET'])
def get_report():
    if not user_appliances:
        return jsonify({'error': 'No appliances data available'}), 400
    
    total_hours = sum(user_appliances.values())
    report = {
        'total_hours': total_hours,
        'appliances': []
    }
    
    for appliance, hours in user_appliances.items():
        percentage = (hours / total_hours) * 100 if total_hours > 0 else 0
        usage_level = 'high' if hours > 8 else 'moderate' if hours > 4 else 'efficient'
        report['appliances'].append({
            'name': appliance,
            'hours': hours,
            'percentage': round(percentage, 1),
            'usage_level': usage_level
        })
    
    return jsonify(report)

@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    if not user_appliances:
        return jsonify({'error': 'No appliances data available'}), 400
    
    base_costs = {
        "Fan": 0.45,
        "Air Conditioner": 7,
        "Refrigerator": 1.5,
        "TV": 0.80,
        "Washing Machine": 4,
        "LED": 0.50
    }
    
    appliances = []
    hours = []
    costs = []
    
    for appliance, hour in user_appliances.items():
        base_cost = base_costs.get(appliance, 0.65)
        cost = base_cost * hour
        appliances.append(appliance)
        hours.append(hour)
        costs.append(cost)
    
    total_cost = sum(costs)
    
    analysis = {
        'total_cost': round(total_cost, 2),
        'appliances': []
    }
    
    for appliance, hour, cost in zip(appliances, hours, costs):
        percentage = (cost / total_cost) * 100 if total_cost > 0 else 0
        analysis['appliances'].append({
            'name': appliance,
            'hours': hour,
            'cost': round(cost, 2),
            'percentage': round(percentage, 1)
        })
    
    # Calculate regression
    if len(hours) > 1:
        X = np.array(hours).reshape(-1, 1)
        y = np.array(costs)
        model = LinearRegression()
        model.fit(X, y)
        analysis['regression'] = {
            'slope': float(model.coef_[0]),
            'intercept': float(model.intercept_)
        }
    
    return jsonify(analysis)

@app.route('/api/mlreport', methods=['GET'])
def get_mlreport():
    if not user_appliances:
        return jsonify({'error': 'No appliances data available'}), 400
    
    base_costs = {
        "Fan": 2,
        "Air Conditioner": 15,
        "Refrigerator": 4,
        "TV": 3,
        "Washing Machine": 5
    }
    
    sorted_apps = sorted(user_appliances.items(), key=lambda x: x[1], reverse=True)
    
    report = {
        'appliances': [],
        'total_savings': 0
    }
    
    for appliance, hours in sorted_apps:
        base_cost = base_costs.get(appliance, 5)
        current_cost = base_cost * hours
        reduced_hours = max(0, hours - 2)
        reduced_cost = base_cost * reduced_hours
        savings = current_cost - reduced_cost
        
        usage_level = 'very_high' if hours > 8 else 'high' if hours > 4 else 'normal'
        
        report['appliances'].append({
            'name': appliance,
            'hours': hours,
            'usage_level': usage_level,
            'savings': round(savings, 2) if hours > 2 else 0
        })
        
        if hours > 2:
            report['total_savings'] += savings
    
    report['total_savings'] = round(report['total_savings'], 2)
    
    return jsonify(report)

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        local_answers = {
            "how to save energy?": "Turn off unused appliances, use LED bulbs, and limit AC usage.",
            "why is my bill high?": "Check for high-consumption appliances and reduce their usage."
        }
        
        if question.lower() in local_answers:
            response_text = local_answers[question.lower()]
        else:
            response = chat_session.send_message(question)
            response_text = response.text
        
        return jsonify({'success': True, 'response': response_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
