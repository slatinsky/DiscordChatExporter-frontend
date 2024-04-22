import { writable } from "svelte/store";


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


async function fetch_channels(guildId: string) {
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
export const selectedGuildId = writable(null);
export const selectedChannelId = writable(null);
export const selectedThreadId = writable(null);

// fetch guilds on startup
fetch_guilds()

selectedGuildId.subscribe((value) => {
    if (value) {
        fetch_channels(value)
    }
    else {
        categories.set([])
    }
})