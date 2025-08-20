// ideal_completion.js
$(document).ready(function() {
    const $tbody = $('#week-vw tbody');

    // Create time slots
    for (let hour = 0; hour < 24; hour++) {
        for (let minute = 0; minute < 60; minute++) {
            const $row = $('<tr>');

            // Show hour only at the start of each hour
            if (minute === 0) {
                const $timeCell = $('<td>')
                    .text(`${String(hour).padStart(2, '0')}:00`)
                    .attr('rowspan', 60)
                    .addClass('time-cell');
                $row.append($timeCell);
            }

            for (let day = 0; day < 7; day++) {
                const $eventCell = $('<td>')
                    .attr('data-time', `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`)
                    .attr('data-day', day)
                    .addClass('minute-cell');

                if (minute === 0) {
                    $eventCell.addClass('first-minute');
                }
                if (minute === 59) {
                    $eventCell.addClass('last-minute');
                }

                $row.append($eventCell);
            }

            $tbody.append($row);
        }
    }

    // Sample events
    const plans = [
        { title: 'Morning Briefing', day: 0, startTime: '09:00', endTime: '10:00' },
        { title: 'Different Meeting', day: 0, startTime: '09:00', endTime: '10:00' },
        { title: 'Lunch Time', day: 0, startTime: '10:30', endTime: '13:00' },
        { title: 'Work on Project', day: 0, startTime: '13:00', endTime: '15:00' },
        { title: 'Meeting with Client', day: 0, startTime: '14:00', endTime: '15:30' },

        // Tuesday (day: 1)
        { title: 'Daily Standup', day: 1, startTime: '10:15', endTime: '10:45' },
        { title: 'Extra Meeting', day: 1, startTime: '09:00', endTime: '10:00' },
        { title: 'Review Designs', day: 1, startTime: '11:00', endTime: '12:00' },
        { title: 'Lunch with Team', day: 1, startTime: '12:00', endTime: '13:00' },
        { title: 'Sprint for Development', day: 1, startTime: '14:00', endTime: '16:00' },

        // Wednesday (day: 2)
        { title: 'Calling the Client', day: 2, startTime: '14:00', endTime: '15:00' },
        { title: 'Weekly Meeting', day: 2, startTime: '09:30', endTime: '10:30' },
        { title: 'Review Code', day: 2, startTime: '11:00', endTime: '12:00' },
        { title: 'Plan Project', day: 2, startTime: '13:00', endTime: '14:30' },
        { title: 'Finish Meeting', day: 2, startTime: '15:00', endTime: '16:00' },

        // Thursday (day: 3)
        { title: 'Extended Work Hours', day: 3, startTime: '15:00', endTime: '21:00' },
        { title: 'Meet the Team', day: 3, startTime: '10:00', endTime: '11:00' },
        { title: 'Review Sprint', day: 3, startTime: '11:30', endTime: '12:30' },
        { title: 'Feedback from Customer', day: 3, startTime: '13:00', endTime: '14:00' },
        { title: 'Demo of Project', day: 3, startTime: '16:00', endTime: '17:00' },

        // Friday (day: 4)
        { title: 'Discuss Project', day: 4, startTime: '15:30', endTime: '16:30' },
        { title: 'Check-in with Team', day: 4, startTime: '10:00', endTime: '11:00' },
        { title: 'Workshop on Design', day: 4, startTime: '11:30', endTime: '13:00' },
        { title: 'Refactor the Code', day: 4, startTime: '13:30', endTime: '15:00' },
        { title: 'End Week Summary', day: 4, startTime: '16:00', endTime: '17:00' },

        // Saturday (day: 5)
        { title: 'Weekend Assignment', day: 5, startTime: '10:00', endTime: '14:00' },
        { title: 'Event for Networking', day: 5, startTime: '15:00', endTime: '17:00' },
        { title: 'Conduct Workshop', day: 5, startTime: '11:00', endTime: '13:00' },
        { title: 'Friends for Lunch', day: 5, startTime: '13:00', endTime: '14:00' },
        { title: 'Downtime Activity', day: 5, startTime: '14:00', endTime: '17:00' },

        // Sunday (day: 6)
        { title: 'Relax Days', day: 6, startTime: '09:00', endTime: '12:00' },
        { title: 'Gather with Family', day: 6, startTime: '12:00', endTime: '15:00' },
        { title: 'Activities Outdoor', day: 6, startTime: '15:00', endTime: '18:00' },
        { title: 'Get Ready for Next Week', day: 6, startTime: '18:00', endTime: '19:00' },
        { title: 'Evening Meal', day: 6, startTime: '19:00', endTime: '21:00' }
    ];

    renderPlans(plans);
});

function renderPlans(plans) {
    const borderWidth = 1;
    const margin = 5;

    const plansByStartTimeAndDay = plans.reduce(function(accumulator, plan) {
        const key = `${plan.startTime}-${plan.day}`;
        accumulator[key] = accumulator[key] || [];
        accumulator[key].push(plan);
        return accumulator;
    }, {});

    $.each(plansByStartTimeAndDay, function(key, planGroup) {
        const groupLength = planGroup.length;
        const totalMargin = margin * (groupLength - 1);
        const availableWidth = 100;
        const planWidth = (availableWidth - totalMargin) / groupLength;
        
        $.each(planGroup, function(index, plan) {
            const start = parseTime(plan.startTime);
            const end = parseTime(plan.endTime);
            const startMinute = start.hours * 60 + start.minutes;
            const endMinute = end.hours * 60 + end.minutes;
            const totalMinutes = endMinute - startMinute;
            const planHeight = totalMinutes + (Math.floor(totalMinutes / 60) * borderWidth);
            const timeStr = `${String(start.hours).padStart(2, '0')}:${String(start.minutes).padStart(2, '0')}`;
            const $startCell = $(`[data-time="${timeStr}"][data-day="${plan.day}"]`).first();

            if ($startCell.length) {
                const $planElement = $('<div>')
                    .addClass('event')
                    .text(`${plan.startTime} - ${plan.endTime}: ${plan.title}`)
                    .css({
                        height: `${planHeight}px`,
                        'background-color': 'rgba(38,137,216,.6)',
                        width:groupLength > 1 ? `calc(${planWidth}% - ${margin}px)` : `${planWidth}px`,
                        left: groupLength > 1 ? `calc(${(planWidth + (margin * 100 / availableWidth)) * index}% + ${margin * index}px)` : '0',
                        position: 'absolute',
                        top: '0',
                        'z-index': index + 1
                    })
                    .on('click', function() {
                        $('.event.selected').removeClass('selected');
                        $(this).addClass('selected');
                    });

                $startCell.css('position', 'relative').append($planElement);
            }
        });
    });
}

function parseTime(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return { hours, minutes };
}