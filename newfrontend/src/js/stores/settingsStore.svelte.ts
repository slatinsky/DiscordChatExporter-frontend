import { derived, writable } from "svelte/store";

export const nameRenderer = writable("nickname");
export const locale = writable('en');  // for date formatting
export const dateFormat = writable('DD/MM/YYYY');
export const timeFormat = writable('HH:mm');

export const currentUserId = writable('');
export const currentUserName1 = writable('Anonymous');
export const currentUserName2 = writable('click to change');
export const currentUserPhoto = writable('/favicon.png');

export function setCurrentUser(id: string, name1: string, name2: string, photo: string) {
    currentUserId.set(id);
    currentUserName1.set(name1);
    currentUserName2.set(name2);
    currentUserPhoto.set(photo);
}

// for {#key} blocks
export const timestampFormat = derived([dateFormat, timeFormat, locale], ([dateFormat, timeFormat, locale]) => {
    return dateFormat + ' ' + timeFormat + ' ' + locale;
});

export const developerMode = writable(false);
export const theme = writable("dark");
export const online = writable(true);
export const gifs = writable(true);
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
        console.log("settingsStore - restored", localstorageKey, "from local storage", restoredValue);
    }
    store.subscribe((value) => {
        localStorage.setItem(localstorageKey, value);
    });
}



withLocalStorage(nameRenderer, "nameRenderer", "string");
withLocalStorage(locale, "locale", "string");
withLocalStorage(dateFormat, "dateFormat2", "string");
withLocalStorage(timeFormat, "timeFormat2", "string");
withLocalStorage(developerMode, "developerMode", "bool");
withLocalStorage(theme, "theme", "string");
withLocalStorage(online, "online", "bool");
withLocalStorage(linkHandler, "linkHandler", "string");
withLocalStorage(channelScrollPosition, "channelScrollPosition", "string");
withLocalStorage(hideSpoilers, "hideSpoilers", "bool");
withLocalStorage(font, "font", "string");
withLocalStorage(currentUserId, "currentUserId", "string");
withLocalStorage(currentUserName1, "currentUserName1", "string");
withLocalStorage(currentUserName2, "currentUserName2", "string");
withLocalStorage(currentUserPhoto, "currentUserPhoto", "string");


// old localstorage keys that should never be used again for backwards compatibility:
// `dateFormat`, `timeFormat`