import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyttsx3
import time
import speech_recognition as sr
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import csv
import os

# Initialize TTS engine
engine = pyttsx3.init()

# Global variable to store commands data
command_results = []
# Global variable to store user details
USER_DATA = {}
#to store username after login
current_username = ""
# Placeholder for valid credentials
USER_DATA_FILE = "user_data.csv"

# File to store user details (You could also use SQLite or other databases)
USER_FILE = "user_data.csv"
# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to get voice command
def get_voice_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Please give a command")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio).lower()
            return command
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            speak("Could not request results; check your network connection.")
            return None

# Initialize GUI
root = tk.Tk()
root.title("AVIWA - 'AI Based Voice Integrated Web Automation' Testing")
root.geometry("800x600")
style = ttk.Style()
style.configure(
    "Rounded.TButton",
    padding=10,  # Adds padding
    relief="solid",  # Makes it flat to add border
    foreground="black",  # Text color
    font=("Comic Sans MS", 12),
)


# Function to show profile page
def show_profile():
    global current_username
    clear_frame()

    # Fetch user details from the USER_DATA dictionary using the current_username
    user_details = USER_DATA.get(current_username, {})

    if not user_details:
        messagebox.showerror("Error", "User details not found.")
        return

    # Header of Profile Page
    tk.Label(content_frame, text="Profile Page", font=("Comic Sans MS", 28), bg="white").pack(pady=20)

    # Display user details on the profile page
    details_text = f"""
    Name: {user_details.get('name', 'N/A')}
    Username: {current_username}
    Email: {user_details.get('email', 'N/A')}
    Designation: {user_details.get('designation', 'N/A')}
    Company: {user_details.get('company', 'N/A')}
    """
    profile_label = tk.Label(content_frame, text=details_text, bg="white", font=("Comic Sans MS", 14), justify="left")
    profile_label.pack(pady=20)

    # Logout button to go back to login
    logout_button = ttk.Button(content_frame, text="Logout", command=signout, style="Rounded.TButton")
    logout_button.pack(pady=20)

# Function to clear the content frame
def clear_frame():
    for widget in content_frame.winfo_children():
        widget.destroy()

# Login Page
# Ensure CSV file exists
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Password", "Email", "Username", "Designation", "Company"])
# Function to load user data from CSV file
def load_user_data():
    global USER_DATA
    USER_DATA = {}
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                USER_DATA[row["Username"]] = {
                    'name': row["Name"],
                    'password': row["Password"],
                    'email': row["Email"],
                    'designation': row["Designation"],
                    'company': row["Company"]
                }


# Function to validate login
def validate_login(username, password):
    """Validate username and password from the CSV file."""
    load_user_data()  # Make sure to reload user data before login attempt
    user_details = USER_DATA.get(username)
    if user_details and user_details['password'] == password:
        return user_details  # Return user details if login is successful
    return None

# Function to save user details
def save_user_details(name, username, password, email, designation, company):
    with open(USER_DATA_FILE, mode='a', newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, password, email, username, designation, company])
    load_user_data()  # Reload user data after saving new user details

# Login Page
def login_page():
    """Display the login page."""
    clear_frame()

    tk.Label(content_frame, text="Login", font=("Comic Sans MS", 28), bg="white").pack(pady=20)

    username_label = tk.Label(content_frame, text="Username:", bg="white", font=("Comic Sans MS", 12))
    username_label.pack(pady=5)

    username_entry = tk.Entry(content_frame, width=50, bd=2, relief="raised")
    username_entry.pack(pady=10, ipady=5)

    password_label = tk.Label(content_frame, text="Password:", bg="white", font=("Comic Sans MS", 12))
    password_label.pack(pady=5)

    password_entry = tk.Entry(content_frame, show="*", width=50, bd=2, relief="raised")
    password_entry.pack(pady=10, ipady=5)

    def attempt_login():
        global current_username
        username = username_entry.get()
        password = password_entry.get()
        user_details = validate_login(username, password)
        if user_details:
            speak(f"Aviva, AI Based voice integrated web automation, Welcomes you {username}")
            current_username = username
            show_home()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    login_button = ttk.Button(content_frame, text="Login", command=attempt_login, style="Rounded.TButton")
    login_button.pack(pady=20)

    signup_button = ttk.Button(content_frame, text="Sign Up", command=signup_page, style="Rounded.TButton")
    signup_button.pack(pady=10)

