import type { Embed, Message } from "../../js/interfaces";

const REQUIRED_POLL_FIELDS = [
	"poll_question_text",
	"victor_answer_votes",
	"total_votes",
	"victor_answer_id",
	"victor_answer_text",
	"victor_answer_emoji_name",
] as const;

export interface MessagePollAnswer {
	key: string;
	text: string;
	emojiName: string | null;
	votes: number;
	percent: number;
	percentageLabel: number | null;
}

export interface ParsedMessagePoll {
	question: string;
	totalVotes: number;
	answer: MessagePollAnswer;
}

export function isRenderablePollEmbed(embed: Embed | null | undefined): embed is Embed {
	if (!embed?.fields?.length) {
		return false;
	}

	const fieldNames = new Set(embed.fields.map((field) => field.name));
	return REQUIRED_POLL_FIELDS.every((fieldName) => fieldNames.has(fieldName));
}

export function getRenderablePollEmbed(message: Message): Embed | null {
	return message.embeds?.find((embed) => isRenderablePollEmbed(embed)) ?? null;
}

export function buildPoll(message: Message): ParsedMessagePoll | null {
	const pollEmbed = getRenderablePollEmbed(message);
	if (!pollEmbed) {
		return null;
	}

	const fields = new Map(pollEmbed.fields.map((field) => [field.name, field.value]));
	const totalVotes = Number(fields.get("total_votes"));
	const winnerVotes = Number(fields.get("victor_answer_votes"));
	const winnerId = fields.get("victor_answer_id") ?? "";

	if (isNaN(totalVotes) || isNaN(winnerVotes) || winnerId === "") {
		return null;
	}

	const percent = totalVotes > 0 ? (winnerVotes / totalVotes) * 100 : 0;
	const percentageLabel = totalVotes > 0 ? Math.max(winnerVotes > 0 ? 1 : 0, Math.round(percent)) : null;

	return {
		question: fields.get("poll_question_text") || "Poll",
		totalVotes,
		answer: {
			key: winnerId,
			text: fields.get("victor_answer_text") ?? "",
			emojiName: fields.get("victor_answer_emoji_name") || null,
			votes: winnerVotes,
			percent,
			percentageLabel,
		},
	};
}