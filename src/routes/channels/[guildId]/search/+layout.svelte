<script>
	// import { guildId } from "src/stores";
import Search from "./Search.svelte";

	export let data;

	// let authors = [];

	// function selectAuthor(name) {
	// 	// remove existing from: in search
	// 	value = value.replace(/from:([a-zA-Z0-9_]+)/g, '');

	// 	value += ' from:' + name + ' ';
	// 	// trim
	// 	value = value.trim();

	// 	// replace multiple spaces
	// 	value = value.replace(/\s+/g, ' ');

	// 	input.focus();
	// }

	// function valueChanged(value) {
	// 	// if value contains from:, get name after from
	// 	if (value.includes('from:')) {
	// 		let name = value.split('from:')[1].trim();
	// 		authors = Object.values(data.guild.authors)
	// 			.filter((author) => author.name.toLowerCase().includes(name.toLowerCase()))
	// 			.slice(0, 10);
	// 	} else {
	// 		authors = [];
	// 	}
	// }

	// $: valueChanged(value);
</script>

<h1>GUILD SEARCH</h1>

<Search authors={data.guild.authors} all_messages={data.guild.messages} guildId={data.guildId}/>



<div>
	<slot />
</div>


