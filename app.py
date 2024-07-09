from flask import Flask, request, jsonify, render_template_string
from threading import Thread
from queue import Queue
import time

app = Flask(__name__)

# Konfigurasi produksi
app.config['ENV'] = 'production'

# Simulated database for showtimes, seat availability, and seating formation
showtimes = {
    "2024-06-26 10:00": {
        "movie": "Galaksi Jauh: Petualangan Antar Bintang",
        "seats": {f"{row}{num}": True for row in "ABCDE" for num in range(1, 11)},
        "sold_tickets": 0,
        "max_tickets": 50,
        "formation": "teater"
    },
    "2024-06-26 13:00": {
        "movie": "Legenda Raja Laut: Kembalinya Sang Pahlawan",
        "seats": {f"{row}{num}": True for row in "ABCDE" for num in range(1, 11)},
        "sold_tickets": 0,
        "max_tickets": 50,
        "formation": "arena"
    },
    "2024-06-26 16:00": {
        "movie": "Misteri Pulau Hantu",
        "seats": {f"{row}{num}": True for row in "ABCDE" for num in range(1, 11)},
        "sold_tickets": 0,
        "max_tickets": 50,
        "formation": "lurus"
    },
    "2024-06-26 19:00": {
        "movie": "Petualangan Waktu: Mesin Penjelajah Masa",
        "seats": {f"{row}{num}": True for row in "ABCDE" for num in range(1, 11)},
        "sold_tickets": 0,
        "max_tickets": 50,
        "formation": "vip"
    }
}

# Booking history
booking_history = []

# FIFO Queue for booking requests
booking_queue = Queue()

# Function to process booking requests from the queue
def process_booking_queue():
    while True:
        if not booking_queue.empty():
            booking_request = booking_queue.get()
            response = process_booking(booking_request)
            booking_queue.task_done()
            print(response)  # Optional: Print response to the console for debugging
        time.sleep(1)

