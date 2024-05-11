<script>
    import { nameRenderer, developerMode, theme, online, gifs, linkHandler, channelScrollPosition, hideSpoilers, font, timestampFormat, dateFormat, timeFormat, locale} from '../../js/stores/settingsStore.svelte';
    import { dateFormats, timeFormats, formatMoment, browserLocales } from '../../js/time';
    import RadioButton from './RadioButton.svelte';
    import RadioGroup from './RadioGroup.svelte';
    import MenuOpenOverlay from './MenuOpenOverlay.svelte';
    import { getLayoutState } from '../../js/stores/layoutState.svelte';
    import Icon from '../icons/Icon.svelte';
    let testDate = '2020-01-16T11:04:47.215+00:00';
    let selectedTab = 'appearance';

    function selectTab(tab) {
        selectedTab = tab;
        layoutState.hideSettingsSideMenu()
    }


    function closeBtn() {
        layoutState.hideSettings()
        layoutState.showSettingsSideMenu()
    }

    const layoutState = getLayoutState()
</script>

<div class="close-btn" on:click={closeBtn}>
    <svg role="img" width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M18.4 4L12 10.4L5.6 4L4 5.6L10.4 12L4 18.4L5.6 20L12 13.6L18.4 20L20 18.4L13.6 12L20 5.6L18.4 4Z"></path></svg>
</div>


