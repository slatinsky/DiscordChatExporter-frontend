import { error, type Load } from "@sveltejs/kit";
import type { Channel, Guild } from "src/js/interfaces";


export const prerender = false;
export const ssr = false;


let channelsCached: Channel[] | null = [];
let guildIdCached: string | null | undefined = null;

export const load: Load = async({ fetch, params, parent }) => {
	let selectedGuildId = params.guildId;
	let selectedChannelId = params.channelId;
	let guilds: Guild[] = (await parent()).guilds;
	let guild: Guild | undefined = guilds.find(g => g._id === selectedGuildId);

    let guildId = params.guildId
    let channels = channelsCached
    if (guildIdCached !== guildId) {  // is cache invalid?
        let response = await fetch('/api/guild/channels?guild_id=' + guildId)
        channels = await response.json()
        channelsCached = channels
        guildIdCached = guildId
    }

	let channel: Channel
	let thread: Channel
    if (channels) {
        channel = channels.find((c: Channel) => c._id === selectedChannelId);
        if (channel && (channel.type === "GuildPublicThread" || channel.type === "GuildPrivateThread")) {
            thread = channel
            channel = channels.find((c: Channel) => c._id === channel.categoryId);
        }
    }
    else {
        console.error('Channels not found')
    }

    return {
        guildId: selectedGuildId,
        channelId: selectedChannelId,
		channel: channel,
		thread: thread,
		guild: guild,
        channels: channels
    };
    throw error(404, 'Not found');
}