<script lang="ts">
    // this file handles app layout
    import {throttle} from 'lodash-es';

    import Channels from "./lib/Channels.svelte";
    import Guilds from "./lib/Guilds.svelte";
    import HeaderMain from "./lib/HeaderMain.svelte";
    import HeaderThread from "./lib/HeaderThread.svelte";
    import SearchResults from "./lib/SearchResults.svelte";
    import Channel from "./lib/Channel.svelte";
    import Thread from "./lib/Thread.svelte";
    import Settings from "./lib/Settings.svelte";
    import ContextMenu from "./lib/components/menu/ContextMenu.svelte";
    import { onDestroy, onMount } from "svelte";
    import { mobilesidepanelshown } from "./js/stores/layoutStore";
    import { searchshown } from "./js/stores/layoutStore";
    import { threadshown } from "./js/stores/layoutStore";
    import { settingsshown } from "./js/stores/layoutStore";
    import { debuglayout } from "./js/stores/layoutStore";
    import { position } from "./js/stores/menuStore";

    let mobile = false
    let windowWidth = window.innerWidth

    function toggleThread() {
      if (!$threadshown && $searchshown) {
        // search and thread can't be shown at the same time
        $searchshown = false
      }
      if (!$threadshown && $mobilesidepanelshown) {
        // hide mobile side panel on thread show
        $mobilesidepanelshown = false
      }
      $threadshown = !$threadshown
    }

    function toggleSearch() {
      if (!$searchshown && $threadshown) {
        // search and thread can't be shown at the same time
        $threadshown = false
      }
      $searchshown = !$searchshown
    }

    function toggleSidePanel() {
      if ($mobilesidepanelshown && $searchshown) {
        // if already shown, just hide search
        $searchshown = false
        return
      }
      if (!$mobilesidepanelshown && $searchshown) {
        // search cannot be shown when side panel is hidden
        $searchshown = false
      }
      $mobilesidepanelshown = !$mobilesidepanelshown
    }

    function toggleSettings() {
      $settingsshown = !$settingsshown
    }


    function resize() {
      windowWidth = window.innerWidth
      if (windowWidth < 800) {
        mobile = true
      } else {
        mobile = false
      }
    }


    onMount(() => {
      window.addEventListener('resize', resize)
      resize()
    })
    onDestroy(() => {
      window.removeEventListener('resize', resize)
    })






    /* capture mouse position for right click context menu */
    function handleMousemove(event) {
      $position = { x: event.clientX, y: event.clientY };
    }
    const handleThrottledMousemove = throttle(handleMousemove, 100, { leading: false, trailing: true });
</script>


<div class:debuglayout={$debuglayout}>
  <main
    class:mobile class:desktop={!mobile}
    class:searchshown={$searchshown} class:searchhidden={!$searchshown}
    class:mobilesidepanelshown={$mobilesidepanelshown} class:mobilesidepanelhidden={!$mobilesidepanelshown}
    class:threadshown={$threadshown} class:threadhidden={!$threadshown}
    on:mousemove={handleThrottledMousemove}
    >
      <div class="guilds"><Guilds /></div>
      <div class="channels"><Channels /></div>
      <div class="header-main"><HeaderMain /></div>
      <div class="channel"><Channel /></div>
      <div class="search-results"><SearchResults /></div>
      <div class="header-thread"><HeaderThread /></div>
      <div class="thread"><Thread /></div>
    </main>
  <div class="settings" class:settingsshown={$settingsshown}><Settings /></div>
  <ContextMenu />
</div>



<div style="position: absolute; bottom: 0; right; 0;z-index: 200">
  <button on:click={() => $debuglayout = !$debuglayout}>$debuglayout {$debuglayout}</button>
  <button on:click={toggleSidePanel}>$mobilesidepanelshown {$mobilesidepanelshown}</button>
  <button on:click={toggleThread}>$threadshown {$threadshown}</button>
  <button on:click={toggleSearch}>$searchshown {$searchshown}</button>
  <button on:click={toggleSettings}>$settingsshown {$settingsshown}</button>
</div>

