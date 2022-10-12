import {get, writable} from "svelte/store";

// $page.params.guildId

export const guildId = writable<string | null>(null);
export const channelId = writable<string | null>(null);

export const guilds = writable(null);
export const channels = writable(null);
export const channelCategories = writable(null);
export const messages = writable(null);

// guildId.subscribe(async (id) => {
//     if (id) {
//         fetchGuilds()
//     }
//     else {
//         guilds.set(null)
//     }
//     console.log("guildId changed to", id)
// })

// channelId.subscribe(async (id) => {
//     if (id) {
//         fetchChannels()
//     }
//     else {
//         channels.set(null)
//     }
//     console.log("channelId changed to", id)
// })

