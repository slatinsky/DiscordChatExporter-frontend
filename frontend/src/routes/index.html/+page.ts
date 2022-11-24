import { goto } from '$app/navigation';

export const prerender = false;
export const ssr = false;

export async function load({ params, parent }) {
    // redirect /index.html to /
    // fixes binserve issue not serving root path
    goto(`/`);
}