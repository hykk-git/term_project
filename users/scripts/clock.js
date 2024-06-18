function calculateTimeRemaining(endTime) {
    const total = Date.parse(endTime) - Date.now();
    const days = Math.floor(total / (1000 * 60 * 60 * 24));
    const hours = Math.floor((total / (1000 * 60 * 60)) % 24);
    const minutes = Math.floor((total / 1000 / 60) % 60);
    return {
        total,
        days,
        hours,
        minutes
    };
}

function initializeClock(endTime) {
    const timerSpan = document.getElementById('event-timer');
    function updateClock() {
        if (endTime === "0") {
            timerSpan.innerHTML = `남은 기간: 0일 0시간 0분`;
        } else {
            const t = calculateTimeRemaining(endTime);
            timerSpan.innerHTML = `남은 기간: ${t.days}일 ${t.hours}시간 ${t.minutes}분`;
            if (t.total <= 0) {
                clearInterval(timeinterval);
            }
        }
    }
    updateClock();
    const timeinterval = setInterval(updateClock, 60000);
}

document.addEventListener("DOMContentLoaded", function() {
    const eventEndDate = document.getElementById('event-timer').getAttribute('data-end-date');
    if (eventEndDate) {
        initializeClock(eventEndDate);
    }
});

function showMessageModal() {
    document.getElementById('messageModal').style.display = 'block';
}

function closeMessageModal() {
    document.getElementById('messageModal').style.display = 'none';
}

function showInbox() {
    fetch('/inbox/')
        .then(response => response.json())
        .then(data => {
            const inboxModal = document.getElementById('inboxModal');
            const inboxContent = document.getElementById('inboxContent');
            inboxContent.innerHTML = '';

            if (data.messages.length === 0) {
                inboxContent.innerHTML = '<p>받은 쪽지가 없습니다.</p>';
            } else {
                data.messages.forEach(message => {
                    const messageDiv = document.createElement('div');
                    messageDiv.classList.add('card', 'mb-2');
                    messageDiv.innerHTML = `
                        <div class="card-body">
                            <p>${message.content}</p>
                            <form method="post" action="/delete_message/${message.id}/">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${data.csrf_token}">
                                <button type="submit" class="btn btn-danger btn-sm">삭제</button>
                            </form>
                        </div>
                    `;
                    inboxContent.appendChild(messageDiv);
                });
            }

            inboxModal.style.display = 'block';
        });
}

function closeInboxModal() {
    document.getElementById('inboxModal').style.display = 'none';
}

function sendMessage(event) {
    event.preventDefault();
    const content = document.getElementById('content').value;

    fetch('/send_message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: new URLSearchParams({ content: content }).toString()
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const successPopup = document.getElementById('successPopup');
            successPopup.innerText = '전송했습니다.';
            successPopup.style.display = 'block';
            setTimeout(() => {
                successPopup.classList.add('fade-out');
                setTimeout(() => {
                    successPopup.style.display = 'none';
                    successPopup.classList.remove('fade-out');
                }, 2000);
            }, 1000);
            closeMessageModal();
        } else {
            alert(data.error);
        }
    });
}
