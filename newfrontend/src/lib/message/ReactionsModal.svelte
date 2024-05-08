<script lang="ts">
    import Image from '../imagegallery/Image.svelte';
    import { onUserRightClick } from './messageRightClick';
	export let reactions

    let showReactions = false;

    let activeReaction

    export function viewReactions(reaction) {
        activeReaction = reaction;
        console.log("activeReaction", activeReaction);
        showReactions = true;
	}
</script>



{#if showReactions}
    <div class="gallery-wrapper" on:click={()=>showReactions=false}>
        <div class="gallery-closebtn" on:click={()=>showReactions=false}>&times;</div>
        <div class="reactions-modal-content" on:click|stopPropagation>
            <div class="reactions-list">
                {#each reactions as reaction}
                    <div class="reaction" title=":{reaction.emoji.name}:" on:click={()=>viewReactions(reaction)} class:active={reaction.emoji._id == activeReaction?.emoji._id}>
                        <Image
                            class="global-reaction-emoji-img"
                            alt={reaction.emoji.name}
                            asset={reaction.emoji?.image}
                            clickable={reaction.emoji._id == activeReaction?.emoji._id}
                        />
                        <span class="reaction-count">{reaction.count}</span>
                    </div>
                {/each}

            </div>
            <div class="reaction-users">

                {#if activeReaction.users}
                    {#each activeReaction.users as user}
                        <div class="reaction-user" on:contextmenu|preventDefault|preventDefault={e=>onUserRightClick(e, user)}>
                            <Image
                                class="global-reaction-user-img"
                                alt={user.name}
                                asset={user.avatar}
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

    .reactions-modal-content {
        width: 500px;
        max-width: 95svw;
        height: 400px;
        max-height: 95svh;

        color: #f2f3f5;

        position: relative;
        display: flex;
        flex-direction: row;
    }

    .reactions-list {
        background-color: #2b2d31;
        width: 94px;
        height: 100%;
        overflow-y: hidden;
        padding-top: 8px;

        border-top-left-radius: 4px;
        border-bottom-left-radius: 4px;
        box-sizing: border-box;

        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .reactions-list .reaction {
        width: 75px;
        height: 32px;
        display: flex;
        align-items: center;
        padding-left: 4px;
        border-radius: 8px;
        margin-bottom: 4px;
    }

    .reactions-list .reaction:hover {
        background-color: #35373c;
        cursor: pointer;
    }
    .reactions-list .reaction.active {
        background-color: #1e1f22;
        cursor: auto;
    }


    :global(.reactions-list .global-reaction-emoji-img) {
        padding: 0 8px 0 4px;
        width: 24px;
        height: auto;
        cursor: pointer;
        box-sizing: content-box;
    }

    .reaction-users {
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

    :global(.reaction-users .global-reaction-user-img) {
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
</style>