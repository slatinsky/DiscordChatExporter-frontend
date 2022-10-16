<script>
	import Search from './Search.svelte';
	export let data;
</script>

<Search
	authors={data.guild.authors}
	all_messages={data.guild.messages}
	guild={data.guild}
	guildId={data.guildId}
/>

<div>
	<slot />
</div>
