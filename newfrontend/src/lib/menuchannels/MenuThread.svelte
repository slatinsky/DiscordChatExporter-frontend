<script lang="ts">
    import { copyTextToClipboard } from "../../js/helpers";
    import type { Channel } from "../../js/interfaces";
    import { getGuildState } from "../../js/stores/guildState.svelte";
    import { contextMenuItems } from "../../js/stores/menuStore";

    export let thread: Channel
    export let parentChannelId: string
    export let isLast: boolean


    function onThreadRightClick(e, id: string, name: string) {
		$contextMenuItems = [
			{
				"name": "Copy thread ID",
				"action": () => {
					copyTextToClipboard(BigInt(id))
				}
			},
			{
				"name": "Copy thread name",
				"action": () => {
					copyTextToClipboard(name)
				}
			}
		]
	}

    async function changeThread(guildId: string, channelId: string, threadId: string) {
        await guildState.changeGuildId(guildId)
        await guildState.changeChannelId(channelId)
        await guildState.changeThreadId(threadId)
    }

    const guildState = getGuildState()
</script>

<div class="thread" class:selected={thread._id == guildState.threadId} on:click={()=>changeThread(thread.guildId, parentChannelId, thread._id)} on:contextmenu|preventDefault={(e) => onThreadRightClick(e, thread._id, thread.name)}>
    <div class="thread-icon">
        {#if isLast}
            <svg class="up" width="12" height="11" viewBox="0 0 12 11" fill="none" aria-hidden="true">
                <path d="M11 9H4C2.89543 9 2 8.10457 2 7V1C2 0.447715 1.55228 0 1 0C0.447715 0 0 0.447715 0 1V7C0 9.20914 1.79086 11 4 11H11C11.5523 11 12 10.5523 12 10C12 9.44771 11.5523 9 11 9Z" fill="currentColor"></path>
            </svg>
        {:else}
            <div class="border"></div>
            <svg class="up" width="12" height="11" viewBox="0 0 12 11" fill="none" aria-hidden="true">
                <path d="M11 9H4C2.89543 9 2 8.10457 2 7V1C2 0.447715 1.55228 0 1 0C0.447715 0 0 0.447715 0 1V7C0 9.20914 1.79086 11 4 11H11C11.5523 11 12 10.5523 12 10C12 9.44771 11.5523 9 11 9Z" fill="currentColor"></path>
            </svg>
            <svg class="down" width="12" height="11" viewBox="0 0 12 11" fill="none" aria-hidden="true" style="transform: rotateX(180deg) translateY(-9px);">
                <path d="M11 9H4C2.89543 9 2 8.10457 2 7V1C2 0.447715 1.55228 0 1 0C0.447715 0 0 0.447715 0 1V7C0 9.20914 1.79086 11 4 11H11C11.5523 11 12 10.5523 12 10C12 9.44771 11.5523 9 11 9Z" fill="currentColor"></path>
            </svg>
        {/if}
    </div>
    <div class="thread-name" title="{thread.msg_count} messages">{thread.name}</div>
</div>


<style>
    .thread {
        display: flex;
        height: 34px;
        margin: 0px 15px 0px 30px;

        align-items: center;
        text-decoration: none;
        cursor: pointer;
    }
    .thread:hover {
        color: white;
    }

    .thread-icon {
        color: #4E5058;
        overflow: visible;
        display: flex;
        flex-direction: column;
        position: relative;
        height: 20px;
    }


    .thread-icon .up {
        margin-top: 1px;
    }
    .thread-icon .down {
        margin-top: -11px;
    }



    .thread-icon .border {
        background: #4E5058;
        border-radius: 2px;
        left: 0px;
        top: 0px;
        position: absolute;
        width: 2px;
        height: 39px;
        z-index: 15;
    }

    .thread-name {
        padding-left: 7px;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        color: #949BA4;
        line-height: 20px;
        font-weight: 500;
        font-size: 16px;
        height: 20px;
        overflow: hidden;
    }
    .selected .thread-name {
        color: white;
    }
</style>