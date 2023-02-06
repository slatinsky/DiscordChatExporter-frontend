// https://stackoverflow.com/questions/400212/how-do-i-copy-to-the-clipboard-in-javascript

import { get } from "svelte/store";
import type { Asset } from "./interfaces";
import { online } from "../routes/settingsStore";

function fallbackCopyTextToClipboard(text) {
    var textArea = document.createElement("textarea");
    textArea.value = text;

    // Avoid scrolling to bottom
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        var successful = document.execCommand('copy');
        var msg = successful ? 'successful' : 'unsuccessful';
        console.log('Fallback: Copying text command was ' + msg);
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }

    document.body.removeChild(textArea);
}
export function copyTextToClipboard(text) {
    if (!navigator.clipboard) {
        fallbackCopyTextToClipboard(text);
        return;
    }
    navigator.clipboard.writeText(text).then(function () {
        console.log('Async: Copying to clipboard was successful! Copied text: ' + text);
    }, function (err) {
        console.error('Async: Could not copy text: ', err);
    });
}

// usage
// copyTextToClipboard("text to copy");

export function checkUrl(asset: Asset) {
	if (!asset)
		return "";
	const url = asset.path;
    if (!url)
        return "";
    if (url.startsWith('https') || url.startsWith('http')) {
        if (!get(online)){
            console.warn("url was not allowed to load, because offline mode is enforced", url);
            return "";
        }
        console.warn('online url', url);
    }
    return "/input/" + url
}

export function getFileNameFromUrl(url) {
    if (!url)
        return "";
    return url.split('/').pop();
}


export function clamp(num: number, min: number, max: number): number {
    return Math.min(Math.max(num, min), max);
}
