import { browser } from '$app/environment';


export async function fetchMessages(guildId, channelId) {
    if (browser) {
        let response = await fetch('/data/' + guildId + '/' + channelId + '/messages.json')
        let data = await response.json()
        return data
    }
}

export async function fetchAuthors(guildId) {
    if (browser) {
        // let response = await fetch('/data/' + guildId + '/authors.json')
        let response = await fetch('/data/authors.json')
        let data = await response.json()
        return data
    }
}