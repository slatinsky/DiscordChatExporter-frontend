
let mobilesidepanelshown = $state(true);
let searchshown = $state(false);
let threadshown = $state(false);
let settingsshown = $state(false);
let debuglayout = $state(false);
let settingssidemenushown = $state(true);

let windowWidth = $state(window.innerWidth);
let windowHeight = $state(window.innerHeight);
let mobile = $derived(windowWidth < 800);


export function getLayoutState() {
    function toggleSidePanel() {
        mobilesidepanelshown = !mobilesidepanelshown;
    }
    function toggleSearch() {
        if (!searchshown) {
            if (threadshown) {
                toggleThread()
            }
        }
        searchshown = !searchshown;
    }

    function showThread() {
        if (!threadshown) {
            if (searchshown) {
                toggleSearch()
            }
        }
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
    };
}

function resize() {
    windowWidth = window.innerWidth
    windowHeight = window.innerHeight
}

window.addEventListener('resize', resize)