<script lang="ts">
    import { getGuildState } from "../../js/stores/guildState.svelte";
    import { getLayoutState } from "../../js/stores/layoutState.svelte";
    import { currentUserName1, currentUserPhoto } from "../../js/stores/settingsStore.svelte";
    import Icon from "../icons/Icon.svelte";
    import AutocompleteUser from "./AutocompleteUser.svelte";
    import UserSelectionModal from "./UserSelectionModal.svelte";

    let showUserSelectionModal = false;

    const guildState = getGuildState()
    const layoutState = getLayoutState()
</script>

<div id="bottom-bar">
    <div style="width: 190px;">
        <AutocompleteUser photo={$currentUserPhoto} name1={$currentUserName1} name2={$currentUserName1} on:click={() => showUserSelectionModal = true}/>
    </div>
    <div id="settings" on:click={layoutState.showSettings}>
        <Icon name="other/settings" width={20} />
    </div>
</div>
<UserSelectionModal bind:showModal={showUserSelectionModal} guildId={guildState.guildId}/>

<style>
    #settings {
        display: grid;
        place-items: center;
        width: 32px;
        height: 32px;
        border-radius: 4px;
        cursor: pointer;
    }

    #settings:hover {
        background-color: #3d3e45;
    }

    #bottom-bar {
        /* margin-top: auto; */
        /* position: sticky; */
        bottom: 0;
        display: flex;
        align-items: center;
        background-color: #232428;
        height: 52px;
        padding: 5px 0 5px 5px;
    }
</style>