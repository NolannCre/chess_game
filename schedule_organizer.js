const timeSlots = [
    '08:00', '09:00', '10:00', '11:00', '12:00', '13:00',
    '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00'
];

const days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'];
const dayLabels = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

let events = {};
let selectedColor = 'default';
let eventIdCounter = 0;

const colorSchemes = {
    default: 'linear-gradient(45deg, #667eea, #764ba2)',
    red: 'linear-gradient(45deg, #ff6b6b, #ee5a52)',
    green: 'linear-gradient(45deg, #51cf66, #40c057)',
    yellow: 'linear-gradient(45deg, #ffd43b, #fab005)',
    blue: 'linear-gradient(45deg, #339af0, #228be6)',
    purple: 'linear-gradient(45deg, #845ef7, #7048e8)'
};

function initializeSchedule() {
    const grid = document.getElementById('scheduleGrid');

    // Header vide pour le coin
    grid.innerHTML = '<div class="time-header"></div>';

    // Headers des jours
    dayLabels.forEach(day => {
        const dayHeader = document.createElement('div');
        dayHeader.className = 'day-header';
        dayHeader.textContent = day;
        grid.appendChild(dayHeader);
    });

    // Créer les lignes de temps
    timeSlots.forEach(time => {
        // Colonne de temps
        const timeSlot = document.createElement('div');
        timeSlot.className = 'time-slot';
        timeSlot.textContent = time;
        grid.appendChild(timeSlot);

        // Cellules pour chaque jour
        days.forEach(day => {
            const cell = document.createElement('div');
            cell.className = 'schedule-cell';
            cell.dataset.day = day;
            cell.dataset.time = time;
            grid.appendChild(cell);
        });
    });
}

