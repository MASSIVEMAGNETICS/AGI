// service_worker.js — Victor Browser Phase-1B

import { normalizeEvent } from './modules/normalize.js';
import { createSnapshot } from './modules/snapshot.js';
import { describeTab } from './modules/describe.js';

// State
let isCaptureEnabled = true;
let isVisionEnabled = false;          // toggle for screenshots
let nativePort = null;
let reconnectAttempts = 0;
const MAX_RECONNECT = 5;
const RECONNECT_DELAY = 3000;

// Native connection (same as before, abbreviated)
function connectToNativeHost() { /* ... same as previous version ... */ }
function sendToNative(envelope) { /* ... */ }

// ────────────────────────────────────────────────
// Autonomy Scheduler — 15 min workspace snapshots
// ────────────────────────────────────────────────

chrome.alarms.create("victor-snapshot", { periodInMinutes: 15 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === "victor-snapshot" && isCaptureEnabled) {
    console.log("[Victor] Autonomy: Taking workspace snapshot");

    const snapshot = await createSnapshot(isVisionEnabled); // includes tabs + descriptions + optional shots

    const envelope = {
      type: "workspaceSnapshot",
      timestamp: new Date().toISOString(),
      data: snapshot
    };

    sendToNative(envelope);

    // Optional: notify user if many tabs or interesting change
    if (snapshot.totalTabs > 25) {
      chrome.notifications.create({
        type: "basic",
        iconUrl: "/icons/icon128.png",
        title: "Victor Notice",
        message: `Workspace snapshot taken — ${snapshot.totalTabs} tabs open. Consider closing duplicates?`
      });
    }

    // Also broadcast to side panel if open
    chrome.runtime.sendMessage({ action: "newSnapshot", data: snapshot });
  }
});

// ────────────────────────────────────────────────
// Core event listeners (tab create/update/remove, navigation, downloads)
// ────────────────────────────────────────────────

// ... same as previous version: onCreated, onUpdated (filtered), onRemoved, webNavigation.onCommitted, downloads.onCreated ...

// ────────────────────────────────────────────────
// Side Panel & Victor Autonomy Output
// ────────────────────────────────────────────────

// Open side panel when action icon clicked (persistent Victor channel)
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });

// Listen for messages from side panel or native host
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "toggleCapture") {
    isCaptureEnabled = msg.enabled;
    chrome.storage.local.set({ isCaptureEnabled });
    sendResponse({ success: true });
  }
  else if (msg.action === "toggleVision") {
    isVisionEnabled = msg.enabled;
    chrome.storage.local.set({ isVisionEnabled });
    chrome.notifications.create({
      type: "basic",
      title: "Victor Vision",
      message: `Vision ${isVisionEnabled ? "ENABLED" : "DISABLED"} — screenshots ${isVisionEnabled ? "will" : "won't"} be captured.`
    });
    sendResponse({ success: true });
  }
  else if (msg.action === "getStatus") {
    sendResponse({ capture: isCaptureEnabled, vision: isVisionEnabled });
  }
  // Native host can send autonomous messages → forward to side panel / notifications
  else if (msg.fromNative && msg.message) {
    chrome.notifications.create({
      type: "basic",
      title: "Victor says:",
      message: msg.message
    });
    // Also send to side panel
    chrome.runtime.sendMessage({ action: "victorMessage", text: msg.message });
  }
});

// Load persisted state
chrome.storage.local.get(
  { isCaptureEnabled: true, isVisionEnabled: false },
  (data) => {
    isCaptureEnabled = data.isCaptureEnabled !== false;
    isVisionEnabled = !!data.isVisionEnabled;
  }
);

// Startup
console.log("[Victor Browser] Phase-1B Service Worker — Vision & Autonomy active");
connectToNativeHost();