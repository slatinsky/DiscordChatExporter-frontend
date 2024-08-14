<script lang="ts">
    import { getGuildState } from "../../js/stores/guildState.svelte";
    import { getLayoutState } from "../../js/stores/layoutState.svelte";
    import Icon from "../icons/Icon.svelte";
    import SearchAutoComplete from "./SearchAutoComplete.svelte";
    import { getSearchState } from "./searchState.svelte";

    const searchState = getSearchState();
    const guildState = getGuildState();
    const layoutState = getLayoutState();


    let focused = $state(false);
    let searchPrompt = $derived.by(()=> {
        setTimeout(() => {
            updateSelection()
        }, 0)
        return searchState.searchPrompt
    });

    function inputOnFocus(event: FocusEvent & { currentTarget: EventTarget & HTMLInputElement; }) {
        console.log("search focus")
        focused = true;
    }


    function updateSelection() {
        if (!domInput) {
            return;
        }

        searchState.setSelection(domInput.selectionStart, domInput.selectionEnd);
        autocomplete.promptChanged();
    }

    async function inputOnKeyDown(event: KeyboardEvent & { currentTarget: EventTarget & HTMLInputElement; }) {
        if (event.key === 'Enter') {
            let searchTerm = event.currentTarget.value;
            if (domInput) {
                domInput.blur();
            }
            await guildState.changeThreadId(null)
            searchState.setSearchPrompt(searchTerm);
            searchState.search(guildState.guildId);
            searchState.addToSearchHistory(searchTerm)

            focused = false;
        }
        else if (event.key === 'ArrowDown') {
            autocomplete.arrowDown()
			event.preventDefault();
		} else if (event.key === 'ArrowUp') {
			autocomplete.arrowUp()
		}
    }

    function inputOnKeyUp(event: KeyboardEvent & { currentTarget: EventTarget & HTMLInputElement; }) {
        if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
            return;
        }
        updateSelection();
    }

    function searchPromptChanged(event: Event & { currentTarget: EventTarget & HTMLInputElement; }) {
        searchState.setSearchPrompt(event.currentTarget.value)
    }

    function focusInput() {
        if (domInput) {
            focused = true;
            domInput.focus();
        }
        else {
            console.error("domInput is undefined")
        }
    }

    function blurInput() {
        if (domInput) {
            focused = false;
            domInput.blur();
            console.warn("search blur")
        }
        else {
            console.error("domInput is undefined")
        }
    }

    let domInput: HTMLInputElement | undefined = $state()
    let autocomplete: SearchAutoComplete;


    function onPageClick(event: MouseEvent) {
        if (!event.target) {
            return;
        }
        if (event.target instanceof HTMLElement) {
            const siw = event.target.closest(".searchinput-wrapper")
            if (!siw) {
                focused = false;
                console.log("search blur")
            }
            else {
                if (domInput) {
                    domInput.focus();
                    console.warn("search focus")
                }
            }
        }
    }
</script>

<svelte:body onclick={onPageClick} />

<div class="searchinput-wrapper" class:focused={focused} class:ismobile={layoutState.mobile}>
    <!-- {searchState.selection.start} {searchState.selection.end} {searchState.selection.textBefore} {searchState.selection.textSelected} {searchState.selection.textAfter} -->
    <input
        onfocus={inputOnFocus}
        onkeydown={inputOnKeyDown}
        onmouseup={updateSelection}
        onkeyup={inputOnKeyUp}
        type="text"
        placeholder="Search"
        value={searchPrompt}
        bind:this={domInput}
        oninput={searchPromptChanged}
    />
    {#if searchPrompt === ''}
        <div class="icon">
            <Icon name="other/magnifying-glass" width={16} />
        </div>
    {:else}
        <button class="icon" onclick={()=>searchState.setSearchPrompt("")}>
            <Icon name="modal/x" width={16} />
        </button>
    {/if}
    <div class="autocomplete">
        <SearchAutoComplete domInput={domInput} visible={focused} bind:this={autocomplete} focusInput={focusInput} blurInput={blurInput} />
    </div>
</div>


<style>
    .searchinput-wrapper {
        position: relative;

        input {
            box-sizing: border-box;
            width: 140px;
            background-color: #202225;
            color: #dbdee1;
            height: 25px;
            border: 0px;
            border-radius: 3px;
            padding: 0px 30px 0 10px;
            margin-right: 10px;
            outline: none;
            font-size: 14px;
            font-weight: 500;
        }
        input::placeholder {
            color: #949ba4;
        }

        .icon {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #949ba4;
            pointer-events: none;
            margin-right: 4px;
        }
        button.icon {
            cursor: pointer;
            pointer-events: all;
        }
    }

    .searchinput-wrapper.focused {
        input {
            width: 250px;
        }
    }


    .searchinput-wrapper.ismobile input {
        width: 100%;
    }
</style>