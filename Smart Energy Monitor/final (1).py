import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import numpy as np
import threading

from sklearn.linear_model import LinearRegression
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyDJvJq4J8Jv4dKCLkylfEWm1N91qWrIxLQ")


class EnergyBillPredictor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Energy Bill Predictor")
        self.root.geometry("1024x700")
        self.root.configure(bg="black")

        # Initialize themes
        self.LIGHT_THEME = {
            "PRIMARY_COLOR": "#2E86C1",
            "SECONDARY_COLOR": "#AED6F1",
            "BACKGROUND": "#F0F0F0",
            "TEXT_COLOR": "#2C3E50",
            "BUTTON_COLOR": "#3498DB",
            "BUTTON_TEXT": "#FFFFFF",
            "ACCENT_COLOR": "#E74C3C",
            "SUCCESS_COLOR": "#2ECC71",
            "HOVER_COLOR": "#2574A9"
        }

        self.current_theme = self.LIGHT_THEME
        self.root.configure(bg=self.current_theme["BACKGROUND"])

        self.frames = {}
        self.user_appliances = {}

        # Initialize menu buttons
        self.menu_buttons = [
            ("🏠 Home", "home"),
            ("📊 Predict Bill", "predict"),
            ("➕ Add Appliance", "add_appliance"),
            ("📈 Usage Report", "report"),
            ("📉 Analysis", "analysis"),
            ("📉 ML Report", "mlreport"),
            ("💬 Chatbot", "chatbot"),
        ]

        # Start with splash screen
        self.initialize_main_content()

    

    def create_scrollable_frame(self, parent):
        container = ttk.Frame(parent)
        canvas = tk.Canvas(container, bg=self.current_theme["BACKGROUND"])

        # Use standard Tkinter scrollbar for width customization instead of ttk
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview, width=20)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Create window in the center of the canvas
        canvas.create_window((512, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Configure canvas width
        canvas.config(width=1000)

        # Bind the canvas to resize event
        def configure_canvas(event):
            # Center the content
            canvas.coords(1, event.width / 2, 0)

        canvas.bind("<Configure>", configure_canvas)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        container.pack(fill="both", expand=True)

        return scrollable_frame

    def initialize_main_content(self):
        # Create frames
        for _, frame_name in self.menu_buttons:
            frame = ttk.Frame(self.root)
            scrollable_frame = self.create_scrollable_frame(frame)
            self.frames[frame_name] = (frame, scrollable_frame)

        # Create pages
        self.create_home_page()
        self.create_add_appliance_page()
        self.create_predict_page()
        self.create_chatbot_page()
        self.create_report_page()
        self.create_analysis_page()
        self.create_mlreport_page()

        # Show home page
        self.show_frame('home')

    def create_navigation_bar(self, parent):
        nav_bar = tk.Frame(parent, bg="black", height=60)
        nav_bar.pack(side="top", fill="x")

        # Center the navigation buttons
        button_frame = tk.Frame(nav_bar, bg="black")
        button_frame.pack(side="top", fill="x")

        # Create a center container for buttons
        center_container = tk.Frame(button_frame, bg="lightblue")
        center_container.pack(anchor="center", pady=5)

        for text, frame_name in self.menu_buttons:
            btn = tk.Button(
                center_container,
                text=text,
                command=lambda f=frame_name: self.show_frame(f),
                bg="#FFFFFF",
                fg="red",
                font=("Helvetica", 12),
                relief="flat",
                padx=15,
                pady=5
            )
            btn.pack(side="left", padx=5, pady=5)

    def show_frame(self, frame_name):
        # Hide all frames
        for frame, _ in self.frames.values():
            frame.pack_forget()

        # Show selected frame
        frame, _ = self.frames[frame_name]
        frame.pack(fill="both", expand=True)

    def create_home_page(self):
        frame, scrollable_frame = self.frames['home']
        self.create_navigation_bar(frame)

        # Centered container
        container = ttk.Frame(scrollable_frame)
        container.pack(pady=50, anchor="center")

        title = ttk.Label(container,
                          text="Welcome to Energy Bill Predictor",
                          font=("Helvetica", 24, "bold"))
        title.pack(pady=20)

        try:
            image = PhotoImage(file="images/save.png")
            label = tk.Label(container, image=image)
            label.image = image
            label.pack(pady=20)
        except:
            print("Warning: Could not load image file")

    def create_add_appliance_page(self):
        frame, scrollable_frame = self.frames['add_appliance']
        self.create_navigation_bar(frame)

        # Centered container
        container = ttk.Frame(scrollable_frame)
        container.pack(pady=50, anchor="center")

        # Title
        ttk.Label(container,
                  text="Add an Appliance",
                  font=("Helvetica", 24, "bold")).pack(pady=20)

        # Appliance selection
        appliance_frame = ttk.Frame(container)
        appliance_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(appliance_frame,
                  text="Select Appliance :",
                  font=("Helvetica", 12)).pack(side="left", padx=5)

        self.appliance_var = tk.StringVar()
        appliance_menu = ttk.Combobox(
            appliance_frame,
            textvariable=self.appliance_var,
            values=["Fan", "Air Conditioner", "Refrigerator", "TV", "Washing Machine","LED",],
            font=("Helvetica", 12),
            state="readonly",
            width=30
        )
        appliance_menu.pack(side="left", padx=5)

        # Hours input
        hours_frame = ttk.Frame(container)
        hours_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(hours_frame,
                  text="Hours per day   :   ",
                  font=("Helvetica", 12)).pack(side="left", padx=5)

        self.hours_var = tk.StringVar()
        hours_entry = ttk.Entry(
            hours_frame,
            textvariable=self.hours_var,
            font=("Helvetica", 12),
            width=32
        )
        hours_entry.pack(side="left", padx=5)

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=20, padx=20)

        add_button = tk.Button(
            button_frame,
            text="Add Appliance",
            command=self.add_appliance,
            bg=self.current_theme["BUTTON_COLOR"],
            fg=self.current_theme["BUTTON_TEXT"],
            font=("Helvetica", 12),
            relief="flat",
            padx=15,
            pady=5
        )
        add_button.pack(side="left", padx=5)

        remove_button = tk.Button(
            button_frame,
            text="Remove Selected",
            command=self.remove_appliance,
            bg=self.current_theme["ACCENT_COLOR"],
            fg=self.current_theme["BUTTON_TEXT"],
            font=("Helvetica", 12),
            relief="flat",
            padx=15,
            pady=5
        )
        remove_button.pack(side="left", padx=5)

        # Listbox to show added appliances
        self.appliance_listbox = tk.Listbox(
            container,
            height=12,
            font=("Helvetica", 12),
            selectmode="single",
            width=70
        )
        self.appliance_listbox.pack(pady=10, padx=20)

        # Add instructions
        instructions = """
        Instructions:
        1. First add your appliances in the 'Add Appliance' section
        2. Come back to this page and click 'Generate Analysis'
        3. View your personalized energy usage analysis and recommendations
        """

        ttk.Label(scrollable_frame,
                  text=instructions,
                  font=("Helvetica", 12,"bold"),
                  foreground="#003366",
                  justify="left").pack(pady=20, padx=20)

    def add_appliance(self):
        appliance = self.appliance_var.get()
        hours = self.hours_var.get()

        if not appliance:
            messagebox.showerror("Error", "Please select an appliance")
            return

        if not hours.isdigit() or int(hours) < 0 or int(hours) > 24:
            messagebox.showerror("Error", "Please enter valid hours (0-24)")
            return

        self.user_appliances[appliance] = int(hours)
        self.update_appliance_list()

        # Clear the inputs
        self.appliance_var.set("")
        self.hours_var.set("")

        messagebox.showinfo("Success", f"{appliance} added successfully!")

    def remove_appliance(self):
        selection = self.appliance_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an appliance to remove")
            return

        appliance = self.appliance_listbox.get(selection[0]).split(" - ")[0]
        del self.user_appliances[appliance]
        self.update_appliance_list()

    def update_appliance_list(self):
        self.appliance_listbox.delete(0, tk.END)
        for app, hrs in self.user_appliances.items():
            self.appliance_listbox.insert(tk.END, f"{app} - {hrs} hrs/day")

    def create_predict_page(self):
        frame, scrollable_frame = self.frames['predict']
        self.create_navigation_bar(frame)

        # Centered container
        container = ttk.Frame(scrollable_frame)
        container.pack(pady=50, anchor="center")

        # Title with larger padding and bigger font
        ttk.Label(container,
                  text="Predict Your Bill",
                  font=("Helvetica", 32, "bold")).pack(pady=30)

        # Create container for bill inputs
        bill_container = ttk.Frame(container)
        bill_container.pack(pady=20, fill="x")

        prev_bill_vars = [tk.StringVar() for _ in range(3)]

        result_text = tk.StringVar()

        # Header with larger font and spacing
        ttk.Label(bill_container,
                  text="Enter Last 3 Months' Data:",
                  font=("Arial", 18, "bold")).pack(pady=20)

        # Create styled entry fields for bills and units
        import datetime

        # Get current month and year
        today = datetime.date.today()

        # Get previous three months
        month_names = []
        for i in range(1, 4):  # Loop for last 3 months
            prev_month = today.replace(day=1) - datetime.timedelta(days=1)  # Go to last month's last day
            month_names.append(prev_month.strftime("%B"))  # Get full month name
            today = prev_month  # Update today to previous month


        month_names.reverse()
        for i,(bill_var) in enumerate(prev_bill_vars):
            entry_frame = ttk.Frame(bill_container)
            entry_frame.pack(pady=15)

            # Month label
            ttk.Label(entry_frame,
                      text=f"{month_names[i]}:",
                      font=("Arial", 14)).pack(side="left", padx=10)

            # Bill entry with currency symbol
            ttk.Label(entry_frame,
                      text="Bill Amount:",
                      font=("Arial", 12)).pack(side="left", padx=5)

            bill_entry = tk.Entry(entry_frame,
                                  textvariable=bill_var,
                                  font=("Arial", 14),
                                  width=10,
                                  justify="center")
            bill_entry.pack(side="left", padx=5)
            bill_entry.insert(0, "")



        # Create frame for the chart
        chart_frame = ttk.Frame(container)
        chart_frame.pack(pady=20, fill="both", expand=True)

        def predict_bill():
            prev_units_vars = []
            for var in prev_bill_vars:
                try:
                    value = var.get().strip()
                    value = int(value)
                    if (value <= 471):
                        value //= 4.71

                    elif (value <= 3087):
                        s=value-471
                        v=s//10.29
                        value=v+100

                    elif (value <= 7275):
                        s = value - 3087
                        v = s // 14.55
                        value = v + 200
                    else:
                        s = value - 7275
                        v = s // 16.64
                        value = v + 500

                    prev_units_vars.append(value)
                except ValueError:
                    prev_units_vars.append(0)
            try:
                # Clear previous chart
                for widget in chart_frame.winfo_children():
                    widget.destroy()

                # Remove currency symbol and convert to float
                bills = np.array([float(var.get().replace('₹', '')) for var in prev_bill_vars])

                # Get units data
                try:
                    units = np.array([float(var) for var in prev_units_vars if var])
                    if len(units) < 3:
                        raise ValueError("Please enter units for all months")
                except ValueError:
                    messagebox.showerror("Input Error", "Please enter valid units for all months")
                    return

                # Create model and predict next month
                months = np.array([1, 2, 3]).reshape(-1, 1)
                bill_model = LinearRegression().fit(months, bills)


                predicted_bill = bill_model.predict(np.array([[4]]))[0]
                pvs=abs(predicted_bill)

                predicted_units=0


                # Create and display the chart
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
                if (pvs <= 471):
                    predicted_units = pvs // 4.71
                elif (pvs <= 3087):
                    s =  pvs- 471
                    v = s // 10.29
                    predicted_units= v + 100
                elif (pvs <= 7275):
                    s = pvs - 3087
                    v = s // 14.55
                    predicted_units = v + 200
                else:
                    s= pvs -7275
                    v = s // 16.64
                    predicted_units = v + 500


                s=predicted_bill
                rounded_predicted_bill=(s++5)//10*10
                result_text.set(f"📊 Predicted Bill: ₹{abs(predicted_bill):,.00f}.00 ({predicted_units:.0f}.0 units)")




                current_month=datetime.datetime.today().strftime("%B")
                # Bar chart for units
                months_labels = month_names + [current_month]
                all_units = np.append(units, predicted_units)
                bars = ax1.bar(months_labels, all_units, color=['#3498DB', '#3498DB', '#3498DB', '#E74C3C'])
                ax1.set_title('Electricity Units Consumption')
                ax1.set_ylabel('Units')
                ax1.tick_params(axis='x', rotation=45)

                # Add value labels on the bars
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width() / 2., height,
                             f'{int(height)}',
                             ha='center', va='bottom')

                # Line chart for bills
                all_bills = np.append(bills,abs( rounded_predicted_bill))
                ax2.plot(months_labels, all_bills, marker='o', color='#2E86C1', linewidth=2)
                ax2.set_title('Electricity Bill Trend')
                ax2.set_ylabel('Cost (₹)')
                ax2.tick_params(axis='x', rotation=45)

                # Add value labels on the points
                for i, cost in enumerate(all_bills):
                    ax2.text(i, cost, f'₹{int(cost)}', ha='center', va='bottom')

                plt.tight_layout()

                # Display chart in the frame
                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=10)

            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid bill amounts and units")

        # Create styled button container
        button_container = ttk.Frame(container)
        button_container.pack(pady=15)

        # Large, styled predict button
        predict_button = tk.Button(button_container,
                                   text="Calculate Prediction",
                                   command=predict_bill,
                                   font=("Arial", 14, "bold"),
                                   bg="#2E86C1",
                                   fg="white",
                                   padx=30,
                                   pady=10,
                                   relief="raised",
                                   cursor="hand2")
        predict_button.pack()

        # Add hover effect to button
        def on_enter(e):
            predict_button['background'] = '#2874A6'

        def on_leave(e):
            predict_button['background'] = '#2E86C1'

        predict_button.bind("<Enter>", on_enter)
        predict_button.bind("<Leave>", on_leave)

        # Result display with large font and padding
        result_frame = ttk.Frame(container)
        result_frame.pack(pady=15)

        tk.Label(result_frame,
                 textvariable=result_text,
                 font=("Arial", 18, "bold"),
                 fg="#2E86C1").pack(pady=10)

    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

    model = genai.GenerativeModel("gemini-2.5-flash")
    chat_session = model.start_chat(history=[])
    def create_chatbot_page(self):
        # --- FIX 1: Configure API Key Directly ---
        # (Replace "YOUR_PASTED_API_KEY" with the actual key you sent)
        genai.configure(api_key="AIzaSyDJvJq4J8Jv4dKCLkylfEWm1N91qWrIxLQ")

        # --- FIX 2: Create Session attached to 'self' ---
        if not hasattr(self, 'chat_session'):
            # Using 2.5-flash as previously discussed
            model = genai.GenerativeModel("gemini-2.5-flash")
            self.chat_session = model.start_chat(history=[])

        frame, scrollable_frame = self.frames['chatbot']
        self.create_navigation_bar(frame)

        # Centered container
        container = ttk.Frame(scrollable_frame)
        container.pack(pady=50, anchor="center")

        ttk.Label(container,
                  text="Chat with Energy Assistant",
                  font=("Helvetica", 24, "bold")).pack(pady=20)

        # Chat Text Area
        chatbot_text = tk.Text(container, height=25, width=170, font=("Arial", 12), bg="#F5F5F5")
        chatbot_text.pack(pady=10)

        # Tags for colors
        chatbot_text.tag_config("user_tag", foreground="blue", font=('Helvetica', 12, "bold"))
        chatbot_text.tag_config("user_text", foreground="black", font=('Arial', 12))
        chatbot_text.tag_config("bot_tag", foreground="green", font=('Helvetica', 12, "bold"))
        chatbot_text.tag_config("bot_text", foreground="black", font=('Arial', 12))

        question_frame = ttk.Frame(container)
        question_frame.pack(pady=10, fill="x")

        question_var = tk.StringVar()

        # Enter key handler
        def on_enter_pressed(event):
            chatbot_reply()

        question_entry = tk.Entry(question_frame, textvariable=question_var, font=("Arial", 12), width=170,
                                  bg="lightgray", highlightcolor="blue")
        question_entry.pack(side="left", padx=5, ipady=15)
        question_entry.bind("<Return>", on_enter_pressed)

        # --- CORE CHAT FUNCTION ---
        def chatbot_reply():
            question = question_var.get()
            if not question.strip(): return

            # 1. Display User Message
            chatbot_text.insert(tk.END, "You: ", "user_tag")
            chatbot_text.insert(tk.END, f"{question}\n", "user_text")
            question_var.set("")
            chatbot_text.see(tk.END)

            # 2. Define background task
            def fetch_response():
                try:
                    local_answers = {
                        "how to save energy?": "Turn off unused appliances, use LED bulbs, and limit AC usage.",
                        "why is my bill high?": "Check for high-consumption appliances and reduce their usage."
                    }

                    if question.lower() in local_answers:
                        response_text = local_answers[question.lower()]
                    else:
                        # --- FIX 3: Use 'self.chat_session' ---
                        # In your old code, you just wrote 'chat_session', which Python didn't know.
                        response = self.chat_session.send_message(question)
                        response_text = response.text

                except Exception as e:
                    response_text = f"Error: {e}"

                # 3. Update GUI safely
                def update_gui():
                    chatbot_text.insert(tk.END, "Bot: ", "bot_tag")
                    chatbot_text.insert(tk.END, f"{response_text}\n\n", "bot_text")
                    chatbot_text.see(tk.END)

                container.after(0, update_gui)

            # 4. Start Thread
            threading.Thread(target=fetch_response, daemon=True).start()

        # Ask Button
        ask_button = tk.Button(
            container,
            text="Send",
            command=chatbot_reply,
            bg="black",
            fg="white",
            font=("Helvetica", 12),
            relief="flat",
            height=0,
            padx=15,
            pady=5
        )
        ask_button.pack(side="left", padx=10)

        # Add instructions

        
    def create_report_page(self):
        frame, scrollable_frame = self.frames['report']
        self.create_navigation_bar(frame)

        # Centered container
        container = ttk.Frame(scrollable_frame)
        container.pack(pady=50, anchor="center")

        # Title
        ttk.Label(container,
                  text="Energy Usage Report",
                  font=("Helvetica", 24, "bold")).pack(pady=20)

        # Create text widget first
        self.report_display = tk.Text(container,
                                      height=15,
                                      width=70,
                                      font=("Arial", 12))
        self.report_display.pack(pady=10)

        def generate_report():
            # Clear previous content
            self.report_display.delete(1.0, tk.END)

            if not self.user_appliances:
                messagebox.showinfo("No Data", "No appliances data to generate report.")
                return

            report_text = "📊 Appliance Usage Report 📊\n\n"
            total_hours = sum(self.user_appliances.values())

            report_text += f"Total Hours of Appliance Usage: {total_hours} hrs/day\n\n"

            # Add appliance details
            for appliance, hours in self.user_appliances.items():
                percentage = (hours / total_hours) * 100
                report_text += f"🔌 {appliance}: {hours} hrs/day ({percentage:.1f}%)\n"

            # Add usage analysis
            report_text += "\n💡 Usage Analysis:\n"
            for appliance, hours in self.user_appliances.items():
                if hours > 8:
                    report_text += f"⚠️ High usage: {appliance} ({hours} hrs/day)\n"
                elif hours > 4:
                    report_text += f"ℹ️ Moderate usage: {appliance} ({hours} hrs/day)\n"
                else:
                    report_text += f"✅ Efficient usage: {appliance} ({hours} hrs/day)\n"

            # Insert the report text
            self.report_display.tag_config("result_style",font=("Arial",13,"bold"),foreground="#fc6f03")
            self.report_display.insert(tk.END, report_text,"result_style")

        # Add generate button with styling
        generate_button = tk.Button(
            container,
            text="Generate Report",
            command=generate_report,
            font=("Arial", 12, "bold"),
            bg="#2E86C1",
            fg="white",
            padx=20,
            pady=10
        )
        generate_button.pack(pady=10)

        # Add instructions
        instructions = """
        Instructions:
        1. First add your appliances in the 'Add Appliance' section
        2. Come back to this page and click 'Generate Analysis'
        3. View your personalized energy usage analysis and recommendations
        """

        ttk.Label(scrollable_frame,
                  text=instructions,
                  font=("Helvetica", 12,"bold"),
                  foreground="#003366",
                  justify="left").pack(pady=20, padx=20)
        
    def create_analysis_page(self):
        frame, scrollable_frame = self.frames['analysis']
        self.create_navigation_bar(frame)

        # Centered container
        container = ttk.Frame(scrollable_frame)
        container.pack(pady=50, anchor="center")

        # Title
        ttk.Label(container,
                  text="Usage Analysis",
                  font=("Helvetica", 24, "bold")).pack(pady=20)

        # Create frame to hold the canvas
        self.chart_frame = ttk.Frame(container)
        self.chart_frame.pack(pady=20, fill="both", expand=True)

        # Create frame for analysis text
        self.analysis_text_frame = ttk.Frame(container)
        self.analysis_text_frame.pack(pady=20, padx=20, fill="x")

        def generate_analysis():
            # Clear previous charts and analysis
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            for widget in self.analysis_text_frame.winfo_children():
                widget.destroy()

            if not self.user_appliances:
                messagebox.showwarning("No Data", "Please add appliances first in the 'Add Appliance' section!")
                return

            # Create DataFrame from user's appliances
            appliances = list(self.user_appliances.keys())
            hours = list(self.user_appliances.values())

            # Estimate energy costs (example calculation - you can modify this)
            energy_costs = []
            for appliance, hour in self.user_appliances.items():
                # Different base costs for different appliances
                base_cost = {
                    "Fan": 0.45,
                    "Air Conditioner": 7,
                    "Refrigerator": 1.5,
                    "TV": 0.80,
                    "Washing Machine": 4,
                    "led":0.50
                }.get(appliance, 0.65)  # Default cost if appliance not in dict
                cost = base_cost * hour
                energy_costs.append(cost)

            data = {
                "Appliance": appliances,
                "Usage_Hours_Per_Day": hours,
                "Energy_Cost_Per_Day": energy_costs
            }
            df = pd.DataFrame(data)

            # Create figure for matplotlib
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
            fig.suptitle('Your Energy Usage Analysis', fontsize=16)

            max_cost = df['Energy_Cost_Per_Day'].max()
            min_cost = df['Energy_Cost_Per_Day'].min()

            def assign_color(x, min_cost, max_cost):
                if x == max_cost:
                    return 'red'  # High cost
                elif x == min_cost:
                    return 'green'  # Low cost
                elif x >= (min_cost + max_cost) / 3:
                    return 'skyblue'  # Moderate-High cost
                else:
                    return 'yellow'  # Moderate-Low cost

            colors = df['Energy_Cost_Per_Day'].apply(lambda x: assign_color(x, min_cost, max_cost))

            # Bar Plot for current usage
            bars = ax1.bar(df['Appliance'], df['Energy_Cost_Per_Day'], color=colors)
            ax1.set_title('Daily Energy Cost by Your Appliances')
            ax1.set_xlabel('Appliance')
            ax1.set_ylabel('Estimated Cost (₹)')
            ax1.tick_params(axis='x', rotation=45)



            # Add value labels on the bars
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width() / 2., height,
                         f'₹{int(height)}',
                         ha='center', va='bottom')

            # Scatter plot with regression line
            X = df['Usage_Hours_Per_Day']
            y = df['Energy_Cost_Per_Day']

            ax2.scatter(X, y)
            ax2.set_title('Your Usage Hours vs Cost')
            ax2.set_xlabel('Usage Hours Per Day')
            ax2.set_ylabel('Estimated Cost (₹)')

            # Add regression line if we have more than one point
            if len(X) > 1:
                model = LinearRegression()
                model.fit(X.values.reshape(-1, 1), y)
                line_x = np.linspace(X.min(), X.max(), 100)
                line_y = model.predict(line_x.reshape(-1, 1))
                ax2.plot(line_x, line_y, color='red', linestyle='--')

            # Adjust layout
            plt.tight_layout()

            # Create canvas for matplotlib figure
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

            # Calculate total daily cost
            total_cost = sum(energy_costs)

            # Add analysis text
            analysis_text = f"""
                    Analysis Summary:

                    📊 Total Daily Energy Cost: ₹{total_cost:.2f}

                    Breakdown by Appliance:
                    """

            for appliance, hours, cost in zip(appliances, hours, energy_costs):
                percentage = (cost / total_cost) * 100
                analysis_text += f"\n• {appliance}: {hours} hours/day - ₹{cost:.2f} ({percentage:.1f}% of total cost)"

            analysis_label = ttk.Label(
                self.analysis_text_frame,
                text=analysis_text,
                font=("Helvetica", 13,"bold"),
                justify="left"
            )
            analysis_label.pack(pady=10)

            # Add recommendations based on usage
            recommendations = "\nRecommendations for Energy Savings:\n"

            for appliance, hours in self.user_appliances.items():
                if hours > 6:
                    recommendations += f"\n• Consider reducing {appliance} usage ({hours} hours/day is high)"
                elif hours > 4:
                    recommendations += f"\n• Monitor {appliance} usage to optimize efficiency"

            recommendations_label = ttk.Label(
                self.analysis_text_frame,
                text=recommendations,
                font=("Helvetica", 13,"bold"),
                justify="left"
            )
            recommendations_label.pack(pady=10)

        # Create styled button for generating analysis
        generate_button = tk.Button(
            container,
            text="Generate Analysis from Your Appliances",
            command=generate_analysis,
            font=("Arial", 12, "bold"),
            bg="#2E86C1",
            fg="white",
            padx=20,
            pady=10,
            relief="raised",
            cursor="hand2"
        )
        generate_button.pack(pady=20)

        # Add hover effect to button
        def on_enter(e):
            generate_button['background'] = '#2874A6'

        def on_leave(e):
            generate_button['background'] = '#2E86C1'

        generate_button.bind("<Enter>", on_enter)
        generate_button.bind("<Leave>", on_leave)

        # Add instructions
        instructions = """
                Instructions:
                1. First add your appliances in the 'Add Appliance' section
                2. Come back to this page and click 'Generate Analysis'
                3. View your personalized energy usage analysis and recommendations
                """

        ttk.Label(scrollable_frame,
                  text=instructions,
                  font=("Helvetica", 12,"bold"),
                  foreground="#003366",
                  justify="left").pack(pady=20, padx=20)

    def create_mlreport_page(self):
        frame, scrollable_frame = self.frames['mlreport']
        self.create_navigation_bar(frame)

        # Centered container
        container = ttk.Frame(scrollable_frame)
        container.pack(pady=50, anchor="center")

        # Title
        ttk.Label(container,
                  text="ML Analysis Report",
                  font=("Helvetica", 24, "bold")).pack(pady=20)

        # Create frame to hold the canvas and analysis
        self.ml_chart_frame = ttk.Frame(container)
        self.ml_chart_frame.pack(pady=20, fill="both", expand=True)

        # Create frame for analysis text
        self.ml_analysis_frame = ttk.Frame(container)
        self.ml_analysis_frame.pack(pady=20, padx=20, fill="x")

        def get_energy_savings(appliance, usage_hours):
            # Base costs for different appliances (₹ per hour)
            base_costs = {
                "Fan": 2,
                "Air Conditioner": 15,
                "Refrigerator": 4,
                "TV": 3,
                "Washing Machine": 5
            }

            # Get base cost for the appliance
            base_cost = base_costs.get(appliance, 5)  # Default 5 if appliance not  # Default 5 if appliance not found

            # Calculate current daily cost
            current_cost = base_cost * usage_hours

            # Calculate cost with 2 hours reduced
            reduced_hours = max(0, usage_hours - 2)  # Ensure hours don't go below 0
            reduced_cost = base_cost * reduced_hours

            # Return potential savings
            return current_cost - reduced_cost

        def analyze_usage_with_ml():
            # Clear previous charts and analysis
            for widget in self.ml_chart_frame.winfo_children():
                widget.destroy()
            for widget in self.ml_analysis_frame.winfo_children():
                widget.destroy()

            if not self.user_appliances:
                messagebox.showwarning("No Data", "Please add appliances first in the 'Add Appliance' section!")
                return

            # Create figure for plots - smaller size
            fig = plt.figure(figsize=(8, 4))
            plt.clf()  # Clear the figure

            # Sort appliances by usage hours
            sorted_apps = sorted(self.user_appliances.items(), key=lambda x: x[1], reverse=True)
            apps, hours = zip(*sorted_apps)

            max_hour = max(hours)
            min_hour = min(hours)
            mid_hour = (max_hour + min_hour) / 2.5

            # Assign colors based on hour usage
            def assign_color(x):
                if x == max_hour:
                    return "red"  # Highest usage
                elif x == min_hour:
                    return "green"  # Lowest usage
                elif x >= mid_hour:
                    return "yellow"  # Moderate-high usage
                else:
                    return "skyblue"  # Moderate-low usage

            colors = [assign_color(h) for h in hours]

            # Create bar chart
            # First subplot with smaller font sizes
            plt.subplot(1, 2, 1)
            bars = plt.bar(apps, hours, color=colors)
            plt.title("Energy Consumption", fontsize=10)
            plt.ylabel("Hours/Day", fontsize=8)
            plt.xlabel("Appliance", fontsize=8)
            plt.xticks(rotation=45, fontsize=8)
            plt.title("Energy Consumption by Appliance", fontsize=12)
            plt.ylabel("Hours/Day")
            plt.xlabel("Appliance")
            plt.xticks(rotation=45)

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{int(height)}h',
                         ha='center', va='bottom')

            # Create pie chart
            plt.subplot(1, 2, 2)
            total_hours = sum(hours)
            plt.pie(hours, labels=apps, autopct='%1.1f%%',
                    startangle=90, colors=plt.cm.Pastel1(np.linspace(0, 1, len(apps))),
                    textprops={'fontsize': 8})
            plt.title("Usage Distribution", fontsize=10)

            plt.tight_layout()

            # Create canvas for matplotlib figure
            canvas = FigureCanvasTkAgg(fig, master=self.ml_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

            # Generate ML Analysis text
            analysis_text = "🤖 Machine Learning Analysis\n\n"

            # Add usage patterns analysis
            analysis_text += "📊 Usage Patterns:\n"
            for appliance, hours in sorted_apps:
                if hours > 8:
                    analysis_text += f"• {appliance}: Very High Usage ({hours} hrs/day)\n"
                elif hours > 4:
                    analysis_text += f"• {appliance}: High Usage ({hours} hrs/day)\n"
                else:
                    analysis_text += f"• {appliance}: Normal Usage ({hours} hrs/day)\n"

            # Add savings predictions
            analysis_text += "\n💰 Predicted Daily Savings:\n"
            total_savings = 0
            for appliance, hours in sorted_apps:
                if hours > 2:
                    savings = get_energy_savings(appliance, hours)
                    total_savings += savings
                    analysis_text += f"• Reduce {appliance} by 2 hrs: Save ₹{savings:.2f}\n"

            analysis_text += f"\n📈 Total Potential Daily Savings: ₹{total_savings:.2f}"

            # Add recommendations
            analysis_text += "\n\n🎯 AI Recommendations:\n"
            for appliance, hours in sorted_apps:
                if hours > 8:
                    analysis_text += f"• Consider using {appliance} in off-peak hours\n"
                elif hours > 5:
                    analysis_text += f"• Monitor {appliance} usage patterns\n"

            # Create text widget for analysis
            analysis_label = ttk.Label(
                self.ml_analysis_frame,
                text=analysis_text,
                font=("Helvetica", 12),
                justify="left"
            )
            analysis_label.pack(pady=10)

        # Create styled button for analysis
        generate_button = tk.Button(
            scrollable_frame,
            text="Generate ML Analysis",
            command=analyze_usage_with_ml,
            font=("Arial", 12, "bold"),
            bg="#2E86C1",
            fg="white",
            padx=20,
            pady=10,
            relief="raised",
            cursor="hand2"
        )
        generate_button.pack(pady=20)

        # Add hover effect to button
        def on_enter(e):
            generate_button['background'] = '#2874A6'

        def on_leave(e):
            generate_button['background'] = '#2E86C1'

        generate_button.bind("<Enter>", on_enter)
        generate_button.bind("<Leave>", on_leave)

        # Add instructions
        instructions = """
        Instructions:
        1. First add your appliances in the 'Add Appliance' section
        2. Click 'Generate ML Analysis' to see detailed insights
        3. View usage patterns and AI-powered recommendations
        """

        ttk.Label(scrollable_frame,
                  text=instructions,
                  font=("Helvetica", 12),
                  justify="left").pack(pady=20, padx=20)



    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = EnergyBillPredictor()
    app.run()