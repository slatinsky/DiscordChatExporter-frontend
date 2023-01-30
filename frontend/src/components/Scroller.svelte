<!-- Virtual scroller component -->
<!-- Now renders with variable item heights -->
<!-- needs refactor to be more readable :) -->

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
	let scrollContainerHeight = estimatedItemHeight * messages.length
	let scrollFromTop: number;

	let elementsPadding = 20;
	let baseIndex = 0;
	let baseIndexOffset = 0;

	$: visibleElementsCount = Math.ceil(scrollWindowHeight / estimatedItemHeight);


	$: baseOffset = (baseIndex * estimatedItemHeight - baseIndexOffset);

	$: topVisibleElementIndex = Math.max(Math.floor((scrollFromTop+baseOffset) / estimatedItemHeight) - elementsPadding, 0);
	$: bottomVisibleElementIndex = topVisibleElementIndex + visibleElementsCount + elementsPadding * 2;
	$: renderedMessages = messages.slice(topVisibleElementIndex, bottomVisibleElementIndex);


	$: console.log("scrollWindowHeight, scrollWindowWidth", scrollWindowHeight, scrollWindowWidth)
	$: console.log("scrollContainerHeightOffset", scrollContainerHeightOffset)
	$: console.log("visibleElementsCount", visibleElementsCount)
	// $: console.log("scrollFromTop", scrollFromTop)
	$: console.log("baseOffset", baseOffset)
	$: console.log("topVisibleElementIndex, bottomVisibleElementIndex", topVisibleElementIndex, bottomVisibleElementIndex)

	let domScrollWindow: HTMLElement;
	let domScrollContainer: HTMLElement;

	let interval: any;

	function scrollListener() {
		scrollFromTop = domScrollWindow.scrollTop;
	}

	function onWindowResize(newWidth: number, newHeight: number) {
		heightsCache = {};  // invalidate cache
	}

	$: onWindowResize(scrollWindowWidth, scrollWindowHeight);



	let heightsCache: Record<number, number> = {};

	onMount(() => {
		domScrollWindow.addEventListener("scroll", scrollListener);
		scrollListener() // call to init without scrolling

		function migrateBaseIndex(newBaseIndex: number) {
			let newOffset = baseIndexOffset;
			if (baseIndex < newBaseIndex - 1) {
				console.log("migrateBaseIndex v1", baseIndex, "-->" ,newBaseIndex);
				
				for (let i = baseIndex; i < newBaseIndex; i++) {
					newOffset += heightsCache[i];
				}
			} else if (baseIndex > newBaseIndex + 1) {
				console.log("migrateBaseIndex v2", baseIndex, "-->" ,newBaseIndex);

				for (let i = baseIndex - 1; i >= newBaseIndex; i--) {
					newOffset -= heightsCache[i];
				}
			}
			else {
				return
			}

			baseIndex = newBaseIndex;
			baseIndexOffset = newOffset;
		}

		function fixTopScrollOutOfBounds(offsetToFix: number) {
			baseIndexOffset -= offsetToFix;
			domScrollWindow.scrollTop -= offsetToFix;
			console.log("fixScrollOutOfBounds", offsetToFix);
		}

		interval = setInterval(() => {
			// count the heights of scroll-absolute-element and get the difference from estimatedItemHeight
			let scrollAbsoluteElements = domScrollWindow.querySelectorAll(".scroll-absolute-element");

			let minTopPosition = Infinity;
			// let maxBottomPosition = -Infinity;

			let renderedIndexes = []
			// save the heights of the elements
			for (let i = 0; i < scrollAbsoluteElements.length; i++) {
				let domElement = scrollAbsoluteElements[i];
				let index = parseInt(domElement.getAttribute("data-index") as string);
				let height = domElement.clientHeight;
				heightsCache[index] = height;
				renderedIndexes.push(index);

				// get absolute top position of the element
				// let topPosition = parseInt(window.getComputedStyle(domElement).top);
				// minTopPosition = Math.min(minTopPosition, topPosition);
				// maxBottomPosition = Math.max(maxBottomPosition, topPosition + height);
			}
			let renderedIndexMax = Math.max(...renderedIndexes);
			let renderedIndexMin = Math.min(...renderedIndexes);

			let renderedIndexCenter = Math.floor((renderedIndexMax + renderedIndexMin) / 2);

			// if baseIndex not in renderedIndexes
			if (!renderedIndexes.includes(baseIndex)) {
				heightsCache = {};  // invalidate cache
				// estimate the position of the new baseIndex
				baseIndex = renderedIndexCenter
				baseIndexOffset = baseIndex * estimatedItemHeight;
				console.warn("baseIndex not in renderedIndexes");
				return
			}


			// update offsets (position top of the element)
			if (baseIndex < renderedIndexMax) {
				// direction: down

				// console.log("renderedIndexes", renderedIndexes);

				// calculate the offset from cache
				let offset = baseIndexOffset
				let endCorrection = 0;
				for (let i = baseIndex; i <= renderedIndexMax; i++) {
					// if the index is rendered, update the offset
					if (renderedIndexes.includes(i)) {
						let domElement = domScrollWindow.querySelector(`.scroll-absolute-element[data-index="${i}"]`)
						domElement.style.top = offset + "px";

						endCorrection = heightsCache[i] - estimatedItemHeight;
					}
					offset += heightsCache[i];
				}

				// fix length of the scroll container
				scrollContainerHeight = estimatedItemHeight * messages.length + endCorrection

				
			}
			if (baseIndex > renderedIndexMin) {
				// direction: up

				// calculate the offset from cache
				let offset = baseIndexOffset + heightsCache[baseIndex];
				for (let i = baseIndex; i >= renderedIndexMin; i--) {
					offset -= heightsCache[i];
					// if the index is rendered, update the offset
					if (renderedIndexes.includes(i)) {
						let domElement = domScrollWindow.querySelector(`.scroll-absolute-element[data-index="${i}"]`)
						domElement.style.top = offset + "px";
						if (offset < 0) {
							fixTopScrollOutOfBounds(offset);
						}

						if (i == 0 && offset > 0) {
							fixTopScrollOutOfBounds(offset);
						}
					}
				}
			}

			migrateBaseIndex(renderedIndexCenter);

			// console.log("heightsCache", heightsCache);
			

		}, 50);
	});

	onDestroy(() => {
		clearInterval(interval);
		domScrollWindow.removeEventListener("scroll", scrollListener);
	});
</script>

<div class="scroll-window" bind:clientHeight={scrollWindowHeight} bind:clientWidth={scrollWindowWidth} bind:this={domScrollWindow}>
	<div class="scroll-container" style="height: {scrollContainerHeight}px;" bind:this={domScrollContainer}>
		{#each renderedMessages as message, i (message._id)}
			<div class="scroll-absolute-element" data-index={topVisibleElementIndex + i} style={"position: absolute; left: 0px;top:0px; width: " + scrollWindowWidth + "px;"}>
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