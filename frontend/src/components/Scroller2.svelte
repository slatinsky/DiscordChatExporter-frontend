<!-- Virtual scroller component -->
<!-- Now renders with variable item heights -->

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


	let containerHeight = containerEstimatedHeight;                         // set


	// centerItem
	let centerItemIndex = 0     // index of the item that is in the center of the screen
	let centerItemTopOffset = 0    // absolute offset from the top of the container


	let heightsCache: Record<number, number> = {}   // cache of heights of items


	// indexes to render
	let indexesToRender: number[] = []
	addIndexToRender(centerItemIndex)  // render first item


	function getCachedHeight(index: number): number {
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
	function removeIndexToRender(index: number): void {
		indexesToRender = indexesToRender.filter((i) => i.index !== index)
	}

	function refreshCenterItem(): void {
		let oldIndex = centerItemIndex
		const newIndex = findCenterItemIndex()  // get middle index of the screen

		if (newIndex === null) {
			console.warn("newIndex is null");
			newIndex = indexesToRender[Math.floor(indexesToRender.length / 2)]  // get middle index of loaded items
		}

		// if the difference is less than 3, then ignore
		// this prevents infinite "feedback" loops
		if (Math.abs(newIndex - oldIndex) <= 2) {
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

	function loadItemDown(): void {
		const lastItemIndex = indexesToRender[indexesToRender.length - 1]
		if (lastItemIndex === messages.length - 1) {
			return
		}

		let newIndexesToRender = [...indexesToRender, lastItemIndex + 1]

		let maxItemsLoaded = 50
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

		let maxItemsLoaded = 50
		if (newIndexesToRender.length > maxItemsLoaded) {
			refreshCenterItem()
			newIndexesToRender.pop()  // remove last item
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

		return closestItem?.index ?? null
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
							containerHeight = offset   // TODO: this is called too many times if rounding error happens
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

		if (lastDomPositions.top < ScreenPositions.bottom + windowHeight) {
			loadItemDown()

			setTimeout(() => {  // wait for timeout at the bottom
				if (interval !== null) {  // don't fire listener if we are unmounting now
					scrollListener()  // rerun, maybe we need to add more items
				}
			}, 1);
		}

		else if (firstDomPositions.bottom > ScreenPositions.top - windowHeight) {
			loadItemUp()

			setTimeout(() => {  // wait for timeout at the top
				if (interval !== null) {  // don't fire listener if we are unmounting now
					scrollListener()  // rerun, maybe we need to add more items
				}
			}, 1);
		}

		setTimeout(() => {  // wait for items to be rendered
			if (interval !== null) {  // don't fire listener if we are unmounting now
				setOffsets()
			}
		}, 0);
	}

	let interval: NodeJS.Timeout | null = null;
	onMount(() => {
		setTimeout(() => {
			domWindow.addEventListener("scroll", scrollListener);
			scrollListener() // call to init without scrolling
		}, 0);

		interval = setInterval(() => {
			scrollListener()
		}, 1000);
	});

	onDestroy(() => {
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
	height: calc(100vh - 51px);
	overflow-y: scroll;
	overflow-x: hidden;
	position: relative;
	width: 100%;
}
</style>