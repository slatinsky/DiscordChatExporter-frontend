import { writable } from "svelte/store";

export const onlyMatches = writable(false)
export const searchTerm = writable('')
export const foundMessageIds = writable([])