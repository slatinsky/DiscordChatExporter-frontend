import { fetchSearch } from "../../js/stores/api";
import { getGuildState } from "../../js/stores/guildState.svelte";

const guildState = getGuildState();

let searchPrompt = $state("");
let selectionStart = $state(0);
let selectionEnd = $state(0);
let submittedSearchPrompt = $state("");
let searchResultsIds = $state([]);
let gotResults = $state(false);
let searching = $state(false);
let error = $state("");
let searchHistory: string[] = $state([]);
let searchManuallyHidden = $state(true);

if (localStorage.searchHistory) {
    searchHistory = JSON.parse(localStorage.searchHistory);
}

export function getSearchState() {

    function clearSearch() {
        if (!gotResults) {
            return;
        }
        searchPrompt = "";
        submittedSearchPrompt = "";
        searchResultsIds = [];
        gotResults = false;
        searching = false;
        error = "";
        guildState.pushState();
    }

    /*
    set non-submitted search prompt
    */
    function setSearchPrompt(newPrompt: string | null) {
        if (newPrompt === null) {
            newPrompt = "";
        }
        searchPrompt = newPrompt;
        if (searchPrompt === "") {
            clearSearch()
        }
        console.log("searchState - setSearchPrompt", $state.snapshot(searchPrompt));
    }

    /*
    load search results
    uses search prompt set using setSearchPrompt
    saves results to searchResultsIds
    */
    async function search(guildId: string | null) {
        if (submittedSearchPrompt === searchPrompt) {
            return;
        }
        submittedSearchPrompt = searchPrompt;
        guildState.pushState();
        searching = true;
        gotResults = false;
        error = "";
        console.log("searchState - search", $state.snapshot(submittedSearchPrompt));

        try {
            searchResultsIds = await fetchSearch(guildId, submittedSearchPrompt);
            console.log(`searchState - search - searchResultsIds count ${searchResultsIds.length}`);
        }
        catch (e) {
            error = "Failed to fetch search results";
        }
        finally {
            searching = false;
            gotResults = true;
            searchManuallyHidden = false;
        }
    }

    function setSelection(newSelectionStart: number | null, newSelectionEnd: number | null) {
        if (newSelectionStart === null || newSelectionEnd === null) {
            return;
        }
        selectionStart = newSelectionStart;
        selectionEnd = newSelectionEnd;
    }

    function addToSearchHistory(newSearch: string) {
        if (searchHistory.includes(newSearch)) {
            searchHistory = searchHistory.filter((search) => search !== newSearch);
        }
        searchHistory = [newSearch, ...searchHistory]
        localStorage.searchHistory = JSON.stringify(searchHistory);
    }

    function clearSearchHistory() {
        searchHistory = [];
        localStorage.searchHistory = JSON.stringify(searchHistory);
    }

    function hideSearch() {
        searchManuallyHidden = true;
    }
    function showSearch() {
        searchManuallyHidden = false;
    }

    return {
        get searchPrompt() {
            return searchPrompt;
        },
        get searchResultsIds() {
            return searchResultsIds;
        },
        get submittedSearchPrompt() {
            return submittedSearchPrompt;
        },
        get canBeVisible() {
            const isShown = submittedSearchPrompt !== "" || searching || error !== "" || gotResults;
            return isShown;
        },
        get searching() {
            return searching;
        },
        get selection() {
            const textBefore = searchPrompt.substring(0, selectionStart);
            const textSelected = searchPrompt.substring(selectionStart, selectionEnd);
            const textAfter = searchPrompt.substring(selectionEnd);
            const lastWord = textBefore.split(' ').pop() || ''
            const lastWordIsKey = !lastWord.includes(':');

            let lastKey = ''
            if (!lastWordIsKey) {
                lastKey = lastWord.split(':')[0]
            }
            else {
                lastKey = lastWord
            }

            let lastValue = ''
            if (lastWordIsKey) {
                lastValue = ''
            }
            else {
                lastValue = lastWord.split(':')[1]
            }
            return {
                start: selectionStart,
                end: selectionEnd,
                textBefore: textBefore,
                textSelected: textSelected,
                textAfter: textAfter,
                lastWord: lastWord,
                lastWordIsKey: lastWordIsKey,
                lastKey: lastKey,
                lastValue: lastValue,
            };
        },
        get searchHistory() {
            return searchHistory;
        },
        get searchManuallyHidden() {
            return searchManuallyHidden;
        },
        addToSearchHistory,
        clearSearchHistory,
        setSearchPrompt,
        search,
        clearSearch,
        setSelection,
        hideSearch,
        showSearch,
    };
}
