import { get, writable } from "svelte/store";

export const searchShown = writable(false)
export const searchResultsMessageIds = writable([])
export const searchPrompt = writable("")
export const isSearching = writable(false)
export const searchPromptLarge = writable(false)
export const searchTemporarilyHidden = writable(false)

export async function submitSearch(guildId: string) {
    // do a fetch to the server to search for the message

    isSearching.set(true);
    searchShown.set(true);
    let query = get(searchPrompt);
    let response = await fetch(`/api/search?guild_id=${encodeURIComponent(guildId)}&prompt=${encodeURIComponent(query)}`);
    let json = await response.json();
    searchResultsMessageIds.set(json);
    searchShown.set(true);
    isSearching.set(false);
}





/*
on mobile we want to temporarily hide the search results after jump (to message) button is clicked
and show it again at the same scroll position when user clicks magnifying glass
*/
export async function hideSearchOnMobile() {
    if (window.innerWidth <= 1000 && !get(searchTemporarilyHidden)) {
        searchShown.set(false);
        searchTemporarilyHidden.set(true);
        window.addEventListener("resize", mobileToDesktopSwitch);
    }
}

export async function showSearchOnMobile() {
    if (get(searchTemporarilyHidden)) {
        searchShown.set(true);
        searchTemporarilyHidden.set(false);
        window.removeEventListener("resize", mobileToDesktopSwitch);
    }
}
function mobileToDesktopSwitch() {
    /*
    disable temporarily hidden search after switching to desktop view
    */
    if (window.innerWidth >= 1000 && get(searchTemporarilyHidden)) {
        searchShown.set(true);
        searchTemporarilyHidden.set(false);
        window.removeEventListener("resize", mobileToDesktopSwitch);
    }
}

export function doSearch(prompt: string, guildId: string) {
    if (prompt == "") {
        searchPrompt.set("");
        return;
    }
    searchPrompt.set(prompt);
    submitSearch(guildId);
}