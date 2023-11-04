import { get, writable } from "svelte/store";

export const searchShown = writable(false)
export const searchResultsMessageIds = writable([])
export const searchPrompt = writable("")
export const isSearching = writable(false)
export const searchPromptLarge = writable(false)

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