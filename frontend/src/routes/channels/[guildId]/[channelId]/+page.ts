import { error } from "@sveltejs/kit";

export const prerender = false;
export const ssr = false;

export async function load({ params, parent }) {
    const { guilds, guild } = await parent();
    let messages = guild.messages[params.channelId]

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