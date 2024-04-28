import { writable } from "svelte/store";

export const searchShown = writable(false)
export const searchResultsMessageIds = writable([])
export const searchPrompt = writable("")
export const isSearching = writable(false)
export const searchPromptLarge = writable(false)
