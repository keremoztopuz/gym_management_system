$(document).ready(function () {
    $('.city-card').click(function (e) {
        e.preventDefault();
        var city = $(this).data('city');
        showClubs(city);

        // Scroll to results
        $('html, body').animate({
            scrollTop: $('#cityClubs').offset().top - 100
        }, 'slow');
    });

    $(document).on('click', '.club-card-link', function (e) {
        e.preventDefault();
        var selectedClub = $(this).data('club');
        showClubDetails(selectedClub);

        $('html, body').animate({
            scrollTop: $('#clubDetails').offset().top - 100
        }, 'slow');
    });

    // BMI Calculator Logic
    if ($('#bmi-height').length) {
        function calculateBMI() {
            var height = $('#bmi-height').val();
            var weight = $('#bmi-weight').val();

            $('#height-val').text(height);
            $('#weight-val').text(weight);

            var heightM = height / 100;
            var bmi = (weight / (heightM * heightM)).toFixed(1);

            $('#bmi-result').text(bmi);

            var category = "";
            var color = "";

            if (bmi < 18.5) {
                category = "Underweight";
                color = "#FFC107"; // Amber
            } else if (bmi >= 18.5 && bmi < 25) {
                category = "Normal Weight";
                color = "#00E676"; // Green
            } else if (bmi >= 25 && bmi < 30) {
                category = "Overweight";
                color = "#FF9800"; // Orange
            } else {
                category = "Obese";
                color = "#FF5252"; // Red
            }

            $('#bmi-category').text(category).css('color', color);
            $('#bmi-result').css('color', color).css('text-shadow', '0 0 20px ' + color + '80');

            // Save to DB (Debounced)
            clearTimeout(window.bmiSaveTimeout);
            window.bmiSaveTimeout = setTimeout(function () {
                $.ajax({
                    url: '/api/save_bmi',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ bmi: parseFloat(bmi), weight: parseFloat(weight) }),
                    success: function (response) {
                        console.log('BMI saved');
                    }
                });
            }, 1000); // Save 1 second after last input
        }

        $('#bmi-height, #bmi-weight').on('input', calculateBMI);
        calculateBMI(); // Initial calculation
    }

    // Dashboard Chart Logic
    if ($('#weightChart').length) {
        $.getJSON('/api/get_bmi_history', function (data) {
            var ctx = document.getElementById('weightChart').getContext('2d');
            var gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(0, 230, 118, 0.5)');
            gradient.addColorStop(1, 'rgba(0, 230, 118, 0)');

            var labels = [];
            var weights = [];

            if (data.length > 0) {
                data.forEach(record => {
                    var date = new Date(record.recorded_at);
                    labels.push(date.toLocaleDateString());
                    weights.push(record.weight);
                });
            } else {
                // Mock data if empty
                labels = ['Start'];
                weights = [70];
            }

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Weight Progress (kg)',
                        data: weights,
                        borderColor: '#00E676',
                        backgroundColor: gradient,
                        borderWidth: 2,
                        pointBackgroundColor: '#00E676',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: '#00E676',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { labels: { color: '#fff' } }
                    },
                    scales: {
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            ticks: { color: '#fff' }
                        },
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            ticks: { color: '#fff' }
                        }
                    }
                }
            });
        });
    }
});

function showClubs(city) {
    // Map Logic
    var map;
    var markers = [];

    // Coordinates for demo
    var cityCoords = {
        "ankara": [39.9334, 32.8597],
        "izmir": [38.4237, 27.1428],
        "istanbul": [41.0082, 28.9784]
    };

    // Mock locations for clubs (offsets from city center)
    function getClubCoords(city, index) {
        var center = cityCoords[city];
        return [center[0] + (Math.random() - 0.5) * 0.1, center[1] + (Math.random() - 0.5) * 0.1];
    }

    // Initialize map if not already done
    if (!window.clubMap) {
        if ($('#clubsMap').length) {
            $('#clubsMap').show();
            window.clubMap = L.map('clubsMap').setView([39.9334, 32.8597], 6);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(window.clubMap);
            window.clubMarkers = [];
        }
    }

    var clubs = getClubs(city);

    // Update Map View
    if (window.clubMap && cityCoords[city]) {
        window.clubMap.setView(cityCoords[city], 11);

        // Clear existing markers
        if (window.clubMarkers) {
            window.clubMarkers.forEach(m => window.clubMap.removeLayer(m));
        }
        window.clubMarkers = [];

        // Add markers for each club
        clubs.forEach((club, index) => {
            var coords = getClubCoords(city, index);
            var marker = L.marker(coords).addTo(window.clubMap)
                .bindPopup("<b>" + club + "</b><br>Premium Fitness Club");
            window.clubMarkers.push(marker);
        });

        // Fix map rendering issues when hidden
        setTimeout(function () { window.clubMap.invalidateSize() }, 400);
    }

    // List Logic
    var cityClubs = $('#cityClubs');
    cityClubs.empty();

    cityClubs.append('<h3 class="section-title">Clubs in ' + city.charAt(0).toUpperCase() + city.slice(1) + '</h3>');

    var clubsContainer = $('<div class="features-grid"></div>');

    for (var i = 0; i < clubs.length; i++) {
        var clubName = clubs[i];
        var clubCard = $('<div class="feature-card club-card-link" data-club="' + clubName + '" style="cursor: pointer;"></div>');
        var icon = $('<div class="feature-icon">🏢</div>');
        var title = $('<h3>' + clubName + '</h3>');
        var desc = $('<p>Click for details</p>');

        clubCard.append(icon);
        clubCard.append(title);
        clubCard.append(desc);
        clubsContainer.append(clubCard);
    }

    cityClubs.append(clubsContainer);
    $('#clubDetails').hide();
}

