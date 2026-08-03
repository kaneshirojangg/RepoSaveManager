<div align="center">

```
                                  ██████╗ ███████╗██████╗  ██████╗
                                  ██╔══██╗██╔════╝██╔══██╗██╔═══██╗
                                  ██████╔╝█████╗  ██████╔╝██║   ██║
                                  ██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║
                                  ██║  ██║███████╗██║     ╚██████╔╝
                                  ╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝

                                        S A V E   M A N A G E R
                                      ── U S E R   M A N U A L ──
```

`[ WINDOWS ]` `[ LINUX ]` `[ BEGINNER FRIENDLY ]` `[ MIT LICENSE ]`

**> A SIMPLE GUIDE TO BACKING UP YOUR CREW'S PROGRESS._**

</div>

---

##  Important notice

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  This project was "vibe coded" — built quickly, iteratively,     │
│  and with a lot of trial and error, rather than engineered       │
│  top-to-bottom with formal specs.                                │
│                                                                  │
│  Repo Save Manager is an ASSIST tool, not a guarantee. It is     │
│  meant to help reduce the pain of losing a run, not replace      │
│  your own good habits.                                           │
│                                                                  │
│  Bugs are likely to appear. Please still keep your own manual    │
│  copies of saves you really care about, and treat this app as    │
│  a helpful safety net, not a bulletproof vault.                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

