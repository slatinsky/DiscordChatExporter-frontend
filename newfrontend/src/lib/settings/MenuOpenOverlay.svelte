<script lang="ts">
    import { settingsSideMenuShown } from "../../js/stores/settingsStore";

    export let leftOffset = 322;
</script>

<div id="menu-open-overlay" style={"left:" + String(leftOffset) + "px"} class:hidden={!$settingsSideMenuShown} on:click={() => $settingsSideMenuShown = false}/>

<style>
    #menu-open-overlay {
		position: fixed;
		top: 0;
		width: 100vw;
		height: 100dvh;
		z-index: 100;
		background-color: rgba(0, 0, 0, 0.8);

		transition: left 0.2s ease-in-out, background-color 0.2s ease-in-out;

		z-index: 1000;
		display: none;
	}

	@media (max-width: 1000px) {
		#menu-open-overlay {
			display: block;
		}
	}

	#menu-open-overlay.hidden {
		left: 0 !important;
		background-color: transparent;
		pointer-events: none;
	}
</style>