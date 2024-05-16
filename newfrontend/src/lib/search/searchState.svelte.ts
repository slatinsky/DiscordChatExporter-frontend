import { fetchSearch } from "../../js/stores/api";
import { getGuildState } from "../../js/stores/guildState.svelte";

const guildState = getGuildState();

let searchPrompt = $state("");
let submittedSearchPrompt = $state("");
let searchResultsIds = $state([]);
let gotResults = $state(false);
let searching = $state(false);
let error = $state("");

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
        }
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
        setSearchPrompt,
        search,
        clearSearch,
    };
}
