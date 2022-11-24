import { writable } from "svelte/store";

export const filters = writable([])
export const searched = writable(false)
export const found_messages = writable([])
