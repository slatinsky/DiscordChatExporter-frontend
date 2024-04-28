<script lang="ts">
    import IconChannelWithThreads from "../icons/IconChannelWithThreads.svelte";
    import IconVoiceChannel from "../icons/IconVoiceChannel.svelte";
    import IconNewsChannel from "../icons/IconNewsChannel.svelte";
    import IconChannel from "../icons/IconChannel.svelte";
    import MenuThread from "./MenuThread.svelte";
    import { selectedChannelId, selectedThreadId } from "../../js/stores/guildStore";
    import { copyTextToClipboard } from "../../js/helpers";
    import { contextMenuItems } from "../../js/stores/menuStore";
    import type { Channel } from "../../js/interfaces";

    export let channel: Channel
    let isOpen = false

    function toggle() {
        isOpen = !isOpen
        if (isOpen) {
            $selectedChannelId = channel._id
        }
    }

    $: {
        if ($selectedChannelId !== channel._id) {
            isOpen = false
        }
    }

    function onChannelRightClick(e, id: string, name: string) {
		$contextMenuItems = [
			{
				"name": "Copy channel ID",
				"action": () => {
					copyTextToClipboard(BigInt(id))
				}
			},
			{
				"name": "Copy channel name",
				"action": () => {
					copyTextToClipboard(name)
				}
			}
		]
	}
</script>

<div class="channel" class:selected={$selectedChannelId == channel._id} on:click={toggle} on:contextmenu|preventDefault={(e) => onChannelRightClick(e, channel._id, channel.name)}>
    <div class="channel-icon">
        {#if channel.threads.length > 0}
            <IconChannelWithThreads />
        {:else if channel.type == "GuildVoiceChat"}
        <!-- Would be nice if DiscordChatExporter also export the nsfw boolean so we can have the other types of channel icons. I will Add forum icon eventually -->
            <IconVoiceChannel />
            {:else if channel.type == "GuildNews"}
            <IconNewsChannel/>
            {:else}
            <IconChannel />
        {/if}
    </div><span title="{channel.msg_count} messages">{channel.name}</span>
</div>
{#each channel.threads as thread}
    {#if isOpen || thread._id == $selectedThreadId}
        <MenuThread thread={thread} isLast={!isOpen || thread === channel.threads[channel.threads.length - 1]} />
    {/if}
{/each}

<style>
	.channel {
		display: flex;
		align-items: center;
		border-radius: 4px;
		width: calc(100% - 40x);
		padding: 4px 6px;
		margin: 1px 8px;
        gap: 5px;
        color: #949BA4;
        cursor: pointer;
        font-weight: 500;
	}

	.channel:hover,
	.channel.selected {
		background-color: #404249;
		color: white;
	}

	.channel-icon {
		width: 24px;
		margin-right: 5px;
	}
</style>