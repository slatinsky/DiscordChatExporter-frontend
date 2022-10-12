import { error } from "@sveltejs/kit";

export const prerender = false;
export const ssr = false;

// function addMessageAuthors(messages, authors) {
//     // loop object key values
//     for (const messageId in messages) {
//         if (messages[messageId].authorId) {
//             messages[messageId].author = authors[messages[messageId].authorId];
//         }
//     }
//     return messages;
// }


export async function load({ params, parent }) {
    const { guilds, guild } = await parent();
    return {
        guilds: guilds,
        guildId: params.guildId,
        channelId: params.channelId,
        channel: guild.channels[params.channelId],
        guild: guild,
        messages: guild.messages[params.channelId]
    };
    throw error(404, 'Not found');
}