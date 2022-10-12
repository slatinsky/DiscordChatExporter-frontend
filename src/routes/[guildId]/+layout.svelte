<script>
	// import { page } from '$app/stores';
	// import { channelCategories, guildId, guilds } from '../../stores';

	export let data;
	// console.log('data2', data);

	// let channels = null
	// let categories = null
	// let guild = null

	// $: guild = $guilds[$page.params.guildId]

	// function fetchInfo(guildId) {
	// fetch('/data/guilds.json')
	//     .then(response => response.json())
	//     .then(data => {
	//         guild = data.find(guild => guild.id === guildId)
	//     })
	// fetch('/data/' + guildId + '/channels.json')
	//     .then(response => response.json())
	//     .then(data => {
	//             channels = data
	//             let _categories = {} // array of categories. Key is category id, value is array of channels
	//             for (let channel of channels) {
	//                 if (channel.type === "GuildTextChat") {
	//                     if (channel.categoryId in _categories) {
	//                         _categories[channel.categoryId].push(channel)
	//                     } else {
	//                         _categories[channel.categoryId] = [channel]
	//                     }
	//                 }
	//             }
	//             categories = _categories
	//             console.log(categories)
	//         }
	//     )
	// }

	// $: {
	//     if (typeof window !== 'undefined') { // client only
	//         // fetchInfo( $page.params.guildId)
	//     }
	// }

	let previousChannelCategory = null;
</script>

<div class="columns">
	<div class="channels">
		<div class="guild-name">{data.guilds[data.guildId].name}</div>
		{#each Object.values(data.guild.categories) as category}
			<div>{category.name}</div>
			{#each category.channelIds as channel}
				<div class="channel">
					<a href="/{data.guildId}/{channel.id}">#{channel.name}</a>
				</div>
			{/each}
		{/each}
	</div>
	<div>
		<slot />
	</div>
</div>

<style>
	.channel {
		margin: 5px 15px;
	}

	.channel:hover {
		background-color: #42474d;
	}

	.channels {
		display: flex;
		flex-direction: column;
		margin: 10px 15px;
		overflow-y: auto;
	}

	.columns {
		display: grid;
		grid-template-columns: 250px auto;
		flex-direction: row;
		background-color: #2f3136;
		height: 100vh;
	}

	.guild-name {
		font-size: 20px;
		font-weight: 600;
	}

	.category-name {
		font-size: 16px;
		font-weight: 600;
		margin: 15px 0 0px 0;
	}
</style>
