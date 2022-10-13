import { error } from "@sveltejs/kit";
import { goto } from '$app/navigation';

export const prerender = false;
export const ssr = false;

export async function load({ fetch, params }) {
    let response = await fetch('/data/guilds.min.json')
    let guilds = await response.json()
    let guildId = params.guildId
    // console.log(guilds)
    return {
        guilds: guilds,
        guildId: guildId
    };
    throw error(404, 'Not found');
}