# Function to process a single booking request
def process_booking(data):
    showtime = data.get('showtime')
    seat = data.get('seat')
    name = data.get('name')

    if not showtime or not seat or not name:
        return {"status": "error", "message": "Missing booking information."}

    if showtimes[showtime]["sold_tickets"] >= showtimes[showtime]["max_tickets"]:
        return {"status": "error", "message": "Maximum number of tickets sold for this showtime."}

    if not showtimes[showtime]["seats"].get(seat, False):
        return {"status": "error", "message": "Seat already booked or invalid seat."}

    showtimes[showtime]["seats"][seat] = False
    showtimes[showtime]["sold_tickets"] += 1
    booking_history.append({
        "name": name,
        "movie": showtimes[showtime]["movie"],
        "showtime": showtime,
        "seat": seat,
        "purchase_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    })
    return {"status": "success", "message": "Seat successfully booked!", "movie": showtimes[showtime]["movie"]}

@app.route('/')
def index():
    showtimes_html = generate_showtimes_html()
    history_html = generate_history_html()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Movie Ticket Booking System</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f9;
            }
            h1, h2, h3 {
                text-align: center;
                color: #333;
            }
            #showtimes {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }
            .showtime {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                max-width: 300px;
                width: 100%;
                transition: transform 0.3s, box-shadow 0.3s;
                cursor: pointer;
                text-align: center;
                position: relative;
            }
            .showtime:hover {
                transform: scale(1.05);
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            }
            .seats {
                display: flex;
                flex-direction: column;
                gap: 10px;
                margin-top: 10px;
            }
            .seat-row {
                display: flex;
                justify-content: center;
                gap: 5px;
            }
            .seat {
                padding: 10px;
                font-size: 14px;
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                transition: background-color 0.3s;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .seat:disabled {
                background-color: #ccc;
                cursor: not-allowed;
            }
            .seat:not(:disabled):hover {
                background-color: #45a049;
            }
            #notification {
                margin-top: 20px;
                text-align: center;
                color: #e74c3c;
            }
            #booking-history {
                margin-top: 20px;
                text-align: center;
            }
            #booking-history table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 18px;
                text-align: left;
            }
            #booking-history table thead tr {
                background-color: #f2f2f2;
                text-align: left;
            }
            #booking-history table th, #booking-history table td {
                padding: 12px 15px;
            }
            #booking-history table th {
                background-color: #f2f2f2;
            }
            #booking-history table tbody tr {
                border-bottom: 1px solid #dddddd;
            }
            #booking-history table tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }
            #booking-history table tbody tr:last-of-type {
                border-bottom: 2px solid #009879;
            }
            #booking-history table tbody tr.active-row {
                font-weight: bold;
                color: #009879;
            }
            .select-button {
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 4px;
                transition: background-color 0.3s;
                margin-top: 10px;
            }
            .select-button:hover {
                background-color: #0056b3;
            }
            .seat-plan {
                display: none;
                flex-direction: column;
                align-items: center;
                margin-top: 10px;
            }
            .showtime[data-formation='teater'] .seat-plan .seat-row:nth-child(even) {
                justify-content: flex-start;
            }
            .showtime[data-formation='arena'] .seat-plan {
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: center;
            }
            .showtime[data-formation='lurus'] .seat-plan .seat-row {
                justify-content: flex-start;
            }
            .showtime[data-formation='vip'] .seat-plan .seat {
                width: 50px;
                height: 50px;
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <h1>Movie Ticket Booking System</h1>
        <div id="showtimes">
            {{ showtimes_html|safe }}
        </div>
        <div id="notification"></div>
        <h2>Booking History</h2>
        <div id="booking-history">
            {{ history_html|safe }}
        </div>
        <script>
            function bookSeat(showtime, seat) {
                const name = prompt("Enter your name:");
                if (!name) {
                    alert("Name is required to book a seat.");
                    return;
                }

                fetch('/book', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ showtime, seat, name })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('notification').innerText = data.message;
                    if (data.status === 'success') {
                        document.getElementById(`${showtime}-${seat}`).disabled = true;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }

            function deleteBooking(index) {
                fetch('/delete_booking', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ index })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        </script>
    </body>
    </html>
    ''', showtimes_html=showtimes_html, history_html=history_html)

def generate_showtimes_html():
    showtimes_html = ""
    for showtime, details in showtimes.items():
        seats_html = generate_seats_html(showtime)
        showtimes_html += f'''
        <div class="showtime" data-formation="{details["formation"]}">
            <h3>{details["movie"]}</h3>
            <p>{showtime}</p>
            <div class="seat-plan">
                {seats_html}
            </div>
            <button class="select-button" onclick="this.nextElementSibling.style.display = 'flex'">Select Seats</button>
        </div>
        '''
    return showtimes_html

def generate_seats_html(showtime):
    seats_html = ""
    seats = showtimes[showtime]["seats"]
    for row in "ABCDE":
        seats_html += '<div class="seat-row">'
        for num in range(1, 11):
            seat = f"{row}{num}"
            disabled = "disabled" if not seats[seat] else ""
            seats_html += f'<button id="{showtime}-{seat}" class="seat" {disabled} onclick="bookSeat(\'{showtime}\', \'{seat}\')">{seat}</button>'
        seats_html += '</div>'
    return seats_html

def generate_history_html():
    history_html = '<table><thead><tr><th>Name</th><th>Movie</th><th>Showtime</th><th>Seat</th><th>Purchase Date</th><th>Action</th></tr></thead><tbody>'
    for i, booking in enumerate(booking_history):
        history_html += f'<tr><td>{booking["name"]}</td><td>{booking["movie"]}</td><td>{booking["showtime"]}</td><td>{booking["seat"]}</td><td>{booking["purchase_date"]}</td><td><button onclick="deleteBooking({i})"><i class="fas fa-trash-alt"></i></button></td></tr>'
    history_html += '</tbody></table>'
    return history_html

@app.route('/book', methods=['POST'])
def book():
    data = request.get_json()
    booking_queue.put(data)
    return jsonify({"status": "pending", "message": "Booking request received. Processing..."})

@app.route('/delete_booking', methods=['POST'])
def delete_booking():
    data = request.get_json()
    index = data.get('index')
    if index is not None and 0 <= index < len(booking_history):
        booking = booking_history.pop(index)
        showtime = booking["showtime"]
        seat = booking["seat"]
        showtimes[showtime]["seats"][seat] = True
        showtimes[showtime]["sold_tickets"] -= 1
        return jsonify({"status": "success", "message": "Booking successfully deleted."})
    return jsonify({"status": "error", "message": "Invalid booking index."})

if __name__ == '__main__':
    # Start the booking processing thread
    booking_thread = Thread(target=process_booking_queue)
    booking_thread.daemon = True
    booking_thread.start()

    # Run the Flask app
    app.run()
