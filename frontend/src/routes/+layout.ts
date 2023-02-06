export const prerender = false;
export const ssr = false;
import type { Load } from '@sveltejs/kit';

export const load: Load = async({ fetch, params }) => {
    let response
    let guilds
    let failed = false
    try {
        response = await fetch('/api/guilds')
        guilds = await response.json()
		console.log("guilds", guilds);
    }
    catch (e) {
        failed = true
    }
    return {
        guilds: guilds,
		selectedGuildId: params.guildId,
        failed: failed
    };
}