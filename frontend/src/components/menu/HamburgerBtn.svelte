<script lang="ts">
	import { isMenuHidden } from "./menuStore";
</script>

<div class="hamburger-menu" on:click={e => $isMenuHidden = !$isMenuHidden}>
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="37" height="32" viewBox="0 0 37 32">
        <path d="M36.833 4.167h-36.333c-0.276 0-0.5-0.224-0.5-0.5v0-2c0-0.276 0.224-0.5 0.5-0.5v0h36.333c0.276 0 0.5 0.224 0.5 0.5v0 2c0 0.276-0.224 0.5-0.5 0.5v0zM36.833 17.5h-36.333c-0.276 0-0.5-0.224-0.5-0.5v0-2c0-0.276 0.224-0.5 0.5-0.5v0h36.333c0.276 0 0.5 0.224 0.5 0.5v0 2c0 0.276-0.224 0.5-0.5 0.5v0zM36.833 30.833h-36.333c-0.276 0-0.5-0.224-0.5-0.5v0-2c0-0.276 0.224-0.5 0.5-0.5v0h36.333c0.276 0 0.5 0.224 0.5 0.5v0 2c0 0.276-0.224 0.5-0.5 0.5v0z"></path>
    </svg>
</div>


<style>
	.hamburger-menu {
		display: none;
		left: 0;
		bottom: 0;
		z-index: 100;

		cursor: pointer;

		transform: scale(0.5);
	}

	.hamburger-menu svg {
		fill: white;
	}

	@media (max-width: 1000px) {
		.hamburger-menu {
			display: block;
		}
	}
</style>