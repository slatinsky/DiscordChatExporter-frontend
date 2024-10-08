import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
		strictPort: true,
		watch: {
			usePolling: false,
		},
		https: false,
		hmr: {
			clientPort: 21012,
		},
		// host: '0.0.0.0',
		port: 5050,
	},
	build: {
		target: 'ES2022',
		outDir: '../../_temp/frontend',
		emptyOutDir: true, // also necessary
	},
})
