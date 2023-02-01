<!--

	Virtual list component
	Renders items with variable item heights
	Tries to eliminate jitter from loading images

	---------------------

	the item in the middle of the screen is chosen as the primary item to render  (centerItemIndex)
	if there is space above or below, more items are rendered
	those items are offset based on the primary item position (if they change size, the reflow is minimal for the user)
	some items are rendered outside of the viewport

	While the users scrolls, the primary item (centerItemIndex) is changed to the item in the middle of the screen
	and height offset is saved (centerItemTopOffset)

	because we don't know the height of all items, the scrollbar position cannot be accurately calculated.
	we just estimate it by the height of one item (itemEstimatedHeight) and the number of items rendered (itemCount).

	As the user scrolls, the scollbar position (centerItemTopOffset) is more and more misaligned with the actual position (itemEstimatedHeight * centerItemIndex).
	We fix the misalignent if the user scrolls to the start of the scroll container or to the end of the scroll container.

	If user scrolls too far, we don't load new items near the primary item,
	but we clear all rendered items and we place new primary item at (itemEstimatedHeight * centerItemIndex) - that indirectly clears the misalignment too

-->


<script lang="ts">
	// types
	interface ScreenPositions {
		top: number;
		middle: number;
		bottom: number;
	}
	import type { MessageIdLoad } from "src/js/interfaces";


	// imports
	import { onDestroy, onMount } from "svelte";
	import {throttle, debounce} from 'lodash-es';
	import {resizeObserver} from "src/js/resizeObserver";


	// props
	export let itemCount: number;          // items count to render
	export let negativeHeight: number = 50;         // negative height of the 100vh container


	// "autofilled" variables after mount
	let windowHeight: number;              // height of "window" div, not browser window
	let windowWidth: number;               // width of "window" div, not browser window
	let domWindow: HTMLElement;            // "window" to scrollable content
	let domContainer: HTMLElement;         // scrollable content


	// values that never change
	let itemEstimatedHeight = 100;                                          // estimated height of each item
	let containerEstimatedHeight = itemEstimatedHeight * itemCount;   // first estimation of the container height


	let maxItemsLoaded = 50;                                                // max items loaded at once. After that, items at the edges are removed. This value is changed at runtime for large screens
	let containerHeight = containerEstimatedHeight;                         // set


	// centerItem
	let centerItemIndex = 0     // index of the item that is in the center of the screen
	let centerItemTopOffset = 0    // absolute offset from the top of the container


	let heightsCache: Record<number, number> = {}   // cache of heights of items


	// indexes to render
	let indexesToRender: number[] = []
	addIndexToRender(centerItemIndex)  // render first item


	function getCachedHeight(index: number): number {
		// if not cached, return estimated height
		if (heightsCache[index] === undefined) {
			if (heights[index] === undefined) {
				console.warn("height not cached");
				return itemEstimatedHeight
			}
			return heights[index]
		}
		return heightsCache[index]
	}

	function addIndexToRender(index: number): void {
		if (indexesToRender.includes(index)) {
			return
		}

		let newIndexesToRender = [...indexesToRender, index]
		newIndexesToRender.sort((a, b) => a - b)
		indexesToRender = newIndexesToRender
	}
	function clearIndexRender(): void {
		indexesToRender = []
	}

	function refreshCenterItem(): void {
		let oldIndex = centerItemIndex
		let newIndex = findCenterItemIndex()  // get middle index of the screen

		if (newIndex === null) {
			console.warn("newIndex is null");
			return
		}

		// DOWN
		if (newIndex > oldIndex) {
			for (let i = oldIndex; i < newIndex; i++) {
				centerItemTopOffset += getCachedHeight(i)
				centerItemIndex += 1
			}
		}

		// UP
		if (newIndex < oldIndex) {
			for (let i = oldIndex; i > newIndex; i--) {
				centerItemTopOffset -= getCachedHeight(i - 1)
				centerItemIndex -= 1
			}
		}

		console.log("refreshed center item", oldIndex, "-->", newIndex);
	}

	function loadNItemsDown(n: number): void {
		let newIndexesToRender = [...indexesToRender]
		for (let i = 0; i < n; i++) {
			const lastItemIndex = newIndexesToRender[newIndexesToRender.length - 1]
			if (lastItemIndex === itemCount - 1) {
				break
			}
			newIndexesToRender = [...newIndexesToRender, lastItemIndex + 1]
		}

		if (newIndexesToRender.length === indexesToRender.length) {
			return  // no change
		}

		console.log("loaded", newIndexesToRender.length - indexesToRender.length, "items down");

		while (true) {
			if (newIndexesToRender.length > maxItemsLoaded) {
				newIndexesToRender.shift()  // remove first item
				console.log("unloaded one item down");
			}
			else {
				break
			}
		}
		indexesToRender = newIndexesToRender
		refreshCenterItem()
	}

	function loadNItemsUp(n: number): void {
		let newIndexesToRender = [...indexesToRender]
		for (let i = 0; i < n; i++) {
			const firstItemIndex = newIndexesToRender[0]
			if (firstItemIndex === 0) {
				break
			}
			newIndexesToRender = [firstItemIndex - 1, ...newIndexesToRender]
		}

		if (newIndexesToRender.length === indexesToRender.length) {
			return  // no change
		}

		console.log("loaded", newIndexesToRender.length - indexesToRender.length, "items up");

		while (true) {
			if (newIndexesToRender.length > maxItemsLoaded) {
				newIndexesToRender.pop()  // remove last item
				console.log("unloaded one item up");
			}
			else {
				break
			}
		}
		indexesToRender = newIndexesToRender
		refreshCenterItem()
	}

	function loadItemDown(): void {
		loadNItemsDown(5)
	}
	function loadItemUp(): void {
		loadNItemsUp(5)
	}

	function fixTopScrollOutOfBounds(offsetToFix: number) {
		centerItemTopOffset -= offsetToFix;
		domWindow.scrollTop -= offsetToFix;
		console.log("fixScrollOutOfBounds", offsetToFix);
		heightsChanged(heights, true)
	}


	function getScreenPositions(): ScreenPositions {
		return {
			top: domWindow.scrollTop,
			middle: domWindow.scrollTop + domWindow.clientHeight / 2,
			bottom: domWindow.scrollTop + domWindow.clientHeight
		}
	}


	function findCenterItemIndex(): number | null {
		const screenPositions = getScreenPositions()

		let closestIndex: number = centerItemIndex
		let closestOffset: number = centerItemTopOffset + heights[centerItemIndex] / 2
		let closestDistance = Math.abs(closestOffset - screenPositions.middle)

		while(true) {
			let nextItemOffset
			let nextItemIndex
			let nextItemDistance

			if (centerItemTopOffset < screenPositions.middle) {  // centerItem is above the screen middle position
				if (heights[closestIndex] === undefined || heights[closestIndex + 1] === undefined) {  // infinite loop protection
					console.warn("undefined height v1", heights[closestIndex], heights[closestIndex + 1])
					return closestIndex
				}
				nextItemOffset = closestOffset + heights[closestIndex] / 2 + heights[closestIndex + 1] / 2
				nextItemIndex = closestIndex + 1
				nextItemDistance = Math.abs(nextItemOffset - screenPositions.middle)
			}
			else if (centerItemTopOffset > screenPositions.middle) {  // centerItem is below the screen middle position
				if (heights[closestIndex] === undefined || heights[closestIndex - 1] === undefined) {  // infinite loop protection
					console.warn("undefined height v2", heights[closestIndex], heights[closestIndex - 1])
					return closestIndex
				}
				nextItemOffset = closestOffset - heights[closestIndex] / 2 - heights[closestIndex - 1] / 2
				nextItemIndex = closestIndex - 1
				nextItemDistance = Math.abs(nextItemOffset - screenPositions.middle)
			}
			else {
				break
			}

			// if the distance is worse, then stop
			if (nextItemDistance > closestDistance) {
				break
			}
			// if the distance is better, then update
			closestIndex = nextItemIndex
			closestOffset = nextItemOffset
			closestDistance = nextItemDistance
		}
		return closestIndex
	}

	function heightsChanged(updatedHeights: Record<string, number>, forceUpdate: boolean = false): void {
		if (heightsCache === null) {
			console.warn("heightsChanged - heightsCache is null, this function should not be called before mount");
			return
		}

		let renderedIndexes = indexesToRender
		let renderedIndexesMin = renderedIndexes[0]
		let renderedIndexesMax = renderedIndexes[renderedIndexes.length - 1]

		let upIndexToUpdate: number | null = null     // indexes above this index (including) need to be repositioned updated. Null means no update needed
		let downIndexToUpdate: number | null = null   // indexes below this index (including) need to be repositioned updated. Null means no update needed

		// updatedHeights contains all heights, but we only need to update the ones that were updated

		// loop all values in renderedIds
		for (let i = 0; i < renderedIndexes.length; i++) {
			const index = renderedIndexes[i]
			const oldHeight: number | undefined = heightsCache[index]
			const newHeight: number = updatedHeights[index]

			if (newHeight === 0) {
				console.warn("heightsChanged - newHeight is 0, probably the component is not mounted yet");
				startOver(centerItemIndex)
				return
			}

			if (isNaN(newHeight)) {
				console.warn("heightsChanged - newHeight is NaN, probably the component is not mounted yet");
				startOver(centerItemIndex)
				return
			}

			if (domItems[index] === undefined) {
				console.warn("heightsChanged - domItems[index] is undefined, probably the component is not mounted yet");
				return
			}

			if (newHeight !== oldHeight) {
				heightsCache[index] = newHeight
				// save item positions we need to relocate
				if (centerItemIndex <= index) {  // down
					downIndexToUpdate = Math.min(downIndexToUpdate ?? Infinity, index)  // closest index to centerItem
				}
				if (centerItemIndex > index) {   // up
					upIndexToUpdate = Math.max(upIndexToUpdate ?? -Infinity, index)  // closest index to centerItem
				}
			}
		}

		// in some cases repositionin is not caused by changed height
		// for example when we scroll to the start of the container and the first item is misaligned
		if (forceUpdate) {
			upIndexToUpdate = centerItemIndex
			downIndexToUpdate = centerItemIndex
		}

		let offset = centerItemTopOffset
		if (downIndexToUpdate !== null) { // down
			// update all indexes below downIndexToUpdate
			for (let i = centerItemIndex; i <= renderedIndexesMax; i++) {  // we need to loop everything from centerItemIndex to renderedIndexesMax, because we need to calculate the offset
				const index = i

				const itemHeight = heights[index] ?? itemEstimatedHeight

				if (downIndexToUpdate <= index) {  // actually update only items below changed index)
					try {
						domItems[index].style.top = offset + "px"
					}
					catch (e) {
						console.warn("heightsChanged - changing height failed, component was probably unmounted");
						return
					}
				}
				offset += itemHeight

				// if the the last item comes out of bounds, we need to increase the container height:
				if (i === renderedIndexesMax) {  // run for the last rendered item only
					// if this is the last item, perfectly align the bottom
					if (index === itemCount - 1) {
						// console.log("setting container height =", offset, offset + itemHeight, containerHeight);
						if (containerHeight !== offset) {
							containerHeight = offset
							console.log("setting container height =", containerHeight);
						}
					}
					// else we estimate the height of the remaining items
					else if (offset + itemHeight > containerHeight) {
						containerHeight += (itemCount - 1 - index) * itemEstimatedHeight
						console.log("estimating new container height +", (itemCount - 1 - index) * itemEstimatedHeight);
					}
				}
			}
		}

		offset = centerItemTopOffset + heightsCache[centerItemIndex]
		if (upIndexToUpdate !== null) { // up
			// console.log("upIndexToUpdate", upIndexToUpdate);

			// update all indexes above upIndexToUpdate
			for (let i = centerItemIndex; i >= renderedIndexesMin; i--) {
				const index = i
				const itemHeight = heights[index] ?? itemEstimatedHeight

				offset -= itemHeight

				if (upIndexToUpdate >= index) {  // actually update only items above changed index)
					try {
						domItems[index].style.top = offset + "px"
					}
					catch (e) {
						console.warn("heightsChanged - changing height failed, component was probably unmounted");
						return
					}
				}

				if (i === 0) {  // run for the first rendered item only
					// because we sometimes assume the height for non-rendered items (itemEstimatedHeight), the start will almost never line up perfectly
					// that's why need to align it when scrolling up:
					// everytime we try to set negative offset - estimate new start position
					if (offset < 0) {
						fixTopScrollOutOfBounds(offset - index * itemEstimatedHeight)
					}
					// and everytime we place 0th item at the top - perfectly align start position
					if (index == 0 && offset > 0) {
						fixTopScrollOutOfBounds(offset);
					}
				}
			}
		}
	}

	function startOver(newCenterItemIndex: number) {
		// try to recover from error
		centerItemIndex = newCenterItemIndex
		centerItemTopOffset = newCenterItemIndex * itemEstimatedHeight
		heightsCache = {}
		clearIndexRender()
		addIndexToRender(centerItemIndex)
	}

	async function scrollListener() {
		if (interval === null) {  // don't fire listener if we are unmounting now
			return
		}

		let ScreenPositions = getScreenPositions()
		let renderedIndexes = indexesToRender
		let renderedIndexesMin = renderedIndexes[0]
		let renderedIndexesMax = renderedIndexes[renderedIndexes.length - 1]

		// calculate first position (up)
		let firstDomTopOffset = centerItemTopOffset + heightsCache[centerItemIndex]
		for (let i = centerItemIndex; i >= renderedIndexesMin; i--) {
			firstDomTopOffset -= heightsCache[i]
		}

		// calculate last position (down)
		let lastDomTopOffset = centerItemTopOffset - heightsCache[centerItemIndex]
		for (let i = centerItemIndex; i <= renderedIndexesMax; i++) {
			lastDomTopOffset += heightsCache[i]
		}

		let firstDomBottomOffset = firstDomTopOffset + heightsCache[renderedIndexesMin]

		// if we scrolled too far, just start over with new center item
		if (lastDomTopOffset !== 0 && firstDomTopOffset !== 0) {   // new items are placed at the offset 0, ignore new items
			if (lastDomTopOffset + 5000 < ScreenPositions.middle || firstDomTopOffset - 5000 > ScreenPositions.middle) {
				let newCenterItemIndex = Math.floor(ScreenPositions.middle / itemEstimatedHeight)

				if (newCenterItemIndex > itemCount - 1) {  // don't scroll past the end (it can happen, because we estimate the height)
					console.warn("too ambitious scroll, fixing scroll to the bottom");

					newCenterItemIndex = itemCount - 1
				}

				const newCenterItemTopOffset = newCenterItemIndex * itemEstimatedHeight
				// it may take a while to the new item to render
				// ignore all subsequent attemts to retry rendering
				if (indexesToRender.indexOf(newCenterItemIndex) === -1) {
					startOver(newCenterItemIndex)
					console.warn("scrolled too far, re-rendering everything - new center index =", centerItemIndex, centerItemTopOffset);
				}
			}
		}

		// if the center item is (relatively) near, load more items to the ScreenPosition
		// this is triggered after we scroll DOWN
		if (lastDomTopOffset < ScreenPositions.bottom + .5 * windowHeight) {
			loadItemDown()

			setTimeout(() => {  // wait for timeout at the bottom
				scrollListener()      // rerun, maybe we need to add more items
			}, 1);
		}

		// same as above, but for scroll UP
		if (firstDomBottomOffset > ScreenPositions.top - .5 * windowHeight) {
			loadItemUp()

			setTimeout(() => {  // wait for timeout at the top
				scrollListener()      // rerun, maybe we need to add more items
			}, 1);
		}
	}

	function calculateRenderedItemCount() {
			// large screens need more items to be rendered
			// TODO: recalculate maxItemsLoaded on window resize
			let newMaxItemsLoaded = Math.max(Math.round(windowHeight * 4 / itemEstimatedHeight), 50)
			if (isNaN(newMaxItemsLoaded)) {
				newMaxItemsLoaded = 50
			}
			if (newMaxItemsLoaded === maxItemsLoaded) {
				return
			}

			maxItemsLoaded = newMaxItemsLoaded
			console.log("maxItemsLoaded set to", maxItemsLoaded);
	}

	$: windowHeight, calculateRenderedItemCount()

	let interval: NodeJS.Timeout | null = null;
	let scrollThrottle = throttle(scrollListener, 100, { leading: false, trailing: true });
	onMount(() => {
		if (itemCount === 0) {
			console.log("no items to render");

			return
		}

		setTimeout(() => {
			calculateRenderedItemCount()
			domWindow.addEventListener("scroll", scrollThrottle, { passive: true });
			scrollListener()              // call to init without scrolling
		}, 0);

		// sometimes we need to fix item positions outside of scroll event
		// because loaded images changed items height
		interval = setInterval(() => {
			scrollListener()
		}, 1000);
	});

	onDestroy(() => {
		// cleanup
		clearInterval(interval);
		interval = null;
		domWindow.removeEventListener("scroll", scrollThrottle, { passive: true });
	});

	let heights: Record<number, number> = {}
	let domItems: Record<number, HTMLElement> = {}

	$: heightsChanged(heights)
</script>

<div class="scroll-window" use:resizeObserver={element => {
		windowHeight = element.clientHeight
		windowWidth = element.clientWidth
	}} bind:this={domWindow} style={"height:calc(100vh - " + negativeHeight + "px)"}>
	<div class="scroll-container" style="height: {containerHeight}px;position:relative;" bind:this={domContainer}>
		{#each indexesToRender as messageIndex (messageIndex)}
			<div class="scroll-absolute-element" data-index={messageIndex} style={"position: absolute; left: 0px; width:100%;"} bind:this={domItems[messageIndex]} use:resizeObserver={element => heights[messageIndex] = element.clientHeight} >
				<slot name="item" index={messageIndex} />
			</div>
		{/each}
	</div>
</div>


<style>
.scroll-window {
	overflow-y: scroll;
	overflow-x: hidden;
	position: relative;
	width: 100%;
}
</style>