# Sign-up Page
def signup_page():
    """Display the signup page with two inputs side by side, centered."""
    clear_frame()

    # Configure the grid layout of the content_frame to center elements
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_rowconfigure(5, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_columnconfigure(3, weight=1)

    tk.Label(content_frame, text="Sign Up Now", font=("Comic Sans MS", 28), bg="white").grid(
        row=0, column=1, columnspan=2, pady=(10, 5), padx=(140, 0)
    )

    def create_entry(label_text, row, column):
        label = tk.Label(content_frame, text=label_text, bg="white", font=("Comic Sans MS", 12))
        label.grid(row=row, column=column, padx=4, pady=10, sticky="e")
        entry = tk.Entry(content_frame, width=40, bd=2, relief="raised")
        entry.grid(row=row, column=column + 1, padx=4, pady=10, sticky="w")
        return entry

    # Create fields for user inputs
    name_entry = create_entry("Name:", 1, 0)
    username_entry = create_entry("Username:", 1, 2)
    password_entry = create_entry("Password:", 2, 0)
    email_entry = create_entry("Email:", 2, 2)
    designation_entry = create_entry("Designation:", 3, 0)
    company_entry = create_entry("Company:", 3, 2)

    def save_user_details():
        name = name_entry.get()
        username = username_entry.get()
        password = password_entry.get()
        email = email_entry.get()
        designation = designation_entry.get()
        company = company_entry.get()

        if not (name and username and password and email and designation and company):
            messagebox.showerror("Error", "All fields are required!")
            return

        # Save user details to CSV
        save_user_details(name, username, password, email, designation, company)
        messagebox.showinfo("Success", "Signup successful! Please login.")
        login_page()

    # Buttons
    signup_button = ttk.Button(content_frame, text="Sign Up", command=save_user_details, style="Rounded.TButton")
    signup_button.grid(row=4, column=1, padx=2, pady=60, sticky="e")  # Align to the right

    back_button = ttk.Button(content_frame, text="Back to Login", command=login_page, style="Rounded.TButton")
    back_button.grid(row=4, column=2, padx=(10, 0), pady=60, sticky="w")  # Align to the left


# Signout Function
def signout():
    clear_frame()  # Clears the home page content
    global current_username
    current_username = ""
    login_page()



# Logo and Navigation Bar
header = tk.Frame(root, bg="black")
header.pack(fill="x")
logo_label = tk.Label(header, text="AVIWA", font=("Papyrus", 16, "bold"), bg="black", fg="white")
logo_label.pack(side="left", padx=10)
# Main application pages
def show_home():
    clear_frame()
    home_page()

def show_analysis():
    clear_frame()
    analysis_page()

def show_log_test():
    clear_frame()
    log_test_page()
tk.Button(header, text="Home", command=show_home, bg="black", fg="white",font=("Comic Sans MS", 11)).pack(side="left", padx=10,pady=5)
tk.Button(header, text="Analysis", command=show_analysis, bg="black", fg="white",font=("Comic Sans MS", 11)).pack(side="left", padx=10, pady=5)
tk.Button(header, text="Log Test", command=show_log_test, bg="black", fg="white",font=("Comic Sans MS", 11)).pack(side="left", padx=10, pady=5)
tk.Button(header, text="Signout", command=signout, bg="green", fg="white",font=("Comic Sans MS", 11)).pack(side="right", padx=10, pady=5)
tk.Button(header, text="Profile", command=show_profile, bg="black", fg="white",font=("Comic Sans MS", 11)).pack(side="left", padx=10, pady=5)

# Gradient canvas for background
gradient_canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
gradient_canvas.pack(fill="both", expand=True)

# Function to create gradient
def create_gradient(canvas, width, height, start_color, end_color):
    r1, g1, b1 = canvas.winfo_rgb(start_color)
    r2, g2, b2 = canvas.winfo_rgb(end_color)
    
    r1, g1, b1 = r1 // 256, g1 // 256, b1 // 256
    r2, g2, b2 = r2 // 256, g2 // 256, b2 // 256
    
    for i in range(height):
        r = int(r1 + (r2 - r1) * i / height)
        g = int(g1 + (g2 - g1) * i / height)
        b = int(b1 + (b2 - b1) * i / height)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color)

# Draw the gradient
create_gradient(gradient_canvas, 1920, 768, "white", "black")