function getClubs(city) {
    var clubs = {
        ankara: ["Ankamall AVM", "Kentpark AVM", "Cepa AVM", "Armada AVM", "Metromall AVM"],
        izmir: ["Balçova Kipa", "Kidsmall", "Gaziemir Optimum", "Kıbrıs Şehitleri", "Ege Perla"],
        istanbul: ["Zorlu AVM", "Ömür Plaza", "FlyInn", "İstiklal AVM", "Marmara Park"]
    };

    return clubs[city] || [];
}

function showClubDetails(selectedClub) {
    var clubInfo = $('#clubDetails');
    clubInfo.empty();

    var detailContainer = $('<div class="feature-card" style="max-width: 1000px; margin: 0 auto; text-align: left;"></div>');
    var title = $('<h2 style="color: var(--primary-color); margin-bottom: 1rem;">' + selectedClub + '</h2>');
    var desc = $('<p style="margin-bottom: 2rem;">Experience premium fitness at ' + selectedClub + '. State of the art equipment and expert trainers waiting for you.</p>');

    // Tabs
    var tabs = $('<div style="display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 1px solid var(--border-color);"></div>');
    var trainersTab = $('<button class="btn btn-outline" id="btn-trainers" style="border-bottom: none; border-radius: 5px 5px 0 0;">Trainers</button>');
    var lessonsTab = $('<button class="btn btn-outline" id="btn-lessons" style="border-bottom: none; border-radius: 5px 5px 0 0;">Group Lessons</button>');

    tabs.append(trainersTab);
    tabs.append(lessonsTab);

    var contentArea = $('<div id="tab-content"></div>');

    detailContainer.append(title);
    detailContainer.append(desc);
    detailContainer.append(tabs);
    detailContainer.append(contentArea);

    clubInfo.append(detailContainer);
    clubInfo.show();

    // Event Listeners for Tabs
    trainersTab.click(function () {
        loadTrainers(selectedClub, contentArea);
    });

    lessonsTab.click(function () {
        loadLessons(selectedClub, contentArea);
    });

    // Load Trainers by default
    loadTrainers(selectedClub, contentArea);
}

function loadTrainers(clubName, container) {
    container.html('<div class="spinner"></div>');

    // Simulate network delay for better UX (optional, remove in production if real API is fast)
    setTimeout(function () {
        $.getJSON('/api/trainers/' + clubName, function (data) {
            container.empty();
            var grid = $('<div class="features-grid"></div>');

            if (data.length === 0) {
                container.html('<p class="fade-in">No trainers found.</p>');
                return;
            }

            $.each(data, function (key, trainer) {
                var card = $('<div class="feature-card fade-in" style="text-align: center; animation-delay: ' + (key * 0.05) + 's; opacity: 0; padding: 2rem;"></div>');
                var img = $('<img src="' + trainer.image_url + '" style="width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 1.5rem; object-fit: cover; border: 3px solid var(--primary-color); box-shadow: 0 0 15px rgba(0, 230, 118, 0.3);">');
                var name = $('<h4 style="color: var(--primary-color); font-size: 1.2rem; margin-bottom: 0.5rem;">' + trainer.name + ' <span style="font-size: 0.9rem; color: var(--text-muted); font-weight: normal;">(Age: ' + trainer.age + ')</span></h4>');
                var expert = $('<p style="font-weight: bold; margin-bottom: 1rem; color: var(--text-main); background: rgba(255,255,255,0.1); display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;">' + trainer.expertise + '</p>');
                var bio = $('<p style="font-size: 0.9rem; color: var(--text-muted); line-height: 1.6;">' + trainer.bio + '</p>');

                card.append(img);
                card.append(name);
                card.append(expert);
                card.append(bio);
                grid.append(card);
            });

            container.append(grid);
        });
    }, 300); // 300ms delay for smooth transition
}

