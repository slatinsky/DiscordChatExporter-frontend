<script lang="ts">
	// this component will always show just the winning answer, because there is no data about other answers in the message embeds.
	// this component is rendering a poll closed message, but we are rendering it as if the pool was created, so we can show more info to the user

	import type { Message } from "../../js/interfaces";
	import { dceToTwemoji } from "../../js/emojis/dceToTwemoji";
	import { twemojiToFilename } from "../../js/emojis/twemojiToFilename";
	import Icon from "../icons/Icon.svelte";
	import { buildPoll } from "./messagePollData";

	export let message: Message;

	const unicodeToTwemoji = dceToTwemoji as Record<string, string>;
	const twemojiFilenames = twemojiToFilename as Record<string, string>;

	function formatVoteCount(votes: number): string {
		return `${votes.toLocaleString()} ${votes === 1 ? "vote" : "votes"}`;
	}

	function getTwemojiFilename(emojiName: string | null): string | null {
		if (!emojiName) {
			return null;
		}

		const twemojiName = unicodeToTwemoji[emojiName];
		if (!twemojiName) {
			return null;
		}

		return twemojiFilenames[twemojiName] ?? null;
	}

	$: poll = buildPoll(message);
	$: answerEmojiTwemojiFilename = getTwemojiFilename(poll?.answer.emojiName ?? null);
</script>

{#if poll}
	<div class="poll-card">
		<div class="poll-question">{poll.question}</div>

		<div class="poll-options">
			<!-- (always is a winner with only one answer) -->
			<div class="poll-option is-winner" style={`--poll-fill-width: ${poll.answer.percent.toFixed(2)}%;`}>
				<div class="poll-option-fill"></div>

				<div class="poll-option-content">
					<div class="poll-option-main">
						{#if poll.answer.emojiName}
							{#if answerEmojiTwemojiFilename}
								<img
									src={`/twemoji-svg/${answerEmojiTwemojiFilename}.svg`}
									alt={poll.answer.emojiName}
									title={poll.answer.emojiName}
									class="poll-emoji-image"
									width="28"
									height="28"
								/>
							{:else}
								<span class="poll-emoji-text">{poll.answer.emojiName}</span>
							{/if}
						{/if}

						{#if poll.answer.text !== ""}
							<div class="poll-option-label">{poll.answer.text}</div>
						{:else if !poll.answer.emojiName}
							<div class="poll-option-label">Untitled answer</div>
						{/if}
					</div>

					<div class="poll-option-stats">
						<span class="poll-option-votes">{formatVoteCount(poll.answer.votes)}</span>
						{#if poll.answer.percentageLabel !== null}
							<span class="poll-option-percent">{poll.answer.percentageLabel}%</span>
						{/if}
						<span class="poll-option-winner-badge" aria-label="Winning answer">
							<Icon name="other/verified" width={24} />
						</span>
					</div>
				</div>
			</div>
		</div>

		<div class="poll-footer">
			<span class="poll-footer-votes">{formatVoteCount(poll.totalVotes)}</span>
			<span class="poll-footer-separator">•</span>
			<span class="poll-footer-closed">Poll closed</span>
		</div>
	</div>
{/if}

<style>
	.poll-card {
		width: min(100%, 680px);
		padding: 16px;
		border-radius: 12px;
		border: 1px solid #3a3d44;
		background:
			linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0)) padding-box,
			#24262d;
		color: #f2f3f5;
	}

	.poll-question {
		margin-bottom: 16px;
		font-weight: 500;
		line-height: 1.25;
	}

	.poll-options {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.poll-option {
		position: relative;
		overflow: hidden;
		border-radius: 10px;
		border: 1px solid transparent;
		background-color: #2b2d31;
	}

	.poll-option.is-winner {
		border-color: #23a559;
	}

	.poll-option-fill {
		position: absolute;
		inset: 0 auto 0 0;
		width: var(--poll-fill-width);
		background-color: rgba(255, 255, 255, 0.08);
	}

	.poll-option.is-winner .poll-option-fill {
		background-color: rgba(35, 165, 89, 0.22);
	}

	.poll-option-content {
		position: relative;
		z-index: 1;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
		min-height: 50px;
		padding: 0 18px;
	}

	.poll-option-main {
		display: flex;
		align-items: center;
		gap: 12px;
		min-width: 0;
		font-size: 1rem;
		font-weight: 600;
	}

	.poll-option-label {
		min-width: 0;
		font-size: 14px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.poll-emoji-image {
		width: 28px;
		height: 28px;
		flex-shrink: 0;
	}

	.poll-emoji-text {
		display: inline-grid;
		place-items: center;
		width: 28px;
		height: 28px;
		flex-shrink: 0;
		/* font-size: 1.55rem; */
		line-height: 1;
	}

	.poll-emoji-image {
		display: block;
		object-fit: contain;
	}

	.poll-option-stats {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-shrink: 0;
		font-weight: 700;
	}

	.poll-option-votes {
		color: #ffffff;
		font-size: 12px;
	}

	.poll-option-percent {
		min-width: 3ch;
		text-align: right;
		/* font-size: 1.05rem; */
	}

	.poll-option-winner-badge {
		display: inline-grid;
		place-items: center;
		width: 32px;
		height: 32px;
		border-radius: 999px;
		background-color: #23a559;
		color: #ffffff;
		font-weight: 800;
	}

	.poll-footer {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-top: 14px;
		color: #b5bac1;
		font-weight: 500;
	}

	.poll-footer-votes {
		color: #ffffff;
		font-size: 14px;
	}

	.poll-footer-separator {
		color: #7f848e;
		font-size: 14px;
	}

	.poll-footer-closed {
		color: #96979e;
		font-size: 14px;
	}
</style>
