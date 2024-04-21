<script lang="ts">
    // this file handles app layout
    import {throttle} from 'lodash-es';

    import Channels from "./lib/Channels.svelte";
    import Guilds from "./lib/Guilds.svelte";
    import HeaderMain from "./lib/HeaderMain.svelte";
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
      // if (!$threadshown && $mobilesidepanelshown) {
      //   // hide mobile side panel on thread show
      //   $mobilesidepanelshown = false
      // }
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
      // if ($mobilesidepanelshown && $searchshown) {
      //   // if already shown, just hide search
      //   $searchshown = false
      //   return
      // }
      // if (!$mobilesidepanelshown && $searchshown) {
      //   // search cannot be shown when side panel is hidden
      //   $searchshown = false
      // }
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


<div class:debuglayout={$debuglayout} style="width: 100%;height: 100%;">
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
      <div class="thread"><Thread /></div>
    </main>
  <div class="settings" class:settingsshown={$settingsshown}><Settings /></div>
  <ContextMenu />
</div>



<div style="position: absolute; bottom: 5px; left: 5px;z-index: 200">
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



  /* DESKTOP NO SEARCH, THREAD SHOWN */
  main.desktop.searchhidden.threadshown {
    grid-template-areas:
    "guilds channels header-main    thread"
    "guilds channels        channel thread";
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
    "guilds channels header-main    header-main   "
    "guilds channels        channel search-results";

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





  /* MOBILE */

  /* hide hidden elements */
  main.mobile.threadhidden .thread,
  main.mobile.searchhidden .search-results {
    display: none;
  }


  /* animate side panel */
  main.mobile .header-main,
  main.mobile .channel,
  main.mobile .thread {
    transition: left 0.2s;
  }


  /* main mobile layout, other elements are positioned absolutely */
  main.mobile {
    width: calc(100vw + 70px + min(236px, 100svw - 100px));
    grid-template-areas:
    "guilds channels";
    grid-template-columns: 70px min(236px, 100svw - 100px);
    grid-template-rows: 1fr;
  }

  /* absolute positioning for mobile elements */
  main.mobile .header-main {
    position: absolute;
    width: 100%;
    height: 48px;
    top: 0;
    left: 0;
  }
  main.mobile .channel {
    position: absolute;
    width: 100%;
    height: calc(100% - 48px);
    top: 48px;
    left: 0;
  }
  main.mobile .thread {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
  }
  main.mobile .search-results {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
  }

  /* side panel shown */
  main.mobile.mobilesidepanelshown .channel,
  main.mobile.mobilesidepanelshown .header-main,
  main.mobile.mobilesidepanelshown .thread {
    left: calc(70px + min(236px, 100svw - 100px));
  }











  /* DEBUG COLORS */
  .debuglayout > .settings {
    background-color: rgb(225, 0, 225);
    border: 1px solid #ff72ff;
  }
  .debuglayout > main .guilds {
    background-color: rgb(116, 58, 58);
    border: 1px solid red;
  }
  .debuglayout > main .channels {
    background-color: blue;
    border: 1px solid #7272ff;
  }
  .debuglayout > main .header-main {
    background-color: rgb(0, 151, 174);
    border: 1px solid #08ffff;
  }
  .debuglayout > main .channel {
    background-color: rgb(30, 0, 0);
    border: 1px solid #ff7272;
  }
  .debuglayout > main .search-results {
    background-color: lightgreen;
    border: 1px solid #72ff72;
  }
  .debuglayout > main .thread {
    background-color: lightblue;
    border: 1px solid #7272ff;
  }

</style>