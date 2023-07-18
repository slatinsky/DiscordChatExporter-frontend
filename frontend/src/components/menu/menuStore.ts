import { writable, type Writable } from "svelte/store";

export const contextMenuItems: Writable<any[]> = writable([]);
export const position = writable({ x: 0, y: 0 });

export const isMenuHidden = writable(false);

// export const setMenuVisible = (e) => {
//     const rect=e.target.getBoundingClientRect();
//     position.set({x:100,y:100});
//     isMenuVisible.set(true);
// }