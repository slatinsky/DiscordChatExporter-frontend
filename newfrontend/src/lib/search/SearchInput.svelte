<script lang="ts">
    import { getGuildState } from "../../js/stores/guildState.svelte";
    import Icon from "../icons/Icon.svelte";
    import { getSearchState } from "./searchState.svelte";

    const searchState = getSearchState();
    const guildState = getGuildState();

    let isFocused = $state(false);

    function inputOnFocus(event: FocusEvent & { currentTarget: EventTarget & HTMLInputElement; }) {
        isFocused = true;
    }


    function inputOnBlur(event: FocusEvent & { currentTarget: EventTarget & HTMLInputElement; }) {
        isFocused = false;
    }


    function inputOnKeyDown(event: KeyboardEvent & { currentTarget: EventTarget & HTMLInputElement; }) {
        if (event.key === 'Enter') {
            domInput.blur();
            searchState.setSearchPrompt(event.currentTarget.value);
            searchState.search(guildState.guildId);
        }
    }


    function searchPromptChanged(event: Event & { currentTarget: EventTarget & HTMLInputElement; }) {
        searchState.setSearchPrompt(event.currentTarget.value)
    }

    let domInput: HTMLInputElement;
</script>
<div class="searchinput-wrapper">
    <input
        type="text"
        placeholder="Search"
        value={searchState.searchPrompt}
        bind:this={domInput}
        onfocus={inputOnFocus}
        onblur={inputOnBlur}
        onkeydown={inputOnKeyDown}
        oninput={searchPromptChanged}
    />
    {#if searchState.searchPrompt === ''}
        <div class="icon">
            <Icon name="other/magnifying-glass" width={16} />
        </div>
    {:else}
        <button class="icon" onclick={()=>searchState.setSearchPrompt("")}>
            <Icon name="modal/x" width={16} />
        </button>
    {/if}
</div>


<style>
    .searchinput-wrapper {
        position: relative;

        input {
            width: 140px;
            background-color: #202225;
            color: #dbdee1;
            height: 25px;
            border: 0px;
            border-radius: 3px;
            padding: 0px 10px;
            outline: none;
            font-size: 14px;
            font-weight: 500;
        }
        input::placeholder {
            color: #949ba4;
        }
        input:focus {
            width: 250px;
        }

        .icon {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #949ba4;
            pointer-events: none;
        }
        button.icon {
            cursor: pointer;
            pointer-events: all;
        }
    }
</style>