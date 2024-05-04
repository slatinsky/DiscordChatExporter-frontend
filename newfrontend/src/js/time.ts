import moment from 'moment/min/moment-with-locales';
import { get } from 'svelte/store';
import {dateFormat, locale, timeFormat } from './stores/settingsStore.svelte';

export const browserLocales = [...new Set(['en', ...navigator.languages.map(lang => lang.split('-')[0])])]

let dateFormats = [
    'DD/MM/YYYY',
    'MM/DD/YYYY',
    'YYYY-MM-DD',
    'D.M.YYYY',
    'D MMMM, YYYY',
    'MMMM D, YYYY',
    'MMM D, YYYY',
    'D MMM, YYYY',
]

// add local formats if not already in the list
for (let lang of navigator.languages) {
    let m = moment(new Date()).locale(lang);

    for (let format_str of ['L', 'l', 'LL', 'll']) {
        let format = m.localeData().longDateFormat(format_str)
        if (!dateFormats.includes(format)) {
            dateFormats.push(format)
        }
    }
}

export {dateFormats}

export let timeFormats = [
    'HH:mm',
    'h:mm a',
    'HH:mm:ss',
    'h:mm:ss a',
    'HH:mm:ss.SSS',
    'h:mm:ss.SSS a',
]



export function formatMoment(date, format) {
    moment.locale(get(locale));
    return moment(date).format(format);
}

export function renderDate(date) {
    return formatMoment(date, get(dateFormat));
}

export function renderTime(date) {
    return formatMoment(date, get(timeFormat));
}

export function renderTimestamp(date) {
    return renderDate(date) + ' ' + renderTime(date);
}


// (modified) https://github.com/vegeta897/snow-stamp/blob/4803e7889da524b8c83bc2d72882b82f02622662/src/convert.js#L1-L9
// Converts a snowflake ID string into a JS Date object using the Discord's epoch (in ms)
const DISCORD_EPOCH = 1420070400000
export function snowflakeToDate(snowflake: string) {
	// Convert snowflake to BigInt to extract timestamp bits
	// https://discord.com/developers/docs/reference#snowflakes
	const milliseconds = BigInt(snowflake) >> 22n
	return new Date(Number(milliseconds) + DISCORD_EPOCH)
}

export function darkenColor(color: string, amount: number) {
    let red = parseInt(color.substring(1, 3), 16);
    let green = parseInt(color.substring(3, 5), 16);
    let blue = parseInt(color.substring(5, 7), 16);

    let redDarker = Math.round(red * (1 - amount)).toString(16).padStart(2, "0");
    let greenDarker = Math.round(green * (1 - amount)).toString(16).padStart(2, "0");
    let blueDarker = Math.round(blue * (1 - amount)).toString(16).padStart(2, "0");

    return "#" + redDarker + greenDarker + blueDarker;
}