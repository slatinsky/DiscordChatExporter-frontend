<script lang="ts">
	import AutocompleteUser from 'src/components/search/AutocompleteUser.svelte';
	import { currentUserId, setCurrentUser } from 'src/components/settings/settingsStore';
	import { checkUrl } from "src/js/helpers";

    export let showModal = false;
    export let guildId: string;

    let searchText = '';
    let inputDom: HTMLInputElement;

    $: if (showModal) {
        setTimeout(() => {
            if (inputDom)
                inputDom.focus()
        }, 100);
    }

    interface AutocompletedUser {
        name1: string;
        name2: string;
        photo: string;
        id: string;
    }

    let users: AutocompletedUser[] = []

    async function autocompleteUsers(searchText: string, guildId: string, _: any) {
        let response = await fetch(`/api/guild/search/autocomplete?guild_id=${encodeURIComponent(guildId)}&key=users&value=${encodeURIComponent(searchText)}`);
        let json = await response.json();

        let newUsers = [];
        if ($currentUserId != '' && 'anonymous'.toLowerCase().includes(searchText)) {
            newUsers.push({
                name1: "Anonymous",
                name2: "",
                photo: "/favicon.png",
                id: ""
            })
        }
        for (let user of json) {
            newUsers.push({
                name1: user.key,
                name2: user.description,
                photo: checkUrl(user.icon),
                id: user.id
            })
        }
        users = newUsers;
        console.log('users', users);
    }

    $: autocompleteUsers(searchText, guildId, $currentUserId);

    function selectUser(user: AutocompletedUser) {
        console.log('selected user', user);
        // setCurrentUser(id: string, name1: string, name2: string, photo: string)
        setCurrentUser(user.id, user.name1, user.name2, user.photo);
        showModal = false;
    }
</script>



{#if showModal}
    <div class="gallery-wrapper" on:click={()=>showModal=false}>
        <div class="gallery-closebtn" on:click={()=>showModal=false}>&times;</div>
        <div id="userselect" on:click|stopPropagation>
            <div id="userselect-inner">
                <div id="input-wrapper">
                    <input type="text" placeholder="Search for a user" bind:value={searchText}  bind:this={inputDom} on:keydown={(e) => {if (e.key == 'Enter') selectUser(users[0])}}/>
                </div>
                {#each users as user}
                    <AutocompleteUser photo={user.photo} name1={user.name1} name2={user.name2} on:click={() => selectUser(user)}/>
                {/each}
            </div>
        </div>
    </div>
{/if}
<style>
    .gallery-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.8);
        z-index: 1000;
        display: flex;
        justify-content: center;
        align-items: center;

        display: flex;
        flex-direction: column;

        text-align: left;
    }

    .gallery-closebtn {
        position: absolute;
        top: -15px;
        right: 0;
        padding: 10px;
        color: white;
        cursor: pointer;

        font-size: 3rem;
        font-weight: 600;
        z-index: 1001;
    }

    #userselect {
        width: 250px;
        max-width: 95svw;
        height: 400px;
        max-height: 95svh;

        color: #f2f3f5;

        position: relative;
        display: flex;
        flex-direction: row;
    }

    #userselect-inner {
        background-color: #2b2d31;
        width: 100%;
        height: calc(100% - 20px);
        overflow-y: auto;
        padding: 0 10px 10px 10px;

        border-top-left-radius: 4px;
        border-bottom-left-radius: 4px;
    }

    #input-wrapper {
        position: sticky;
        top: 0;
        background-color: #2b2d31;
        padding: 12px 0;
    }

    input {
		width: calc(100% - 30px);
		background-color: #202225;
		color: white;
		height: 25px;
		border: 0px;
		border-radius: 3px;
		padding: 0px 10px;
		outline: none;


	}
	input::placeholder {
		color: #909297;
	}


</style>