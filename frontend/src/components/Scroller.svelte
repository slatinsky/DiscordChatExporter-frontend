<!-- Unfinished virtual scroller component -->
<!-- Now renders with fixed item heights -->

<script lang="ts">
	import type { Message } from "src/js/interfaces";
	import MessageLoader from "src/routes/channels/[guildId]/[channelId]/MessageLoader.svelte";
	import { onDestroy, onMount } from "svelte";


	export let messages: Message[];
	export let selectedGuildId: string;


	function randomColor(): string {
		let random_color = `#${Math.floor(Math.random() * 16777215).toString(16)}`;
		// sometimes the random color is not valid
		if (/^#[0-9A-F]{6}$/i.test(random_color)) {
			return random_color;
		} else {
			return randomColor();
		}
	}

	function randomIntInRange(min: number, max: number): number {
		return Math.floor(Math.random() * (max - min + 1)) + min;
	}


	let estimatedItemHeight = 100;
	let scrollWindowHeight: number;
	let scrollWindowWidth: number;
	let scrollContainerHeightOffset: number;
	let scrollFromTop: number;

	let elementsPadding = 2;

	$: visibleElementsCount = Math.ceil(scrollWindowHeight / estimatedItemHeight);
	$: topVisibleElementIndex = Math.max(Math.floor(scrollFromTop / estimatedItemHeight) - elementsPadding, 0);
	$: bottomVisibleElementIndex = topVisibleElementIndex + visibleElementsCount + elementsPadding * 2;
	$: renderedMessages = messages.slice(topVisibleElementIndex, bottomVisibleElementIndex);




	$: console.log("scrollWindowHeight, scrollWindowWidth", scrollWindowHeight, scrollWindowWidth)
	$: console.log("scrollContainerHeightOffset", scrollContainerHeightOffset)
	$: console.log("visibleElementsCount", visibleElementsCount)
	$: console.log("scrollFromTop", scrollFromTop)
	$: console.log("topVisibleElementIndex, bottomVisibleElementIndex", topVisibleElementIndex, bottomVisibleElementIndex)

	let domScrollWindow: HTMLElement;
	let domScrollContainer: HTMLElement;

	let interval: any;

	function scrollListener() {
		scrollFromTop = domScrollWindow.scrollTop;
	}

	onMount(() => {
		domScrollWindow.addEventListener("scroll", scrollListener);

		interval = setInterval(() => {
			// count the heights of scroll-absolute-element and get the difference from estimatedItemHeight
			let scrollAbsoluteElements = domScrollWindow.querySelectorAll(".scroll-absolute-element");
			let scrollAbsoluteElementHeights = Array.from(scrollAbsoluteElements).map((element) => element.clientHeight);
			let totalHeight = scrollAbsoluteElementHeights.reduce((a, b) => a + b, 0);
			let difference = totalHeight - (estimatedItemHeight * scrollAbsoluteElementHeights.length);
			let averageHeight = totalHeight / scrollAbsoluteElementHeights.length;
			console.log("difference", difference, "averageHeight", averageHeight);
		}, 1000);
	});

	onDestroy(() => {
		clearInterval(interval);
		domScrollWindow.removeEventListener("scroll", scrollListener);
	});

	
</script>

<div class="scroll-window" bind:clientHeight={scrollWindowHeight} bind:clientWidth={scrollWindowWidth} bind:this={domScrollWindow}>
	<div class="scroll-container" style="height: {estimatedItemHeight * messages.length}px;" bind:this={domScrollContainer}>
		{#each renderedMessages as message, i (message._id)}
			<div class="scroll-absolute-element" style={"position: absolute; left: 0px; top: " + (estimatedItemHeight * (topVisibleElementIndex + i)) + "px; width: " + scrollWindowWidth + "px;"}>
				<MessageLoader messageId={message._id} selectedGuildId={selectedGuildId} />
				<!-- <div style={"background-color:" + randomColor() + ";height: " + randomIntInRange(5, 300) + "px;"}></div> -->
			</div>
			
		{/each}
	</div>
</div>


<style>
.scroll-window {
	height: calc(100vh - 51px);
	overflow-y: scroll;
	overflow-x: hidden;
	position: relative;
	width: 100%;
}
</style>