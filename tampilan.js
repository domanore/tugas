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