If something looks or behaves oddly, that's expected from time to time — this
manual has a [Troubleshooting](#troubleshooting) section near the end to help
you figure out what's going on.

---

## ▸ Table of contents

1. [What is this?](#what-is-this)
2. [Download](#download)
3. [Install — Windows](#install--windows)
4. [Install — Linux](#install--linux)
5. [First launch](#first-launch)
6. [Understanding the dashboard](#understanding-the-dashboard)
7. [How to use it (step by step)](#how-to-use-it-step-by-step)
8. [Troubleshooting](#troubleshooting)
9. [Uninstall](#uninstall)
10. [Good habits (read this!)](#good-habits-read-this)
11. [Notes for the curious](#notes-for-the-curious)

---

<a id="what-is-this"></a>
## ▸ 01. What is this?

Repo Save Manager is a small desktop app that watches over your **R.E.P.O.**
save folders in the background. If your whole crew goes down and the game wipes
your save, this app already has a mirrored copy sitting in a backup folder,
ready to hand back to you.

Think of it like a spare key hidden under the mat — except the "mat" is a
folder on your computer, and the "key" is your save file.

```
┌────────────────────────────────────────────────────────────┐
│  YOUR SAVE FOLDER                BACKUP FOLDER             │
│  ┌─────────────────┐             ┌──────────────────┐      │
│  │ REPO_SAVE_...   │  ──copy──▶  │ REPO_SAVE_...    │      │
│  │ (the real save) │             │ (the safety net) │      │
│  └─────────────────┘             └──────────────────┘      │
└────────────────────────────────────────────────────────────┘
```

[↑ back to top](#-table-of-contents)

---

<a id="download"></a>
## ▸ 02. Download

Download the file for your operating system:

**Windows** - **[RepoSaveManager-windows.exe](https://github.com/kaneshirojangg/RepoSaveManager/releases/latest/download/RepoSaveManager-windows.exe)**

**Linux** - **[RepoSaveManager-linux.tar.gz](https://github.com/kaneshirojangg/RepoSaveManager/releases/latest/download/RepoSaveManager-linux.tar.gz)**

Then follow the matching install guide below.

[↑ back to top](#-table-of-contents)

---

<a id="install--windows"></a>
## ▸ 03. Install — Windows

1. Click **[RepoSaveManager-windows.exe](https://github.com/kaneshirojangg/RepoSaveManager/releases/latest/download/RepoSaveManager-windows.exe)**.
2. Save the file anywhere.
3. Double-click the `.exe` to open the app.
4. If Windows shows a security warning, choose **More info** → **Run anyway**.
5. Pick your save folder and backup folder when the app asks.

[↑ back to top](#-table-of-contents)

---

<a id="install--linux"></a>
## ▸ 04. Install — Linux

1. Click **[RepoSaveManager-linux.tar.gz](https://github.com/kaneshirojangg/RepoSaveManager/releases/latest/download/RepoSaveManager-linux.tar.gz)**.
2. Extract the archive.
3. Open the extracted folder.
4. Run:
   ```bash
   bash install.sh
   ```
5. Open **Repo Save Manager** from your app menu.

[↑ back to top](#-table-of-contents)

---

<a id="first-launch"></a>
## ▸ 05. First launch

The first time you open the app, choose two folders:

```
  ┌───────────────────────────┐   ┌──────────────────────────────┐
  │  R.E.P.O. SAVE FOLDER     │   │  BACKUP FOLDER               │
  │                           │   │                              │
  │  Where the game keeps     │   │  Where YOU want the safety   │
  │  your live saves.         │   │  copies stored. Can be any   │
  │                           │   │  folder, drive, or location. │
  └───────────────────────────┘   └──────────────────────────────┘
```

If you do not know the save folder, click **Auto-Detect** first.

Your save folder should contain folders like `REPO_SAVE_2026_07_07_21_09_48`.

When both folders are set, click **Test Configuration**, then **Save**.

[↑ back to top](#-table-of-contents)

---

<a id="understanding-the-dashboard"></a>
## ▸ 06. Understanding the dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│  ● MONITORING ACTIVE        REPO SAVE MANAGER        07:08 JUL 26   │
├───────────────────────┬────────────────────────┬────────────────────┤
│  (1) DETECTED SAVES   │  (2) SELECTED SAVE     │  (3) PATHS PANEL   │
│                       │                        │                    │
│  ▣ REPO_SAVE_2109_48  │  ID   REPO_SAVE_2109_48│  Save: C:\...      │
│    ● backed up        │  Label  Luna & Oreyun2 │  Backup: D:\...    │
│                       │  Backup  ✓ up to date  │                    │
│  ▢ REPO_SAVE_1802_11  │  Modified  2h ago      │                    │
│    ○ no backup        │  Size   3.1 KB         │                    │
│                       │  [Create Backup]       │                    │
│                       │  [Load Backup]         │                    │
├───────────────────────┴────────────────────────┴────────────────────┤
│  (4) ACTION BAR:  Refresh | Open Save Folder | Open Backup | ...    │
├───────────────────────────────────────────────────────────────────  │
│  (5) ACTIVITY LOG                                                   │
│  21:09:48  ✓ Backup created  → REPO_SAVE_2109_48                    │
│  21:41:02  ↻ Backup updated  → REPO_SAVE_2109_48                    │
│  22:03:15  ☠ Save deleted    → REPO_SAVE_1802_11  [restore offered] │
└─────────────────────────────────────────────────────────────────────┘
```

```
(1) DETECTED SAVES ── every save folder the app has found. Click one to
                       select it. A small badge under the name shows its
                       backup health at a glance:

                         ● backed up        → you're safe
                         ○ no backup        → make one soon
                         ⚠ backup outdated  → you've played more
                                              recently than your last
                                              backup — back it up again

(2) SELECTED SAVE  ── details for whichever save is currently selected,
                       plus the two buttons you'll use most:
                         Create Backup  → mirror this save right now
                         Load Backup    → restore this save from backup

(3) PATHS PANEL    ── a quick reminder of which folders you configured

(4) ACTION BAR     ── quick actions: refresh the list, open either
                       folder in your file manager, delete a backup,
                       open settings, or exit

(5) ACTIVITY LOG   ── a running history of everything the app has done,
                       newest at the bottom
```

If you ever see a colored banner appear above the dashboard, it's the app
proactively flagging something:

```
┌──────────────────────────────────────────────────────────────────┐
│  ☠  RED BANNER   → a save is missing (likely a death-wipe).      │
│                     A one-click restore is offered right there.  │
│                                                                  │
│  ⚠  AMBER BANNER → a save has new progress that isn't backed up  │
│                     yet. Click "Back Up Now" to catch it up.     │
└──────────────────────────────────────────────────────────────────┘
```

[↑ back to top](#-table-of-contents)

---

<a id="how-to-use-it-step-by-step"></a>
## ▸ 07. How to use it (step by step)

```
01 ── SELECT A SAVE
      Click a save card on the left. Its details fill in on the right.

02 ── CREATE A BACKUP
      Click "Create Backup". The whole save folder is mirrored into
      your backup location. Safe to click again later — it updates
      the same backup instead of piling up duplicates.

03 ── RESTORE A SAVE
      Click "Load Backup". The app will always ask you to confirm
      before it touches anything.

04 ── REFRESH THE LIST
      Added, removed, or moved save folders? Click "Refresh Saves".

05 ── TURN ON MONITORING
      Click "Start" next to the monitoring pill at the top. The app
      will now watch your save folder in the background and pop up
      a restore prompt the moment it notices a save got wiped.

06 ── RENAME A SAVE (COSMETIC ONLY)
      Click the pencil icon ✎ next to a save's title to give it a
      friendly label, like a crew or run name. This is just for your
      own reference — it never touches the real save files.
```

```
┌──────────────────────────────────────────────────────────────────┐
│  GOLDEN RULE:  no backup, no safety net.                         │
│  Get in the habit of clicking "Create Backup" after a good run,  │
│  or just leave monitoring turned on while you play.              │
└──────────────────────────────────────────────────────────────────┘
```

[↑ back to top](#-table-of-contents)

---

<a id="troubleshooting"></a>
## ▸ 08. Troubleshooting

```
┌──────────────────────────────────────────────────────────────────┐
│  PROBLEM: Windows shows "Windows protected your PC"              │
│  TRY:     Click "More info" → "Run anyway". This is normal for   │
│           independent apps not distributed through the Microsoft │
│           Store — it isn't a sign anything is wrong.             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  PROBLEM: Double-clicking the .exe does nothing / shows an error │
│  TRY:     Make sure you extracted the ZIP first (right-click →   │
│           Extract All) — running it straight from inside the     │
│           zip without extracting will fail. Also make sure the   │
│           "_internal" folder is still sitting next to the .exe.  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  PROBLEM: "python: command not found" / "python is not recognized"│
│  TRY:     (Only relevant if running from source.) On some        │
│           systems the command is `python3` instead of `python`.  │
│           On Windows, make sure you ticked "Add python.exe to    │
│           PATH" during install, then reopen PowerShell.          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  PROBLEM: The app closes itself a few seconds after opening      │
│  TRY:     Re-download the ZIP to make sure you have the latest   │
│           version — this was a known issue in earlier versions.  │
│           If it still happens, note whatever error text appears  │
│           and report it.                                          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  PROBLEM: A save badge or button looks cut off                   │
│  TRY:     Resize the window a little larger, or scroll — the     │
│           save list and detail panel both support scrolling.     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  PROBLEM: "Folder Not Found" when opening Save/Backup folder     │
│  TRY:     Open Settings and re-check both paths still exist —    │
│           a drive letter or folder may have moved.               │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  PROBLEM: Monitoring won't start                                 │
│  TRY:     This usually means an optional background-watching     │
│           component isn't available on your system. You can      │
│           still back up and restore manually without it.         │
└──────────────────────────────────────────────────────────────────┘
```

Still stuck? Since this app is vibe coded and still maturing, the most useful
thing you can do is note exactly what you clicked (or typed), what you
expected, and what happened instead — that makes any bug much faster to
track down.

[↑ back to top](#-table-of-contents)

---

<a id="uninstall"></a>
## ▸ 09. Uninstall

**Windows** — delete the whole `RepoSaveManager-main` folder you extracted
(and the Desktop shortcut, if you made one). This won't touch your actual
R.E.P.O. saves or your backup folder — only the app itself.

**Linux** — if you used `install.sh`:
```bash
bash uninstall.sh
```
This removes the launcher, icon, and installed app files. Otherwise, delete
the extracted `RepoSaveManager-main` folder the same way as Windows.

[↑ back to top](#-table-of-contents)

---

<a id="good-habits-read-this"></a>
## ▸ 10. Good habits (read this!)

```
[x] Keep monitoring turned on while you play, if you can
[x] Click "Create Backup" after a run you'd hate to lose
[x] Every now and then, peek at the Activity Log to confirm backups
    are actually happening
[x] Don't rely on any single tool — occasionally copy important
    saves somewhere else too (a USB drive, cloud folder, etc.)
[ ] Don't assume "no news is good news" — check in on it sometimes
```

[↑ back to top](#-table-of-contents)

---

<a id="notes-for-the-curious"></a>
## ▸ 11. Notes for the curious

```
> each save is a single folder named REPO_SAVE_<timestamp>
> the save files inside are opaque, encrypted binary — this app
  can't read or edit their contents, only copy the whole folder
> the app tells saves apart using: folder name → folder timestamp
  → a hash of the main save file
> the game's own internal backup rotation is never touched by
  this app — it only manages its own separate backup copy
```

[↑ back to top](#-table-of-contents)

<div align="center">

```
──────────────────────  END OF TRANSMISSION  ──────────────────────
```

</div>