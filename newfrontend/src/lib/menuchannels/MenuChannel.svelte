<script lang="ts">
    import MenuThread from "./MenuThread.svelte";
    import { copyTextToClipboard } from "../../js/helpers";
    import { contextMenuItems } from "../../js/stores/menuStore";
    import type { Channel } from "../../js/interfaces";
    import { getGuildState } from "../../js/stores/guildState.svelte";
    import { linkHandler } from "../../js/stores/settingsStore.svelte";
    import ChannelIcon from "./ChannelIcon.svelte";

    interface MyProps {
        channel: Channel;
    }
    let { channel }: MyProps = $props();

    let isOpen: boolean = $state(false)
    const guildState = getGuildState()

    async function toggle() {
        isOpen = !isOpen
        if (isOpen) {
            await guildState.changeChannelId(channel._id)
            await guildState.pushState()
        }
    }

    $effect(() => {
        if (guildState.channelId !== channel._id) {
            isOpen = false
        }
        if (guildState.channelId === channel._id) {
            isOpen = true
        }
    })

    function onChannelRightClick(e, id: string, name: string) {
		$contextMenuItems = [
            {
				"name": `Open channel in discord ${$linkHandler === 'app' ? "app" : "web"}`,
				"action": () => {
					window.open(($linkHandler === "app" ? "discord://" : "") + `https://discord.com/channels/${BigInt(guildState.guildId)}/${BigInt(id)}`,'_blank')
				}
			},
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

<div class="channel" class:selected={guildState.channelId == channel._id} on:click={toggle} on:contextmenu|preventDefault={(e) => onChannelRightClick(e, channel._id, channel.name)}>
    <div class="channel-icon">
        <ChannelIcon channel={channel} width={20} />
    </div><span title="{channel.msg_count} messages">{channel.name}</span>
</div>
{#each channel.threads as thread}
    {#if isOpen || thread._id == guildState.threadId}
        <MenuThread parentChannelId={channel._id} thread={thread} isLast={!isOpen || thread === channel.threads[channel.threads.length - 1]} />
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