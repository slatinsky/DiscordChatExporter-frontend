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
        let response = await fetch('/api/channels?guild_id=' + guildId)
        channels = await response.json()
        channelsCached = channels
        guildIdCached = guildId
    }

	let channel
    if (channels) {
        channels.find((c: Channel) => c._id === selectedChannelId);
    }

    return {
        guildId: selectedGuildId,
        channelId: selectedChannelId,
		channel: channel,
		guild: guild,
        channels: channels
    };
    throw error(404, 'Not found');
}