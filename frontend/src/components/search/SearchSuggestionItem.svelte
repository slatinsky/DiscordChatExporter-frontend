<script lang="ts">

	export let index
	export let highlightedIndex

	function selectOptionKey(key: string) {
		console.log(key);
	}
</script>


<div class="search-option" on:click={() => selectOptionKey('id')}>
	<slot />
</div>


<style>
	.search-options {
		background-color: #18191c;
		border-radius: 5px;
		padding: 2px 5px;
		max-width: 700px;
		min-width: 500px;

		position: absolute;
		top: 50px;
		right: 50px;

		z-index: 100;
		max-height: 70vh;
		overflow-y: auto;
	}
	.search-option {
		padding: 5px 5px;
		margin: 5px 10px;
		border-radius: 5px;
	}

	.search-option:hover {
		background-color: #2f3136;
	}
</style>