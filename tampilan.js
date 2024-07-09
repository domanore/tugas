document.addEventListener('DOMContentLoaded', function() {
    const showtimes = {
        "Showtime 1": {
            movie: "Movie 1",
            formation: "Formation 1",
            seats: generateSeats()
        },
        "Showtime 2": {
            movie: "Movie 2",
            formation: "Formation 2",
            seats: generateSeats()
        }
    };

    const bookingHistory = [];

    function generateSeats() {
        const seats = {};
        for (let row of "ABCDE") {
            for (let num = 1; num <= 10; num++) {
                seats[`${row}${num}`] = true;
            }
        }
        return seats;
    }

    function renderShowtimes() {
        const showtimesContainer = document.getElementById('showtimes');
        showtimesContainer.innerHTML = '';
        for (const [showtime, details] of Object.entries(showtimes)) {
            const showtimeDiv = document.createElement('div');
            showtimeDiv.className = 'showtime';
            showtimeDiv.innerHTML = `
                <h3>${details.movie}</h3>
                <p>${showtime}</p>
                <div class="seat-plan" id="seat-plan-${showtime}">
                    ${renderSeats(showtime)}
                </div>
                <button class="select-button" onclick="toggleSeatPlan('${showtime}')">Select Seats</button>
            `;
            showtimesContainer.appendChild(showtimeDiv);
        }
    }

    function renderSeats(showtime) {
        const seats = showtimes[showtime].seats;
        let seatsHtml = '';
        for (let row of "ABCDE") {
            seatsHtml += '<div class="seat-row">';
            for (let num = 1; num <= 10; num++) {
                const seat = `${row}${num}`;
                const disabled = seats[seat] ? '' : 'disabled';
                seatsHtml += `<button id="${showtime}-${seat}" class="seat" ${disabled} onclick="bookSeat('${showtime}', '${seat}')">${seat}</button>`;
            }
            seatsHtml += '</div>';
        }
        return seatsHtml;
    }

    window.toggleSeatPlan = function(showtime) {
        const seatPlan = document.getElementById(`seat-plan-${showtime}`);
        seatPlan.style.display = seatPlan.style.display === 'flex' ? 'none' : 'flex';
    }

    window.bookSeat = function(showtime, seat) {
        const name = prompt("Enter your name:");
        if (!name) {
            alert("Name is required to book a seat.");
            return;
        }

        const seatElement = document.getElementById(`${showtime}-${seat}`);
        seatElement.disabled = true;
        showtimes[showtime].seats[seat] = false;

        bookingHistory.push({ showtime, seat, name });
        renderNotification(`Seat ${seat} for ${showtimes[showtime].movie} successfully booked by ${name}!`);
        renderBookingHistory();
    }

    function renderNotification(message) {
        const notification = document.getElementById('notification');
        notification.innerText = message;
        setTimeout(() => notification.innerText = '', 5000);
    }

    function renderBookingHistory() {
        const historyBody = document.querySelector('#booking-history tbody');
        historyBody.innerHTML = '';
        bookingHistory.forEach((booking, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${booking.showtime}</td>
                <td>${booking.seat}</td>
                <td>${booking.name}</td>
                <td><button onclick="deleteBooking(${index})">Delete</button></td>
            `;
            historyBody.appendChild(row);
        });
    }

    window.deleteBooking = function(index) {
        const booking = bookingHistory[index];
        showtimes[booking.showtime].seats[booking.seat] = true;
        document.getElementById(`${booking.showtime}-${booking.seat}`).disabled = false;
        bookingHistory.splice(index, 1);
        renderBookingHistory();
    }

    renderShowtimes();
});
