import { derived, get, readable, writable } from "svelte/store";
import { threadshown } from "./layoutStore";
import { initRouter } from "./router";
import type { Channel } from "../interfaces";



async function fetchGuilds() {
    try {
        const response = await fetch('/api/guilds')
        const response_json = await response.json()
        console.log("guilds", response_json);
        guilds.set(response_json)
    }
    catch (e) {
        console.error("Failed to fetch guilds", e)
    }

    initRouter()
}


async function fetchCategoriesChannelsThreads(guildId: string) {
    try {
        const response = await fetch(`/api/channels?guild_id=${guildId}`)
        let json_response: Channel[] = await response.json()

        let categories_temp = []
        let channels_temp = []
        let lost_threads = []

        // create categories
        let found_categories_ids: string[] = []
        for (let channel of json_response) {
            if (channel.type !== "GuildPublicThread" && channel.type !== "GuildPrivateThread") {
                if (!found_categories_ids.includes(channel.categoryId)) {
                    let category = {
                        _id: channel.categoryId,
                        name: channel.category,
                        channels: [],
                        msg_count: 0,
                    }
                    categories_temp.push(category)
                    found_categories_ids.push(channel.categoryId)
                }
            }
        }

        // create channels (excluding threads)
        for (let channel of json_response) {
            if (channel.type !== "GuildPublicThread" && channel.type !== "GuildPrivateThread") {
                channel["threads"] = []
                channels_temp.push(channel)
            }
        }

        // add threads to their respective channels
        for (let channel of json_response) {
            if (channel.type === "GuildPublicThread" || channel.type === "GuildPrivateThread") {
                let parent_channel = channels_temp.find((c) => c._id === channel.categoryId)
                if (parent_channel) {
                    parent_channel.msg_count += channel.msg_count
                    parent_channel.threads.push(channel)
                }
                else {
                    lost_threads.push(channel)
                }
            }
        }

        // add channels to their respective categories
        for (let channel of channels_temp) {
            let category = categories_temp.find((c) => c._id === channel.categoryId)
            if (category) {
                category.msg_count += channel.msg_count
                category.channels.push(channel)
            }
            else {
                console.error("(this will never happen) - Category not found for channel", channel)
            }
        }

        // push threads without parent channel to a separate category so they are shown in the UI
        if (lost_threads.length > 0) {
            let msg_count = lost_threads.reduce((acc, thread) => acc + thread.msg_count, 0)
            categories_temp.push({
                _id: '0',
                name: 'Lost threads / forums',
                channels: [{
                    _id: '0',
                    type: 'GuildTextChat',
                    categoryId: '0',
                    category: 'Lost threads / forums',
                    name: 'Lost threads / forums',
                    topic: null,
                    threads: lost_threads,
                    msg_count: msg_count,
                    guildId: guildId,
                }]
            })
        }

        categories.set(categories_temp)
        console.log("categories", categories_temp);

        // sort categories, channels and threads by message count
        categories.update((categories) => {
            categories.forEach((category) => {
                category.channels.sort((a, b) => b.msg_count - a.msg_count)
                category.channels.forEach((channel) => {
                    channel.threads.sort((a, b) => b.msg_count - a.msg_count)
                })
            })
            return categories.sort((a, b) => b.msg_count - a.msg_count)
        })
    }
    catch (e) {
        console.error("Failed to fetch channels", e)
    }
}


async function fetchMessageIds(guildId: string, channelId: string) {
    try {
        let response = await fetch(`/api/message-ids?guild_id=${guildId}&channel_id=${channelId}`)
        let messageIds = await response.json()
        return messageIds
    }
    catch (e) {
        console.error("Failed to fetch message ids", e)
        return []
    }
}


export let guilds = writable([]);
export let categories = writable([]);


let selectedGuildId_set: any
export const selectedGuildId = readable(null, (set) => {
    selectedGuildId_set = set
})
export const selectedChannelId = writable(null);
export const selectedChannelMessageIds = writable([]);
export const selectedThreadId = writable(null);
export const selectedThreadMessageIds = writable([]);


export function selectGuild(guildId: string) {
    if (guildId === get(selectedGuildId)) {
        return
    }
    selectedGuildId_set(guildId)
    selectedChannelId.set(null)
    selectedChannelMessageIds.set([])
    selectedThreadId.set(null)
    selectedThreadMessageIds.set([])
}

// TODO: select channel, select thread, history tracking


// read only references
export const selectedGuild = derived(selectedGuildId, ($selectedGuildId) => {
    let guild = get(guilds).find(g => g._id === $selectedGuildId)
    if (!guild) {
        return null
    }
    return guild
});
selectedGuild.subscribe((newGuild) => {
    if (newGuild) {
        fetchCategoriesChannelsThreads(newGuild._id)
    }
    else {
        categories.set([])
    }
    selectedChannelId.set(null)
    selectedChannelMessageIds.set([])
})



export const selectedChannel = derived(selectedChannelId, ($selectedChannelId) => {
    let channel = get(categories).flatMap(c => c.channels).find(c => c._id === $selectedChannelId)
    if (!channel) {
        return null
    }
    return channel
});
selectedChannel.subscribe(async (newChannel) => {
    if (newChannel) {
        selectedChannelMessageIds.set(await fetchMessageIds(newChannel.guildId, newChannel._id))
    }
    if (newChannel && get(selectedThread) && newChannel._id !== get(selectedThread).categoryId) {
        selectedThreadId.set(null)
        selectedThreadMessageIds.set([])
        threadshown.set(false)
    }
    else {
        selectedThreadId.set(null)
        selectedThreadMessageIds.set([])
        threadshown.set(false)
    }
})



export const selectedThread = derived(selectedThreadId, ($selectedThreadId) => {
    let thread = get(categories).flatMap(c => c.channels).flatMap(c => c.threads).find(c => c._id === $selectedThreadId)
    if (!thread) {
        return null
    }
    return thread
});
selectedThread.subscribe(async (newThread) => {
    if (newThread) {
        selectedThreadMessageIds.set(await fetchMessageIds(newThread.guildId, newThread._id))
        threadshown.set(true)
    }
    else {
        threadshown.set(false)
    }
})



// fetch guilds on startup
fetchGuilds()

