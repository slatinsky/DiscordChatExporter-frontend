<script lang="ts">
    import Icon from "../icons/Icon.svelte";
    import {startingDayOfTheWeek} from "../../js/stores/settingsStore.svelte";

    interface MyProps {
        chooseDate: (dateSring: string) => void;
    }
    let { chooseDate }: MyProps = $props();

    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth() + 1;

    const SUNDAY = 0;
    const MONDAY = 1;

    startingDayOfTheWeek

    const daysAbbreviations = $derived.by(() => {
        if ($startingDayOfTheWeek === SUNDAY) return ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'];
        if ($startingDayOfTheWeek === MONDAY) return ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];
    });


    function getDaysCount(year, month) {
        return new Date(year, month, 0).getDate();
    }

    let selectedMonth = $state(currentMonth);
    let selectedMonthName = $derived.by(() => {
        let date = new Date(selectedYear, selectedMonth - 1, 1);
        return date.toLocaleString('default', { month: 'long' });
    });
    let selectedYear = $state(currentYear);

    let prevMonthMonth = $derived(selectedMonth === 1 ? 12 : selectedMonth - 1);
    let prevMonthYear = $derived(selectedMonth === 1 ? selectedYear - 1 : selectedYear);

    let nextMonthMonth = $derived(selectedMonth === 12 ? 1 : selectedMonth + 1);
    let nextMonthYear = $derived(selectedMonth === 12 ? selectedYear + 1 : selectedYear);

    let prevMonthDaysCount = $derived(getDaysCount(selectedYear, selectedMonth - 1));
    let thisMonthDaysCount = $derived(getDaysCount(selectedYear, selectedMonth));
    let dayOfTheWeek = $derived(new Date(selectedYear, selectedMonth - 1, 1).getDay());  // 0 is Sunday, for first day of the week

    function pad2(n) { return n < 10 ? '0' + n : n; }

    function isInFuture(dateString) {
        return new Date(dateString) > new Date() && dateString !== `${currentYear}-${pad2(currentMonth)}-${pad2(new Date().getDate())}`;
    }

    function isToday(dateString) {
        return dateString === `${currentYear}-${pad2(currentMonth)}-${pad2(new Date().getDate())}`;
    }

    let calendarRows = $derived.by(() => {
        let rows = [];
        let row = [];

        // push days from previous month if day of the week is not 0
        for (let i = dayOfTheWeek - $startingDayOfTheWeek; i > 0; i--) {
            const dateString = `${prevMonthYear}-${prevMonthMonth}-${prevMonthDaysCount - i}`
            row.push({
                date: dateString,
                day: prevMonthDaysCount - i,
                isThisMonth: false,
                isToday: isToday(dateString),
                isInFuture: isInFuture(dateString)
            });
        }
        row.reverse();

        // fill the rest
        for (let i = dayOfTheWeek; i < 7 + $startingDayOfTheWeek; i++) {
            const dateString = `${selectedYear}-${pad2(selectedMonth)}-${pad2(i - dayOfTheWeek + 1)}`
            row.push({
                date: dateString,
                day: i - dayOfTheWeek + 1,
                isThisMonth: true,
                isToday: isToday(dateString),
                isInFuture: isInFuture(dateString)
            });
        }

        rows.push(row);
        console.log("rows", rows);

        let currentDay = row[row.length - 1].day + 1;

        for (let j = 0; j < 5; j++) {
            row = [];
            for (let i = 0; i < 7; i++) {
                if (currentDay <= thisMonthDaysCount) {
                    const dateString = `${selectedYear}-${pad2(selectedMonth)}-${pad2(currentDay)}`;
                    row.push({
                        date: dateString,
                        day: currentDay,
                        isThisMonth: true,
                        isToday: isToday(dateString),
                        isInFuture: isInFuture(dateString)
                    });
                    currentDay++;
                } else {
                    const dateString = `${nextMonthYear}-${pad2(nextMonthMonth)}-${pad2(currentDay - thisMonthDaysCount)}`
                    row.push({
                        date: dateString,
                        day: currentDay - thisMonthDaysCount,
                        isThisMonth: false,
                        isToday: isToday(dateString),
                        isInFuture: isInFuture(dateString)
                    });
                    currentDay++;
                }
            }
            rows.push(row);
        }

        return rows;
    })


    function selectNextMonth() {
        if (selectedMonth === 12) {
            selectedMonth = 1;
            selectedYear++;
        } else {
            selectedMonth++;
        }
    }

    function selectPrevMonth() {
        if (selectedMonth === 1) {
            selectedMonth = 12;
            selectedYear--;
        } else {
            selectedMonth--;
        }
    }