<style>

  .settings {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: none;
    z-index: 200;
    background-color: #2B2D31;
  }
  .settings.settingsshown {
    display: block;
  }
  

  .guilds {
    grid-area: guilds;
  }
  .channels {
    grid-area: channels;
    background-color: #2B2D31;
  }
  .header-main {
    grid-area: header-main;
    background-color: #313338;
  }
  .channel {
    grid-area: channel;
    overflow: hidden;
    background-color: #313338;
  }
  .search-results {
    grid-area: search-results;
    background-color: #2B2D31;
  }
  .thread {
    grid-area: thread;
    background-color: #313338;
  }

  /* COMMON */
  main {
    display: grid;
    width: 100%;
    height: 100%;
  }

  /* DESKTOP NO SEARCH, NO THREAD */
  main.desktop.searchhidden.threadhidden {
    grid-template-areas:
    "guilds channels header-main"
    "guilds channels        channel";
    grid-template-columns: 70px 236px 1fr;
    grid-template-rows: 48px 1fr;
  }
  main.desktop.searchhidden.threadhidden .search-results {
    display: none;
  }
  main.desktop.searchhidden.threadhidden .thread {
    display: none;
  }
  main.desktop.searchhidden.threadhidden .header-thread {
    display: none;
  }



  /* DESKTOP NO SEARCH, THREAD SHOWN */
  main.desktop.searchhidden.threadshown {
    grid-template-areas:
    "guilds channels header-main header-thread"
    "guilds channels        channel     thread";
    grid-template-columns: 70px 236px 1fr 1fr;
    grid-template-rows: 48px 1fr;
  }
  main.desktop.searchhidden.threadshown .search-results {
    display: none;
  }


  /* DESKTOP WITH SEARCH */
  main.desktop.searchshown.threadhidden,
  main.desktop.searchshown.threadshown {
    grid-template-areas:
    "guilds channels header-main header-main   "
    "guilds channels        channel    search-results";

    grid-template-columns: 70px 236px 1fr 400px;
    grid-template-rows: 48px 1fr;
  }
  main.desktop.searchshown.threadshown .search-results,
  main.desktop.searchshown.threadhidden .search-results {
    display: block;
  }
  main.desktop.searchshown.threadshown .thread,
  main.desktop.searchshown.threadhidden .thread {
    display: none;
  }
  main.desktop.searchshown.threadshown .header-thread,
  main.desktop.searchshown.threadhidden .header-thread {
    display: none;
  }

  /* MOBILE SIDEPANEL, NO THREAD */
  main.mobile.searchhidden.mobilesidepanelshown.threadhidden {
    width: calc(100vw + 70px + min(236px, 100svw - 100px) + 100vw);
    grid-template-areas:
    "guilds channels header-main"
    "guilds channels        channel";
    grid-template-columns: 70px min(236px, 100svw - 100px) 100vw;
    grid-template-rows: 48px 1fr;
  }
  main.mobile.searchhidden.mobilesidepanelshown.threadhidden .search-results {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelshown.threadhidden .thread {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelshown.threadhidden .header-thread {
    display: none;
  }


  /* MOBILE SIDEPANEL, WITH THREAD */
  main.mobile.searchhidden.mobilesidepanelshown.threadshown {
    width: calc(70px + min(236px, 100svw - 100px) + 100vw);
    grid-template-areas:
    "guilds channels header-thread"
    "guilds channels        thread";
    grid-template-columns: 70px min(236px, 100svw - 100px) 100vw;
    grid-template-rows: 48px 1fr;
  }
  main.mobile.searchhidden.mobilesidepanelshown.threadshown .search-results {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelshown.threadshown .channel {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelshown.threadshown .header-main {
    display: none;
  }








   /* MOBILE NO SIDE PANEL, NO THREAD */
  main.mobile.searchhidden.mobilesidepanelhidden.threadhidden {
    width: 100vw;
    grid-template-areas:
    "header-main"
    "channel" !important;
    grid-template-columns: 1fr;
    grid-template-rows: 48px 1fr;
  }
  main.mobile.searchhidden.mobilesidepanelhidden.threadhidden .guilds {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelhidden.threadhidden .channels {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelhidden.threadhidden .search-results {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelhidden.threadhidden .thread {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelhidden.threadhidden .header-thread {
    display: none;
  }

  /* MOBILE NO SIDE PANEL, WITH THREAD */
  main.mobile.searchhidden.mobilesidepanelhidden.threadshown {
    width: 100vw;
    grid-template-areas:
    "header-thread"
    "thread" !important;
    grid-template-columns: 1fr;
    grid-template-rows: 48px 1fr;
  }
  main.mobile.searchhidden.mobilesidepanelhidden.threadshown .guilds {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelhidden.threadshown .header-main {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelhidden.threadshown .channels {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelhidden.threadshown .search-results {
    display: none;
  }
  main.mobile.searchhidden.mobilesidepanelhidden.threadshown .channel {
    display: none;
  }




  /* MOBILE WITH SEARCH */
  main.mobile.searchshown {
    width: 100svw;
    grid-template-areas:
    "header-main   "
    "search-results";

    grid-template-columns: 1fr;
    grid-template-rows: 48px 1fr;
  }
  main.mobile.searchshown .guilds {
    display: none;
  }
  main.mobile.searchshown .header-thread {
    display: none;
  }
  main.mobile.searchshown .channels {
    display: none;
  }
  main.mobile.searchshown .channel {
    display: none;
  }
  main.mobile.searchshown .thread {
    display: none;
  }











  /* DEBUG COLORS */
  .debuglayout {
    width: 100%;
    height: 100%;
  }
  .debuglayout > .settings {
    background-color: rgb(225, 0, 225)
  }
  .debuglayout > main .guilds {
    background-color: rgb(116, 58, 58)
  }
  .debuglayout > main .channels {
    background-color: blue
  }
  .debuglayout > main .header-main {
    background-color: rgb(0, 151, 174)
  }
  .debuglayout > main .channel {
    background-color: rgb(30, 0, 0)
  }
  .debuglayout > main .search-results {
    background-color: lightgreen
  }
  .debuglayout > main .thread {
    background-color: lightblue
  }
  .debuglayout > main .header-thread {
    background-color: rgb(0, 57, 171)
  }

</style>