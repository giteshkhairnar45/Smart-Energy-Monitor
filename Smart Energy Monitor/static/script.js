// Global state
let currentPage = 'home';
let unitsChart = null;
let billsChart = null;
let analysisChart = null;
let regressionChart = null;
let mlConsumptionChart = null;
let mlPieChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeBillInputs();
    loadAppliances();
    setupEventListeners();
});

// Navigation
function initializeNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const page = btn.dataset.page;
            showPage(page);
        });
    });
}

function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    const targetPage = document.getElementById(pageName);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.page === pageName);
    });
    
    currentPage = pageName;
}

// Initialize bill inputs with month names
function initializeBillInputs() {
    const monthNames = getLastThreeMonths();
    const container = document.getElementById('bill-inputs');
    container.innerHTML = '';
    
    monthNames.forEach((month, index) => {
        const group = document.createElement('div');
        group.className = 'bill-input-group';
        group.innerHTML = `
            <label>${month}:</label>
            <input type="number" id="bill-${index}" class="form-control" placeholder="Enter bill amount (₹)" min="0" step="0.01">
        `;
        container.appendChild(group);
    });
}

function getLastThreeMonths() {
    const months = [];
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December'];
    const today = new Date();
    
    for (let i = 1; i <= 3; i++) {
        const date = new Date(today.getFullYear(), today.getMonth() - i, 1);
        months.push(monthNames[date.getMonth()]);
    }
    
    return months.reverse();
}

// Setup event listeners
function setupEventListeners() {
    // Add appliance
    document.getElementById('add-appliance-btn').addEventListener('click', addAppliance);
    document.getElementById('remove-appliance-btn').addEventListener('click', removeAppliance);
    
    // Predict bill
    document.getElementById('predict-btn').addEventListener('click', predictBill);
    
    // Generate report
    document.getElementById('generate-report-btn').addEventListener('click', generateReport);
    
    // Generate analysis
    document.getElementById('generate-analysis-btn').addEventListener('click', generateAnalysis);
    
    // Generate ML report
    document.getElementById('generate-mlreport-btn').addEventListener('click', generateMLReport);
    
    // Chatbot
    document.getElementById('send-chat-btn').addEventListener('click', sendChatMessage);
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

// Appliance Management
async function loadAppliances() {
    try {
        const response = await fetch('/api/appliances');
        const data = await response.json();
        updateApplianceList(data);
    } catch (error) {
        console.error('Error loading appliances:', error);
    }
}

async function addAppliance() {
    const appliance = document.getElementById('appliance-select').value;
    const hours = document.getElementById('hours-input').value;
    
    if (!appliance) {
        alert('Please select an appliance');
        return;
    }
    
    if (!hours || hours < 0 || hours > 24) {
        alert('Please enter valid hours (0-24)');
        return;
    }
    
    try {
        const response = await fetch('/api/appliances', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ appliance, hours: parseInt(hours) })
        });
        
        const data = await response.json();
        if (data.success) {
            updateApplianceList(data.appliances);
            document.getElementById('appliance-select').value = '';
            document.getElementById('hours-input').value = '';
            alert(`${appliance} added successfully!`);
        } else {
            alert(data.error || 'Error adding appliance');
        }
    } catch (error) {
        console.error('Error adding appliance:', error);
        alert('Error adding appliance');
    }
}

