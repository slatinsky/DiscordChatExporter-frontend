import { error } from "@sveltejs/kit";

export const prerender = false;
export const ssr = false;


export async function load({ params, parent }) {
    const { guilds, guild } = await parent();
    let messages = guild.messages[params.channelId]

    return {
        guilds: guilds,
        guildId: params.guildId,
    };
}