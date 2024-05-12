import type { Message } from "./interfaces";
import { snowflakeToDate } from "./time";

export function checkUrl(asset) {
	if (!asset)
		return "";
	const url = asset.path;
    if (!url)
        return "";
    if (url.startsWith('https') || url.startsWith('http')) {
        console.warn('online url', url);
        return url;
    }
    return "/input/" + encodeURI(url)
}


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



export function humanFileSize(bytes: number, decimalPlaces: number) {
    if (bytes < 1024) {
        return `${bytes} B`;
    } else if (bytes < 1024 * 1024) {
        return `${Math.round(bytes / 1024 * Math.pow(10, decimalPlaces)) / Math.pow(10, decimalPlaces)} KB`;
    } else if (bytes < 1024 * 1024 * 1024) {
        return `${Math.round(bytes / 1024 / 1024 * Math.pow(10, decimalPlaces)) / Math.pow(10, decimalPlaces)} MB`;
    } else {
        return `${Math.round(bytes / 1024 / 1024 / 1024 * Math.pow(10, decimalPlaces)) / Math.pow(10, decimalPlaces)} GB`;
    }
}

export function isObjectEqual(a: any, b: any) {
	return JSON.stringify(a) === JSON.stringify(b)
}

export function isDateDifferent(previousMessage: Message | null, message: Message) {
    if (!previousMessage) {
        return true;
    }
    if (!message) {
        return true;
    }

    let prevDate = snowflakeToDate(previousMessage._id);
    let date = snowflakeToDate(message._id);

    return prevDate.getDate() !== date.getDate() || prevDate.getMonth() !== date.getMonth() || prevDate.getFullYear() !== date.getFullYear()
}