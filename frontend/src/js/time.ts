import moment from 'moment/min/moment-with-locales';
import { get } from 'svelte/store';
import {timestampFormat } from '../routes/settingsStore';

function renderTimestamp1(date) {
    return moment(date).format('YYYY-MM-DD HH:mm:ss');
}

function renderTimestamp2(date) {
    return moment(date).utcOffset(0).format('YYYY-MM-DD HH:mm:ss');
}

function renderTimestamp3(date) {
    return date;
}

function renderTimestamp4(date) {
    return moment(date).format();
}

function renderTimestamp5(date) {
    return moment(date).utcOffset(0).format();
}


function renderTimestamp6(date) {
    return moment(date).format('MMMM Do YYYY, h:mm:ss a');
}


function renderTimestampLang1(date, lang) {
    let m = moment(date).locale(lang);
    let format = m.format('LLL')
    return format;
}
function renderTimestampLang2(date, lang) {
    let m = moment(date).locale(lang);
    let format = m.format('LLLL')
    return format;
}

const timestampRenderersDup = []
timestampRenderersDup.push(renderTimestamp1);
timestampRenderersDup.push(renderTimestamp2);
timestampRenderersDup.push(renderTimestamp3);
timestampRenderersDup.push(renderTimestamp4);
timestampRenderersDup.push(renderTimestamp5);
timestampRenderersDup.push(renderTimestamp6);
navigator.languages.forEach(lang => {
    timestampRenderersDup.push((date) => renderTimestampLang1(date, lang));
});

navigator.languages.forEach(lang => {
    timestampRenderersDup.push((date) => renderTimestampLang2(date, lang));
});

// deduplicate timestampRenderers if they return same value
export const timestampRenderers = [];
let testDate = '2020-09-16T11:04:47.215+00:00';
timestampRenderersDup.forEach(renderer => {
    let found = false;
    timestampRenderers.forEach(renderer2 => {
        if (renderer(testDate) === renderer2(testDate)) {
            found = true;
        }
    });
    if (!found) {
        timestampRenderers.push(renderer);
    }
});

export function renderTimestamp(date) {
    return timestampRenderers[get(timestampFormat)](date);
}

export function renderDate(date) {
    return moment(date).format('YYYY-MM-DD');
}