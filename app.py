from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Function to get the database connection
def get_db_connection():
    conn = sqlite3.connect('car_rental.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route to view all customers
@app.route('/customers')
def customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Customer")
    customers = cur.fetchall()  # Fetch all customer records
    conn.close()  # Close the connection after use
    return render_template('customer.html', customers=customers)

# Route to add a new customer
@app.route('/add_customer', methods=['POST'])
def add_customer():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            contact_number = request.form['contact_number']
            email = request.form['email']
            driver_license = request.form['driver_license']
            address = request.form['address']

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO Customer (first_name, last_name, contact_number, email, driver_license_number, address) VALUES (?, ?, ?, ?, ?, ?)",
                (first_name, last_name, contact_number, email, driver_license, address)
            )
            conn.commit()
        except Exception as e:
            print("An error occurred:", e)
        finally:
            conn.close()

        return redirect('/customers')



# Route to update a customer's details
@app.route('/update_customer/<int:customer_id>', methods=['POST'])
def update_customer(customer_id):
    conn = None
    if request.method == 'POST':
        try:
            # Extract form data
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            contact_number = request.form['contact_number']
            email = request.form['email']
            driver_license = request.form['driver_license']
            address = request.form['address']

            # Establish database connection
            conn = get_db_connection()
            cur = conn.cursor()

            # Update customer data (use the correct column for the primary key)
            cur.execute("""
                UPDATE Customer
                SET first_name = ?, last_name = ?, contact_number = ?, email = ?, driver_license_number = ?, address = ?
                WHERE customer_id = ?
            """, (first_name, last_name, contact_number, email, driver_license, address, customer_id))
            conn.commit()

        except Exception as e:
            print("An error occurred while updating:", e)
        finally:
            if conn:
                conn.close()

        return redirect('/customers')

# Route to delete a customer
@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete the customer record using the correct column name
        cur.execute("DELETE FROM Customer WHERE customer_id = ?", (customer_id,))
        conn.commit()

    except Exception as e:
        print("An error occurred while deleting:", e)
    finally:
        if conn:
            conn.close()

    return redirect('/customers')


@app.route('/cars', methods=['GET', 'POST'])
def manage_cars():
    conn = get_db_connection()

    if request.method == 'POST':
        # Handling car addition form submission
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        registration_number = request.form['registration_number']
        rental_price_per_day = request.form['rental_price_per_day']
        availability_status = request.form['availability_status']
        last_maintenance_date = request.form['last_maintenance_date']
        license_plate = request.form['license_plate']

        # Insert new car into the database
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Car (make, model, year, registration_number, rental_price_per_day, availability_status, last_maintenance_date, license_plate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (make, model, year, registration_number, rental_price_per_day, availability_status, last_maintenance_date, license_plate))
        conn.commit()

    # Retrieve all available cars (filtering by availability status)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Car WHERE availability_status = 'available'")
    available_cars = cur.fetchall()

    conn.close()

    # Render the template with available cars data
    return render_template('cars.html', cars=available_cars)

