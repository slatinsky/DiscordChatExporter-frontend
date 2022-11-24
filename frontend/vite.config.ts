import { sveltekit } from '@sveltejs/kit/vite';
import type { UserConfig } from 'vite';

const config: UserConfig = {
	plugins: [sveltekit()],
	server: {
		strictPort: true,
		watch: {
			usePolling: true,
		},
		https: false,
		hmr: {
			clientPort: 5050,
		},
		// host: '0.0.0.0',
		port: 5050,
	}
};

export default config;
