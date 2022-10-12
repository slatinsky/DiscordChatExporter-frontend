import { error } from "@sveltejs/kit";
import { goto } from '$app/navigation';

export const prerender = false;
export const ssr = false;

export async function load({ fetch, params }) {
    let response = await fetch('/data/guilds.json')
    let guilds = await response.json()
    // console.log(guilds)
    return {
        guilds: guilds
    };
    throw error(404, 'Not found');
}