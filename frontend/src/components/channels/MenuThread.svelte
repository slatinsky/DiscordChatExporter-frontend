<script>
	import IconThread from 'src/components/icons/IconThread.svelte';
	import IconThreadMiddle from 'src/components/icons/IconThreadMiddle.svelte';
	import { copyTextToClipboard } from '../../js/helpers';
	import { contextMenuItems } from '../menu/menuStore';

	export let name;
	export let id;
	export let guildId;
	export let selectedChannelId;
	export let isLast;

	function onRightClick(e, id) {
		$contextMenuItems = [
			{
				"name": "Copy thread/forum post ID",
				"action": () => {
					copyTextToClipboard(BigInt(id))
				}
			}
		]
	}
</script>

<div class="thread" title={name}>
    <div class="thread-icon">
        {#if isLast}
		    <IconThread />
        {:else}
            <IconThreadMiddle />
        {/if}
    </div>
	
	<a
		href="/channels/{guildId}/{id}"
		on:contextmenu|preventDefault={(e) => onRightClick(e, id)}
	>
		<div class="thread-name" class:selected={selectedChannelId == id}>
			{name}
		</div>
	</a> <br />
</div>

<style>
    a {
        color: var(--channel-text-read);
    }
    .thread-icon {
        width: 18px;
        color: var(--channel-text-read);
        overflow: visible;
    }
	.thread {
		display: flex;
		height: 17px;
		margin: 0px 15px 0px 30px;
		font-size: small;
		align-items: flex-start;
		text-decoration: none;

		overflow: hidden;
	}

	.thread-name {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
        color: var(--channel-text-read);

	}

    .thread-name.selected {
        color: var(--channel-text-unread);
	}

	.thread:hover {
		color: white;
	}
</style>
