import type { Category, Channel } from "../interfaces";

export async function fetchMessageIds(guildId: string | null, channelId: string, direction: "before" | "after" | "around" | "first" | "last", messageId: string | null = null, limit: number = 50) {
    if (guildId === null) {
        guildId = "000000000000000000000000"
    }
    if (messageId === null || messageId === "first") {
        messageId = "000000000000000000000000"
    }
    else if (messageId === "last") {
        messageId = "999999999999999999999999"
    }
    try {
        let response
        if (direction === "first") {
            response = await fetch(`/api/guild/messages?guild_id=${encodeURIComponent(guildId)}&channel_id=${encodeURIComponent(channelId)}&next_page_cursor=0&limit=${encodeURIComponent(limit)}`)
        }
        else if (direction === "last") {
            response = await fetch(`/api/guild/messages?guild_id=${encodeURIComponent(guildId)}&channel_id=${encodeURIComponent(channelId)}&prev_page_cursor=999999999999999999999999&limit=${encodeURIComponent(limit)}`)
        }
        else if (direction === "before") {
            response = await fetch(`/api/guild/messages?guild_id=${encodeURIComponent(guildId)}&channel_id=${encodeURIComponent(channelId)}&prev_page_cursor=${encodeURIComponent(messageId)}&limit=${encodeURIComponent(limit)}`)
        }
        else if (direction === "after") {
            response = await fetch(`/api/guild/messages?guild_id=${encodeURIComponent(guildId)}&channel_id=${encodeURIComponent(channelId)}&next_page_cursor=${encodeURIComponent(messageId)}&limit=${encodeURIComponent(limit)}`)
        }
        else {
            response = await fetch(`/api/guild/messages?guild_id=${encodeURIComponent(guildId)}&channel_id=${encodeURIComponent(channelId)}&around_page_cursor=${encodeURIComponent(messageId)}&limit=${encodeURIComponent(limit)}`)
        }

        let messageIds = await response.json()
        return messageIds
    }
    catch (e) {
        console.error("api - Failed to fetch message ids", e)
        return []
    }
}

export async function fetchSearch(guildId: string | null, prompt: string, direction: "before" | "after" | "around" | "first" | "last", messageId: string | null = null, limit: number = 50) {
    if (guildId === null) {
        guildId = "000000000000000000000000"
    }
    if (messageId === null || messageId === "first") {
        messageId = "000000000000000000000000"
    }
    else if (messageId === "last") {
        messageId = "999999999999999999999999"
    }
    try {
        let response
        if (direction === "first") {
            response = await fetch(`/api/guild/search?guild_id=${encodeURIComponent(guildId)}&prompt=${encodeURIComponent(prompt)}&next_page_cursor=0&limit=${encodeURIComponent(limit)}`)
        }
        else if (direction === "last") {
            response = await fetch(`/api/guild/search?guild_id=${encodeURIComponent(guildId)}&prompt=${encodeURIComponent(prompt)}&prev_page_cursor=999999999999999999999999&limit=${encodeURIComponent(limit)}`)
        }
        else if (direction === "before") {
            response = await fetch(`/api/guild/search?guild_id=${encodeURIComponent(guildId)}&prompt=${encodeURIComponent(prompt)}&prev_page_cursor=${encodeURIComponent(messageId)}&limit=${encodeURIComponent(limit)}`)
        }
        else if (direction === "after") {
            response = await fetch(`/api/guild/search?guild_id=${encodeURIComponent(guildId)}&prompt=${encodeURIComponent(prompt)}&next_page_cursor=${encodeURIComponent(messageId)}&limit=${encodeURIComponent(limit)}`)
        }
        else {
            response = await fetch(`/api/guild/search?guild_id=${encodeURIComponent(guildId)}&prompt=${encodeURIComponent(prompt)}&around_page_cursor=${encodeURIComponent(messageId)}&limit=${encodeURIComponent(limit)}`)
        }

        let messageIds = await response.json()
        return messageIds
    }
    catch (e) {
        console.error("api - Failed to fetch search", e)
        return []
    }
}

export async function fetchPinnedMessages(guildId: string | null, channelId: string, direction: "before" | "after" | "around" | "first" | "last", messageId: string | null = null, limit: number = 50) {
    const prompt = `pinned:true in_id:${encodeURIComponent(channelId)}`
    return fetchSearch(guildId, prompt, direction, messageId, limit)
}

export async function fetchSearchCount(guildId: string | null, prompt: string): Promise<number | string> {
    // delay a bit to make sure (faster) search query runs first
    await new Promise(r => setTimeout(r, 25));

    if (guildId === null) {
        guildId = "000000000000000000000000"
    }
    try {
        let response = await fetch(`/api/guild/search/count?guild_id=${encodeURIComponent(guildId)}&prompt=${encodeURIComponent(prompt)}`)
        let count = await response.text()
        // if numeric, return as number
        try {
            return Number(count)
        }
        catch (e) {
            return "error"
        }
    }
    catch (e) {
        console.error("api - Failed to fetch search count", e)
        return "error"
    }
}

export async function fetchAutocomplete(guildId: string | null, key: string, value: string, limit: number = 3) {
    if (guildId === null) {
        guildId = "000000000000000000000000"
    }
    try {
        let response = await fetch(`/api/guild/search/autocomplete?guild_id=${encodeURIComponent(guildId)}&key=${encodeURIComponent(key)}&value=${encodeURIComponent(value)}&limit=${encodeURIComponent(limit)}`)
        let json = await response.json()
        return json
    }
    catch (e) {
        console.error("api - Failed to fetch autocomplete", e)
        return []
    }
}



export async function fetchGuilds() {
    try {
        const response = await fetch('/api/guilds')
        const guilds = await response.json()
        console.log("guilds", guilds);
        return guilds
        // guilds.set(response_json)
    }
    catch (e) {
        console.error("api - Failed to fetch guilds", e)
    }
    return []
}


export async function fetchCategoriesChannelsThreads(guildId: string): Promise<Category[]> {
    if (guildId === null) {
        guildId = "000000000000000000000000"
    }
    console.log("aaaaaa fetchCategoriesChannelsThreads", guildId);
    try {
        const response = await fetch(`/api/guild/channels?guild_id=${guildId}`)
        let json_response: Channel[] = await response.json()

        let categories_temp = []
        let channels_temp = []
        let lost_threads = []



        // create categories
        if (guildId === "000000000000000000000000") {
            let category = {
                _id: '0',
                name: "Direct Messages",
                channels: [],
                msg_count: 0,
            }
            categories_temp.push(category)
        }
        else {
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
        }

        // create channels (excluding threads)
        for (let channel of json_response) {
            if (channel.type !== "GuildPublicThread" && channel.type !== "GuildPrivateThread") {
                channel["threads"] = []
                if (guildId === "000000000000000000000000") {
                    channel["categoryId"] = '0'
                }
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

        console.log("categories", categories_temp);
        categories_temp = categories_temp.sort((a, b) => b.msg_count - a.msg_count)
        categories_temp.forEach((category) => {
            category.channels = category.channels.sort((a, b) => b.msg_count - a.msg_count)
            category.channels.forEach((channel) => {
                channel.threads = channel.threads.sort((a, b) => b.msg_count - a.msg_count)
            })
        })

        return categories_temp
    }
    catch (e) {
        console.error("api - Failed to fetch channels", e)
    }
    return []
}