async function removeAppliance() {
    const list = document.getElementById('appliance-list');
    const selected = list.querySelector('li.selected');
    
    if (!selected) {
        alert('Please select an appliance to remove');
        return;
    }
    
    const appliance = selected.dataset.appliance;
    
    try {
        const response = await fetch(`/api/appliances/${encodeURIComponent(appliance)}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.success) {
            updateApplianceList(data.appliances);
        } else {
            alert(data.error || 'Error removing appliance');
        }
    } catch (error) {
        console.error('Error removing appliance:', error);
        alert('Error removing appliance');
    }
}

function updateApplianceList(appliances) {
    const list = document.getElementById('appliance-list');
    list.innerHTML = '';
    
    for (const [appliance, hours] of Object.entries(appliances)) {
        const li = document.createElement('li');
        li.dataset.appliance = appliance;
        li.textContent = `${appliance} - ${hours} hrs/day`;
        li.addEventListener('click', () => {
            list.querySelectorAll('li').forEach(item => item.classList.remove('selected'));
            li.classList.add('selected');
        });
        list.appendChild(li);
    }
}

// Bill Prediction
async function predictBill() {
    const bills = [];
    for (let i = 0; i < 3; i++) {
        const value = document.getElementById(`bill-${i}`).value;
        if (!value) {
            alert('Please enter all 3 months of bill data');
            return;
        }
        bills.push(parseFloat(value));
    }
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ bills })
        });
        
        const data = await response.json();
        if (data.success) {
            displayPrediction(data);
        } else {
            alert(data.error || 'Error predicting bill');
        }
    } catch (error) {
        console.error('Error predicting bill:', error);
        alert('Error predicting bill');
    }
}

function displayPrediction(data) {
    const resultBox = document.getElementById('prediction-result');
    resultBox.innerHTML = `
        <h2>Predicted Bill: ₹${data.predicted_bill.toFixed(2)} (${data.predicted_units.toFixed(1)} units)</h2>
    `;
    
    // Units chart
    const unitsCtx = document.getElementById('units-chart').getContext('2d');
    if (unitsChart) unitsChart.destroy();
    unitsChart = new Chart(unitsCtx, {
        type: 'bar',
        data: {
            labels: data.month_names,
            datasets: [{
                label: 'Units',
                data: [...data.previous_units, data.predicted_units],
                backgroundColor: ['#3b82f6', '#3b82f6', '#3b82f6', '#ef4444'],
                borderColor: ['#60a5fa', '#60a5fa', '#60a5fa', '#f87171'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Electricity Units Consumption',
                    color: '#ffffff',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    ticks: { color: '#e5e7eb' },
                    grid: { color: '#2d2d2d' }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: '#e5e7eb' },
                    grid: { color: '#2d2d2d' }
                }
            }
        }
    });
    
    // Bills chart
    const billsCtx = document.getElementById('bills-chart').getContext('2d');
    if (billsChart) billsChart.destroy();
    billsChart = new Chart(billsCtx, {
        type: 'line',
        data: {
            labels: data.month_names,
            datasets: [{
                label: 'Bill Amount (₹)',
                data: [...data.previous_bills, data.rounded_bill],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#60a5fa',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Electricity Bill Trend',
                    color: '#ffffff',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    labels: { color: '#e5e7eb' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#e5e7eb' },
                    grid: { color: '#2d2d2d' }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: '#e5e7eb' },
                    grid: { color: '#2d2d2d' }
                }
            }
        }
    });
}

// Generate Report
async function generateReport() {
    try {
        const response = await fetch('/api/report');
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        const content = document.getElementById('report-content');
        let html = '<h3>Appliance Usage Report</h3>';
        html += `<p><strong>Total Hours of Appliance Usage: ${data.total_hours} hrs/day</strong></p><ul>`;
        
        data.appliances.forEach(app => {
            html += `<li><strong>${app.name}:</strong> ${app.hours} hrs/day (${app.percentage}%)</li>`;
        });
        
        html += '</ul><h3>Usage Analysis</h3><ul>';
        
        data.appliances.forEach(app => {
            let level = 'Efficient usage';
            let statusClass = 'status-efficient';
            if (app.usage_level === 'high') {
                level = 'High usage';
                statusClass = 'status-high';
            } else if (app.usage_level === 'moderate') {
                level = 'Moderate usage';
                statusClass = 'status-moderate';
            }
            html += `<li><span class="${statusClass}">${level}:</span> ${app.name} (${app.hours} hrs/day)</li>`;
        });
        
        html += '</ul>';
        content.innerHTML = html;
    } catch (error) {
        console.error('Error generating report:', error);
        alert('Error generating report');
    }
}

// Generate Analysis
async function generateAnalysis() {
    try {
        const response = await fetch('/api/analysis');
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // Bar chart
        const analysisCtx = document.getElementById('analysis-chart').getContext('2d');
        if (analysisChart) analysisChart.destroy();
        analysisChart = new Chart(analysisCtx, {
            type: 'bar',
            data: {
                labels: data.appliances.map(a => a.name),
                datasets: [{
                    label: 'Daily Energy Cost (₹)',
                    data: data.appliances.map(a => a.cost),
                    backgroundColor: data.appliances.map((a, i) => {
                        const maxCost = Math.max(...data.appliances.map(ap => ap.cost));
                        const minCost = Math.min(...data.appliances.map(ap => ap.cost));
                        if (a.cost === maxCost) return '#ef4444';
                        if (a.cost === minCost) return '#22c55e';
                        if (a.cost >= (minCost + maxCost) / 3) return '#3b82f6';
                        return '#f59e0b';
                    }),
                    borderColor: data.appliances.map((a, i) => {
                        const maxCost = Math.max(...data.appliances.map(ap => ap.cost));
                        const minCost = Math.min(...data.appliances.map(ap => ap.cost));
                        if (a.cost === maxCost) return '#f87171';
                        if (a.cost === minCost) return '#4ade80';
                        if (a.cost >= (minCost + maxCost) / 3) return '#60a5fa';
                        return '#fbbf24';
                    }),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Daily Energy Cost by Your Appliances',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#e5e7eb' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#e5e7eb' },
                        grid: { color: '#2d2d2d' }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#e5e7eb' },
                        grid: { color: '#2d2d2d' }
                    }
                }
            }
        });
        
        // Regression chart
        if (data.regression) {
            const regressionCtx = document.getElementById('regression-chart').getContext('2d');
            if (regressionChart) regressionChart.destroy();
            
            const hours = data.appliances.map(a => a.hours);
            const costs = data.appliances.map(a => a.cost);
            const minHour = Math.min(...hours);
            const maxHour = Math.max(...hours);
            const lineHours = Array.from({length: 100}, (_, i) => minHour + (maxHour - minHour) * i / 99);
            const lineCosts = lineHours.map(h => data.regression.slope * h + data.regression.intercept);
            
            regressionChart = new Chart(regressionCtx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Usage Hours vs Cost',
                        data: hours.map((h, i) => ({x: h, y: costs[i]})),
                        backgroundColor: '#3b82f6',
                        borderColor: '#60a5fa',
                        pointRadius: 8,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2
                    }, {
                        label: 'Regression Line',
                        data: lineHours.map((h, i) => ({x: h, y: lineCosts[i]})),
                        type: 'line',
                        borderColor: '#ef4444',
                        borderWidth: 3,
                        fill: false,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Usage Hours vs Cost',
                            color: '#ffffff',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            labels: { color: '#e5e7eb' }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Usage Hours Per Day',
                                color: '#e5e7eb'
                            },
                            ticks: { color: '#e5e7eb' },
                            grid: { color: '#2d2d2d' }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Estimated Cost (₹)',
                                color: '#e5e7eb'
                            },
                            beginAtZero: true,
                            ticks: { color: '#e5e7eb' },
                            grid: { color: '#2d2d2d' }
                        }
                    }
                }
            });
        }
        
        // Analysis content
        const content = document.getElementById('analysis-content');
        let html = `<h3>Analysis Summary</h3>`;
        html += `<p><strong>Total Daily Energy Cost: ₹${data.total_cost}</strong></p>`;
        html += `<h3>Breakdown by Appliance:</h3><ul>`;
        
        data.appliances.forEach(app => {
            html += `<li>• ${app.name}: ${app.hours} hours/day - ₹${app.cost} (${app.percentage}% of total cost)</li>`;
        });
        
        html += '</ul><h3>Recommendations for Energy Savings:</h3><ul>';
        
        data.appliances.forEach(app => {
            if (app.hours > 6) {
                html += `<li>• Consider reducing ${app.name} usage (${app.hours} hours/day is high)</li>`;
            } else if (app.hours > 4) {
                html += `<li>• Monitor ${app.name} usage to optimize efficiency</li>`;
            }
        });
        
        html += '</ul>';
        content.innerHTML = html;
    } catch (error) {
        console.error('Error generating analysis:', error);
        alert('Error generating analysis');
    }
}

// Generate ML Report
async function generateMLReport() {
    try {
        const response = await fetch('/api/mlreport');
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // Consumption chart
        const mlConsumptionCtx = document.getElementById('ml-consumption-chart').getContext('2d');
        if (mlConsumptionChart) mlConsumptionChart.destroy();
        mlConsumptionChart = new Chart(mlConsumptionCtx, {
            type: 'bar',
            data: {
                labels: data.appliances.map(a => a.name),
                datasets: [{
                    label: 'Hours/Day',
                    data: data.appliances.map(a => a.hours),
                    backgroundColor: data.appliances.map(a => {
                        const maxHour = Math.max(...data.appliances.map(ap => ap.hours));
                        const minHour = Math.min(...data.appliances.map(ap => ap.hours));
                        const midHour = (maxHour + minHour) / 2.5;
                        if (a.hours === maxHour) return '#ef4444';
                        if (a.hours === minHour) return '#22c55e';
                        if (a.hours >= midHour) return '#f59e0b';
                        return '#3b82f6';
                    }),
                    borderColor: data.appliances.map(a => {
                        const maxHour = Math.max(...data.appliances.map(ap => ap.hours));
                        const minHour = Math.min(...data.appliances.map(ap => ap.hours));
                        const midHour = (maxHour + minHour) / 2.5;
                        if (a.hours === maxHour) return '#f87171';
                        if (a.hours === minHour) return '#4ade80';
                        if (a.hours >= midHour) return '#fbbf24';
                        return '#60a5fa';
                    }),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Energy Consumption by Appliance',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#e5e7eb' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#e5e7eb' },
                        grid: { color: '#2d2d2d' }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Hours/Day',
                            color: '#e5e7eb'
                        },
                        ticks: { color: '#e5e7eb' },
                        grid: { color: '#2d2d2d' }
                    }
                }
            }
        });
        
        // Pie chart
        const mlPieCtx = document.getElementById('ml-pie-chart').getContext('2d');
        if (mlPieChart) mlPieChart.destroy();
        mlPieChart = new Chart(mlPieCtx, {
            type: 'pie',
            data: {
                labels: data.appliances.map(a => a.name),
                datasets: [{
                    data: data.appliances.map(a => a.hours),
                    backgroundColor: [
                        '#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4'
                    ],
                    borderColor: '#1a1a1a',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Usage Distribution',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'right',
                        labels: { color: '#e5e7eb' }
                    }
                }
            }
        });
        
        // ML Report content
        const content = document.getElementById('mlreport-content');
        let html = '<h3>Machine Learning Analysis</h3>';
        html += '<h3>Usage Patterns</h3><ul>';
        
        data.appliances.forEach(app => {
            let level = 'Normal Usage';
            if (app.usage_level === 'very_high') level = 'Very High Usage';
            else if (app.usage_level === 'high') level = 'High Usage';
            html += `<li><strong>${app.name}:</strong> ${level} (${app.hours} hrs/day)</li>`;
        });
        
        html += '</ul><h3>Predicted Daily Savings</h3><ul>';
        
        data.appliances.forEach(app => {
            if (app.savings > 0) {
                html += `<li>Reduce <strong>${app.name}</strong> by 2 hrs: Save ₹${app.savings}</li>`;
            }
        });
        
        html += `</ul><p><strong>Total Potential Daily Savings: ₹${data.total_savings}</strong></p>`;
        html += '<h3>AI Recommendations</h3><ul>';
        
        data.appliances.forEach(app => {
            if (app.hours > 8) {
                html += `<li>• Consider using ${app.name} in off-peak hours</li>`;
            } else if (app.hours > 5) {
                html += `<li>• Monitor ${app.name} usage patterns</li>`;
            }
        });
        
        html += '</ul>';
        content.innerHTML = html;
    } catch (error) {
        console.error('Error generating ML report:', error);
        alert('Error generating ML report');
    }
}

// Chatbot
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const question = input.value.trim();
    
    if (!question) return;
    
    // Display user message
    addChatMessage('user', question);
    input.value = '';
    
    try {
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        if (data.success) {
            addChatMessage('bot', data.response);
        } else {
            addChatMessage('bot', `Error: ${data.error}`);
        }
    } catch (error) {
        console.error('Error sending chat message:', error);
        addChatMessage('bot', 'Sorry, I encountered an error. Please try again.');
    }
}

function addChatMessage(sender, text) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const header = document.createElement('div');
    header.className = 'message-header';
    header.textContent = sender === 'user' ? 'You' : 'Bot';
    
    const content = document.createElement('div');
    content.textContent = text;
    
    messageDiv.appendChild(header);
    messageDiv.appendChild(content);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