function loadLessons(clubName, container) {
    container.html('<div class="spinner"></div>');

    setTimeout(function () {
        $.getJSON('/api/lessons/' + clubName, function (data) {
            container.empty();

            if (Object.keys(data).length === 0) {
                container.html('<p class="fade-in">No lessons found.</p>');
                return;
            }

            // Calendar Container
            var calendarDiv = $('<div id="calendar" class="fade-in" style="margin-bottom: 3rem; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 15px;"></div>');
            container.append(calendarDiv);

            // Initialize FullCalendar
            var events = [];
            var daysMap = { "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 0 };
            var today = new Date();
            var currentDay = today.getDay(); // 0-6

            $.each(data, function (day, lessons) {
                var targetDay = daysMap[day];
                var diff = targetDay - currentDay;
                if (diff < 0) diff += 7; // Next occurrence

                var date = new Date(today);
                date.setDate(today.getDate() + diff);
                var dateStr = date.toISOString().split('T')[0];

                $.each(lessons, function (i, lesson) {
                    events.push({
                        title: lesson.title,
                        start: dateStr + 'T' + lesson.time,
                        allDay: false,
                        extendedProps: { instructor: lesson.instructor }
                    });
                });
            });

            var calendarEl = document.getElementById('calendar');
            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'timeGridWeek',
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'timeGridWeek,timeGridDay'
                },
                height: 500,
                events: events,
                themeSystem: 'standard',
                eventColor: '#00E676',
                eventTextColor: '#000'
            });
            calendar.render();


            var delayCounter = 0;
            $.each(data, function (day, lessons) {
                if (lessons.length > 0) {
                    var dayHeader = $('<h3 class="fade-in" style="margin-top: 2.5rem; margin-bottom: 1.5rem; border-left: 4px solid var(--primary-color); padding-left: 15px; animation-delay: ' + (delayCounter * 0.05) + 's; opacity: 0; font-size: 1.5rem;">' + day + '</h3>');
                    container.append(dayHeader);
                    delayCounter++;

                    var list = $('<div style="display: grid; gap: 1rem;"></div>');

                    $.each(lessons, function (i, lesson) {
                        var item = $('<div class="fade-in" style="background: rgba(30, 30, 30, 0.6); backdrop-filter: blur(5px); padding: 1.5rem; border-radius: var(--radius-md); display: flex; justify-content: space-between; align-items: center; animation-delay: ' + (delayCounter * 0.05) + 's; opacity: 0; transition: all 0.3s ease; border: 1px solid transparent;"></div>');

                        // Add hover effect via JS since inline styles are used
                        item.hover(
                            function () {
                                $(this).css({
                                    'transform': 'translateX(10px)',
                                    'border-color': 'var(--primary-color)',
                                    'background': 'rgba(30, 30, 30, 0.9)'
                                });
                            },
                            function () {
                                $(this).css({
                                    'transform': 'translateX(0)',
                                    'border-color': 'transparent',
                                    'background': 'rgba(30, 30, 30, 0.6)'
                                });
                            }
                        );

                        var info = $('<div><div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;"><strong style="color: var(--primary-color); font-size: 1.2rem; font-family: var(--font-heading);">' + lesson.time + '</strong> <span style="width: 1px; height: 15px; background: var(--text-muted);"></span> <strong style="font-size: 1.1rem;">' + lesson.title + '</strong></div><span style="color: var(--text-muted); font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem;">👤 ' + lesson.instructor + '</span></div>');

                        var actionDiv = $('<div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem;"></div>');
                        var cap = $('<span style="display: block; font-size: 0.8rem; color: var(--text-muted);">Capacity: <span style="color: var(--primary-color); font-weight: bold;">' + lesson.capacity + '</span></span>');
                        var joinBtn = $('<button class="btn" style="padding: 5px 15px; font-size: 0.8rem; min-width: 80px;">Join</button>');

                        joinBtn.click(function (e) {
                            e.stopPropagation();

                            $.ajax({
                                url: '/api/reserve_lesson',
                                type: 'POST',
                                contentType: 'application/json',
                                data: JSON.stringify({
                                    title: lesson.title,
                                    time: lesson.time,
                                    day: day,
                                    club: clubName
                                }),
                                success: function (response) {
                                    Swal.fire({
                                        title: 'Joined!',
                                        text: 'You have successfully booked ' + lesson.title + ' at ' + lesson.time,
                                        icon: 'success',
                                        confirmButtonColor: '#00E676',
                                        background: '#1a1a1a',
                                        color: '#fff'
                                    });
                                },
                                error: function (xhr) {
                                    if (xhr.status === 401) {
                                        Swal.fire({
                                            title: 'Login Required',
                                            text: 'Please login to book a class.',
                                            icon: 'warning',
                                            confirmButtonColor: '#FF9800',
                                            background: '#1a1a1a',
                                            color: '#fff'
                                        });
                                    } else {
                                        Swal.fire({
                                            title: 'Error',
                                            text: 'Could not book class. Please try again.',
                                            icon: 'error',
                                            confirmButtonColor: '#FF5252',
                                            background: '#1a1a1a',
                                            color: '#fff'
                                        });
                                    }
                                }
                            });
                        });

                        actionDiv.append(cap);
                        actionDiv.append(joinBtn);

                        item.append(info);
                        item.append(actionDiv);
                        list.append(item);
                        delayCounter++;
                    });

                    container.append(list);
                }
            });
        });
    }, 300);
}
