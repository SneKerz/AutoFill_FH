
import tkinter as tk
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import cv2
from PIL import Image as PIL
from pdf417decoder import PDF417Decoder
from threading import Thread

def preprocess_image(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Enhance contrast
    contrast = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)

    # Binarize the image
    _, binary = cv2.threshold(contrast, 120, 255, cv2.THRESH_BINARY)

    return binary

def autofill_form():
    # Read values from the UI
    first_name = first_name_var.get()
    last_name = last_name_var.get()
    phone_number = phone_number_var.get()
    email = email_var.get()
    booking_reference = booking_reference_var.get()
    airline_name = airline_name_var.get()
    flight_number = flight_number_var.get()
    flight_date = flight_date_var.get()

    # Initialize WebDriver
    webdriver_path = 'C:\\Users\\virst\\Downloads\\geckodriver-v0.34.0-win32\\geckodriver.exe'
    firefox_binary_path = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
    options = Options()
    options.binary_location = firefox_binary_path
    service = Service(webdriver_path)
    driver = webdriver.Firefox(service=service, options=options)

    # Open the webpage
    form_url = 'https://flighthelp.eu/gate-fast-claim/'
    driver.get(form_url)
    time.sleep(2)

    # Autofill the form
    driver.find_element(By.ID, 'input_19_148_3').send_keys(first_name)
    driver.find_element(By.ID, 'input_19_148_6').send_keys(last_name)
    driver.find_element(By.ID, 'input_19_54_raw').send_keys(phone_number)
    driver.find_element(By.ID, 'input_19_57').send_keys(email)
    driver.find_element(By.ID, 'input_19_61').send_keys(booking_reference)

    boarding_airport_select = Select(driver.find_element(By.ID, 'input_19_178'))
    boarding_airport_select.select_by_index(1)
    
    destination_airport_value = destination_airport_var.get()
    destination_airport_field = driver.find_element(By.ID, 'input_19_180')
    destination_airport_field.send_keys(destination_airport_value)
    time.sleep(2)  # Wait for autocomplete options to appear
    destination_airport_field.send_keys(Keys.ARROW_DOWN, Keys.ENTER)

    # Autocomplete for Airline Name
    airline_name_field = driver.find_element(By.ID, 'input_19_66-ts-control')
    airline_name_field.send_keys(airline_name)
    time.sleep(2)  # Wait for autocomplete options to appear
    airline_name_field.send_keys(Keys.ENTER)

    # Flight Number and Date
    driver.find_element(By.ID, 'input_19_135').send_keys(flight_number)
    driver.find_element(By.ID, 'input_19_69').send_keys(flight_date)

    # Keep the browser open
    input("Press Enter in the console to close the browser...")
    driver.quit()

# Create the Tkinter UI
root = tk.Tk()
root.title("Form Autofill")

# Define variables
first_name_var = tk.StringVar()
last_name_var = tk.StringVar()
phone_number_var = tk.StringVar()
email_var = tk.StringVar()
booking_reference_var = tk.StringVar()
destination_airport_var = tk.StringVar()
airline_name_var = tk.StringVar()
flight_number_var = tk.StringVar()
flight_date_var = tk.StringVar()

# Create UI elements
tk.Label(root, text="First Name").grid(row=0, column=0)
tk.Entry(root, textvariable=first_name_var).grid(row=0, column=1)

tk.Label(root, text="Last Name").grid(row=1, column=0)
tk.Entry(root, textvariable=last_name_var).grid(row=1, column=1)

tk.Label(root, text="Phone Number").grid(row=2, column=0)
tk.Entry(root, textvariable=phone_number_var).grid(row=2, column=1)

tk.Label(root, text="Email").grid(row=3, column=0)
tk.Entry(root, textvariable=email_var).grid(row=3, column=1)

tk.Label(root, text="Booking Reference").grid(row=4, column=0)
tk.Entry(root, textvariable=booking_reference_var).grid(row=4, column=1)

tk.Label(root, text="Destination Airport").grid(row=8, column=0)
tk.Entry(root, textvariable=destination_airport_var).grid(row=8, column=1)

tk.Label(root, text="Airline Name").grid(row=5, column=0)
tk.Entry(root, textvariable=airline_name_var).grid(row=5, column=1)

tk.Label(root, text="Flight Number").grid(row=6, column=0)
tk.Entry(root, textvariable=flight_number_var).grid(row=6, column=1)

tk.Label(root, text="Flight Date (DD-MM-YYYY)").grid(row=7, column=0)
tk.Entry(root, textvariable=flight_date_var).grid(row=7, column=1)


def scan_barcode():
    def barcode_scanning():
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                continue
        
            ret, frame = cap.read()
            if not ret:
                continue

            processed_frame = preprocess_image(frame)
            pil_image = PIL.fromarray(processed_frame)
            decoder = PDF417Decoder(pil_image)

            if decoder.decode() > 0:
                decoded_data = decoder.barcode_data_index_to_string(0)
                print("Barcode Data:", decoded_data)

                # Barcode format: M1FirstName/LastName BookingRef DepartureAirportCodeDestinationAirportCodeAirlineCode FlightNumber ...
                parts = decoded_data.split()
                if len(parts) >= 4:
                    name_part = parts[0]
                    booking_ref = parts[1]
                    airport_airline = parts[2]  # Contains Departure, Destination airports, and Airline code
                    flight_num = parts[3]  # Flight number

                    # Extracting the destination airport code and airline code
                    destination_airport_code = airport_airline[-5:-2]  # Last 3 characters before airline code
                    airline_code = airport_airline[-2:]  # Last 2 characters (airline code)

                    # Split name part for first and last name
                    names = name_part[2:].split('/')
                    if len(names) >= 2:
                        first_name_var.set(names[1])
                        last_name_var.set(names[0])

                    # Set other details
                    booking_reference_var.set(booking_ref)
                    destination_airport_var.set(destination_airport_code)
                    flight_number_var.set(airline_code + flight_num)  # Correctly combine airline code and flight number

                    # Stop the camera and close window
                    cap.release()
                    cv2.destroyAllWindows()
                    return

            # Display the resulting frame
            cv2.imshow('Barcode/QR code reader', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


        cap.release()
        cv2.destroyAllWindows()

    # Start scanning in a new thread
    Thread(target=barcode_scanning).start()

# Add a button for barcode scanning
tk.Button(root, text="Scan Barcode", command=scan_barcode).grid(row=9, column=0, columnspan=2)




tk.Button(root, text="Start Autofill", command=autofill_form).grid(row=8, column=0, columnspan=2)

# Run the application
root.mainloop()

