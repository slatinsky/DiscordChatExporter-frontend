<script>
    import moment from 'moment';

	export let data;

	let updateChannels = [];
	let updateThreads = [];
	let newThreads = [];
	let commandsUpdate = '';
	let commandsUpdateT = '';
	let commandsThreads = '';
    let commandsUpdateLength = 3;
    let commandsUpdateTLength = 3;
    let commandsThreadsLength = 3;
	let token = 'TOKEN_HERE';
	let customArguments = '';
    let explainCommands = true;
    let exportHtml = false;

    function cleanTimestamp(timestamp) {
        return moment(timestamp).utcOffset(0).add(1, 'seconds').format()  // add one second, so the last message won't be included in the next backup
    }

	function generateCommands(_, __, ___, ____, _____) {
		commandsUpdate = '';
		for (let i = 0; i < updateChannels.length; i++) {
			let channel = updateChannels[i];
            let channelId = BigInt(channel.channelId);
            if (explainCommands)
                commandsUpdate += `# ${channel.channel.name} (${channel.channel.category})\n`;
            if (exportHtml) {
			    commandsUpdate += `DiscordChatExporter.Cli export --token ${token} --media --reuse-media --format HtmlDark --after "${cleanTimestamp(channel.newestMessage.timestamp)}" --channel ${channelId} ${customArguments}\n`;
                commandsUpdate += `DiscordChatExporter.Cli export --token ${token} --format Json --after "${cleanTimestamp(channel.newestMessage.timestamp)}" --channel ${channelId} ${customArguments}\n`;
            }
            else {
                commandsUpdate += `DiscordChatExporter.Cli export --token ${token} --media --reuse-media --format Json --after "${cleanTimestamp(channel.newestMessage.timestamp)}" --channel ${channelId} ${customArguments}\n`;
            }
		}
		// remove last new line
		commandsUpdate = commandsUpdate.slice(0, -1);

		commandsUpdateT = '';
		for (let i = 0; i < updateThreads.length; i++) {
			let channel = updateThreads[i];
            let channelId = BigInt(channel.channelId);
            if (explainCommands)
                commandsUpdateT += `# ${channel.channel.name} (${channel.channel.category})\n`;
            if (exportHtml) {
                commandsUpdateT += `DiscordChatExporter.Cli export --token ${token} --media --reuse-media --format HtmlDark --after "${cleanTimestamp(channel.newestMessage.timestamp)}" --channel ${channelId} ${customArguments}\n`;
                commandsUpdateT += `DiscordChatExporter.Cli export --token ${token} --format Json --after "${cleanTimestamp(channel.newestMessage.timestamp)}" --channel ${channelId} ${customArguments}\n`;
            }
            else {
                commandsUpdateT += `DiscordChatExporter.Cli export --token ${token} --media --reuse-media --format Json --after "${cleanTimestamp(channel.newestMessage.timestamp)}" --channel ${channelId} ${customArguments}\n`;
            }
		}
		// remove last new line
		commandsUpdateT = commandsUpdateT.slice(0, -1);

		commandsThreads = '';
        let previousChannelExplain = '';
		for (let i = 0; i < newThreads.length; i++) {
			let channel = newThreads[i];
            let channelId = BigInt(channel.channelId);
            if (explainCommands) {
                let channelExplain = `# ${channel.channel.name} (${channel.channel.category})\n`
                if (channelExplain != previousChannelExplain) {
                    commandsThreads += channelExplain;
                    previousChannelExplain = channelExplain;
                }
            }
            if (exportHtml) {
                commandsThreads += `DiscordChatExporter.Cli export --token ${token} --media --reuse-media --format HtmlDark --channel ${channelId} ${customArguments}\n`;
                commandsThreads += `DiscordChatExporter.Cli export --token ${token} --format Json --channel ${channelId} ${customArguments}\n`;
            }
            else {
                commandsThreads += `DiscordChatExporter.Cli export --token ${token} --media --reuse-media --format Json --channel ${channelId} ${customArguments}\n`;
            }
		}

        // remove last new line
        commandsThreads = commandsThreads.slice(0, -1);
        commandsUpdateLength = Math.min(commandsUpdate.split('\n').length + 1, 20);
        commandsUpdateTLength = Math.min(commandsUpdateT.split('\n').length + 1, 20);
        commandsThreadsLength = Math.min(commandsThreads.split('\n').length + 1, 20);
	}

	function processData(data) {
		console.log('data', data);
		if (!data.guild) {
			return;
		}
		updateChannels = [];
		for (const [channelId, channel] of Object.entries(data.guild.messages)) {
			// get largest message id
			let largestMessageId = Object.keys(channel).reduce((a, b) => {
				let _a = BigInt(a);
				let _b = BigInt(b);
				return _a > _b ? _a : _b;
			});

			// get timestamp of largest message id
			let newestMessage = channel[largestMessageId.toString().padStart(24, '0')];

            let fullChannel = data.guild.channels[channelId];

            if (fullChannel.type === "GuildTextChat") {
                updateChannels.push({
                    channelId: channelId,
                    channel: fullChannel,
                    newestMessage: newestMessage
                });
            }
            else {
                updateThreads.push({
                    channelId: channelId,
                    channel: fullChannel,
                    newestMessage: newestMessage
                });
            }

			// find new threads
			for (const [messageId, message] of Object.entries(channel)) {
				if (message.type === 'ThreadCreated') {
					// if thread does not already exist
					if (!data.guild.messages[message.reference.channelId]) {
						newThreads.push({
							channelId: message.reference.channelId,
							messageId: messageId,
							message: message,
                            channel: data.guild.channels[channelId]
						});
					}
				}
			}
		}
		updateChannels = updateChannels;
		generateCommands(updateChannels);
	}

	$: generateCommands(updateChannels, token, explainCommands, exportHtml, customArguments);
	$: processData(data);
