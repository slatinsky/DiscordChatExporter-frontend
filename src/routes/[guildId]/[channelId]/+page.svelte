<script>
    // import Counter from './Counter.svelte';
    // import welcome from '$lib/images/svelte-welcome.webp';
    // import welcome_fallback from '$lib/images/svelte-welcome.png';

    // interface Message {
    // 	id: string;
    // 	type: string;
    // 	timestamp: string;
    // 	timestampEdited: string;
    // 	callEndedTimestamp: string;
    // 	isPinned: boolean;
    // 	content: string;
    // }

    // interface Author {
    // 	id: string;
    // 	name: string;
    // 	discriminator: string;
    // 	nickname: string;
    // 	color: string;
    // 	isBot: boolean;
    // 	avatarUrl: string;
    // }

    // interface Attachment {
    // 	id: string;
    // 	filename: string;
    // 	url: string;
    // 	proxyUrl: string;
    // 	size: number;
    // 	height: number;
    // 	width: number;
    // }

    // interface Embed {
    // 	title: string;
    // 	description: string;
    // 	url: string;
    // 	timestamp: string;
    // 	color: number;
    // 	footer: {
    // 		text: string;
    // 		iconUrl: string;
    // 		proxyIconUrl: string;
    // 	};
    // 	image: {
    // 		url: string;
    // 		proxyUrl: string;
    // 		height: number;
    // 		width: number;
    // 	};
    // 	thumbnail: {
    // 		url: string;
    // 		proxyUrl: string;
    // 		height: number;
    // 		width: number;
    // 	};
    // 	video: {
    // 		url: string;
    // 		height: number;
    // 		width: number;
    // 	};
    // 	provider: {
    // 		name: string;
    // 		url: string;
    // 	};
    // }

    // interface Sticker {
    // 	id: string;
    // 	name: string;
    // 	description: string;
    // 	formatType: number;
    // 	tags: string;
    // 	asset: string;
    // 	packId: string;
    // 	packName: string;
    // 	sortValue: number;
    // 	previewAsset: string;
    // }

    // interface Reaction {
    // 	emoji: {
    // 		id: string;
    // 		name: string;
    // 		isAnimated: boolean;
    // 		imageUrl: string;
    // 	};
    // 	count: number;
    // }

    // interface Mention {
    // 	id: string;
    // 	name: string;
    // 	discriminator: string;
    // 	nickname: string;
    // 	color: string;
    // 	isBot: boolean;
    // 	avatarUrl: string;
    // }

    // interface Channel {
    // 	id: string;
    // 	type: string;
    // 	categoryId: string;
    // 	category: string;
    // 	name: string;
    // 	topic: string;
    // }

    // interface Guild {
    // 	id: string;
    // 	name: string;
    // 	iconUrl: string;
    // }

    // interface DateRange {
    // 	after: string;
    // 	before: string;
    // }

    // interface ApiResponse {
    // 	guild: Guild;
    // 	channel: Channel;
    // 	dateRange: DateRange;
    // 	messages: Message[];
    // }


    // let json: ApiResponse;

    import axios from 'axios';
    import Preamble from "../../../components/Preamble.svelte";
    import Message from "../../../components/Message.svelte";
    import Postamble from "../../../components/Postamble.svelte";




    import { page } from '$app/stores';

    function preprocessMessages(json) {
        let references_to_find = {};
        for (const message of json.messages) {
            if (message.reference) {
                references_to_find[message.reference.messageId] = message;
            }
        }

        for (const message of json.messages) {
            if (message.id in references_to_find) {
                references_to_find[message.id].referencedMessage = message;
            }
        }
        return json
    }

    let title = "JSON READER";
    let json = null

    if (typeof window !== 'undefined') { // client only
        // load external json file "in/Hypixel New Year Cakes - Cake Player - cake-memes [762886404169793568].json" using axios
        axios
            .get('/in/' + $page.params.id + '.json')
            .then(function (response) {
                // handle success
                console.log(response);

                json = preprocessMessages(response.data);
                title = "#" + json.channel.name + " | " + json.channel.category + " | " + json.guild.name;
            });
    }


</script>

<svelte:head>
    <title>{title}</title>
    <meta name="description" content="Svelte demo app"/>
</svelte:head>

<section>
    {#if json}
        <Preamble id={json.guild.id} name={json.guild.name} iconUrl={json.guild.iconUrl} channelCategory={json.channel.category} channelName={json.channel.name}/>

        <div class="chatlog">
            <div class=chatlog__message-group>
                {#each json.messages as message}
                    <Message message={message}/>
                {/each}
            </div>
        </div>

        <Postamble messageCount="{json.messages.length}"/>
<!--        <pre>{JSON.stringify(json, null, 2)}</pre>-->
    {:else}
        <p>loading...</p>
    {/if}
</section>

<style>

</style>