function addEvent() {
    const title = document.getElementById('eventTitle').value.trim();
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;

    // Récupérer les jours sélectionnés
    const selectedDays = [];
    document.querySelectorAll('.days-selector input[type="checkbox"]:checked').forEach(checkbox => {
        selectedDays.push(checkbox.value);
    });

    if (!title || !startTime || !endTime) {
        alert('Veuillez remplir tous les champs');
        return;
    }

    if (selectedDays.length === 0) {
        alert('Veuillez sélectionner au moins un jour');
        return;
    }

    if (startTime >= endTime) {
        alert('L\'heure de fin doit être après l\'heure de début');
        return;
    }

    // Ajouter l'événement pour chaque jour sélectionné
    selectedDays.forEach(day => {
        const eventId = 'event_' + (++eventIdCounter);
        const event = {
            id: eventId,
            title: title,
            startTime: startTime,
            endTime: endTime,
            day: day,
            color: selectedColor,
            completed: false
        };

        if (!events[day]) {
            events[day] = [];
        }

        events[day].push(event);
    });

    // Vider le formulaire
    document.getElementById('eventTitle').value = '';
    document.getElementById('startTime').value = '';
    document.getElementById('endTime').value = '';

    // Décocher toutes les cases
    document.querySelectorAll('.days-selector input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });

    renderEvents();
    updateStats();
    updateNextEvent();
}

function renderEvents() {
    // Nettoyer toutes les cellules
    document.querySelectorAll('.schedule-cell').forEach(cell => {
        cell.innerHTML = '';
    });

    // Obtenir le prochain événement pour le mettre en évidence
    const nextEvent = getNextEvent();

    // Ajouter les événements
    Object.keys(events).forEach(day => {
        events[day].forEach(event => {
            const startHour = parseInt(event.startTime.split(':')[0]);
            const startMinute = parseInt(event.startTime.split(':')[1]);
            const endHour = parseInt(event.endTime.split(':')[0]);
            const endMinute = parseInt(event.endTime.split(':')[1]);

            // CORRECTION PRINCIPALE : Vérifier que les heures sont dans timeSlots et créer des blocs pour chaque heure
            const availableHours = timeSlots.map(slot => parseInt(slot.split(':')[0]));
            
            // Trouver toutes les heures concernées par cet événement
            const eventHours = [];
            for (let hour = startHour; hour < endHour; hour++) {
                if (availableHours.includes(hour)) {
                    eventHours.push(hour);
                }
            }
            
            // Si l'événement se termine avec des minutes, ajouter l'heure de fin
            if (endMinute > 0 && availableHours.includes(endHour)) {
                eventHours.push(endHour);
            }

            console.log(`Événement "${event.title}" : heures ${eventHours.join(', ')}`); // Debug

            // Créer un bloc pour chaque heure
            eventHours.forEach((hour, index) => {
                const timeSlot = hour.toString().padStart(2, '0') + ':00';
                const cell = document.querySelector(`[data-day="${day}"][data-time="${timeSlot}"]`);
                
                console.log(`Recherche cellule pour ${day} à ${timeSlot}:`, cell); // Debug
                
                if (cell) {
                    const eventElement = document.createElement('div');
                    eventElement.className = 'event';
                    
                    const isFirstSegment = (index === 0);
                    const isLastSegment = (index === eventHours.length - 1);
                    
                    // Appliquer les styles selon l'état
                    if (event.completed) {
                        eventElement.classList.add('completed');
                    } else {
                        eventElement.style.background = colorSchemes[event.color];
                    }

                    // Marquer le prochain événement
                    if (nextEvent && nextEvent.id === event.id) {
                        eventElement.classList.add('next-event');
                    }

                    // Contenu différent selon le segment
                    if (isFirstSegment && !isLastSegment) {
                        // Premier segment d'un événement multi-créneaux
                        eventElement.innerHTML = `
                            <input type="checkbox" class="event-checkbox" ${event.completed ? 'checked' : ''} 
                                   onchange="toggleEventCompletion('${event.id}', '${day}')">
                            <div class="event-content">
                                <div class="event-title">${event.title}</div>
                                <div class="event-time">${event.startTime} →</div>
                            </div>
                            <button class="event-delete" onclick="deleteEvent('${event.id}', '${day}')">×</button>
                        `;
                    } else if (isLastSegment && !isFirstSegment) {
                        // Dernier segment
                        if (hour === endHour && endMinute > 0) {
                            // Segment partiel pour les minutes
                            const minuteHeight = Math.max(20, (endMinute / 60) * 46);
                            eventElement.style.height = `${minuteHeight}px`;
                            eventElement.style.maxHeight = `${minuteHeight}px`;
                        }
                        
                        eventElement.innerHTML = `
                            <div class="event-content continuation">
                                <div class="event-continuation">↓</div>
                                <div class="event-time-end">→ ${event.endTime}</div>
                            </div>
                        `;
                    } else if (!isFirstSegment && !isLastSegment) {
                        // Segments intermédiaires
                        eventElement.innerHTML = `
                            <div class="event-content continuation">
                                <div class="event-continuation">↓</div>
                                <div class="event-title-small">${event.title}</div>
                            </div>
                        `;
                    } else {
                        // Événement d'une seule heure
                        eventElement.innerHTML = `
                            <input type="checkbox" class="event-checkbox" ${event.completed ? 'checked' : ''} 
                                   onchange="toggleEventCompletion('${event.id}', '${day}')">
                            <div class="event-content">
                                <div class="event-title">${event.title}</div>
                                <div class="event-time">${event.startTime} - ${event.endTime}</div>
                            </div>
                            <button class="event-delete" onclick="deleteEvent('${event.id}', '${day}')">×</button>
                        `;
                    }

                    cell.appendChild(eventElement);
                    console.log(`Bloc ajouté pour ${day} à ${timeSlot}`); // Debug
                } else {
                    console.log(`Cellule non trouvée pour ${day} à ${timeSlot}`); // Debug
                }
            });
        });
    });
}

function deleteEvent(eventId, day) {
    events[day] = events[day].filter(event => event.id !== eventId);
    if (events[day].length === 0) {
        delete events[day];
    }
    renderEvents();
    updateStats();
    updateNextEvent();
}

function toggleEventCompletion(eventId, day) {
    const event = events[day].find(e => e.id === eventId);
    if (event) {
        event.completed = !event.completed;
        renderEvents();
        updateStats();
        updateNextEvent();
    }
}

function clearSchedule() {
    if (confirm('Êtes-vous sûr de vouloir effacer tout l\'emploi du temps ?')) {
        events = {};
        renderEvents();
        updateStats();
        updateNextEvent();
    }
}

function updateStats() {
    const totalEvents = Object.values(events).reduce((sum, dayEvents) => sum + dayEvents.length, 0);
    const completedEvents = Object.values(events).reduce((sum, dayEvents) =>
        sum + dayEvents.filter(event => event.completed).length, 0);
    const busyDays = Object.keys(events).length;

    // Simuler "aujourd'hui" avec lundi
    const todayEvents = events['lundi'] ? events['lundi'].length : 0;

    document.getElementById('totalEvents').textContent = totalEvents;
    document.getElementById('completedEvents').textContent = completedEvents;
    document.getElementById('todayEvents').textContent = todayEvents;
    document.getElementById('busyDays').textContent = busyDays;
}

function getNextEvent() {
    const now = new Date();
    const currentDay = now.getDay(); // 0 = dimanche, 1 = lundi, etc.
    const currentTime = now.getHours() * 60 + now.getMinutes(); // Minutes depuis minuit

    const dayOrder = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
    const currentDayName = dayOrder[currentDay];

    let nextEvent = null;
    let minTimeDiff = Infinity;

    // Parcourir tous les événements
    Object.keys(events).forEach(day => {
        events[day].forEach(event => {
            if (event.completed) return; // Ignorer les événements terminés

            const eventTime = parseInt(event.startTime.split(':')[0]) * 60 +
                parseInt(event.startTime.split(':')[1]);

            let dayIndex = dayOrder.indexOf(day);
            let timeDiff;

            if (dayIndex === currentDay) {
                // Même jour
                if (eventTime > currentTime) {
                    timeDiff = eventTime - currentTime;
                } else {
                    timeDiff = (7 * 24 * 60) + eventTime - currentTime; // Semaine suivante
                }
            } else {
                // Autre jour
                let dayDiff = dayIndex - currentDay;
                if (dayDiff < 0) dayDiff += 7; // Semaine suivante

                timeDiff = (dayDiff * 24 * 60) + eventTime - currentTime;
            }

            if (timeDiff < minTimeDiff) {
                minTimeDiff = timeDiff;
                nextEvent = { ...event, day: day, timeDiff: timeDiff };
            }
        });
    });

    return nextEvent;
}

function updateNextEvent() {
    const nextEvent = getNextEvent();
    const indicator = document.getElementById('nextEventIndicator');
    const content = document.getElementById('nextEventContent');

    if (nextEvent) {
        const dayNames = {
            'lundi': 'Lundi',
            'mardi': 'Mardi',
            'mercredi': 'Mercredi',
            'jeudi': 'Jeudi',
            'vendredi': 'Vendredi',
            'samedi': 'Samedi',
            'dimanche': 'Dimanche'
        };

        // Calculer le temps restant
        const hours = Math.floor(nextEvent.timeDiff / 60);
        const minutes = nextEvent.timeDiff % 60;
        let timeText;

        if (hours < 1) {
            timeText = `dans ${minutes} minute${minutes > 1 ? 's' : ''}`;
        } else if (hours < 24) {
            timeText = `dans ${hours}h${minutes > 0 ? minutes + 'm' : ''}`;
        } else {
            const days = Math.floor(hours / 24);
            const remainingHours = hours % 24;
            timeText = `dans ${days} jour${days > 1 ? 's' : ''} ${remainingHours > 0 ? remainingHours + 'h' : ''}`;
        }

        content.innerHTML = `
                    <div><strong>${nextEvent.title}</strong></div>
                    <div>${dayNames[nextEvent.day]} ${nextEvent.startTime} - ${nextEvent.endTime}</div>
                    <div class="next-event-time">${timeText}</div>
                `;

        indicator.style.display = 'block';
    } else {
        indicator.style.display = 'none';
    }
}

function saveSchedule() {
    const scheduleData = {
        events: events,
        eventIdCounter: eventIdCounter,
        savedAt: new Date().toISOString(),
        version: "1.0"
    };

    const dataStr = JSON.stringify(scheduleData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `emploi-du-temps-${new Date().toISOString().split('T')[0]}.json`;
    link.click();

    // Nettoyer l'URL
    setTimeout(() => URL.revokeObjectURL(link.href), 100);

    alert('Emploi du temps sauvegardé avec succès !');
}

function loadSchedule(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/json') {
        alert('Veuillez sélectionner un fichier JSON valide');
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        try {
            const scheduleData = JSON.parse(e.target.result);

            // Vérifier la structure des données
            if (!scheduleData.events || typeof scheduleData.events !== 'object') {
                throw new Error('Format de fichier invalide');
            }

            // Demander confirmation avant de remplacer
            const totalCurrentEvents = Object.values(events).reduce((sum, dayEvents) => sum + dayEvents.length, 0);
            if (totalCurrentEvents > 0) {
                if (!confirm('Cela remplacera votre emploi du temps actuel. Voulez-vous continuer ?')) {
                    return;
                }
            }

            // Charger les données
            events = scheduleData.events || {};
            eventIdCounter = scheduleData.eventIdCounter || 0;

            // Rafraîchir l'affichage
            renderEvents();
            updateStats();
            updateNextEvent();

            alert(`Emploi du temps chargé avec succès !\nSauvegardé le: ${scheduleData.savedAt ? new Date(scheduleData.savedAt).toLocaleString('fr-FR') : 'Date inconnue'}`);

        } catch (error) {
            alert('Erreur lors du chargement du fichier: ' + error.message);
        }
    };

    reader.readAsText(file);

    // Réinitialiser l'input file
    event.target.value = '';
}

// Gestion des couleurs
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.color-option').forEach(option => {
        option.addEventListener('click', function () {
            document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            selectedColor = this.dataset.color;
        });
    });
});

// Initialiser l'application
document.addEventListener('DOMContentLoaded', function() {
    initializeSchedule();
    updateStats();
    updateNextEvent();
    
    // Mettre à jour le prochain événement toutes les minutes
    setInterval(updateNextEvent, 60000);
});