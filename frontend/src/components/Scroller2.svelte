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
	we just estimate it by the height of one item (itemEstimatedHeight) and the number of items rendered (messages.length).

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
	import MessageLoader from "src/routes/channels/[guildId]/[channelId]/MessageLoader.svelte";
	import { onDestroy, onMount } from "svelte";


	// props
	export let messages: MessageIdLoad[];        // items to render
	export let selectedGuildId: string;


	// "autofilled" variables after mount
	let windowHeight: number;              // height of "window" div, not browser window
	let windowWidth: number;               // width of "window" div, not browser window
	let domWindow: HTMLElement;            // "window" to scrollable content
	let domContainer: HTMLElement;         // scrollable content


	// values that never change
	let itemEstimatedHeight = 100;                                          // estimated height of each item
	let containerEstimatedHeight = itemEstimatedHeight * messages.length;   // first estimation of the container height


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

			// try to cache manually
			// get bt data-index attribute
			let domItem = domContainer.querySelector(`[data-index="${index}"]`) as HTMLElement
			if (domItem) {
				let height = domItem.offsetHeight
				heightsCache[index] = height
				console.warn("height found manually", index);
				return height
			}
			else {
				console.warn("height not cached");
				return itemEstimatedHeight
			}

		}
		return heightsCache[index] ?? itemEstimatedHeight
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
	function removeIndexToRender(index: number): void {
		indexesToRender = indexesToRender.filter((i) => i.index !== index)
	}

	function refreshCenterItem(): void {
		let oldIndex = centerItemIndex
		let newIndex = findCenterItemIndex()  // get middle index of the screen



		// if the difference is less than 3, then ignore
		// this prevents infinite "feedback" loops
		// if (Math.abs(newIndex - oldIndex) <= 2) {
		// 	return
		// }

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

	function loadItemDown(): void {
		const lastItemIndex = indexesToRender[indexesToRender.length - 1]
		if (lastItemIndex === messages.length - 1) {
			return
		}

		let newIndexesToRender = [...indexesToRender, lastItemIndex + 1]

		if (newIndexesToRender.length > maxItemsLoaded) {
			refreshCenterItem()
			newIndexesToRender.shift()  // remove first item
			console.log("unloaded one item down");
		}

		indexesToRender = newIndexesToRender  // apply
	}
	function loadItemUp(): void {
		const firstItemIndex = indexesToRender[0]
		if (firstItemIndex === 0) {
			return
		}

		let newIndexesToRender = [firstItemIndex - 1, ...indexesToRender]

		if (newIndexesToRender.length > maxItemsLoaded) {
			refreshCenterItem()
			newIndexesToRender.pop()  // remove last item
			setOffsets()
			console.log("unloaded one item up");
		}

		indexesToRender = newIndexesToRender  // apply
	}

	function fixTopScrollOutOfBounds(offsetToFix: number) {
		centerItemTopOffset -= offsetToFix;
		domWindow.scrollTop -= offsetToFix;
		console.log("fixScrollOutOfBounds", offsetToFix);
	}


	function getScreenPositions(): ScreenPositions {
		return {
			top: domWindow.scrollTop,
			middle: domWindow.scrollTop + domWindow.clientHeight / 2,
			bottom: domWindow.scrollTop + domWindow.clientHeight
		}
	}

	function getDomPositions(itemDom: ItemDom): ScreenPositions {
		return {
			top: itemDom.element.offsetTop,
			middle: itemDom.element.offsetTop + itemDom.element.clientHeight / 2,
			bottom: itemDom.element.offsetTop + itemDom.element.clientHeight
		}
	}


	interface ItemDom {
		index: number;
		element: HTMLElement;
	}


	function findCenterItemIndex(): number | null {
		const itemDoms = getItemDoms()
		const screenPositions = getScreenPositions()

		let closestItem: ItemDom | null = null
		let closestDistance = Infinity

		for (let i = 0; i < itemDoms.length; i++) {
			const itemDom = itemDoms[i]
			const domPositions = getDomPositions(itemDom)

			let distance = Math.abs(domPositions.middle - screenPositions.middle)
			if (distance < closestDistance) {
				closestDistance = distance
				closestItem = itemDom
			}
		}

		let newIndex = closestItem?.index ?? null

		if (newIndex === null) {
			console.warn("newIndex is null, using fallback (middle index of loaded items)");
			newIndex = indexesToRender[Math.floor(indexesToRender.length / 2)]  // get middle index of loaded items
		}

		return newIndex
	}

	function getItemDoms(): ItemDom[] {
		let elements = []
		for (let i = 0; i < domContainer.children.length; i++) {
			const element = domContainer.children[i] as HTMLElement;
			const index = parseInt(element.getAttribute("data-index") || "0")
			elements.push({
				index,
				element
			})
		}
		return elements
	}

	function getFirstDom(itemDoms:ItemDom[]): ItemDom | null {
		if (itemDoms.length === 0) {
			return null
		}
		return itemDoms[0]
	}

	function getLastDom(itemDoms:ItemDom[]): ItemDom | null {
		if (itemDoms.length === 0) {
			return null
		}
		return itemDoms[itemDoms.length - 1]
	}

	function setOffsets(): void {
		const itemDoms = getItemDoms()
		let offset = centerItemTopOffset
		for (let i = 0; i < itemDoms.length; i++) {  // DOWN
			const index = itemDoms[i].index
			const element = itemDoms[i].element
			const height = element.clientHeight
			let itemHeight = height
			if (isNaN(itemHeight)) {
				console.log("NaN height", index, element);
				itemHeight = itemEstimatedHeight
			}
			heightsCache[index] = itemHeight

			if (index >= centerItemIndex) {
				// console.log("set offset1", index, offset);
				element.style.top = offset + "px"
				offset += itemHeight

				// if the the last item comes out of bounds, we need to increase the container height:
				if (i === itemDoms.length - 1) {  // run for the last rendered item only
					// if this is the last item, perfectly align the bottom
					// 10 is just to avoid rounding errors
					if (index === messages.length - 1) {
						// console.log("setting container height =", offset, offset + itemHeight, containerHeight);
						if (containerHeight !== offset) {
							containerHeight = offset
							console.log("setting container height =", containerHeight);
						}
					}
					// else we estimate the height of the remaining items
					else if (offset + itemHeight > containerHeight) {
						containerHeight += (messages.length - 1 - index) * itemEstimatedHeight
						console.log("estimating new container height +", (messages.length - 1 - index) * itemEstimatedHeight);
					}
				}
			}
		}

		offset = centerItemTopOffset
		for (let i = itemDoms.length - 1; i >= 0; i--) {  // UP
			const index = itemDoms[i].index
			const element = itemDoms[i].element
			const height = element.clientHeight
			let itemHeight = height
			if (isNaN(itemHeight)) {
				itemHeight = itemEstimatedHeight
			}
			heightsCache[index] = itemHeight

			if (index < centerItemIndex) {
				// console.log("set offset2", index, offset);
				offset -= itemHeight
				element.style.top = offset + "px"

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

	function scrollListener() {
		let ScreenPositions = getScreenPositions()
		let itemDoms = getItemDoms()
		let firstDom = getFirstDom(itemDoms)
		let lastDom = getLastDom(itemDoms)

		let firstDomPositions = getDomPositions(firstDom as ItemDom)
		let lastDomPositions = getDomPositions(lastDom as ItemDom)

		// center item may be misaligned from the scroll position

		// TODO: correct the misalignment
		// let centerItemMisalignment = centerItemIndex * itemEstimatedHeight - centerItemTopOffset  // in px

		// if we scrolled too far, just start over with new center item
		if (lastDomPositions.top !== 0 && firstDomPositions.top !== 0) {   // new items are placed at the offset 0, ignore new items
			if (lastDomPositions.top + 5000 < ScreenPositions.middle || firstDomPositions.top - 5000 > ScreenPositions.middle) {
				let newCenterItemIndex = Math.floor(ScreenPositions.middle / itemEstimatedHeight)

				if (newCenterItemIndex > messages.length - 1) {  // don't scroll past the end (it can happen, because we estimate the height)
					console.warn("too ambitious scroll, fixing scroll to the bottom");

					newCenterItemIndex = messages.length - 1
				}

				const newCenterItemTopOffset = newCenterItemIndex * itemEstimatedHeight
				// it may take a while to the new item to render
				// ignore all subsequent attemts to retry rendering
				if (indexesToRender.indexOf(newCenterItemIndex) === -1) {
					centerItemTopOffset = newCenterItemTopOffset
					centerItemIndex = newCenterItemIndex
					heightsCache = {}
					clearIndexRender()
					addIndexToRender(centerItemIndex)
					console.warn("scrolled too far, re-rendering everything - new center index =", centerItemIndex, centerItemTopOffset);
				}
			}
		}

		// if the center item is (relatively) near, load more items to the ScreenPosition
		// this is triggered after we scroll DOWN
		if (lastDomPositions.top < ScreenPositions.bottom + 0.5 * windowHeight) {
			loadItemDown()

			setTimeout(() => {  // wait for timeout at the bottom
				if (interval !== null) {  // don't fire listener if we are unmounting now
					scrollListener()      // rerun, maybe we need to add more items
				}
			}, 1);
		}

		// same as above, but for scroll UP
		if (firstDomPositions.bottom > ScreenPositions.top - 0.5 * windowHeight) {
			loadItemUp()

			setTimeout(() => {  // wait for timeout at the top
				if (interval !== null) {  // don't fire listener if we are unmounting now
					scrollListener()      // rerun, maybe we need to add more items
				}
			}, 1);
		}

		// recalculate absolute positions
		setTimeout(() => {                // wait for items to be rendered
			if (interval !== null) {      // don't fire listener if we are unmounting now
				setOffsets()
			}
		}, 0);
	}

	let interval: NodeJS.Timeout | null = null;
	onMount(() => {
		setTimeout(() => {
			// large screens need more items to be rendered
			// TODO: recalculate maxItemsLoaded on window resize
			maxItemsLoaded = Math.max(Math.round(windowHeight * 4 / itemEstimatedHeight), 50)
			console.log("maxItemsLoaded set to", maxItemsLoaded);

			domWindow.addEventListener("scroll", scrollListener);
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
		domWindow.removeEventListener("scroll", scrollListener);
	});
</script>

<div class="scroll-window" bind:clientHeight={windowHeight} bind:clientWidth={windowWidth} bind:this={domWindow}>
	<div class="scroll-container" style="height: {containerHeight}px;" bind:this={domContainer}>
		{#each indexesToRender as messageIndex (messageIndex)}
			<div class="scroll-absolute-element" data-index={messageIndex} style={"position: absolute; left: 0px;top:0px; width: " + windowWidth + "px;"}>
				<MessageLoader messageId={messages[messageIndex]._id} selectedGuildId={selectedGuildId} />
			</div>
		{/each}
	</div>
</div>


<style>
.scroll-window {
	height: calc(100vh - 51px);  /* Header height is 50px */
	overflow-y: scroll;
	overflow-x: hidden;
	position: relative;
	width: 100%;
}
</style>