</script>

<div class="calendar">
    <div class="calendar-top">
        <div class="calendar-header">
            <button onclick={selectPrevMonth} class="arrow left">
                <Icon name="other/dropdown" width={13} />
            </button>
            <div class="header-month">{selectedMonthName} {selectedYear}</div>
            {#if selectedMonth === currentMonth && selectedYear === currentYear}
                <!-- placeholder for the arrow if can't go more in the future -->
                <div style="width: 13px"></div>
            {:else}
                <button onclick={selectNextMonth} class="arrow right">
                    <Icon name="other/dropdown" width={13} />
                </button>
            {/if}
        </div>
        <hr>
        <div class="calendar-body">
            <div class="calendar-day-names">
                {#each daysAbbreviations as day}
                    <div>{day}</div>
                {/each}
            </div>
            <div class="calendar-grid">
                {#each calendarRows as row}
                    <div class="calendar-row">
                        {#each row as dayObj}
                            <div class="calendar-day" class:thismonth={dayObj.isThisMonth} class:infuture={dayObj.isInFuture} class:today={dayObj.isToday} onclick={() => {
                                if (!dayObj.isInFuture) {
                                    chooseDate(dayObj.date)
                                }
                            }}>
                                {dayObj.day}
                            </div>
                        {/each}
                    </div>
                {/each}
            </div>
        </div>
    </div>
    <div class="calendar-footer">
        You can also do <button class="hint" onclick={()=>chooseDate(String(currentYear - 1))}>{currentYear - 1}</button>
    </div>
</div>

<style>


    /* calendar body */
    .calendar {
        width: 100%;
        display: flex;
        flex-direction: column;
        background-color: #111214;
        border-radius: 5px;

        .calendar-top {
            background-color: #313338;
            border-radius: 4px;
            border: 1px solid #111214;
            padding: 20px 20px;

            .calendar-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: #b9bbbe;
                padding: 8px 0 20px 0;

                    /* navigation arrows */
                    button.arrow {
                        width: 17px;
                        height: 17px;
                        background-color: #313338;
                        color: #b9bbbe;
                        border-radius: 2px;

                        border: 1px solid #111214;

                        display: grid;
                        place-items: center;
                        cursor: pointer;
                    }

                    button.arrow.left {
                        transform: rotate(90deg);
                    }
                    button.arrow.right {
                        transform: rotate(-90deg);
                    }

                .header-month {
                    font-size: 13px;
                    font-weight: 600;
                    text-transform: uppercase;
                    color: #f9f9f9;
                }
            }

            hr {
                border: 0;
                border-top: 1px solid #27292d;
                margin: 0 0 8px 0;
            }

            .calendar-body {
                flex: 1;

                display: flex;
                flex-direction: column;
                gap: 4px;
                padding: 0;

                .calendar-day-names {
                    display: flex;
                    justify-content: space-between;
                    font-weight: 500;
                    font-size: 13px;
                    color: #a9a9ab;
                    margin: 0 11px 10px 11px;
                }

                .calendar-grid {

                    border-radius: 4px;
                    border: 1px solid #111214;
                    overflow: hidden;
                    user-select: none;


                    .calendar-row {
                        display: flex;

                        .calendar-day {
                            width: 100%;
                            height: 42px;
                            display: grid;
                            place-items: center;

                            border: 1px solid #111214;

                            background-color: #2b2d31;
                            color: #66676a;

                            font-size: 13px;
                            font-weight: 500;
                            cursor: pointer;
                            margin: -1px;
                            &.thismonth {
                                background-color: #313338;
                                color: #f9f9f9;
                                font-weight: 400;
                            }
                            &.thismonth:hover {
                                background-color: #5865f2;
                            }

                            &.infuture {
                                background-color: #2b2d31;
                                color: #66676a;
                                cursor: auto;
                            }
                            &.infuture:hover {
                                background-color: #2b2d31;
                            }

                            &.today {
                                padding-top: 5px;
                                border-bottom: 6px solid #5865f2;
                            }
                        }
                    }
                }
            }
        }

        .calendar-footer {
            padding: 20px 20px;
            font-size: 16px;
            font-weight: 400;
            color: #caccce;

            display: flex;
            gap: 4px;

            align-items: center;

            .hint {
                background-color: #5865f2;
                padding: 0 3px;
                font-weight: 500;
                font-size: 14px;
                color: #ffffff;
                border-radius: 3px;
                cursor: pointer;
            }

            .hint:hover {
                background-color: #707bf4;
            }
        }
    }



</style>