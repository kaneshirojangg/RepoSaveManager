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
manual has a [Troubleshooting](#-troubleshooting) section near the end to help you
figure out what's going on.

---

## ▸ Table of contents

```
01. What is this?
02. Download
03. Install — Windows
04. Install — Linux
05. First launch
06. Understanding the dashboard
07. How to use it (step by step)
08. Troubleshooting
09. Uninstall
10. Good habits (read this!)
11. Notes for the curious
```

---

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

---

## ▸ 02. Download

```
STEP 01 ── go to the GitHub Releases page
STEP 02 ── find the newest version at the top
STEP 03 ── download the file that matches your operating system
```

**[⇩ Latest Release](https://github.com/RepoSaveManager/RepoSaveManager/releases/latest)**

### Windows (download ZIP)
**[RepoSaveManager-windows.zip](https://github.com/kaneshirojangg/RepoSaveManager/releases/latest/download/RepoSaveManager-windows.zip)**

### Linux (download tar.gz)
**[RepoSaveManager-linux.tar.gz](https://github.com/kaneshirojangg/RepoSaveManager/releases/latest/download/RepoSaveManager-linux.tar.gz)**

You do not need to install Python, git, or any other tool. The release already
has everything packaged inside it.

---

## ▸ 03. Install — Windows

```
┌──────────────────────────────────────────────────────────────────┐
│  WINDOWS SETUP WIZARD                                            │
└──────────────────────────────────────────────────────────────────┘

  STEP 01 ── download RepoSaveManager-windows.zip
  STEP 02 ── right-click the zip → "Extract All..."
  STEP 03 ── open the extracted folder
  STEP 04 ── double-click  Repo Save Manager.exe
  STEP 05 ── if Windows shows a security warning, click
             "More info" → "Run anyway"
             (this is normal for small independent apps)
  STEP 06 ── set your save + backup folders when asked
```

> Keep the whole extracted folder together — don't move just the `.exe` file
> on its own, or it may not find its files.

---

## ▸ 04. Install — Linux

```
┌──────────────────────────────────────────────────────────────────┐
│  LINUX SETUP WIZARD                                              │
└──────────────────────────────────────────────────────────────────┘

  STEP 01 ── download RepoSaveManager-linux.tar.gz
  STEP 02 ── extract the archive (right-click → Extract, or:
             tar -xzf RepoSaveManager-linux.tar.gz )
  STEP 03 ── open a terminal in that extracted folder
  STEP 04 ── run this once:

                 bash install.sh

  STEP 05 ── open "Repo Save Manager" from your app menu / desktop
```

Don't want it installed system-wide? You can instead mark
`RepoSaveManager.desktop` as trusted / executable and open it directly from
the extracted folder.

---

## ▸ 05. First launch

The very first time you open the app, it needs to know two locations:

```
  ┌───────────────────────────┐   ┌──────────────────────────────┐
  │  R.E.P.O. SAVE FOLDER     │   │  BACKUP FOLDER               │
  │                           │   │                              │
  │  Where the game keeps     │   │  Where YOU want the safety   │
  │  your live saves.         │   │  copies stored. Can be any   │
  │                           │   │  folder, drive, or location. │
  └───────────────────────────┘   └──────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────────────────┐
│  TIP: Don't know where your save folder is?                      │
│  Click "Auto-Detect" and the app will try the common R.E.P.O.    │
│  install locations for you.                                      │
└──────────────────────────────────────────────────────────────────┘
```

Your save folder should contain folders that look like this:
`REPO_SAVE_2026_07_07_21_09_48`

Once both folders are set, click **Test Configuration** to make sure
everything checks out green, then click **Save**.

---

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

---

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

---

## ▸ 08. Troubleshooting

```
┌──────────────────────────────────────────────────────────────────┐
│  PROBLEM: The app closes itself a few seconds after opening      │
│  TRY:     Update to the latest release — this was a known issue  │
│           in earlier builds and should be fixed now. If it still │
│           happens, run the app from a terminal/command prompt so │
│           you can see the error message, and report it.          │
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
thing you can do is note exactly what you clicked, what you expected, and what
happened instead — that makes any bug much faster to track down.

---

## ▸ 09. Uninstall

**Linux** — if you used `install.sh`:

```bash
bash uninstall.sh
```
This removes the launcher, icon, and installed app files.

**Windows** — just delete the folder you extracted the release into.

---

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

---

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

<div align="center">

```
──────────────────────  END OF TRANSMISSION  ──────────────────────
```

</div>
