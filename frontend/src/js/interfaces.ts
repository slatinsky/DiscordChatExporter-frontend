export interface Guild {
	_id: string;
	name: string;
	icon: Asset;
}

export interface Asset {
	_id: string;
	originalPath: string;
	localPath: string;
	remotePath: string;
	path: string;
	extension: string;
	type: "image" | "video" | "audio" | "unknown";
	width: number;
	height: number;
	sizeBytes: number;
	filenameWithHash: string;
	filenameWithoutHash: string;
	colorDominant: null | [number, number, number];
	colorPalette: null | [number, number, number][];
}

export interface Channel {
	_id: string;
	type: "GuildTextChat" | "DirectTextChat" | "GuildVoiceChat" | "DirectGroupTextChat" | "GuildCategory" | "GuildNews" | "GuildNewsThread" | "GuildPublicThread" | "GuildPrivateThread" | "GuildStageVoice" | "GuildDirectory" | "GuildForum";
	categoryId: string;
	category: string;
	name: string;
	topic: string | null;
	guildId: string;
}

export interface Author {
	name: string;
	discriminator: string;
	nickname: string;
	color: string;
	isBot: boolean;
	avatar: Asset;
	_id: string;
}

export interface Sticker {
	name: string;
	format: "Png" | "Apng" | "Lottie";
	_id: string;
	source: Asset;
}

export interface Emoji {
	id: string;
	name: string;
	isAnimated: boolean;
	image: Asset;
	source: "default" | "custom";
	guildId: string | null;
}

export interface Reaction {
	emoji: Emoji;
	count: number;
}

export interface Mention {
	name: string;
	discriminator: string;
	nickname: string;
	isBot: boolean;
	_id: string;
}

export interface Embed {
	title: string;
	url: string;
	timestamp: string | null;
	description: string;
	thumbnail: Asset;
	images: Asset[];
	image?: Asset;
	fields: {
		name: string;
		value: string;
		isInline: boolean;
	}[];
	color?: string;
	author?: {
		name: string;
		url: string;
		icon?: Asset;
	};
	footer?: {
		text: string;
		icon: Asset;
	};
}

export interface Message {
	_id: string;
	type: "Reply";
	timestamp: string;
	timestampEdited: string | null;
	callEndedTimestamp: string | null;
	isPinned: boolean;
	content: {
		timestamp: string;
		content: string;
	}[];
	author: Author;
	stickers: Sticker[] | null;
	reactions: Emoji[] | null;
	emotes: Reaction[] | null;   // emotes in the message
	mentions: Mention[] | null;
	attachments: Asset[] | null;
	embeds: NewType[] | null;
	reference: {
		messageId: string;
		channelId: string;
		guildId: string;
	} | null;
	guildId: string;
	channelId: string;
	channelName: string;
}

export interface MessageIdLoad {
	_id: string;
	loaded: boolean;
}