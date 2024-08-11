import { getSearchState } from "../../lib/search/searchState.svelte";

const searchState = getSearchState();

let mobilesidepanelshown = $state(false);
let searchManuallyHidden = $state(false);
let threadshown = $state(false);
let searchshown = $derived(!searchManuallyHidden && searchState.canBeVisible && !threadshown);
let settingsshown = $state(false);
let debuglayout = $state(false);
let settingssidemenushown = $state(true);

let windowWidth = $state(window.innerWidth);
let windowHeight = $state(window.innerHeight);
let mobile = $derived(windowWidth < 800);

let channelpinnedshown = $state(false);
let threadpinnedshown = $state(false);


export function getLayoutState() {
    function toggleSidePanel() {
        mobilesidepanelshown = !mobilesidepanelshown;
    }
    function toggleSearch() {
        searchManuallyHidden = !searchManuallyHidden;
    }

    function showThread() {
        threadshown = true;
    }
    function hideThread() {
        threadshown = false;
    }
    function toggleThread() {
        if (threadshown) {
            hideThread()
        }
        else {
            showThread()
        }
    }

    function showSettings() {
        if (!settingsshown) {
            settingssidemenushown = true;
        }
        settingsshown = true;
    }
    function hideSettings() {
        settingsshown = false;
    }
    function toggleSettings() {
        if (settingsshown) {
            hideSettings()
        }
        else {
            showSettings()
        }
    }

    function toggleDebugLayout() {
        debuglayout = !debuglayout;
    }

    function showSettingsSideMenu() {
        settingssidemenushown = true;
    }
    function hideSettingsSideMenu() {
        settingssidemenushown = false;
    }
    function toggleSettingsSideMenu() {
        if (settingssidemenushown) {
            hideSettingsSideMenu()
        }
        else {
            showSettingsSideMenu()
        }
    }

    async function toggleChannelPinned() {
        if (channelpinnedshown) {
            hideChannelPinned()
        }
        else {
            await showChannelPinned()
        }
    }
    function hideChannelPinned() {
        channelpinnedshown = false;
    }
    async function showChannelPinned() {
        channelpinnedshown = true;
    }
    async function toggleThreadPinned() {
        if (threadpinnedshown) {
            hideThreadPinned()
        }
        else {
            await showThreadPinned()
        }
    }
    function hideThreadPinned() {
        threadpinnedshown = false;
    }
    async function showThreadPinned() {
        threadpinnedshown = true;
    }

    return {
        get mobilesidepanelshown() {
            return mobilesidepanelshown;
        },
        get searchshown() {
            return searchshown;
        },
        get threadshown() {
            return threadshown;
        },
        get settingsshown() {
            return settingsshown;
        },
        get debuglayout() {
            return debuglayout;
        },
        get mobile() {
            return mobile;
        },
        get windowWidth() {
            return windowWidth;
        },
        get windowHeight() {
            return windowHeight;
        },
        get settingssidemenushown() {
            return settingssidemenushown;
        },
        get channelpinnedshown() {
            return channelpinnedshown;
        },
        get threadpinnedshown() {
            return threadpinnedshown;
        },

        showThread,
        hideThread,
        toggleThread,
        toggleSearch,
        toggleSidePanel,
        showSettings,
        hideSettings,
        toggleSettings,
        toggleDebugLayout,
        showSettingsSideMenu,
        hideSettingsSideMenu,
        toggleSettingsSideMenu,
        toggleChannelPinned,
        hideChannelPinned,
        showChannelPinned,
        toggleThreadPinned,
        hideThreadPinned,
        showThreadPinned,
    };
}

function resize() {
    windowWidth = window.innerWidth
    windowHeight = window.innerHeight
}

window.addEventListener('resize', resize)