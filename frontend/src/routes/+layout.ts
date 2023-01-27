export const prerender = false;
export const ssr = false;

export async function load({ fetch, params }) {
    let response
    let guilds
    let guildId
    let failed = false
    try {
        response = await fetch('/api/guilds')
        guilds = await response.json()
		console.log("guilds", guilds);

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