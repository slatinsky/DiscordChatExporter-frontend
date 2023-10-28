import type { Load } from "@sveltejs/kit";
import type { Channel, Guild } from "src/js/interfaces";

export const prerender = false;
export const ssr = false;

export const load: Load = async({ fetch, params, parent }) => {
	let selectedGuildId = params.guildId;
	let selectedChannelId = params.channelId;
    const { guilds, channels } = await parent();
	let channel = channels.find((c: Channel) => c._id === selectedChannelId);
	let guild: Guild | undefined = guilds.find(g => g._id === selectedGuildId);

	let messages
	try {
        let response = await fetch(`/api/message-ids?guild_id=${selectedGuildId}&channel_id=${selectedChannelId}`)
        let messageIds = await response.json()

		messages = messageIds.map((messageId: string) => {
			return {
				_id: messageId,
				loaded: false,
			}
		})
    }
    catch (e) {
		console.error(e)
    }

    return {
        guild: guild,
        guildId: selectedGuildId,
		channel: channel,
        channelId: selectedChannelId,
        messages: messages,
    };
}