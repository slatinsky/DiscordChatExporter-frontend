<script lang="ts">
	import type { Channel } from "src/js/interfaces";
	import MenuChannel from './MenuChannel.svelte';
	import MenuCategory from "src/components/channels/MenuCategory.svelte";


	export let channels: Channel[] = [];
	export let selectedChannelId: string | null = null;
	export let selectedGuildId: string | null = null;

	let channelsByCategoryId: any = {};  // {categoryId: channels}
	let categoryId_msgCount: any = [];   // {categoryId: msgCount}
	let channelsNoCategory: Channel[] = []; // channels without category

	// interface Channel with channels array
	interface ChannelTree extends Channel {
		threads: Channel[]
	}

	function getCategoriesFromChannels(allChannels: Channel[]) {
		let threads: Channel[] = allChannels.filter(channel => channel.type === "GuildPublicThread" || channel.type === "GuildPrivateThread")
		let channels: ChannelTree[] = allChannels.filter(channel => channel.type !== "GuildPublicThread" && channel.type !== "GuildPrivateThread" && channel.categoryId !== null) // Only add to list if channel has a category
		channelsNoCategory = allChannels.filter(channel => channel.categoryId === null) // all channels without category
		// create channel for threads without channel
		channels.push({
			_id: '0',
			type: 'GuildTextChat',
			categoryId: '0',
			category: 'Lost threads / forums',
			name: 'Lost threads / forums',
			topic: null,
			threads: [],
			msg_count: 0,
			guildId: selectedGuildId as string,
		})
		console.log(channelsNoCategory);

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

			// increase msg count
			channel.msg_count += thread.msg_count
		})

		// sort threads by message count
		channels.forEach(channel => {
			channel.threads.sort((a, b) => b.msg_count - a.msg_count)
		})


		// categorise channels by category
		let channelsByCategoryId: Record<string, ChannelTree[]> = {}
		channels.forEach(channel => {
			if (!channelsByCategoryId[channel.categoryId]) {
				channelsByCategoryId[channel.categoryId] = []
			}
			channelsByCategoryId[channel.categoryId].push(channel)
		})

		// sort channels by message count in each category
		Object.values(channelsByCategoryId).forEach((channels: ChannelTree[]) => {
			channels.sort((a, b) => b.msg_count - a.msg_count)
		})

		// remove lost threads category if it contains no threads
		if (channelsByCategoryId['0'][0].threads.length === 0) {
			delete channelsByCategoryId['0']
		}

		return channelsByCategoryId
	}

	function processChannels(channels: Channel[]) {
		channelsByCategoryId = getCategoriesFromChannels(channels)

		// count message count in each category
		categoryId_msgCount = Object.values(channelsByCategoryId).map((channels: ChannelTree[]) => {
			return {
				categoryId: channels[0].categoryId,
				msg_count: channels.reduce((acc, channel) => acc + channel.msg_count, 0)
			}
		})

		// sort category ids by message count
		categoryId_msgCount.sort((a, b) => b.msg_count - a.msg_count)
	}

	$: processChannels(channels);
</script>

<!-- Print categories from the largest msg_count to the smallest msg_count | Added: After listing channels with no category. They always comes first --> 
{#if channelsNoCategory.length > 0}
	{#each channelsNoCategory as channel}
	<div class="channel">
		<MenuChannel
			name={channel.name}
			id={channel._id}
			guildId={channel.guildId}
			isSelected={selectedChannelId == channel._id}
			threadCount={channel?.threads?.length ?? 0}
			type={channel.type}
		/>
	</div>
	{/each}
{/if}
{#each categoryId_msgCount as obj}
	{@const channels = channelsByCategoryId[obj.categoryId]}
	<MenuCategory {channels} guildId={selectedGuildId} selectedChannelId={selectedChannelId}/>
{/each}