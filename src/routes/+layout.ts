import { error } from "@sveltejs/kit";
import { goto } from '$app/navigation';

export const prerender = false;
export const ssr = false;

export async function load({ fetch, params }) {
    let response
    let guilds
    let guildId
    let failed = false
    try {
        response = await fetch('/data/guilds.min.json')
        guilds = await response.json()
        guildId = params.guildId
    }
    catch (e) {
        failed = true
    }

    // console.log(guilds)
    return {
        guilds: guilds,
        guildId: guildId,
        failed: failed
    };
}