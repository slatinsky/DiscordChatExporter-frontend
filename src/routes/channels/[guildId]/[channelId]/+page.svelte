<script>
	import { onDestroy, onMount } from "svelte";
	import { channelScrollPosition } from "../../../settingsStore";
	import Messages from "./Messages.svelte";
    export let data;

    /** --- start JUMP TO HASH */
    function searchForMessageId(messageId, recursionDepth = 0) {
        if (messageId === 0) {
            console.log('messageId is 0, aborting');
            return;
        }

		if (recursionDepth > 300) {
			console.error('recursion depth exceeded');
			return;
		}
		let elMessage = document.getElementById(messageId.toString().padStart(24, '0'));
		if (elMessage) {
            elMessage.scrollIntoView();

            // wait for load
			setTimeout(() => {
                elMessage = document.getElementById(messageId.toString().padStart(24, '0'));  // message element might have been rerendered by svelte, reselect it
				elMessage.scrollIntoView({block: 'start'});
			}, 0);
			console.log('found message', messageId, "- recursion depth", recursionDepth);
			return;
		}

		let visibleMessageIds = []
		for (const mg of document.querySelectorAll('.message-group')) {
			visibleMessageIds.push([BigInt(mg.dataset.mgfirst), BigInt(mg.dataset.mglast)]);
		}

		// console.log('visibleMessageIds', visibleMessageIds);

		let bestRange = null;
		let bestError = BigInt("999999999999999999999999999999")

		for (let i = 0; i < visibleMessageIds.length; i++) {
			let first = BigInt(visibleMessageIds[i][0]);
			let last = BigInt(visibleMessageIds[i][1]);
			let currentError = last - first;  // we want to find the smallest message group that contains the message we want to scroll to
			if (messageId >= first && messageId <= last && currentError < bestError) {
				bestError = currentError;
				bestRange = [first,last];
				// console.log('found message in visible range', messageId, first, last, bestError);
			}
		}

		if (bestRange) {
			let first = bestRange[0];
			let last = bestRange[1];
			let el = document.querySelector('.message-group[data-mgfirst="' + first.toString().padStart(24, '0') + '"][data-mglast="' + last.toString().padStart(24, '0') + '"]')
				if (el) {
					el.scrollIntoView();
					setTimeout(() => {
						searchForMessageId(messageId, recursionDepth+1)
					}, recursionDepth + 1);
				}
				else {
					console.log('could not find message group with id', closestMessageId);
				}
				return;
		} else {
			console.log('message not found', messageId, "trying again");
			setTimeout(() => {
				searchForMessageId(messageId, recursionDepth+10)
			}, (recursionDepth + 1) * 100);
		}
	}
    function hashChanged() {
        try {
            searchForMessageId(BigInt(window.location.hash.replace('#', '')));
        } catch (e) {
            console.error(e);
            console.warn("Url hash does not contain a valid message id");
        }
	}
    onMount(() => {
        window.addEventListener("hashchange", hashChanged);
	});
    onDestroy(() => {
        window.removeEventListener("hashchange", hashChanged);
    });
    $: hashChanged(data.channelId);
    /** --- end JUMP TO HASH */


    /** --- start SCROLL TO CHANNEL BOTTOM ON LOAD */
    let mainChatlog
    function scrollToBottom(_, recursion_count = 0) {
        // scroll to bottom only if no hash (message id) is set to be scrolled to
        if (window.location.hash !== '')
            return

        if ($channelScrollPosition === "bottom") {
            if (recursion_count === 0) {
                // console.log('scrollToBottom: recursion limit reached');
                return;
            }
            if (mainChatlog) {
                mainChatlog.scrollTop = mainChatlog.scrollHeight;
            }
            else {
                console.warn('no mainChatlog');
            }
            setTimeout(() => {
                scrollToBottom(_, recursion_count - 1);
            }, 10);
        }
    }
    $: scrollToBottom(data.channelId, 50);
    /** --- end SCROLL TO CHANNEL BOTTOM ON LOAD */
</script>

<svelte:head>
    <title>{data.guild.channels[data.channelId]?.name ?? "Unknown channel"} | DiscordChatExporter frontend</title>
    <meta name="description" content="Svelte demo app"/>
</svelte:head>

{#if data.messages}
<section>
    <div class="chatlog" id="main-chatlog" bind:this={mainChatlog}>
        <div class=chatlog__message-group>
            <div id="top" />
            {#key data.channelId}
                {#if data.mainChannelMessage}
                <div class="back-main-channel">
                    <a href="/channels/{data.guildId}/{data.mainChannelMessage.channelId}/#{data.mainChannelMessage.id}">← BACK TO MAIN CHANNEL</a>
                </div>
                {/if}
            {/key}
            {#if mainChatlog}
                <Messages messages={Object.values(data.messages)} guild={data.guild} guildId={data.guildId} channelId={data.channelId} rootId={mainChatlog}/>
            {/if}
            <div id="bottom" />
        </div>
    </div>
</section>
{:else}
<div class="error">
    <p>Channel ID {BigInt(data.channelId)} was not exported</p>
</div>
{/if}

<style>
    .error {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        text-align: center;
        padding: 2rem;
        background-color: var(--panel-messages-bg);
    }
 section {
     background-color: var(--panel-messages-bg);
     /*height: 100vh;*/
 }

 .chatlog {
     overflow-y: auto;
     max-height: calc(100vh - 88px);
     margin-right: 5px;
 }

 .back-main-channel {
     padding: 10px 25px;
     margin-bottom: 5px;
 }
</style>



