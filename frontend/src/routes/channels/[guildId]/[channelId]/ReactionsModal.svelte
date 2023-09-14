<script lang="ts">
	import type { Author, Reaction } from 'src/js/interfaces';
	import ImageGallery from './ImageGallery.svelte';
	import { checkUrl } from 'src/js/helpers';
	export let reactions: Reaction[]

    let showReactions = false;

    let activeReaction: Reaction

    export function viewReactions(reaction: Reaction) {
        activeReaction = reaction;
        console.log("activeReaction", activeReaction);
        showReactions = true;
	}
</script>



{#if showReactions}
    <div class="gallery-wrapper" on:click={()=>showReactions=false}>
        <div class="gallery-closebtn" on:click={()=>showReactions=false}>&times;</div>
        <div id="reactions" on:click|stopPropagation>
            <div id="reactions-list">
                {#each reactions as reaction}
                    <div class="reaction" title=":{reaction.emoji.name}:" on:click={()=>viewReactions(reaction)} class:active={reaction.emoji._id == activeReaction?.emoji._id}>
                        {#if reaction.emoji._id == activeReaction?.emoji._id}
                            <ImageGallery
                                imgclass="reaction-emoji-img"
                                alt={reaction.emoji.name}
                                asset={reaction.emoji?.image}
                                width="100%"
                                height="100%"
                            />
                        {:else}
                            <img
                                class='reaction-emoji-img'
                                src={checkUrl(reaction.emoji?.image)}
                                alt={reaction.emoji.name}
                                width="100%"
                                height="100%"
                            />
                        {/if}
                        <span class="reaction-count">{reaction.count}</span>
                    </div>
                {/each}

            </div>
            <div id="reaction-users">

                {#if activeReaction.users}
                    {#each activeReaction.users as user}
                        <div class="reaction-user">
                            <ImageGallery
                                imgclass="reaction-user-img"
                                alt={user.name}
                                asset={user.avatar}
                                width={user.avatar?.width ?? 24}
                                height={user.avatar?.height ?? 24}
                            />
                            <span class="reaction-user-nickname">{user.nickname}</span>
                            <span class="reaction-user-name">{user.name}</span>
                        </div>
                        <div class="reaction-user-hr"></div>
                    {/each}
                {:else}
                    <div class="reactions-users-not-exported">Reaction users not exported</div>
                {/if}
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

    #reactions {
        width: 500px;
        max-width: 95svw;
        height: 400px;
        max-height: 95svh;

        color: #f2f3f5;

        position: relative;
        display: flex;
        flex-direction: row;
    }

    #reactions-list {
        background-color: #2b2d31;
        width: 82px;
        height: calc(100% - 20px);
        overflow-y: auto;
        padding: 10px;

        border-top-left-radius: 4px;
        border-bottom-left-radius: 4px;
    }

    #reactions-list .reaction {
        width: 66px;
        height: 32px;
        display: flex;
        align-items: center;
        padding-left: 4px;
        border-radius: 8px;
        margin-bottom: 4px;
    }

    #reactions-list .reaction:hover {
        background-color: #35373c;
        cursor: pointer;
    }
    #reactions-list .reaction.active {
        background-color: #1e1f22;
        cursor: auto;
    }


    :global(#reactions-list .reaction-emoji-img) {
        padding: 4px 8px 4px 4px;
        width: 24px;
        height: 24px;
        cursor: pointer;
    }

    #reaction-users {
        background-color: #313338;
        width: calc(100% - 82px);
        height: 100%;
        overflow-y: auto;
        padding: 0 10px;

        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
    }

    .reaction-user-hr {
        width: 100%;
        height: 1px;
        background-color: #3a3c42;
    }

    .reaction-user {
        display: flex;
        gap: 10px;
        height: 44px;
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;

        align-items: center;

    }



    .reaction-user .reaction-user-nickname {
        color: #dbdee1;
    }

    .reaction-user .reaction-user-name {
        color: #97999d;
        font-weight: 500;
    }

    :global(#reaction-users .reaction-user-img) {
        width: 24px;
        height: 24px;
        border-radius: 50%;
    }

    .reaction-count {
        font-weight: 700;
        font-size: 14px;
        line-height: 18px;
        color: #dbdee1;
    }


    .reactions-users-not-exported {
        color: #dbdee1;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }



    /* :global(.profile-avatar) {
        width: 80px;
        height: 80px;
        border-radius: 50%;
    } */
</style>