</script>

<div class="container">
	<h1>Backup helper</h1>
    <h3>Generate commands to extend your server backup automatically.</h3>
    <p>This tool will generate commands to extend your server backup without downloading duplicate messages. Just run these commands, move your new backup to '/static/input' and run START_VIEWER.bat again to apply changes. This tool WON'T FIND NEW CHANNELS</p>

	<div class="form">
        <div class="form-input">
            <label for="token"> Token </label>
            <input type="text" id="token" bind:value={token} />
        </div>

        <div class="form-input">
            <label for="custom"> Custom arguments </label>
            <input type="text" id="custom" bind:value={customArguments} />
        </div>
        <div>
            <!-- checkbox -->
            <input type="checkbox" id="threads" bind:checked={explainCommands} />
            <label for="threads"> Explain commands </label>
        </div>
        <div>
            <!-- checkbox -->
            <input type="checkbox" id="html" bind:checked={exportHtml} />
            <label for="html"> Export HTML (not recomended)</label>
        </div>
    </div>

    <h2>Extend existing channels:</h2>
    <p>These commands will extend your export of existing channels:</p>
    {#key commandsUpdateLength}
        <textarea bind:value={commandsUpdate} rows={commandsUpdateLength} />
    {/key}

    <h2>Extend existing threads:</h2>
    <p>These commands will extend your export of existing threads:</p>
    {#key commandsUpdateTLength}
        <textarea bind:value={commandsUpdateT} rows={commandsUpdateTLength} />
    {/key}

	<h2>Download missing threads:</h2>
    <p>These commands will download missing threads. These threads were found in the backup, but weren't exported:</p>
    {#key commandsThreadsLength}
        {#if newThreads.length > 0}
            <textarea bind:value={commandsThreads} rows={commandsThreadsLength} />
        {:else}
            <p>Great! All threads are archived</p>
        {/if}
    {/key}
</div>

<style>
	textarea {
		width: 100%;
	}

    .container {
        padding: 1rem;
    }

    .form {
        display: flex;
        flex-direction: column;
        gap: .5rem;
    }

    .form > .form-input {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: .5rem;
    }

    .form-input input {
        max-width: 600px;
        width: 100%;
    }
</style>