# Add content_frame on top of the gradient canvas
content_frame = tk.Frame(gradient_canvas, bg="white", highlightbackground="black", highlightthickness=1)
content_frame.place(relwidth=0.9, relheight=0.9, relx=0.05, rely=0.05)

# Home Page
def home_page():

    url_label = tk .Label(content_frame, text="Enter Website URL:", font=("Comic Sans MS", 16),bg="white",)
    url_label.pack(pady=15)
    url_entry = tk.Entry(content_frame, width=80,bd=2, relief="raised")
    url_entry.pack(pady=20,ipady=5)

    def start_testing():
        url = url_entry.get()
        if not url:
            speak("Please enter a URL.")
            return

        driver = webdriver.Chrome()  # Ensure ChromeDriver is in PATH
        driver.get(url)
        time.sleep(3)  # Allow page to load
        wait = WebDriverWait(driver, 10)

        while True:
            command = get_voice_command()
            if command is None:
                continue
            
            result = {"command": command, "status": "success", "error": None}
            try:
                
                
                if "search for" in command:
                    search_term = command.replace("search for", "").strip()
                    search_box = None

                        # Handle Amazon
                    if "amazon" in driver.current_url:
                        search_box = wait.until(EC.element_to_be_clickable((By.ID, "twotabsearchtextbox")))
                        
                        # Handle Flipkart
                    elif "flipkart" in driver.current_url:
                        search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
                        
                        # General e-commerce sites and other cases
                    else:
                        try:
                                # General search field identifiers
                            search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))  # Common name attribute
                        except:
                            try:
                                search_box = wait.until(EC.element_to_be_clickable((By.ID, "search")))  # General ID-based approach
                            except:
                                try:
                                    search_box = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "search-box")))  # Class-based approach
                                except:
                                    try:
                                        search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='search']")))  # Generic approach
                                    except:
                                        speak("Search bar not found on this website.")
                                        result["status"] = "failure"
                                        continue

                    if search_box:
                        search_box.clear()
                        search_box.send_keys(search_term)
                        search_box.send_keys(Keys.RETURN)  # Submit search
                        speak(f"Searched for {search_term}")

    

                
                elif "click on" in command and "product" in command:
                    words = command.split()
                    # Extract the index (first, second, etc.) and map it to an integer
                    if "first" in words:
                        product_index = 1
                    elif "second" in words:
                        product_index = 2
                    elif "third" in words:
                        product_index = 3
                    else:
                        product_index = int(words[words.index("product") - 1])

                    # Find product by index (example for Flipkart or Amazon)
                    product_xpath = f"(//div[contains(@class,'product')])[{product_index}]"  # Adjust this based on product listing
                    product = wait.until(EC.element_to_be_clickable((By.XPATH, product_xpath)))
                    product.click()
                    print(f"Clicked on product {product_index}")
                    engine.say(f"Clicked on product {product_index}")
                    engine.runAndWait()
                
                elif "add to cart" in command:
                    add_cart_button = driver.find_element(By.CLASS_NAME, "add-to-cart")
                    add_cart_button.click()
                    speak("Added item to cart.")
                
                elif "click" in command:
                    button_name = command.replace("click", "").strip().lower()
                    button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{button_name}')] | "
                        f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{button_name}')]")
                    ))

                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        speak(f"Clicked on {button_name} button.")
                    else:
                        speak(f"{button_name} button is not clickable.")


                elif "scroll down" in command:
                    driver.execute_script("window.scrollBy(0, 250);")
                    speak("Scrolled down.")

                elif "scroll up" in command:
                    driver.execute_script("window.scrollBy(0, -250);")
                    speak("Scrolled up.")

                elif "enter" in command:
                    parts = command.split()
                    if len(parts) >= 3:
                        # The first word is 'enter', the second is the field name, and the rest is the value
                        field_name = parts[1].lower()
                        value = ' '.join(parts[2:])
                        input_field = wait.until(EC.element_to_be_clickable((By.NAME, field_name)))
                        input_field.clear()
                        input_field.send_keys(value)
                        speak(f"Entered {value} in {field_name}.")


                elif "stop" in command:
                    speak("Stopping the automation.")
                    break

                else:
                    result["status"] = "failure"
                    speak("Unknown command.")
                    continue

            except Exception as e:
                result["status"] = "failure"
                result["error"] = str(e)
                speak(f"An error occurred:{command}")

            command_results.append(result)

        driver.quit()
        speak("Testing complete.")

    tk.Button(content_frame, text="Start Testing",font=("Comic Sans MS", 12),bg="white" ,command=start_testing).pack(pady=10)
    image_path = "1.png"  # Replace with your image file path
  
    img = Image.open(image_path)  # Open the image
    img = img.resize((600, 300))  # Resize the image to fit in your window
    img_tk = ImageTk.PhotoImage(img)  # Convert image to Tkinter format
    image_label = tk.Label(content_frame, image=img_tk,bg="white")  # Create a label to hold the image
    image_label.image = img_tk  # Keep a reference to avoid garbage collection
    image_label.pack(pady=20)


    
