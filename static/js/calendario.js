const prevMonthBtn = document.getElementById('prevMonth');
const nextMonthBtn = document.getElementById('nextMonth');
const currentMonth = document.getElementById('currentMonth');
const dates = document.getElementById('dates');
const eventDate = document.getElementById('eventDate');
const eventTitle = document.getElementById('eventTitle');
const addEventBtn = document.getElementById('addEvent');
const eventList = document.getElementById('eventList');

// Variables globales
const today = new Date();
let currentDisplayedMonth = today.getMonth();
let currentDisplayedYear = today.getFullYear();
const events = [];

// Función para renderizar el calendario
function renderCalendar() {
    const firstDay = new Date(currentDisplayedYear, currentDisplayedMonth, 1);
    const lastDay = new Date(currentDisplayedYear, currentDisplayedMonth + 1, 0);
    currentMonth.textContent = `${firstDay.toLocaleString('default', { month: 'long' })} ${currentDisplayedYear}`;
    dates.innerHTML = '';

    for (let i = 0; i < firstDay.getDay(); i++) {
        const dateDiv = document.createElement('div');
        dateDiv.className = 'date';
        dates.appendChild(dateDiv);
    }

    for (let i = 1; i <= lastDay.getDate(); i++) {
        const dateDiv = document.createElement('div');
        dateDiv.className = 'date';
        dateDiv.textContent = i;
        dateDiv.addEventListener('click', () => handleDateClick(i));
        dates.appendChild(dateDiv);
    }

    // Mostrar citas agendadas para el mes actual
    renderEventList();
}

// Función para manejar el clic en una fecha
function handleDateClick(day) {
    const selectedDate = new Date(currentDisplayedYear, currentDisplayedMonth, day);
    eventDate.value = selectedDate.toISOString().substr(0, 10);
}

// Función para agregar una cita
addEventBtn.addEventListener('click', () => {
    const date = eventDate.value;
    const time = eventTime.value;
    const title = eventTitle.value;

    if (date && time && title) {
        events.push({ datetime: `${date} ${time}`, title });
        eventDate.value = '';
        eventTime.value = '';
        eventTitle.value = '';
        renderEventList();
    }
});

// Función para renderizar la lista de citas
function renderEventList() {
    eventList.innerHTML = '';

    for (const event of events) {
        const eventItem = document.createElement('li');

        // Divide la fecha y la hora
        const [eventDate, eventTime] = event.datetime.split(' ');

        // Crea elementos para fecha, hora y título
        const dateElement = document.createElement('div');
        dateElement.textContent = `Fecha: ${eventDate}`;

        const timeElement = document.createElement('div');
        timeElement.textContent = `Hora: ${eventTime}`;

        const titleElement = document.createElement('div');
        titleElement.textContent = `Titulo: ${event.title}`;

        // Agrega los elementos al elemento de la cita
        eventItem.appendChild(dateElement);
        eventItem.appendChild(timeElement);
        eventItem.appendChild(titleElement);

        // Agrega el elemento de la cita a la lista de citas
        eventList.appendChild(eventItem);
    }
}

// Botones para cambiar de mes
prevMonthBtn.addEventListener('click', () => {
    currentDisplayedMonth--;
    if (currentDisplayedMonth < 0) {
        currentDisplayedMonth = 11;
        currentDisplayedYear--;
    }
    renderCalendar();
});

nextMonthBtn.addEventListener('click', () => {
    currentDisplayedMonth++;
    if (currentDisplayedMonth > 11) {
        currentDisplayedMonth = 0;
        currentDisplayedYear++;
    }
    renderCalendar();
});

document.addEventListener('DOMContentLoaded', function() {
    renderCalendar();
});