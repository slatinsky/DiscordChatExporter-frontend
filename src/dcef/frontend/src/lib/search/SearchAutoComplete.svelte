<script lang="ts">
    import { checkUrl } from "../../js/helpers";
    import { fetchAutocomplete } from "../../js/stores/api";
    import { findChannelsByName, findThreadsByName, getGuildState } from "../../js/stores/guildState.svelte";
    import Icon from "../icons/Icon.svelte";
    import ChannelIcon from "../menuchannels/ChannelIcon.svelte";
    import SearchCalendar from "./SearchCalendar.svelte";
    import { getSearchState } from "./searchState.svelte";
    import { getLayoutState } from "../../js/stores/layoutState.svelte";

    interface MyProps {
        domInput: HTMLInputElement;
        visible: boolean;
        focusInput: () => void;
        blurInput: () => void;
    }
    let { domInput, visible, focusInput, blurInput}: MyProps = $props();

    const searchState = getSearchState()
    const guildState = getGuildState();
    const layoutState = getLayoutState();

    let lastWord = $derived(searchState.selection.lastWord);
    let isKey = $derived(searchState.selection.lastWordIsKey);
    let lastKey = $derived(searchState.selection.lastKey);
    let lastValue = $derived(searchState.selection.lastValue);
    let allHistory = $derived(searchState.searchHistory);
    let fromAutoComplete = $state([])
    let mentionAutoComplete = $state([])
    let channelAutoComplete = $state([])
    let threadAutoComplete = $state([])
    let filenameAutoComplete = $state([])
    let emojisAutoComplete = $state([])
    let selectBoolean = $state(false)

    let showCalendar = $state(false)

    let selectedSuggestionIndex = $state(-1);

    // hidden means that the option will be shown only if 2 or more characters of a new word are typed in the search prompt
    const allSearchOptions = [
        { key: 'from', value: 'user', hidden: false },
        { key: 'mentions', value: 'user', hidden: false },
        { key: 'has', value: 'link, embed or file', hidden: false },
        { key: 'before', value: 'specific date', hidden: false },
        { key: 'during', value: 'specific date', hidden: false },
        { key: 'after', value: 'specific date', hidden: false },
        { key: 'in', value: 'channel', hidden: false },
        { key: 'pinned', value: 'true or false', hidden: false },
        { key: 'reaction', value: 'emoji', hidden: false },
        { key: 'message_id', value: 'message id', hidden: true },
        { key: 'in_id', value: 'channel id', hidden: true },
        { key: 'category_id', value: 'category id', hidden: true },
        { key: 'from_id', value: 'user id', hidden: true },
        { key: 'mentions_id', value: 'user id', hidden: true },
        { key: 'reaction_from_id', value: 'user id', hidden: true },
        { key: 'reaction_id', value: 'reaction id', hidden: true }
    ]

    let searchOptions = $derived.by(()=> {  // filtered by key
        if (isKey) {
            return allSearchOptions.filter(option => {
                if (option.hidden && lastKey.length < 2) {
                    return false
                }
                return option.key.startsWith(lastKey.toLowerCase())
            })
        }
        return []
    })

    const allHasOptions = [
        'link',
        'embed',
        'poll',
        'file',
        'video',
        'image',
        'sound',
        'sticker',
    ]

    let hasOptions: string[] = $state([])

    let allDateOptions = $state([])
    let dateOptions = $state([])
    function generateDateOptions() {
        function pad2(n) { return n < 10 ? '0' + n : n; }
        const currentYear = new Date().getFullYear()
        const previousYear = currentYear - 1
        const currentMonth = new Date().getMonth() + 1

        let allDateOptions = [
            {
                display: 'today',
                value: `${currentYear}-${pad2(new Date().getMonth() + 1)}-${pad2(new Date().getDate())}`,
            },
            {
                display: 'yesterday',
                value: `${currentYear}-${pad2(new Date().getMonth() + 1)}-${pad2(new Date().getDate() - 1)}`,
            }
        ]

        const monthNames = {
            1: 'january',
            2: 'february',
            3: 'march',
            4: 'april',
            5: 'may',
            6: 'june',
            7: 'july',
            8: 'august',
            9: 'september',
            10: 'october',
            11: 'november',
            12: 'december',
        }


        // add years from 2015 to current year to allDateOptions
        for (let i = 2015; i <= currentYear; i++) {
            allDateOptions.push({
                display: i.toString(),
                value: i.toString()
            })
        }


        // add months from 1 to 12 to allDateOptions
        for (let i = 1; i <= 12; i++) {
            let dateString = ''
            if (currentMonth >= i) {
                dateString = `${currentYear}-${pad2(i)}`
            }
            else {
                dateString = `${previousYear}-${pad2(i)}`
            }

            allDateOptions.push({
                display: monthNames[i],
                value: dateString
            })
        }

        return allDateOptions
    }
    allDateOptions = generateDateOptions()





    let history = $derived.by(()=> {
        if (lastWord.length === 0) {
            return allHistory.slice(0, 5)
        }
        return (allHistory.filter(searchPrompt => searchPrompt.includes(lastWord))).slice(0, 5)
    })

    function clearHistory() {
        searchState.clearSearchHistory();
    }

    async function selectFullSuggestion(suggestion: string): any {
        const selection = searchState.selection;
        let newSearchPrompt = selection.textBefore
        if (selection.lastWord.length !== 0) {
            newSearchPrompt = newSearchPrompt.slice(0, selection.lastWord.length * -1)
        }
        newSearchPrompt += suggestion;
        if (selection.textAfter.length > 0 && selection.textAfter[0] !== ' ') {
            // remove next word till space or end
            let nextSpace = selection.textAfter.indexOf(' ')
            if (nextSpace === -1) {
                // no space found, remove the word after
            }
            else {
                newSearchPrompt += selection.textAfter.slice(nextSpace + 1);
            }
        }
        else {
            newSearchPrompt += selection.textAfter;
        }
        await guildState.changeThreadId(null)
        searchState.setSearchPrompt(newSearchPrompt);
        searchState.search(guildState.guildId)
        searchState.addToSearchHistory(newSearchPrompt)
        setTimeout(() => {
            blurInput();
        }, 0);
    }

    function selectKeySuggestion(suggestion: string): any {
        const selection = searchState.selection;
        console.log("selectKeySuggestion selection", selection);
        let newSearchPrompt = selection.textBefore
        if (selection.lastWord.length !== 0) {
            newSearchPrompt = newSearchPrompt.slice(0, selection.lastWord.length * -1)
        }
        newSearchPrompt += suggestion + ':';
        if (selection.textAfter.length > 0 && selection.textAfter[0] !== ' ') {
            // remove next word till space or end
            let nextSpace = selection.textAfter.indexOf(' ')
            if (nextSpace === -1) {
                // no space found, remove the word after
            }
            else {
                newSearchPrompt += selection.textAfter.slice(nextSpace + 1);
            }
        }
        else {
            newSearchPrompt += selection.textAfter;
        }
        searchState.setSearchPrompt(newSearchPrompt);
    }

    async function selectAndSearch(searchTerm: string): Promise<any> {
        console.log("searching for", searchTerm);
        await guildState.changeThreadId(null)
        searchState.setSearchPrompt(searchTerm)
        searchState.search(guildState.guildId)
        searchState.addToSearchHistory(searchTerm)
    }
    function restoreFocus(): any {
        // domInput.focus();
        focusInput();
    }

    export function arrowUp() {
        selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, 0);
    }
    export function arrowDown() {
        selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, searchOptions.length - 1);
    }
    export async function promptChanged() {
        selectedSuggestionIndex = -1;
        if (searchState.selection.lastWord.length === 0) {
            dateOptions = []
            hasOptions = []
            fromAutoComplete = []
            mentionAutoComplete = []
            channelAutoComplete = []
            threadAutoComplete = []
            filenameAutoComplete = []
            emojisAutoComplete = []
            selectBoolean = false
            showCalendar = false
        }
        else if (isKey && lastKey.length > 0) {
            dateOptions = allDateOptions.filter(filter => filter.display.startsWith(lastKey.toLowerCase()))
            hasOptions = allHasOptions.filter(filter => filter.startsWith(lastKey.toLowerCase()))
            const usersPromise = fetchAutocomplete(guildState.guildId, "users", searchState.selection.lastKey, 3)
            const fileNamePromise = fetchAutocomplete(guildState.guildId, "filenames", searchState.selection.lastKey, 3)
            const emojisPromise = fetchAutocomplete(guildState.guildId, "reactions", searchState.selection.lastKey, 3)
            channelAutoComplete = findChannelsByName(searchState.selection.lastKey).slice(0, 3)
            threadAutoComplete = findThreadsByName(searchState.selection.lastKey).slice(0, 3)
            fromAutoComplete = await usersPromise
            mentionAutoComplete = await usersPromise
            filenameAutoComplete = await fileNamePromise
            emojisAutoComplete = await emojisPromise
            selectBoolean = false
            showCalendar = false
        }
        else if (lastKey.toLowerCase() === 'from') {
            mentionAutoComplete = []
            channelAutoComplete = []
            threadAutoComplete = []
            filenameAutoComplete = []
            emojisAutoComplete = []
            fromAutoComplete = await fetchAutocomplete(guildState.guildId, "users", searchState.selection.lastValue, 10)
            selectBoolean = false
            showCalendar = false
        }
        else if (lastKey.toLowerCase() === 'mentions') {
            fromAutoComplete = []
            channelAutoComplete = []
            threadAutoComplete = []
            filenameAutoComplete = []
            emojisAutoComplete = []
            mentionAutoComplete = await fetchAutocomplete(guildState.guildId, "users", searchState.selection.lastValue, 10)
            selectBoolean = false
            showCalendar = false
        }
        else if (lastKey.toLowerCase() === 'in') {
            fromAutoComplete = []
            mentionAutoComplete = []
            filenameAutoComplete = []
            emojisAutoComplete = []
            channelAutoComplete = findChannelsByName(searchState.selection.lastValue).slice(0, 10)
            threadAutoComplete = findThreadsByName(searchState.selection.lastValue).slice(0, 10)
            selectBoolean = false
            showCalendar = false
        }
        else if (lastKey.toLowerCase() === 'file') {
            fromAutoComplete = []
            mentionAutoComplete = []
            channelAutoComplete = []
            threadAutoComplete = []
            emojisAutoComplete = []
            filenameAutoComplete = await fetchAutocomplete(guildState.guildId, "filenames", searchState.selection.lastValue, 10)
            selectBoolean = false
            showCalendar = false
        }
        else if (lastKey.toLowerCase() === 'pinned') {
            fromAutoComplete = []
            mentionAutoComplete = []
            channelAutoComplete = []
            threadAutoComplete = []
            filenameAutoComplete = []
            emojisAutoComplete = []
            selectBoolean = true
            showCalendar = false
        }
        else if (['before', 'during', 'after'].includes(lastKey.toLowerCase())) {
            fromAutoComplete = []
            mentionAutoComplete = []
            channelAutoComplete = []
            threadAutoComplete = []
            filenameAutoComplete = []
            emojisAutoComplete = []
            selectBoolean = false
            showCalendar = true
        }
        else if (lastKey.toLowerCase() === 'has') {
            hasOptions = allHasOptions.filter(filter => filter.startsWith(lastValue.toLowerCase()))
            fromAutoComplete = []
            mentionAutoComplete = []
            channelAutoComplete = []
            threadAutoComplete = []
            filenameAutoComplete = []
            emojisAutoComplete = []
            selectBoolean = false
            showCalendar = false
        }
        else if (lastKey.toLowerCase() === 'reaction') {
            fromAutoComplete = []
            channelAutoComplete = []
            threadAutoComplete = []
            filenameAutoComplete = []
            emojisAutoComplete = await fetchAutocomplete(guildState.guildId, "reactions", searchState.selection.lastValue, 10)
            mentionAutoComplete = []
            selectBoolean = false
            showCalendar = false
        }
        else {
            console.log("no autocomplete for", lastKey);
            fromAutoComplete = []
            mentionAutoComplete = []
            channelAutoComplete = []
            threadAutoComplete = []
            filenameAutoComplete = []
            emojisAutoComplete = []
            selectBoolean = false
            showCalendar = false
        }
    }


    function escapeValue(value: string) {
        value = value.replace(/"/g, '\\"');
        if (value.includes(' ')) {
            value = `"${value}"`;
        }
        return value;
    }
</script>

<div class="autocomplete list" class:visible={visible} class:ismobile={layoutState.mobile}>
    <!-- <div>lastWord: {lastWord}</div>
    <div>isKey: {isKey}</div>
    <div>lastKey: {lastKey}</div>
    <div>lastValue: {lastValue}</div>
    <div>selectedSuggestionIndex: {selectedSuggestionIndex}</div> -->
    {#if showCalendar}
        <SearchCalendar chooseDate={(dateString)=>{
            selectFullSuggestion(`${lastKey}:${dateString} `)
        }}/>
    {:else}
        {#if searchState.searchPrompt.length > 0 && isKey}
            <div class="searchfor">
                <div class="text-wrap">
                    <div class="searchfor-txt">Search For: </div>
                    <div class="searchfor-value">{searchState.searchPrompt}</div>
                </div>
                <div class="searchfor-entericon">enter</div>
            </div>
        {/if}
        {#if hasOptions.length > 0}
            <hr>
            <div class="list-group">
                <div class="category">
                    <div>Message Contains</div>
                </div>
                {#each hasOptions as hasOption, i}
                    <div class="item item-user" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectFullSuggestion(`has:${hasOption} `)}>
                        {#if isKey}
                            <span class="key">has:</span>
                        {/if}
                        <span class="displayname">{hasOption}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
        {#if fromAutoComplete.length > 0}
            <hr>
            <div class="list-group">
                <div class="category">
                    <div>From User</div>
                </div>
                {#each fromAutoComplete as user, i}
                    <div class="item item-user" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectFullSuggestion(`from:${escapeValue(user.key)} `)} title={user.description2}>
                        {#if isKey}
                            <span class="key">from:</span>
                        {/if}
                        <img src={checkUrl(user.icon)} alt="">
                        <span class="displayname">{user.description}</span> <span class="username">{user.key}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
        {#if mentionAutoComplete.length > 0}
            <hr>
            <div class="list-group">
                <div class="category">
                    <div>Mentions User</div>
                </div>
                {#each mentionAutoComplete as user, i}
                    <div class="item item-user" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectFullSuggestion(`mentions:${escapeValue(user.key)} `)} title={user.description2}>
                        {#if isKey}
                            <span class="key">mentions:</span>
                        {/if}
                        <img src={checkUrl(user.icon)} alt="">
                        <span class="displayname">{user.description}</span> <span class="username">{user.key}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
        {#if emojisAutoComplete.length > 0}
            <hr>
            <div class="list-group">
                <div class="category">
                    <div>Reaction</div>
                </div>
                {#each emojisAutoComplete as emoji, i}
                    <div class="item item-emoji" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectFullSuggestion(`reaction:${escapeValue(emoji.key)} `)} title={emoji.description2}>
                        {#if isKey}
                            <span class="key">reaction:</span>
                        {/if}
                        <img src={checkUrl(emoji.icon)} alt="">
                        <span class="displayname">{emoji.key}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
        {#if channelAutoComplete.length > 0}
            <hr>
            <div class="list-group">
                <div class="category">
                    <div>In Channel</div>
                </div>
                {#each channelAutoComplete as channel, i}
                    <div class="item item-channel" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectFullSuggestion(`in:${escapeValue(channel.name)} `)} title={`${channel.msg_count} messages`}>
                        {#if isKey}
                            <span class="key">in:</span>
                        {/if}
                        <span class="channelname"><ChannelIcon channel={channel} width={16} />{channel.name}</span> <span class="categoryname">{channel.category}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
        {#if threadAutoComplete.length > 0}
            <hr>
            <div class="list-group">
                <div class="category">
                    <div>In Thread</div>
                </div>
                {#each threadAutoComplete as channel, i}
                    <div class="item item-channel" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectFullSuggestion(`in:${escapeValue(channel.name)} `)} title={`${channel.msg_count} messages`}>
                        {#if isKey}
                            <span class="key">in:</span>
                        {/if}
                        <span class="channelname"><ChannelIcon channel={channel} width={16} />{channel.name}</span> <span class="categoryname">{channel.category}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
        {#if filenameAutoComplete.length > 0}
            <hr>
            <div class="list-group">
                <div class="category">
                    <div>Files</div>
                </div>
                {#each filenameAutoComplete as file, i}
                    <div class="item item-user" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectFullSuggestion(`file:${escapeValue(file.key)} `)} title={file.description2}>
                        {#if isKey}
                            <span class="key">file:</span>
                        {/if}
                        <!-- <img src={checkUrl(file.icon)} alt=""> -->
                        <span class="displayname">{file.description}</span> <span class="username">{file.key}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
        {#if searchOptions.length > 0}
            <hr>
            <div class="list-group">
                <div class="category">
                    <div>Search Options</div>
                    <a href="https://support.discord.com/hc/en-us/articles/115000468588-Using-Search" target="_blank" class="help-btn">
                        <Icon name="other/help" width={16} />
                    </a>
                </div>
                {#each searchOptions as filter, i}
                    <div class="item item-txt" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectKeySuggestion(filter.key)} title={`${filter.key}: ${filter.value}`}>
                        <span class="key">{filter.key}:</span> <span class="value">{filter.value}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
        {#if selectBoolean}
            <hr>
            <div class="list-group">
                <div class="item item-user" class:highlighted={selectedSuggestionIndex === 0} onclick={()=>selectFullSuggestion(`${lastKey}:true `)}>
                    <span class="key">true</span>
                </div>
                <div class="item item-user" class:highlighted={selectedSuggestionIndex === 1} onclick={()=>selectFullSuggestion(`${lastKey}:false `)}>
                    <span class="key">false</span>
                </div>
            </div>
        {/if}
        {#if dateOptions.length > 0}
            <hr>
            <div class="list-group">
                <div class="category">
                    <div>Dates</div>
                </div>
                {#each dateOptions as dateOption, i}
                    <div class="item item-user" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectFullSuggestion(`before:${dateOption.value} `)}>
                        {#if isKey}
                            <span class="key">before:</span>
                        {/if}
                        <span class="displayname">{dateOption.display}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                    <div class="item item-user" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectFullSuggestion(`during:${dateOption.value} `)}>
                        {#if isKey}
                            <span class="key">during:</span>
                        {/if}
                        <span class="displayname">{dateOption.display}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                    <div class="item item-user" class:highlighted={selectedSuggestionIndex === i} onclick={()=>selectFullSuggestion(`after:${dateOption.value} `)}>
                        {#if isKey}
                            <span class="key">after:</span>
                        {/if}
                        <span class="displayname">{dateOption.display}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
        {#if history.length > 0}
            <hr>
            <div class="list-group">
                <div class="category">
                    <div>History</div>
                    <button class="help-btn" onclick={clearHistory}>
                        <Icon name="other/bin" width={16} />
                    </button>
                </div>
                {#each history as searchPrompt}
                    <div class="item item-txt" onclick={()=>selectAndSearch(searchPrompt)} title={searchPrompt}>
                        <span class="value">{searchPrompt}</span>
                        <div class="gradient">
                            <div class="icon"><Icon name="other/plus" width={18} /></div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    {/if}
</div>



<style>
    .autocomplete::-webkit-scrollbar-track {
        background-color: #111214;
    }
    .autocomplete::-webkit-scrollbar-corner {
        background-color: #111214;
    }
    .autocomplete::-webkit-resizer {
        background-color: #111214;
    }
    .autocomplete::-webkit-scrollbar {
        width: 0px;
        height: 3px;
    }
    .autocomplete:hover::-webkit-scrollbar {
        width: 11px;
    }
    .autocomplete::-webkit-scrollbar-thumb {
        height: 50px;
        background-color: #2c2c2c;
        border-radius: 3px;

        width: 5px;
        border-radius: 10px;

        /*left+right scrollbar padding magix*/
        background-clip: padding-box;
        border: 3px solid #111214;
    }

    .autocomplete {
        position: absolute;
        top: 32px;
        left: 0px;
        background-color: #111214;
        width: 100%;
        max-width: 320px;
        z-index: 100;
        border-radius: 3px;

        max-height: 100svh;
        overflow-y: auto;

        &.ismobile {
            max-width: 100%;
        }

        display: none;
        &.visible {
            display: block;
        }

        .searchfor {
            display: flex;
            flex-wrap: nowrap;
            gap: 3px;
            align-items: center;

            height: 55px;
            background-color: #232428;
            padding: 15px;

            .text-wrap {
                display: flex;
                flex-wrap: nowrap;
                align-items: baseline;
                gap: 3px;
                flex: 1;
                overflow: hidden;

                .searchfor-txt {
                    text-transform: uppercase;
                    color: #c4c9ce;
                    font-weight: 400;
                    font-size: 12px;
                }

                .searchfor-value {
                    font-size: 15px;
                    font-weight: 600;
                    color: white;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    font-size: 15px;
                    flex: 1;
                }
            }



            .searchfor-entericon {
                color: #c4c9ce;
                background-color: #80848e;
                border: 1px solid #313338;
                height: 23px;
                padding: 1px 6px 4px 6px;
                border-radius: 4px;
                cursor: default;
                text-align: center;
                font-size: 12px;
                text-transform: uppercase;
                font-weight: 600;
                box-shadow: inset 0 -4px 0 #1e1f22;
            }
        }
    }

    .category {
        padding: 5px 20px 10px 20px;
        text-transform: uppercase;
        font-weight: 800;
        color: #b5bac1;
        font-size: 12px;

        display: flex;
        justify-content: space-between;
        flex-wrap: nowrap;

        .help-btn {
            cursor: pointer;
            color: #b5bac1;
        }
        .help-btn:hover {
            color: #d8dbde;
        }
    }

    .list {
        .list-group {
            padding: 10px 0;

            .item {
                padding: 0 10px;
                margin: 0 10px;
                cursor: pointer;
                height: 34px;
                display: flex;
                align-items: center;
                border-radius: 3px;
                font-size: 16px;

                display: flex;
                flex-wrap: nowrap;

                position: relative;

                overflow: hidden;

                .gradient {
                    position: absolute;
                    top: 0;
                    right: 0;
                    width: 60px;
                    height: 100%;
                    background: linear-gradient(90deg, #00000000 0%, #111214dd 70%, #111214 100%);

                    display: flex;
                    justify-content: end;
                    align-items: center;
                    padding-right: 8px;

                    .icon {
                        color: #dbdee1;
                        display: none;
                    }
                }

                &:hover,
                &.highlighted {
                    background-color: #232528;
                    .gradient {
                        background: linear-gradient(90deg, #00000000 0%, #313338dd 70%, #313338 100%);
                        .icon {
                            display: block;
                        }
                    }
                }
            }

            .item-txt {
                .key {
                    font-weight: 600;
                    color: #b5bac1;
                    margin-right: 5px;
                }

                .value {
                    font-weight: 500;
                    color: #949ba4;
                    white-space: nowrap;
                }
            }

            .item-user {
                .key {
                    font-size: 16px;
                    font-weight: 400;
                    color: #949ba4;
                    margin-right: 5px;
                }

                img {
                    width: 20px;
                    height: 20px;
                    margin-right: 5px;
                    border-radius: 50%;
                }

                .displayname {
                    font-size: 16px;
                    font-weight: 500;
                    color: #dbdee1;
                    margin-right: 5px;
                    white-space: nowrap;
                }

                .username {
                    font-size: 16px;
                    font-weight: 500px;
                    color: #949ba4;
                    white-space: nowrap;
                }
            }

            .item-emoji {
                .key {
                    font-size: 16px;
                    font-weight: 400;
                    color: #949ba4;
                    margin-right: 5px;
                }

                img {
                    width: 20px;
                    height: 20px;
                    margin-right: 5px;
                    object-fit: contain;
                }

                .displayname {
                    font-size: 16px;
                    font-weight: 500;
                    color: #dbdee1;
                    margin-right: 5px;
                    white-space: nowrap;
                }
            }

            .item-channel {
                .key {
                    font-size: 16px;
                    font-weight: 400;
                    color: #949ba4;
                    margin-right: 5px;
                }

                .channelname {
                    font-size: 16px;
                    font-weight: 500;
                    color: #949ba4;
                    margin-right: 5px;
                    white-space: nowrap;

                    display: flex;
                    flex-wrap: nowrap;
                    gap: 5px;

                    align-items: center;
                }

                .categoryname {
                    font-size: 10px;
                    font-weight: 600;
                    color: #676c72;
                    white-space: nowrap;
                    text-transform: uppercase;
                    margin-top: 4px;
                }
            }

            .item:hover {
                .key {
                    color: #dbdee1;
                }
                .value {
                    color: #dbdee1;
                }
            }
        }

        hr {
            display: block;
            margin: 0 20px;
            border: 0;
            padding: 0;
            border-top: 1px solid #2e2f34;
        }
    }
</style>