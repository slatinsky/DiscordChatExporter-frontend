<script lang="ts">
	import {throttle, debounce} from 'lodash-es';
	import { clamp } from 'src/js/helpers';
	import {resizeObserver} from "src/js/resizeObserver";
	import { onMount, onDestroy } from "svelte";
	import { tick } from 'svelte';
	export let negativeHeight: number = 50   // negative height of the 100vh container
	export let itemCount: number;            // items count to render

	export let startPosition: number = 0     // index of the item to start rendering from. Is reactive

	let centerItemIndex: number = 0          // index of the item in the center of the window
	let centerItemOffset: number = 0         // offset of the item in the center of the window

	let renderingDisabled: boolean = false   // disable rendering of new items

	let highlightedIndex: number = -1

	let mounted: boolean = false

	export async function jumpToIndex(index: number) {
		if (itemCount <= index) {
			console.error("jumpToIndex   itemCount <= index", itemCount, index);
			return
		}
		if (index < 0) {
			console.error("jumpToIndex   index < 0", index);
			return
		}
		console.log("jumpToIndex", index);
		
		await new Promise(resolve => {  // await mounted = true
			const interval = setInterval(() => {
				if (mounted) {
					clearInterval(interval)
					resolve(null)
				}
			}, 5);
		});
		await tick();

		if (domWindow) {
			await tick();
			while (true) {
				// scroll to estimated position
				const estimatedOffset = itemOffsets[index] || centerItemOffset - (index - centerItemIndex) * itemEstimatedHeight
				// domWindow.scrollTop = estimatedOffset
				await tick();
				await new Promise(r => setTimeout(r, 100));

				highlightedIndex = index

				let minRenderedIndex = Math.min(...indexesToRender)
				let maxRenderedIndex = Math.max(...indexesToRender)

				let diff = Math.abs(index - centerItemIndex)

				// go up if needed
				if (index < minRenderedIndex) {
					console.log("go up", index, "<", minRenderedIndex, index - minRenderedIndex);
					// scroll up
					domWindow.scrollTop -= Math.max(diff * itemEstimatedHeight * 0.8, windowHeight || 1000)
				}
				// go down if needed
				else if (index > maxRenderedIndex) {
					console.log("go down", index, ">", maxRenderedIndex, index - maxRenderedIndex);
					// scroll down
					domWindow.scrollTop += Math.max(diff * itemEstimatedHeight * 0.8, windowHeight || 1000)
				}
				else {
					break
				}

				await tick();

				await new Promise(r => setTimeout(r, 100));
			}


			await tick();

			await new Promise(r => setTimeout(r, 100));

			// scroll to exact position
			domWindow.scrollTop = itemOffsets[index] + itemHeights[index] / 2 - windowHeight / 2

			await new Promise(r => setTimeout(r, 500));

			domWindow.scrollTop = itemOffsets[index] + itemHeights[index] / 2 - windowHeight / 2  // there has to be a better way to do this

			await new Promise(r => setTimeout(r, 6000));

			highlightedIndex = -1

		}
		else {
			console.error("domWindow is undefined - jumpToIndex");
		}
	}

	// observed heights and widths of divs
	let windowHeight: number | undefined
	let windowWidth: number | undefined
	let itemHeights:  Record<number, number>  = {}
	let itemOffsets:  Record<number, number>  = {}

	// dom elements
	let domWindow: HTMLElement | undefined
	let domContainer: HTMLElement | undefined
	let domItems: Record<number, HTMLElement> = {}

	// indexes to render
	let indexesToRender: number[] = []

	// max div size is 33554400px, we cannot exceed this limit
	const MAX_DIV_SIZE = 33554400
	const itemEstimatedHeight = Math.min(MAX_DIV_SIZE / itemCount * 0.9, 100)
	let containerHeightEstimated = itemEstimatedHeight * itemCount

	function scrollListener() {
		// console.log("scrollListener");
		renderMoreItems()
	}

	let scrollThrottledListener = throttle(scrollListener, 100, { leading: false, trailing: true });

	function updateIndexesToRender(newItemsToRender: number[]) {
		for (const index in itemHeights) {
			if (!newItemsToRender.includes(parseInt(index))) {
				delete itemHeights[index]
			}
		}
		for (const index in domItems) {
			if (!newItemsToRender.includes(parseInt(index))) {
				delete domItems[index]
			}
		}
		indexesToRender = newItemsToRender
	}

	function getItemHeight(index: number) {
		return itemHeights[index] || itemEstimatedHeight
	}

	function calculateItemOffset(itemIndex: number) {
		// calculate from centerItemOffset

		let offset = centerItemOffset
		let index = centerItemIndex

		while (index > itemIndex) {
			index--
			offset -= getItemHeight(index)
		}
		while (index < itemIndex) {
			offset += getItemHeight(index)
			index++
		}
		console.log("calculateItemOffset", itemIndex, offset);
		return offset
	}

	async function updateItemOffsets() {
		let offset = centerItemOffset
		let index = centerItemIndex
		// down
		while (true) {
			index--
			if (!itemHeights[index]) {
				break
			}
			offset -= getItemHeight(index)
			itemOffsets[index] = offset
		}

		// up
		offset = centerItemOffset
		index = centerItemIndex
		while (true) {
			if (!itemHeights[index]) {
				break
			}
			itemOffsets[index] = offset
			offset += getItemHeight(index)
			index++
		}

		// fix top items out of bounds
		const lowestOffset = Math.min(...Object.values(itemOffsets))
		if (lowestOffset < 0) {
			// move all items up
			// await tick();
			// renderingDisabled = true
			// await tick();
			for (const index in itemOffsets) {
				itemOffsets[index] -= lowestOffset
				if (index === centerItemIndex.toString()) {
					centerItemOffset -= lowestOffset
					domWindow?.scrollBy(0, -lowestOffset)
				}
			}
			// await tick();
			// renderingDisabled = false
			await tick();
			console.warn("fix top items out of bounds by offset", lowestOffset);
		}

		// fix top items too far down
		if (indexesToRender.includes(0)) {
			const zeroOffset = itemOffsets[0] || 0
			if (zeroOffset > 0) {
				// move all items down
				for (const index in itemOffsets) {
					itemOffsets[index] -= zeroOffset
				}
				console.warn("fix top items too far down by offset", zeroOffset);
			}
		}

		if (containerHeightEstimated === undefined) {
			console.warn("containerHeightEstimated is undefined");
			return
		}

		const highestIndex = Math.max(...indexesToRender)
		const highestBottomOffset = itemOffsets[highestIndex] || itemEstimatedHeight * highestIndex + getItemHeight(highestIndex)
		if (highestIndex === itemCount - 1) {
			// resize container to exactly match the last item
			console.warn("fix bottom items to match last item by offset", containerHeightEstimated - highestBottomOffset);
			containerHeightEstimated = highestBottomOffset
		}
		else if (highestBottomOffset > containerHeightEstimated) {
			let estimatedOffsetDiff = (itemCount - 1 - highestIndex) * itemEstimatedHeight
			containerHeightEstimated = highestBottomOffset + estimatedOffsetDiff
			console.warn("fix bottom items out of bounds by offset", estimatedOffsetDiff);
		}
	}

	function findNewCenterItem() {
		if (windowHeight === undefined) {
			console.error("windowHeight is undefined");
			return
		}
		// center scroll position
		const scrollTopPosition = domWindow?.scrollTop || 0
		const scrollCenterPosition = scrollTopPosition + windowHeight / 2

		// find the closest item in itemOffsets
		let closestItemIndex = centerItemIndex
		let closestItemOffset = centerItemOffset

		for (const index in itemOffsets) {
			if (!indexesToRender.includes(parseInt(index))) {  // skip items that are not rendered
				continue
			}
			const offset = itemOffsets[index]
			if (Math.abs(offset - scrollCenterPosition) < Math.abs(closestItemOffset - scrollCenterPosition)) {
				closestItemIndex = parseInt(index)
				closestItemOffset = offset
			}
		}

		// update center item
		if (closestItemIndex !== centerItemIndex) {
			// console.log("new center index", centerItemIndex, "=>", closestItemIndex);
			centerItemIndex = closestItemIndex
			centerItemOffset = closestItemOffset
		}
	}

	function giveUp() {
		// start rendering from the beginning
		// happens at the start or when the user scrolled too far and it is not worth it to render all the items between
		const scrollTopPosition = domWindow?.scrollTop || 0
		const estimatedCenterItemIndex = Math.floor(scrollTopPosition / itemEstimatedHeight)
		centerItemIndex = clamp(0, estimatedCenterItemIndex, itemCount - 1)
		centerItemOffset = centerItemIndex * itemEstimatedHeight
		itemOffsets = {}
		itemHeights = {}
		domItems = {}
		itemOffsets[centerItemIndex] = centerItemOffset

		updateIndexesToRender([estimatedCenterItemIndex])
	}

	function renderMoreItems() {
		if (renderingDisabled) {
			return
		}
		if (windowHeight === undefined) {
			console.error("windowHeight is undefined");
			return
		}
		if (indexesToRender.length === 0) {
			console.error("indexesToRender is empty");
			return
		}
		// get window scroll position
		const scrollTopPosition = domWindow?.scrollTop || 0
		const scrollBottomPosition = scrollTopPosition + windowHeight

		let firstItemIndex = indexesToRender[0]
		let lastItemIndex = indexesToRender[indexesToRender.length - 1]

		// top item offset
		let topItemOffset = itemOffsets[firstItemIndex]
		// bottom item offset
		let bottomItemOffset = itemOffsets[lastItemIndex] + getItemHeight(lastItemIndex)  // + getItemHeight() makes from undefined NaN


		if (topItemOffset === undefined) {
			// console.warn("topItemOffset is undefined");
			return
		}

		let loadPadding = Math.max(windowHeight, 1000)
		let unloadPadding = Math.max(windowHeight, 1000) * 4
		let giveUpPadding = Math.max(windowHeight, 1000) * 10

		// render more items if needed
		if (topItemOffset > scrollTopPosition - loadPadding) {
			const newIndex = firstItemIndex - 1
			if (newIndex >= 0) {
				updateIndexesToRender([newIndex, ...indexesToRender])
			}
		}

		if (isNaN(bottomItemOffset)) {
			// console.warn("bottomItemOffset is NaN");
			return
		}

		if (bottomItemOffset < scrollBottomPosition + loadPadding) {
			const newIndex = lastItemIndex + 1
			if (newIndex < itemCount) {
				updateIndexesToRender([...indexesToRender, newIndex])
			}
		}

		// we need to reloacate center item, before we unload items. Else the center item would be stuck at the edge and no item would be unloaded
		findNewCenterItem()

		// unload items if needed
		if (topItemOffset < scrollTopPosition - unloadPadding) {
			const newIndex = firstItemIndex + 1
			const indexToRemove = indexesToRender[0]
			if (newIndex < itemCount && indexToRemove !== centerItemIndex) {
				updateIndexesToRender(indexesToRender.slice(1))
				// console.log("unload top", newIndex);
			}
		}
		if (bottomItemOffset > scrollBottomPosition + unloadPadding) {
			const newIndex = lastItemIndex - 1
			const indexToRemove = indexesToRender[indexesToRender.length - 1]
			if (newIndex >= 0 && indexToRemove !== centerItemIndex) {
				updateIndexesToRender(indexesToRender.slice(0, -1))
				// console.log("unload bottom", newIndex);
			}
		}


		// // give up if we are too far from the center
		if (topItemOffset < scrollTopPosition - giveUpPadding) {
			console.warn("give up top", topItemOffset,"<", scrollTopPosition - giveUpPadding);
			giveUp()
		}
		if (bottomItemOffset > scrollBottomPosition + giveUpPadding) {
			console.warn("give up bottom", bottomItemOffset,">", scrollBottomPosition + giveUpPadding);
			giveUp()
		}
	}

	async function updatedItemHeight(index: number, newHeight: number) {
		const oldItemHeight = itemHeights[index] || itemEstimatedHeight
		itemHeights[index] = newHeight
		// console.log("updatedItemHeight", index," ", oldItemHeight, "=>", newHeight);
		await updateItemOffsets()
		renderMoreItems()
	}

	function updatedWindowWidthHeight(newWidth: number, newHeight: number) {
		windowWidth = newWidth
		windowHeight = newHeight
	}

	async function startPositionChanged(newStartPosition: number) {
		await tick();
		if (domWindow) {
			domWindow.scrollTop = itemOffsets[newStartPosition] || startPosition * itemEstimatedHeight
		}
		else {  // not mounted yet
			console.error("domWindow is undefined - startPositionChanged");
		}
	}

	$: startPositionChanged(startPosition)


	onMount(async() => {
		if (itemCount === 0) {
			console.log("no items to render");
			return
		}
		await tick();
		if (domWindow) {
			domWindow.scrollTop = startPosition * itemEstimatedHeight
		}
		else {
			console.error("domWindow is undefined - scroll to startPosition");
		}

		console.log({windowHeight, windowWidth, containerHeightEstimated, itemHeights, domWindow, domContainer, domItems, indexesToRender});
		if (domWindow) {
			domWindow.addEventListener("scroll", scrollThrottledListener, { passive: true });
		}
		else {
			console.error("domWindow is undefined - mount");
		}

		giveUp()

		mounted = true
	})

	onDestroy(() => {
		if (domWindow) {
			domWindow.removeEventListener("scroll", scrollThrottledListener);
		}
		else {
			console.error("domWindow is undefined - unmount");
		}
	})

</script>
<div class="scroll-window" use:resizeObserver={element => updatedWindowWidthHeight(element.clientWidth, element.clientHeight)} bind:this={domWindow} style={"height:calc(100dvh - " + negativeHeight + "px)"}>
	<div class="scroll-container" style="height: {containerHeightEstimated}px;position:relative;" bind:this={domContainer}>
		{#each indexesToRender as messageIndex (messageIndex)}
			<div class="scroll-absolute-element" data-index={messageIndex} style={"position: absolute; left: 0px; width:100%;top:" + (itemOffsets[messageIndex] || 0) + "px"} class:highlight={highlightedIndex == messageIndex} class:center={centerItemIndex == messageIndex} bind:this={domItems[messageIndex]} use:resizeObserver={element => updatedItemHeight(messageIndex, element.clientHeight)} >
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

.highlight {
	background-color: #4e4913 !important;
}

/*DEBUG ONLY - highlight center item*/
/* .center {
	background-color: #1d6774 !important;
} */
</style>