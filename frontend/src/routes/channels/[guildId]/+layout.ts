import { error, type Load } from "@sveltejs/kit";
import type { Channel, Guild } from "src/js/interfaces";


export const prerender = false;
export const ssr = false;

let guildIdFetched: string | null = null;
let json: Channel | null = null;

export const load: Load = async({ fetch, params, parent }) => {
	let selectedGuildId = params.guildId;
	let selectedChannelId = params.channelId;
	let guilds: Guild[] = (await parent()).guilds;
	let guild: Guild | undefined = guilds.find(g => g._id === selectedGuildId);

    let channels
    let guildId = params.guildId
    if (guildIdFetched === guildId) {  // prevent fetching the same guild multiple times in a row
        channels = json
    } else {
        let response = await fetch('/api/channels?guild_id=' + guildId)
        channels = await response.json()
    }

	let channel = channels.find((c: Channel) => c._id === selectedChannelId);

    return {
        guildId: selectedGuildId,
        channelId: selectedChannelId,
		channel: channel,
		guild: guild,
        channels: channels
    };
    throw error(404, 'Not found');
}