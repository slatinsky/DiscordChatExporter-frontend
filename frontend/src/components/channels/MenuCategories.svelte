<script lang="ts">
	import type { Channel } from "src/js/interfaces";
	import MenuCategory from "src/components/channels/MenuCategory.svelte";


	export let channels: Channel[] = [];
	export let selectedChannelId: string | null = null;
	export let selectedGuildId: string | null = null;

	let channelsByCategoryId: any = {};

	// interface Channel with channels array
	interface ChannelTree extends Channel {
		threads: Channel[]
	}

	function getCategoriesFromChannels(allChannels: Channel[]) {
		let threads: Channel[] = allChannels.filter(channel => channel.type === "GuildPublicThread" || channel.type === "GuildPrivateThread")
		let channels: ChannelTree[] = allChannels.filter(channel => channel.type !== "GuildPublicThread" && channel.type !== "GuildPrivateThread")
		// create channel for threads without channel
		channels.push({
			_id: '0',
			type: 'GuildTextChat',
			categoryId: '0',
			category: 'Lost threads / forums',
			name: 'Lost threads / forums',
			topic: null,
			threads: [],
			guildId: selectedGuildId as string,
		})

		// add channels array to all channels
		channels.forEach(channel => {
			channel.threads = []
		})

		// add threads to channels
		threads.forEach(thread => {
			let channel = channels.find(channel => channel._id === thread.categoryId)
			if (!channel) {
				channel = channels.find(channel => channel._id === '0')
			}
			// @ts-ignore
			channel.threads.push(thread)
		})

		// sort threads by _id
		channels.forEach(channel => {
			channel.threads.sort((a, b) => a._id.localeCompare(b._id))
		})


		// categorise channels by category
		let channelsByCategoryId: Record<string, ChannelTree[]> = {}
		channels.forEach(channel => {
			if (!channelsByCategoryId[channel.categoryId]) {
				channelsByCategoryId[channel.categoryId] = []
			}
			channelsByCategoryId[channel.categoryId].push(channel)
		})

		// remove lost threads category if it contains no threads
		if (channelsByCategoryId['0'][0].threads.length === 0) {
			delete channelsByCategoryId['0']
		}

		return channelsByCategoryId
	}

	function processChannels(channels: Channel[]) {
		channelsByCategoryId = getCategoriesFromChannels(channels)
		console.log(channelsByCategoryId);
	}

	$: processChannels(channels);
</script>


{#each Object.values(channelsByCategoryId) as channels}
	<MenuCategory {channels} guildId={selectedGuildId} selectedChannelId={selectedChannelId}/>
{/each}