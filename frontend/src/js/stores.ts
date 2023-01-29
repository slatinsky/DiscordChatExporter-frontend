import {writable} from "svelte/store";

export const guildId = writable<string | null>(null);
export const channelId = writable<string | null>(null);
export const guilds = writable(null);
export const channels = writable(null);
export const channelCategories = writable(null);
export const messages = writable(null);
