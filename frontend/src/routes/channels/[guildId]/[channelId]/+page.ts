import { error } from "@sveltejs/kit";

export const prerender = false;
export const ssr = false;

export async function load({ params, parent }) {
    const { guilds, guild } = await parent();


    // calculate thread exit message
    let mainChannelMessage = null
    let channelId = params.channelId
    if (channelId in guild.threadIdToMessageId) {
        let messageIdBack = guild.threadIdToMessageId[channelId]
        console.log('threadIdToMessageId', messageIdBack);
        // loop through all data.messages channels
        console.log('data.messages', messages);
        for (let channelIdLoop in guild.messages) {
            if (guild.messages[channelIdLoop][messageIdBack]) {
                mainChannelMessage = guild.messages[channelIdLoop][messageIdBack]
                break
            }
        }
    }

	let messages
	try {
        let response = await fetch('/api/channel/' + params.channelId + '/messages')
        let messageIds = await response.json()
		console.log("messageIds", messageIds);

		messages = messageIds.map(messageId => {
			return {
				_id: messageId,
				loaded: false,
			}
		})

        // guildId = params.guildId
    }
    catch (e) {
        // failed = true
    }


    return {
        guilds: guilds,
        guildId: params.guildId,
        channelId: params.channelId,
        channel: guild.channels[params.channelId],
        guild: guild,
        messages: messages,
        mainChannelMessage: mainChannelMessage
    };
}