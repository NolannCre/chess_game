const timeSlots = [
    '08:00', '09:00', '10:00', '11:00', '12:00', '13:00',
    '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00'
];

const days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'];
const dayLabels = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

let events = {};
let selectedColor = 'default';
let eventIdCounter = 0;
let touchStartTime = 0;

const colorSchemes = {
    default: 'linear-gradient(45deg, #667eea, #764ba2)',
    red: 'linear-gradient(45deg, #ff6b6b, #ee5a52)',
    green: 'linear-gradient(45deg, #51cf66, #40c057)',
    yellow: 'linear-gradient(45deg, #ffd43b, #fab005)',
    blue: 'linear-gradient(45deg, #339af0, #228be6)',
    purple: 'linear-gradient(45deg, #845ef7, #7048e8)'
};

// Fonction utilitaire pour les notifications mobiles
function showNotification(message, type = 'info') {
    // Créer l'élément de notification s'il n'existe pas
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 300px;
        `;
        document.body.appendChild(notificationContainer);
    }

    const notification = document.createElement('div');
    notification.style.cssText = `
        background: ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#51cf66' : '#339af0'};
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transform: translateX(320px);
        transition: transform 0.3s ease;
        font-size: 14px;
        word-wrap: break-word;
    `;
    notification.textContent = message;
    
    notificationContainer.appendChild(notification);
    
    // Animation d'entrée
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto-suppression après 3 secondes
    setTimeout(() => {
        notification.style.transform = 'translateX(320px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Fonction utilitaire pour gérer les événements tactiles et clics
function addTouchClickHandler(element, callback) {
    if (!element) return;
    
    // Gestionnaire pour les événements tactiles
    element.addEventListener('touchstart', function(e) {
        touchStartTime = Date.now();
    }, { passive: true });
    
    element.addEventListener('touchend', function(e) {
        e.preventDefault();
        const touchDuration = Date.now() - touchStartTime;
        
        // Éviter les déclenchements accidentels (tap trop rapide ou trop long)
        if (touchDuration > 50 && touchDuration < 500) {
            callback(e);
        }
    });
    
    // Gestionnaire pour les clics classiques (desktop)
    element.addEventListener('click', function(e) {
        // Éviter le double déclenchement sur mobile
        if (e.detail === 0) return; // Événement déclenché par le clavier
        callback(e);
    });
}

function initializeSchedule() {
    const grid = document.getElementById('scheduleGrid');
    if (!grid) {
        console.error('Element scheduleGrid non trouvé');
        return;
    }

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
    console.log('addEvent appelée'); // Debug mobile
    
    const titleElement = document.getElementById('eventTitle');
    const startTimeElement = document.getElementById('startTime');
    const endTimeElement = document.getElementById('endTime');
    
    if (!titleElement || !startTimeElement || !endTimeElement) {
        console.error('Éléments du formulaire non trouvés');
        showNotification('Erreur: Éléments du formulaire manquants', 'error');
        return;
    }
    
    const title = titleElement.value.trim();
    const startTime = startTimeElement.value;
    const endTime = endTimeElement.value;

    console.log('Données du formulaire:', { title, startTime, endTime }); // Debug

    // Récupérer les jours sélectionnés avec une approche plus robuste
    const selectedDays = [];
    const checkboxes = document.querySelectorAll('.days-selector input[type="checkbox"]');
    
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedDays.push(checkbox.value);
            console.log('Jour sélectionné:', checkbox.value); // Debug
        }
    });

    // Validations avec notifications visuelles
    if (!title) {
        showNotification('Veuillez saisir un titre pour l\'événement', 'error');
        titleElement.focus();
        return;
    }

    if (!startTime) {
        showNotification('Veuillez sélectionner une heure de début', 'error');
        startTimeElement.focus();
        return;
    }

    if (!endTime) {
        showNotification('Veuillez sélectionner une heure de fin', 'error');
        endTimeElement.focus();
        return;
    }

    if (selectedDays.length === 0) {
        showNotification('Veuillez sélectionner au moins un jour', 'error');
        return;
    }

    if (startTime >= endTime) {
        showNotification('L\'heure de fin doit être après l\'heure de début', 'error');
        return;
    }

    console.log('Validation passée, ajout des événements...'); // Debug

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
        console.log('Événement ajouté pour', day, ':', event); // Debug
    });

    // Vider le formulaire
    titleElement.value = '';
    startTimeElement.value = '';
    endTimeElement.value = '';

    // Décocher toutes les cases
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    renderEvents();
    updateStats();
    updateNextEvent();
    
    showNotification(`Événement "${title}" ajouté avec succès !`, 'success');
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

            // Créer un bloc pour chaque heure
            eventHours.forEach((hour, index) => {
                const timeSlot = hour.toString().padStart(2, '0') + ':00';
                const cell = document.querySelector(`[data-day="${day}"][data-time="${timeSlot}"]`);
                
                if (cell) {
                    const eventElement = document.createElement('div');
                    eventElement.className = 'event';
                    
                    // Améliorer la taille des éléments tactiles
                    eventElement.style.minHeight = '44px'; // Taille recommandée pour les éléments tactiles
                    
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
                        eventElement.innerHTML = `
                            <input type="checkbox" class="event-checkbox" ${event.completed ? 'checked' : ''} 
                                   data-event-id="${event.id}" data-day="${day}">
                            <div class="event-content">
                                <div class="event-title">${event.title}</div>
                                <div class="event-time">${event.startTime} →</div>
                            </div>
                            <button class="event-delete" data-event-id="${event.id}" data-day="${day}" 
                                    style="min-width: 44px; min-height: 44px; padding: 8px;">×</button>
                        `;
                    } else if (isLastSegment && !isFirstSegment) {
                        if (hour === endHour && endMinute > 0) {
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
                        eventElement.innerHTML = `
                            <div class="event-content continuation">
                                <div class="event-continuation">↓</div>
                                <div class="event-title-small">${event.title}</div>
                            </div>
                        `;
                    } else {
                        eventElement.innerHTML = `
                            <input type="checkbox" class="event-checkbox" ${event.completed ? 'checked' : ''} 
                                   data-event-id="${event.id}" data-day="${day}">
                            <div class="event-content">
                                <div class="event-title">${event.title}</div>
                                <div class="event-time">${event.startTime} - ${event.endTime}</div>
                            </div>
                            <button class="event-delete" data-event-id="${event.id}" data-day="${day}"
                                    style="min-width: 44px; min-height: 44px; padding: 8px;">×</button>
                        `;
                    }

                    cell.appendChild(eventElement);
                    
                    // Ajouter les gestionnaires d'événements tactiles pour les éléments interactifs
                    const checkbox = eventElement.querySelector('.event-checkbox');
                    const deleteBtn = eventElement.querySelector('.event-delete');
                    
                    if (checkbox) {
                        addTouchClickHandler(checkbox, function() {
                            toggleEventCompletion(checkbox.dataset.eventId, checkbox.dataset.day);
                        });
                    }
                    
                    if (deleteBtn) {
                        addTouchClickHandler(deleteBtn, function() {
                            deleteEvent(deleteBtn.dataset.eventId, deleteBtn.dataset.day);
                        });
                    }
                }
            });
        });
    });
}

function deleteEvent(eventId, day) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cet événement ?')) {
        events[day] = events[day].filter(event => event.id !== eventId);
        if (events[day].length === 0) {
            delete events[day];
        }
        renderEvents();
        updateStats();
        updateNextEvent();
        showNotification('Événement supprimé', 'success');
    }
}

function toggleEventCompletion(eventId, day) {
    const event = events[day].find(e => e.id === eventId);
    if (event) {
        event.completed = !event.completed;
        renderEvents();
        updateStats();
        updateNextEvent();
        showNotification(
            event.completed ? 'Événement marqué comme terminé' : 'Événement marqué comme non terminé', 
            'success'
        );
    }
}

function clearSchedule() {
    if (confirm('Êtes-vous sûr de vouloir effacer tout l\'emploi du temps ?')) {
        events = {};
        renderEvents();
        updateStats();
        updateNextEvent();
        showNotification('Emploi du temps effacé', 'success');
    }
}

function updateStats() {
    const totalEvents = Object.values(events).reduce((sum, dayEvents) => sum + dayEvents.length, 0);
    const completedEvents = Object.values(events).reduce((sum, dayEvents) =>
        sum + dayEvents.filter(event => event.completed).length, 0);
    const busyDays = Object.keys(events).length;

    // Simuler "aujourd'hui" avec lundi
    const todayEvents = events['lundi'] ? events['lundi'].length : 0;

    const totalEventsEl = document.getElementById('totalEvents');
    const completedEventsEl = document.getElementById('completedEvents');
    const todayEventsEl = document.getElementById('todayEvents');
    const busyDaysEl = document.getElementById('busyDays');

    if (totalEventsEl) totalEventsEl.textContent = totalEvents;
    if (completedEventsEl) completedEventsEl.textContent = completedEvents;
    if (todayEventsEl) todayEventsEl.textContent = todayEvents;
    if (busyDaysEl) busyDaysEl.textContent = busyDays;
}

function getNextEvent() {
    const now = new Date();
    const currentDay = now.getDay();
    const currentTime = now.getHours() * 60 + now.getMinutes();

    const dayOrder = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
    const currentDayName = dayOrder[currentDay];

    let nextEvent = null;
    let minTimeDiff = Infinity;

    Object.keys(events).forEach(day => {
        events[day].forEach(event => {
            if (event.completed) return;

            const eventTime = parseInt(event.startTime.split(':')[0]) * 60 +
                parseInt(event.startTime.split(':')[1]);

            let dayIndex = dayOrder.indexOf(day);
            let timeDiff;

            if (dayIndex === currentDay) {
                if (eventTime > currentTime) {
                    timeDiff = eventTime - currentTime;
                } else {
                    timeDiff = (7 * 24 * 60) + eventTime - currentTime;
                }
            } else {
                let dayDiff = dayIndex - currentDay;
                if (dayDiff < 0) dayDiff += 7;

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

    if (nextEvent && indicator && content) {
        const dayNames = {
            'lundi': 'Lundi',
            'mardi': 'Mardi',
            'mercredi': 'Mercredi',
            'jeudi': 'Jeudi',
            'vendredi': 'Vendredi',
            'samedi': 'Samedi',
            'dimanche': 'Dimanche'
        };

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
    } else if (indicator) {
        indicator.style.display = 'none';
    }
}

function saveSchedule() {
    const scheduleData = {
        events: events,
        eventIdCounter: eventIdCounter,
        savedAt: new Date().toISOString(),
        version: "1.1"
    };

    const dataStr = JSON.stringify(scheduleData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `emploi-du-temps-${new Date().toISOString().split('T')[0]}.json`;
    
    // Pour mobile, déclencher le téléchargement différemment
    if ('ontouchstart' in window) {
        document.body.appendChild(link);
    }
    
    link.click();

    setTimeout(() => {
        URL.revokeObjectURL(link.href);
        if (link.parentNode) {
            link.parentNode.removeChild(link);
        }
    }, 100);

    showNotification('Emploi du temps sauvegardé avec succès !', 'success');
}

function loadSchedule(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/json') {
        showNotification('Veuillez sélectionner un fichier JSON valide', 'error');
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        try {
            const scheduleData = JSON.parse(e.target.result);

            if (!scheduleData.events || typeof scheduleData.events !== 'object') {
                throw new Error('Format de fichier invalide');
            }

            const totalCurrentEvents = Object.values(events).reduce((sum, dayEvents) => sum + dayEvents.length, 0);
            if (totalCurrentEvents > 0) {
                if (!confirm('Cela remplacera votre emploi du temps actuel. Voulez-vous continuer ?')) {
                    return;
                }
            }

            events = scheduleData.events || {};
            eventIdCounter = scheduleData.eventIdCounter || 0;

            renderEvents();
            updateStats();
            updateNextEvent();

            showNotification(
                `Emploi du temps chargé avec succès !\nSauvegardé le: ${scheduleData.savedAt ? new Date(scheduleData.savedAt).toLocaleString('fr-FR') : 'Date inconnue'}`,
                'success'
            );

        } catch (error) {
            showNotification('Erreur lors du chargement du fichier: ' + error.message, 'error');
        }
    };

    reader.readAsText(file);
    event.target.value = '';
}

// Initialisation améliorée pour mobile
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM chargé, initialisation...'); // Debug
    
    // Initialiser l'interface
    initializeSchedule();
    updateStats();
    updateNextEvent();
    
    // Gestionnaire pour le bouton d'ajout d'événement
    const addEventBtn = document.getElementById('addEventBtn');
    if (addEventBtn) {
        console.log('Bouton addEvent trouvé, ajout des gestionnaires...'); // Debug
        addTouchClickHandler(addEventBtn, addEvent);
    } else {
        console.error('Bouton addEventBtn non trouvé'); // Debug
    }
    
    // Gestionnaire pour le bouton de sauvegarde
    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) {
        addTouchClickHandler(saveBtn, saveSchedule);
    }
    
    // Gestionnaire pour le bouton d'effacement
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        addTouchClickHandler(clearBtn, clearSchedule);
    }
    
    // Gestionnaire pour le sélecteur de couleurs
    document.querySelectorAll('.color-option').forEach(option => {
        addTouchClickHandler(option, function() {
            document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');
            selectedColor = option.dataset.color;
        });
    });
    
    // Gestionnaire pour le chargement de fichier
    const loadInput = document.getElementById('loadInput');
    if (loadInput) {
        loadInput.addEventListener('change', loadSchedule);
    }
    
    // Mettre à jour le prochain événement toutes les minutes
    setInterval(updateNextEvent, 60000);
    
    console.log('Initialisation terminée'); // Debug
});
