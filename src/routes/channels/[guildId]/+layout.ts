import { error } from "@sveltejs/kit";
import { goto } from '$app/navigation';


export const prerender = false;
export const ssr = false;

let guildIdFetched = null;
let json = null;

export async function load({ params, parent }) {
    let guild
    let guildId = params.guildId
    if (guildIdFetched === guildId) {  // prevent fetching the same guild multiple times in a row
        guild = json
    } else {
        let response = await fetch('/data/' + guildId + '/guild.min.json')
        guild = await response.json()
        guildIdFetched = guildId
        json = guild
    }

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
        channelId: params.channelId,
        guild: guild
    };
    throw error(404, 'Not found');
}