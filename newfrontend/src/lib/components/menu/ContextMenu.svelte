<script>
	import Menu from './Menu.svelte';
    import { contextMenuItems } from '../../../js/stores/menuStore';

	function closeMenu() {
		$contextMenuItems = [];
	}

	function onClick(item) {
		closeMenu()
		item.action()
	}
</script>

{#key $contextMenuItems}
	{#if $contextMenuItems.length > 0}
		<Menu on:click={closeMenu} on:clickoutside={closeMenu}>
			{#each $contextMenuItems as item}
				<div on:click={()=>onClick(item)} class="menu-option">
					{item.name}
				</div>
			{/each}
		</Menu>
	{/if}
{/key}


<style>
	div {
		padding: 10px 20px;
		cursor: default;
		font-size: 14px;
		display: flex;
		align-items: center;
		grid-gap: 5px;
        color: #787A7E   ;
	}
	div:hover {
		background: #4752C4;
        color: white;
	}
	/* div.disabled {
		color: #0006;
	}
	div.disabled:hover {
		background: white;
	} */
</style>