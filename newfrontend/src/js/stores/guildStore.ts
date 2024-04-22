import { derived, get, writable } from "svelte/store";
import { threadshown } from "./layoutStore";


async function fetch_guilds() {
    try {
        const response = await fetch('/api/guilds')
        const response_json = await response.json()
        console.log("guilds", response_json);
        guilds.set(response_json)
    }
    catch (e) {
        console.error("Failed to fetch guilds", e)
    }
}


async function fetch_categories_channels_threads(guildId: string) {
    try {
        const response = await fetch(`/api/channels?guild_id=${guildId}`)
        let json_response = await response.json()

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
                category.channels.push(channel)
            }
            else {
                console.error("(this will never happen) - Category not found for channel", channel)
            }
        }

        // push threads without parent channel to a separate category so they are shown in the UI
        if (lost_threads.length > 0) {
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
                    msg_count: 0,
                    guildId: guildId,
                }]
            })
        }

        categories.set(categories_temp)
        console.log("categories", categories_temp);
    }
    catch (e) {
        console.error("Failed to fetch channels", e)
    }
}



export let guilds = writable([]);
export let categories = writable([]);

// changed externally
export const selectedGuildId = writable(null);  
export const selectedChannelId = writable(null);
export const selectedThreadId = writable(null);

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
        fetch_categories_channels_threads(newGuild._id)
    }
    else {
        categories.set([])
    }
    selectedChannelId.set(null)
})



export const selectedChannel = derived(selectedChannelId, ($selectedChannelId) => {
    let channel = get(categories).flatMap(c => c.channels).find(c => c._id === $selectedChannelId)
    if (!channel) {
        return null
    }
    return channel
});
selectedChannel.subscribe((newChannel) => {
    if (newChannel && get(selectedThread) && newChannel._id !== get(selectedThread).categoryId) {
        selectedThreadId.set(null)
        threadshown.set(false)
    }
    else {
        selectedThreadId.set(null)
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
selectedThread.subscribe((newThread) => {
    if (newThread) {
        threadshown.set(true)
    }
    else {
        threadshown.set(false)
    }
})

// fetch guilds on startup
fetch_guilds()

