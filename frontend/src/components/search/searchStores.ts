import { writable } from "svelte/store";

export const searchShown = writable(false)
export const searchResultsMessageIds = writable([])
export const searchPrompt = writable("")