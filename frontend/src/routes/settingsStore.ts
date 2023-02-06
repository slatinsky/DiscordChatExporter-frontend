import { writable } from "svelte/store";


export const nameRenderer = writable("nickname");
export const timestampFormat = writable(0);
export const developerMode = writable(false);
export const theme = writable("dark");
export const online = writable(false);
export const linkHandler = writable("app");
export const channelScrollPosition = writable("bottom");
export const hideSpoilers = writable(true);
export const font = writable("ggsans");

function withLocalStorage(store, localstorageKey: string, type = "string") {
    const restoredValue = localStorage.getItem(localstorageKey);
    if (restoredValue) {
        if (type === "int") {
            store.set(parseInt(restoredValue));
        }
        else if (type === "bool") {
            store.set(restoredValue === "true");
        }
        else {
            store.set(restoredValue);
        }
        console.log("restored", localstorageKey, "from local storage", restoredValue);
    }
    store.subscribe((value) => {
        localStorage.setItem(localstorageKey, value);
    });
}


withLocalStorage(nameRenderer, "nameRenderer", "string");
withLocalStorage(timestampFormat, "timestampFormat", "int");
withLocalStorage(developerMode, "developerMode", "bool");
withLocalStorage(theme, "theme", "string");
withLocalStorage(online, "online", "bool");
withLocalStorage(linkHandler, "linkHandler", "string");
withLocalStorage(channelScrollPosition, "channelScrollPosition", "string");
withLocalStorage(hideSpoilers, "hideSpoilers", "bool");
withLocalStorage(font, "font", "string");

