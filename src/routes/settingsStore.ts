import { writable } from "svelte/store";


export const nameRenderer = writable("nickname");
export const timestampFormat = writable(0);
export const developerMode = writable(false);

// restore from local storage
const storedNameRenderer = localStorage.getItem("nameRenderer");
if (storedNameRenderer) {
    nameRenderer.set(storedNameRenderer);
    console.log("restored nameRenderer from local storage", storedNameRenderer);
}
const storedTimestampFormat = localStorage.getItem("timestampFormat");
if (storedTimestampFormat) {
    timestampFormat.set(parseInt(storedTimestampFormat));
    console.log("restored timestampFormat from local storage", storedTimestampFormat);
}
const storedDeveloperMode = localStorage.getItem("developerMode");
if (storedDeveloperMode) {
    developerMode.set(storedDeveloperMode === 'true');
    console.log("restored developerMode from local storage", storedDeveloperMode);
}

timestampFormat.subscribe((value) => {
    // save to local storage
    localStorage.setItem("timestampFormat", value);
});
nameRenderer.subscribe((value) => {
    // save to local storage
    localStorage.setItem("nameRenderer", value);
});
developerMode.subscribe((value) => {
    // save to local storage
    localStorage.setItem("developerMode", value);
});