<div class="container" class:hidden={!layoutState.settingsshown} class:mobilemenuhidden={!layoutState.settingssidemenushown}>
    <div class="tabs">
        <div class="category">App settings</div>
        <div class="tab" class:selected={selectedTab == "appearance"} on:click={() => selectTab("appearance")}>Appearance</div>
        <div class="tab" class:selected={selectedTab == "privacy"} on:click={() => selectTab("privacy")}>Privacy & Safety</div>
        <div class="tab" class:selected={selectedTab == "accessibility"} on:click={() => selectTab("accessibility")}>Accessibility</div>

        <hr>

        <div class="category">Advanced settings</div>
        <div class="tab" class:selected={selectedTab == "advanced"} on:click={() => selectTab("advanced")}>Advanced</div>
    </div>

    <div class="settings-scroller">
        <MenuOpenOverlay leftOffset={233} />

        <div class="settings">
            {#if selectedTab == "appearance"}
                <div class="title-wrapper">
                    <div class="hamburger-btn" on:click={layoutState.toggleSettingsSideMenu}>
                        <Icon name="other/hamburger" width={37*.5} height={32*.5} />
                    </div>
                    <div class="title">Appearance</div>
                </div>

                <RadioGroup
                    title={"Name format"}
                >
                    <RadioButton
                        title={"Display name"}
                        name={"nameRenderer"}
                        value={"nickname"}
                        bind:group={$nameRenderer}
                    />

                    <RadioButton
                        title={"Username"}
                        name={"nameRenderer"}
                        value={"handle"}
                        bind:group={$nameRenderer}
                    />

                    <RadioButton
                        title={"Both"}
                        name={"nameRenderer"}
                        value={"both"}
                        bind:group={$nameRenderer}
                    />
                </RadioGroup>

                <hr>

                <RadioGroup
                    title={"Date locale"}
                    description="Only affects date and time formats. This list is based on your browser's language settings."
                >
                    {#each browserLocales as localeItem, i}
                        <RadioButton
                            title={localeItem}
                            name={"dateRenderers"}
                            value={localeItem}
                            bind:group={$locale}
                        />
                    {/each}
                </RadioGroup>

                <hr>
                {#key $timestampFormat}
                    <RadioGroup
                        title={"Date format"}
                        description={$dateFormat}
                    >
                        {#each dateFormats as dateFormatItem, i}
                            <RadioButton
                                title={formatMoment(testDate, dateFormatItem)}
                                name={"dateRenderers"}
                                value={dateFormatItem}
                                bind:group={$dateFormat}
                            />
                        {/each}
                    </RadioGroup>
                {/key}

                <hr>

                <RadioGroup
                    title={"Time format"}
                    description={$timeFormat}
                >
                    {#each timeFormats as timeFormatItem, i}
                        <RadioButton
                            title={formatMoment(testDate, timeFormatItem)}
                            name={"timeRenderers"}
                            value={timeFormatItem}
                            bind:group={$timeFormat}
                        />
                    {/each}
                </RadioGroup>

                <hr>

                <RadioGroup
                    title={"Default scroll position"}
                    description={"For channels/threads/forum posts"}
                >
                    <RadioButton
                        title={"Bottom"}
                        name={"channelScrollPosition"}
                        value={"bottom"}
                        bind:group={$channelScrollPosition}
                    />

                    <RadioButton
                        title={"Top"}
                        name={"channelScrollPosition"}
                        value={"top"}
                        bind:group={$channelScrollPosition}
                    />
                </RadioGroup>

                <hr>

                <RadioGroup
                    title={"Theme"}
                    description={"Only dark theme works correctly at the moment"}
                >
                    <RadioButton
                        title={"Dark"}
                        name={"theme"}
                        value={"dark"}
                        bind:group={$theme}
                    />

                    <RadioButton
                        title={"Black [Work in progress]"}
                        name={"theme"}
                        value={"black"}
                        bind:group={$theme}
                    />

                    <RadioButton
                        title={"White [Work in progress]"}
                        name={"theme"}
                        value={"white"}
                        bind:group={$theme}
                    />
                </RadioGroup>
            {/if}

            {#if selectedTab == "privacy"}
                <div class="title-wrapper">
                    <HamburgerBtn />
                    <div class="title">Privacy & Safety</div>
                </div>

                <RadioGroup
                    title={"Online mode"}
                    description={"If enabled, this will allow you to view emojis, stickers, attachments, embeds, etc. that you don't have downloaded"}
                >
                    <RadioButton
                        title={"Yes"}
                        name={"online"}
                        value={true}
                        bind:group={$online}
                    />
                    <RadioButton
                        title={"No"}
                        name={"online"}
                        value={false}
                        bind:group={$online}
                    />
                </RadioGroup>

                <hr>

                <RadioGroup
                    title={"Render tenor gifs"}
                    description={"If enabled, this option will render remote tenor gif instead of showing a thumbnail. Requires online mode to be enabled."}
                >
                    <RadioButton
                        title={"Yes"}
                        name={"gifs"}
                        value={true}
                        bind:group={$gifs}
                    />
                    <RadioButton
                        title={"No"}
                        name={"gifs"}
                        value={false}
                        bind:group={$gifs}
                    />
                </RadioGroup>

                <hr>

                <RadioGroup
                    title={"Hide/blur spoilers"}
                >
                    <RadioButton
                        title={"Yes"}
                        name={"hideSpoilers"}
                        value={true}
                        bind:group={$hideSpoilers}
                    />

                    <RadioButton
                        title={"No"}
                        name={"hideSpoilers"}
                        value={false}
                        bind:group={$hideSpoilers}
                    />
                </RadioGroup>

            {/if}

            {#if selectedTab == "accessibility"}
                <div class="title-wrapper">
                    <HamburgerBtn />
                    <div class="title">Accessibility</div>
                </div>

                <RadioGroup
                    title={"Discord font"}
                >
                    <RadioButton
                        title={"gg sans (new discord font)"}
                        name={"font"}
                        value={"ggsans"}
                        bind:group={$font}
                    />

                    <RadioButton
                        title={"Whitney (old discord font)"}
                        name={"font"}
                        value={"whitney"}
                        bind:group={$font}
                    />

                    <RadioButton
                        title={"Arial"}
                        name={"font"}
                        value={"arial"}
                        bind:group={$font}
                    />

                    <RadioButton
                        title={"Times New Roman"}
                        name={"font"}
                        value={"timesnewroman"}
                        bind:group={$font}
                    />

                    <RadioButton
                        title={"Comic Sans"}
                        name={"font"}
                        value={"comicsans"}
                        bind:group={$font}
                    />
                </RadioGroup>
            {/if}


            {#if selectedTab == "advanced"}
                <div class="title-wrapper">
                    <HamburgerBtn />
                    <div class="title">Advanced</div>
                </div>

                <!-- "discord://" URL protocol for invoking application has to be registered -->
                <RadioGroup
                    title={"Open discord links"}
                    description={"Right click message to open in Discord"}
                >
                    <RadioButton
                        title={"In browser"}
                        name={"linkHandler"}
                        value={"browser"}
                        bind:group={$linkHandler}
                    />

                    <RadioButton
                        title={"In discord app"}
                        name={"linkHandler"}
                        value={"app"}
                        bind:group={$linkHandler}
                    />
                </RadioGroup>

                <hr>
                <RadioGroup
                    title={"Show memory usage"}
                >
                    <RadioButton
                        title={"Disabled"}
                        name={"developerMode"}
                        value={false}
                        bind:group={$developerMode}
                    />
                    <RadioButton
                        title={"Enabled"}
                        name={"developerMode"}
                        value={true}
                        bind:group={$developerMode}
                    />
                </RadioGroup>
            {/if}
        </div>
    </div>
</div>

<style>
    .hidden {
        display: none !important;
    }

    .container {
        position: fixed;
        top: 0;
        left: 0;
        display: grid;
        grid-template-columns: 1fr 2fr;
        height: 100dvh;
        width: 100vw;
        z-index: 1000;
        min-width: 700px;
        background-color: #313338;
    }
    @media (max-width: 1000px) {
        .container {
            width: calc(233px + 100vw);
            left: 0px;
            grid-template-columns: 233px 2fr;
            transition: left 0.2s ease-in-out;
        }
        .container.mobilemenuhidden {
            left: -233px;
        }
    }

    .tabs {
        background-color: #2b2d31;
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding-top: 30px;
        padding-left: 30px;
        padding-right: 10px;
        align-items: flex-end;
    }

    .tab {
        width: 200px;
        border-radius: 5px;
        cursor: pointer;

        padding-top: 6px;
        padding-bottom: 6px;
        padding-left: 10px;
        margin-bottom: 2px;
        border-radius: 4px;

        position: relative;
        font-size: 16px;
        line-height: 20px;
        cursor: pointer;
        font-weight: 500;

        color: #b5bac1;
    }

    .tab:hover
    {
        background-color: #35373c;
        color: #dbdee1;
    }

    .tab.selected {
        background-color: #404249;
        color: white;
    }

    .tabs .category {
        width: 200px;
        color:#949ba4;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .02em;
        font-size: 12px;
        line-height: 16px;
        margin-bottom: 5px;
    }

    .tabs hr {
        border: 0;
        height: 1px;
        background: #3b3d44;
        margin: 5px 30px 15px 0;
        width: 172px;
    }

    .settings-scroller {
        position: relative;
        padding-top: 30px;
        background-color: #313338;
        padding-left: 35px;
        padding-right: 35px;
        width: 100%;
        max-height: 100vh;

        overflow-y: auto;
    }
    @media (max-width: 1000px) {
        .settings-scroller {
            margin-right: -233px;
            margin-left: 0px;
        }
    }

    .settings {
        width: 100%;
        max-width: 660px;
    }

    .close-btn {
        position: absolute;
        top: 30px;
        right: 30px;
        cursor: pointer;

        display: grid;
        place-items: center;

        width: 32px;
        height: 32px;

        border: 2px solid #b5bac1;
        border-radius: 50%;
        left: auto;
        z-index: 1005;
    }
    .close-btn svg {
        color: #b5bac1;
    }
    .close-btn:hover {
        border: 2px solid #dbdee1;
    }
    .close-btn:hover svg {
        color: #dbdee1;
    }

    .settings .title-wrapper {
        display: flex;
        gap: 20px;

        align-items: center;
        padding-bottom: 20px;
    }

    .settings .title {
        font-weight: 600;
        font-size: 20px;
        line-height: 24px;
        color: #f2f3f5;
    }

    .settings hr {
        border: 0;
        height: 1px;
        background: #3f4147;
        margin: 30px 0 40px 0;
    }

    .hamburger-btn {
        display: none;
    }
    @media (max-width: 1000px) {
        .hamburger-btn {
            display: block;
        }
    }
</style>
