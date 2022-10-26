import { writable } from "svelte/store";

export const isMenuVisible = writable(false);
export const position = writable({ x: 0, y: 0 });

export const setMenuVisible = (e) => {
    position.set({ x: e.clientX, y: e.clientY });
    isMenuVisible.set(true);
}