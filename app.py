from flask import Flask, request, jsonify, render_template # type: ignore
from threading import Thread
from queue import Queue
import time

app = Flask(__name__)

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
    return render_template('index.html', showtimes_html=showtimes_html, history_html=history_html)

def generate_showtimes_html():
    html = ""
    for showtime, details in showtimes.items():
        seats_html = generate_seat_plan_html(showtime)
        html += f'''
        <div class="showtime">
            <h3>{details["movie"]}</h3>
            <p><strong>Showtime:</strong> {showtime}</p>
            <p><strong>Formation:</strong> {details["formation"]}</p>
            <button class="select-button" onclick="selectSeat('{showtime}')">Select Seat</button>
            <div class="seat-plan" data-showtime="{showtime}">
                <div class="seats">
                    {seats_html}
                </div>
            </div>
        </div>
        '''
    return html

def generate_seat_plan_html(showtime):
    html = ""
    for row in "ABCDE":
        html += '<div class="seat-row">'
        for num in range(1, 11):
            seat_id = f"{row}{num}"
            available = showtimes[showtime]["seats"].get(seat_id, False)
            seat_button = f'<button class="seat" {"disabled" if not available else ""} onclick="bookSeat(\'{showtime}\', \'{seat_id}\')">{seat_id}</button>'
            html += seat_button
        html += '</div>'
    return html

def generate_history_html():
    if not booking_history:
        return '<p>No bookings yet.</p>'

    html = '''
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Movie</th>
                <th>Showtime</th>
                <th>Seat</th>
                <th>Purchase Date</th>
            </tr>
        </thead>
        <tbody>
    '''
    for i, booking in enumerate(booking_history, 1):
        html += f'''
        <tr>
            <td>{i}</td>
            <td>{booking["name"]}</td>
            <td>{booking["movie"]}</td>
            <td>{booking["showtime"]}</td>
            <td>{booking["seat"]}</td>
            <td>{booking["purchase_date"]}</td>
        </tr>
        '''
    html += '''
        </tbody>
    </table>
    '''
    return html

@app.route('/book-seat', methods=['POST'])
def book_seat():
    data = request.json
    booking_queue.put(data)
    return jsonify({"status": "pending", "message": "Booking request is being processed."})

@app.route('/delete-booking', methods=['POST'])
def delete_booking():
    booking_id = int(request.form['bookingId']) - 1

    if booking_id < 0 or booking_id >= len(booking_history):
        return jsonify({"status": "error", "message": "Invalid booking ID."})

    booking = booking_history.pop(booking_id)
    showtime = booking["showtime"]
    seat = booking["seat"]
    showtimes[showtime]["seats"][seat] = True
    showtimes[showtime]["sold_tickets"] -= 1

    return jsonify({"status": "success", "message": "Booking successfully deleted."})

if __name__ == '__main__':
    booking_thread = Thread(target=process_booking_queue)
    booking_thread.daemon = True
    booking_thread.start()
    app.run(debug=True, port=8000)
