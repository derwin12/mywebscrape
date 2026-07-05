// Decision-tree content for the xLights Troubleshooter.
// This is a STARTER draft — verify/correct the technical steps before publishing.
//
// Node shape:
//   question node: { type: "question", text, options: [{ label, next }] }
//   solution node: { type: "solution", title, steps: [string], links?: [{label, href}] }

const TREE = {
  start: {
    type: "question",
    text: "What's going wrong?",
    options: [
      { label: "A sequence won't play or looks wrong", next: "seq_root" },
      { label: "Controller / lights aren't lighting up", next: "controller_root" },
      { label: "Scheduled show won't run", next: "schedule_root" },
      { label: "Music/audio is out of sync", next: "audio_root" },
      { label: "xLights won't open or keeps crashing", next: "crash_root" },
    ],
  },

  // ---------------- Sequence playback ----------------
  seq_root: {
    type: "question",
    text: "When you play the sequence in the xLights sequencer, what happens?",
    options: [
      { label: "Nothing lights up at all", next: "seq_no_output" },
      { label: "Only some props/controllers light up", next: "seq_partial_output" },
      { label: "Effects play but timing looks wrong vs. the music", next: "audio_root" },
      { label: "xLights shows an error when I try to play", next: "seq_error" },
    ],
  },
  seq_no_output: {
    type: "solution",
    title: "No output at all during playback",
    steps: [
      "Confirm you're in a mode that outputs to controllers — Layout tab, not just Sequencer preview (check View > Preview settings or the output toggle).",
      "Open Tools > Controllers and confirm at least one output (E1.31/Artnet/DDP/etc.) is enabled and not greyed out.",
      "Check Tools > Test to send a manual test pattern — if that also fails, this is a controller/network problem, not a sequence problem (see the controller branch).",
      "Verify the sequence's model(s) are actually assigned to a controller output in the Layout tab (unassigned models won't output).",
    ],
  },
  seq_partial_output: {
    type: "solution",
    title: "Only some props light up",
    steps: [
      "Check each affected model's Start Channel / controller connection in the Layout tab — a mismatched start channel is the most common cause.",
      "Look for channel overlap between models sharing the same controller/universe.",
      "Confirm the effect layer for the missing model isn't muted, hidden, or on a disabled layer/timing track.",
      "Re-run Tools > Test on just the affected controller output to isolate wiring vs. sequence config.",
    ],
  },
  seq_error: {
    type: "solution",
    title: "xLights shows an error on playback",
    steps: [
      "Note the exact error text — Help > View Log Files (or the xlights.log in your show folder) will have more detail.",
      "If it mentions a missing/corrupt media file, re-link the audio under the sequence's Settings tab.",
      "If it mentions rendering, try Render All to force a full re-render before playing.",
      "If the sequence file itself won't open, try loading the .xbkp backup from the show folder.",
    ],
  },

  // ---------------- Controller / lighting ----------------
  controller_root: {
    type: "question",
    text: "How is the controller connected to your computer/network?",
    options: [
      { label: "USB", next: "controller_usb" },
      { label: "Network (Ethernet/WiFi, e.g. E1.31/Artnet/DDP)", next: "controller_network" },
      { label: "I'm not sure", next: "controller_unsure" },
    ],
  },
  controller_usb: {
    type: "solution",
    title: "USB-connected controller isn't lighting up",
    steps: [
      "Check Windows/mac Device Manager for the USB-to-serial driver — reinstall it if the port isn't listed or shows an error.",
      "In Tools > Controllers, confirm the correct COM/serial port is selected and matches Device Manager.",
      "Try a different USB cable/port — many 'controller' issues are actually a bad cable.",
      "Power-cycle the controller after reconnecting USB.",
    ],
  },
  controller_network: {
    type: "solution",
    title: "Network-connected controller isn't lighting up",
    steps: [
      "Ping the controller's IP address from your computer — if it doesn't respond, fix networking before touching xLights.",
      "Confirm the controller's IP is on the same subnet as your computer (e.g. both 192.168.1.x) and not double-assigned to another device.",
      "In Tools > Controllers, verify the protocol (E1.31/Artnet/DDP) and universe/start-channel match what's configured on the controller itself.",
      "Temporarily disable any firewall blocking UDP traffic on the sequencing PC.",
      "Use Tools > Test with a single-color pattern to confirm connectivity independent of any sequence.",
    ],
  },
  controller_unsure: {
    type: "solution",
    title: "Identifying your controller connection",
    steps: [
      "Check the controller's manual/label — most modern controllers (Falcon, FPP, ESPixelStick, etc.) use network protocols (E1.31/Artnet/DDP) rather than USB.",
      "If there's an Ethernet cable or WiFi antenna on the controller, it's network-based — use the network branch above.",
      "If it connects via a USB cable directly to your PC, use the USB branch above.",
    ],
  },

  // ---------------- Scheduled show ----------------
  schedule_root: {
    type: "question",
    text: "Are you scheduling through the xLights Scheduler, or a separate player like FPP?",
    options: [
      { label: "xLights Scheduler", next: "schedule_xlights" },
      { label: "Falcon Player (FPP) or another standalone player", next: "schedule_fpp" },
    ],
  },
  schedule_xlights: {
    type: "solution",
    title: "xLights Scheduler show won't run",
    steps: [
      "Confirm the Scheduler is actually running (Tools > Scheduler) and the schedule's date/time window covers now.",
      "Check that the playlist referenced by the schedule still points to valid, existing sequence files.",
      "Verify the computer isn't set to sleep — scheduled playback won't fire if the PC is asleep.",
      "Check the schedule's day-of-week/date settings for an off-by-one mistake.",
    ],
  },
  schedule_fpp: {
    type: "solution",
    title: "FPP / standalone player show won't run",
    steps: [
      "Log into the FPP web UI and check the Status page for the current player state and any errors.",
      "Confirm the schedule entry's playlist exists and enabled, and the day/time range is correct (FPP uses its own clock — verify NTP/time sync).",
      "Check Content > File Manager to confirm the sequence + media files actually uploaded to the player.",
      "Review the FPP log (Status/Logs page) for errors at the scheduled start time.",
    ],
  },

  // ---------------- Audio sync ----------------
  audio_root: {
    type: "question",
    text: "Is the sync issue happening in the xLights sequencer preview, or on the actual show playback (props)?",
    options: [
      { label: "In the sequencer preview only", next: "audio_preview" },
      { label: "On the actual physical show", next: "audio_show" },
    ],
  },
  audio_preview: {
    type: "solution",
    title: "Audio/effects out of sync in the sequencer",
    steps: [
      "Re-render the sequence (Render All) — stale renders are the most common cause of preview drift.",
      "Confirm the media file's sample rate/format is one xLights handles well (44.1kHz MP3/WAV are safest).",
      "Check that no other timing tracks or tempo markers were accidentally shifted.",
    ],
  },
  audio_show: {
    type: "solution",
    title: "Audio/effects out of sync on the physical show",
    steps: [
      "If using FM transmission or an external audio source, confirm the player's audio output isn't delayed relative to the light output.",
      "Verify the same media file version is deployed to the player as was used when rendering the sequence.",
      "Check for network latency/frame-drop on remote controllers — high universe counts on a congested network can cause visible lag.",
      "If using FPP, check the audio output device setting matches your actual amp/transmitter.",
    ],
  },

  // ---------------- Crashes ----------------
  crash_root: {
    type: "question",
    text: "Does xLights crash immediately on launch, or after you open/do something specific?",
    options: [
      { label: "Immediately on launch", next: "crash_launch" },
      { label: "After opening a specific sequence or show folder", next: "crash_sequence" },
      { label: "Randomly during use", next: "crash_random" },
    ],
  },
  crash_launch: {
    type: "solution",
    title: "xLights crashes on launch",
    steps: [
      "Update to the latest xLights release — launch crashes are frequently fixed in newer builds.",
      "Update your graphics drivers; xLights relies on OpenGL for previews.",
      "Try renaming/moving the xlights.db and xlights_networks.xml config files in your show folder to rule out corrupt config.",
      "Check Help > View Log Files (or the log left from the last run) for a stack trace to search in the xLights forums/Facebook group.",
    ],
  },
  crash_sequence: {
    type: "solution",
    title: "Crashes tied to a specific sequence/show folder",
    steps: [
      "Try opening a different, known-good sequence to confirm the crash is specific to this file.",
      "Restore from the automatic .xbkp backup xLights keeps alongside the .xsq file.",
      "Check the show folder for a corrupted media file referenced by the sequence.",
      "Try opening the sequence on another machine/xLights install to isolate a local install issue.",
    ],
  },
  crash_random: {
    type: "solution",
    title: "Random crashes during use",
    steps: [
      "Update graphics drivers and xLights itself to the latest versions first.",
      "Watch Task Manager/Activity Monitor for memory usage climbing toward your system limit on large shows.",
      "Reduce real-time preview effects/model count if the crash correlates with heavy preview rendering.",
      "Check Help > View Log Files after a crash for the specific error to search against known issues.",
    ],
  },
};

const START_NODE = "start";