# Analysis Page
def analysis_page():
    tk.Label(content_frame, text="Analysis Page - Test Results and Report", font=("Comic Sans MS", 20),bg="white").pack(pady=10)

    success_count = sum(1 for result in command_results if result["status"] == "success")
    failure_count = len(command_results) - success_count
    failure_rate = (failure_count / len(command_results)) * 100 if command_results else 0

    fig, ax = plt.subplots()
    ax.pie([success_count, failure_count], labels=["Success", "Failure"], autopct='%1.1f%%', colors=["#4CAF50", "#FF5722"])
    ax.set_title("Test Execution Success vs Failure")
    canvas = FigureCanvasTkAgg(fig, master=content_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

    def generate_pdf_report():
        pdf = FPDF()
        margin = 5  # Margin size in mm
        page_width = pdf.w
        page_height = pdf.h

        def add_border():
            pdf.set_draw_color(0, 0, 0)  # Black color
            pdf.rect(margin, margin, page_width - 2 * margin, page_height - 2 * margin)

        # Add a title page
        pdf.add_page()
        add_border()
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, "AVIWA Test Report", 0, 1, "C")
        pdf.ln(10)

        # Add summary section
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Total Commands: {len(command_results)}", 0, 1)
        pdf.cell(0, 10, f"Successful Commands: {success_count}", 0, 1)
        pdf.cell(0, 10, f"Failed Commands: {failure_count}", 0, 1)
        pdf.cell(0, 10, f"Failure Rate: {failure_rate:.2f}%", 0, 1)
        pdf.ln(10)

        # Add website description based on failure rate
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Website Testing Summary", 0, 1)
        pdf.set_font("Arial", "", 14)
        if failure_rate == 0:
            description = (
                "The tested websites demonstrated excellent performance with no detected failures. "
                "They are highly reliable and well-suited for automation tasks."
            )
        elif 1 <= failure_rate <= 25:
            description = (
                "The tested websites performed well with minimal failures. "
                "They are generally reliable but may require minor optimizations."
            )
        elif 26 <= failure_rate <= 50:
            description = (
                "The tested websites showed moderate performance with some areas needing improvement. "
                "Consider addressing identified issues for smoother automation."
            )
        elif 51 <= failure_rate <= 75:
            description = (
                "The tested websites faced significant challenges during automation. "
                "They may not be fully optimized for automation workflows and require attention."
            )
        else:  # 76-100%
            description = (
                "The tested websites exhibited a high failure rate, indicating potential reliability issues. "
                "Comprehensive evaluation and fixes are recommended before automation."
            )
        pdf.multi_cell(0, 10, description)
        pdf.ln(10)


        # Save the pie chart as an image and add it to the PDF
        pie_chart_path = "pie_chart.png"
        fig, ax = plt.subplots()
        ax.pie(
            [success_count, failure_count],
            labels=["Success", "Failure"],
            autopct='%1.1f%%',
            colors=["#4CAF50", "#FF5722"]
        )
        ax.set_title("Test Execution Success vs Failure")
        plt.savefig(pie_chart_path)
        plt.close()
        pdf.image(pie_chart_path, x=margin + 10, y=pdf.get_y(), w=page_width - 2 * margin - 20)
        pdf.ln(100)


        # Add detailed results section
        pdf.add_page()
        add_border()
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 20, "Detailed Command Results:", 0, 1)
        pdf.ln(5)

        for i, result in enumerate(command_results, 1):
            # Bold font for the title
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"{i}. Command:", 0, 1)

            # Normal font for the value
            pdf.set_font("Arial", "", 14)
            pdf.cell(0, 10, f"   {result['command']}", 0, 1)

            # Bold font for the status title
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "   Status:", 0, 1)

            # Normal font for the status value
            pdf.set_font("Arial", "", 14)
            pdf.cell(0, 10, f"      {result['status']}", 0, 1)

            if result["error"]:
                # Bold font for the error title
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "   Error:", 0, 1)

                # Normal font for the error value
                pdf.set_font("Arial", "", 14)
                pdf.cell(0, 10, f"      {result['error']}", 0, 1)

            pdf.ln(2)

            # Add a new page with a border if content exceeds the page height
            if pdf.get_y() > page_height - margin - 20:
                pdf.add_page()
                add_border()

        # Save the PDF
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if save_path:
            pdf.output(save_path)
            messagebox.showinfo("Report Saved", f"Report saved to {save_path}")

        # Remove the temporary pie chart image
        import os
        if os.path.exists(pie_chart_path):
            os.remove(pie_chart_path)


    tk.Button(content_frame, text="Generate PDF Report",font=("Comic Sans MS", 12),bg="white" , command=generate_pdf_report).pack(pady=10)

