import { error } from "@sveltejs/kit";
import { goto } from '$app/navigation';


export const prerender = false;
export const ssr = false;

export async function load({ params, parent }) {
    let guildId = params.guildId
    let response = await fetch('/data/' + guildId + '/guild.json')
    let guild = await response.json()
    // console.log("eee", params.guildId);
    // console.log("iii", guild);

    // if (!params.channelId) {
    //     // select first channel by browsing to localhost:3000/[guildId]/[channelId]
    //     goto(`/${params.guildId}/${Object.keys(channels)[0]}`);
    //     return
    // }

    const { guilds } = await parent();
    return {
        guilds: guilds,
        guildId: params.guildId,
        guild: guild
    };
    throw error(404, 'Not found');
}