# Route to update a car's details
@app.route('/update_car/<int:car_id>', methods=['POST'])
def update_car(car_id):
    conn = get_db_connection()
    try:
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        registration_number = request.form['registration_number']
        rental_price_per_day = request.form['rental_price_per_day']
        availability_status = request.form['availability_status']
        last_maintenance_date = request.form['last_maintenance_date']
        license_plate = request.form['license_plate']

        cur = conn.cursor()
        cur.execute("""
            UPDATE Car
            SET make = ?, model = ?, year = ?, registration_number = ?, rental_price_per_day = ?, availability_status = ?, last_maintenance_date = ?, license_plate = ?
            WHERE car_id = ?
        """, (make, model, year, registration_number, rental_price_per_day, availability_status, last_maintenance_date, license_plate, car_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating car: {e}")
    finally:
        conn.close()

    return redirect('/cars')

# Route to delete a car
@app.route('/delete_car/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    conn = get_db_connection()

    try:
        # Delete the car from the database
        cur = conn.cursor()
        cur.execute("DELETE FROM Car WHERE car_id = ?", (car_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting car: {e}")
    finally:
        conn.close()

    return redirect('/cars')

@app.route('/rentals', methods=['GET', 'POST'])
def manage_rentals():
    conn = get_db_connection()  # Open the connection at the start
    cur = conn.cursor()

    if request.method == 'POST':
        try:
            # Get form data
            customer_id = request.form.get('customer_id')
            car_id = request.form.get('car_id')
            rental_start_date = request.form.get('rental_start_date')
            rental_end_date = request.form.get('rental_end_date')
            payment_status = request.form.get('payment_status')
            rental_status = request.form.get('status')  # Ensure this matches your form input name

            # Convert the rental start and end dates to datetime objects
            rental_start_date = datetime.strptime(rental_start_date, '%Y-%m-%d').date()
            rental_end_date = datetime.strptime(rental_end_date, '%Y-%m-%d').date()

            # Calculate the number of rental days
            rental_days = (rental_end_date - rental_start_date).days

            if rental_days <= 0:
                return "Rental end date must be after the start date", 400

            # Fetch the rental price per day for the selected car
            cur.execute("SELECT rental_price_per_day FROM Car WHERE car_id = ?", (car_id,))
            car = cur.fetchone()

            if car is None:
                return "Car with this ID does not exist", 400

            rental_price_per_day = car['rental_price_per_day']
            total_rent = rental_days * rental_price_per_day

            # Insert the rental record into the database
            cur.execute("""INSERT INTO Rental (customer_id, car_id, rental_start_date, rental_end_date, total_rent, payment_status, status)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                           (customer_id, car_id, rental_start_date, rental_end_date, total_rent, payment_status, rental_status))
            conn.commit()

        except sqlite3.Error as e:
            print(f"Database error: {e}")  # Log the error
            return "A database error occurred", 500
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "An error occurred", 500

    # This part executes for both GET and POST requests.
    # Retrieve all rentals after handling the POST request
    cur.execute('''SELECT Rental.rental_id, Car.make, Car.model, Customer.first_name, Customer.last_name, 
                          Rental.rental_start_date, Rental.rental_end_date, Rental.total_rent, 
                          Rental.payment_status, Rental.status 
                   FROM Rental 
                   JOIN Car ON Rental.car_id = Car.car_id 
                   JOIN Customer ON Rental.customer_id = Customer.customer_id''')
    rentals = cur.fetchall()

    conn.close()  # Close the connection after all operations are complete

    return render_template('rentals.html', rentals=rentals)


# Initialize the database (create tables)
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Create the Customer table if it doesn't exist
    cur.execute('''CREATE TABLE IF NOT EXISTS Customer (
                    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    contact_number TEXT,
                    email TEXT,
                    driver_license_number TEXT NOT NULL,
                    address TEXT
                );''')

    # Create the Car table if it doesn't exist
    cur.execute('''CREATE TABLE IF NOT EXISTS Car (
                    car_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    registration_number TEXT NOT NULL,
                    rental_price_per_day REAL NOT NULL,
                    availability_status TEXT NOT NULL,
                    last_maintenance_date TEXT NOT NULL,
                    license_plate TEXT NOT NULL
                );''')

    # Create the Rental table if it doesn't exist
    cur.execute('''CREATE TABLE IF NOT EXISTS Rental (
                    rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    car_id INTEGER NOT NULL,
                    rental_start_date DATE NOT NULL,
                    rental_end_date DATE NOT NULL,
                    total_rent REAL NOT NULL,
                    payment_status TEXT NOT NULL CHECK (payment_status IN ('Paid', 'Pending')),
                    status TEXT NOT NULL CHECK (status IN ('Active', 'Completed', 'Cancelled')),
                    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
                    FOREIGN KEY (car_id) REFERENCES Car(car_id)
                );''')

    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

if __name__ == "__main__":
    app.run(debug=True)