# Log Test Page
def log_test_page():
    tk.Label(content_frame, text="Log Test Page - Analyze Web Log Files", font=("Comic Sans MS", 16),bg="white").pack(pady=10)
    log_display = scrolledtext.ScrolledText(content_frame, width=80, height=15)
    log_display.pack(pady=10)
    
    # Placeholder to store the generated report
    analysis_report = []

    def analyze_log():
        file_path = filedialog.askopenfilename(title="Select Log File", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if not file_path:
            return

        # Read the log file
        with open(file_path, 'r') as file:
            logs = file.readlines()
        log_display.insert("end", "".join(logs) + "\n")

        # Analyze basic log details
        analysis_report.append(f"File Analyzed: {file_path}\n")
        analysis_report.append(f"Total Requests: {len(logs)}\n")

        # Count errors (404 and 500)
        error_count = sum(1 for line in logs if "404" in line or "500" in line)
        failure_rate = (error_count / len(logs)) * 100 if logs else 0
        analysis_report.append(f"Total Errors: {error_count}\n")
        analysis_report.append(f"Failure Rate: {failure_rate:.2f}%\n")

        # List up to 5 error details
        error_details = [line.strip() for line in logs if "404" in line or "500" in line][:5]
        analysis_report.append("Error Details (First 5):\n" + "\n".join(error_details) + "\n")

        # Use the log data file for training the model
        try:
            # Load dataset and preprocess
            dataset = pd.read_csv(file_path)
            if 'Status' not in dataset.columns:
                raise ValueError("Dataset must contain a 'status' column.")

            # Example preprocessing: filtering numeric columns for simplicity
            features = dataset.drop(columns=['Status'], errors='ignore')
            labels = dataset['Status']

            # Convert categorical data to numeric if necessary
            for column in features.select_dtypes(include=['object']).columns:
                features[column] = features[column].astype('category').cat.codes

            # Split dataset into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

            # Train the Random Forest Classifier
            model = RandomForestClassifier(n_estimators=10, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            # Generate a classification report
            report = classification_report(y_test, y_pred)
            analysis_report.append("--- Log Analysis Report ---\n")
            analysis_report.append(report + "\n")

            # Display the report in the log_display
            log_display.insert("end", f"\n{report}\n")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing the dataset: {str(e)}")
            return

    # Export report to a file
    def export_report():
        if not analysis_report:
            messagebox.showwarning("Warning", "No analysis report to save.")
            return

    # Ask user where to save the report
    save_path = filedialog.asksaveasfilename(
        title="Save Report",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )

    if save_path:
        # Write the report to the file
        with open(save_path, 'w') as report_file:
            report_file.write("\n".join(analysis_report))
        messagebox.showinfo("Report Saved", f"Report saved to {save_path}")

   
    

    # Log display
    log_display = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=80, height=20, font=("Comic Sans MS", 12))
    log_display.pack(pady=10)
    
    tk.Button(content_frame, text="Analyze Log", font=("Comic Sans MS", 12),bg="white", command=analyze_log).pack(pady=15)
    tk.Button(content_frame, text="Export Report", font=("Comic Sans MS", 12),bg="white", command=export_report).pack(pady=5)

# Start with the login page
login_page()

root.mainloop()
