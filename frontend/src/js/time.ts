import moment from 'moment/min/moment-with-locales';
import { get } from 'svelte/store';
import {dateFormat, locale, timeFormat } from 'src/components/settings/settingsStore';

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