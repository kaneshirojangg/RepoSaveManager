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

**Step 1.** Go to the project page:
**[github.com/kaneshirojangg/RepoSaveManager](https://github.com/kaneshirojangg/RepoSaveManager)**

**Step 2.** Click the green **`<> Code`** button.

**Step 3.** Click **`Download ZIP`**.

```
┌───────────────────────────────────┐
│  <> Code  ▾                       │
│  ┌───────────────────────────┐    │
│  │  Clone            HTTPS   │    │
│  │  Open with GitHub Desktop │    │
│  │  Download ZIP        ← ●  │    │
│  └───────────────────────────┘    │
└───────────────────────────────────┘
```

**Step 4.** The file **`RepoSaveManager-main.zip`** downloads to your
`Downloads` folder.

No GitHub account, git, or command-line tools needed for this part.

Now go to **[Install — Windows](#install--windows)** or
**[Install — Linux](#install--linux)**.

[↑ back to top](#-table-of-contents)

---

<a id="install--windows"></a>
## ▸ 03. Install — Windows

No Python, no terminal, no setup — just extract and double-click.

1. Open your **Downloads** folder and find **`RepoSaveManager-main.zip`**.
2. Right-click it → **Extract All...** → **Extract**.
3. Open the extracted **`RepoSaveManager-main`** folder.
4. Find **`Repo Save Manager.exe`** and double-click it to open the app.
5. If Windows shows a blue **"Windows protected your PC"** security warning,
   click **More info** → **Run anyway**. (This is normal for small
   independent apps that aren't from the Microsoft Store.)
6. Set your save + backup folders when asked.

```
┌──────────────────────────────────────────────────────────────────┐
│  ⚠  IMPORTANT: Keep the WHOLE folder together.                   │
│                                                                    │
│  Repo Save Manager.exe needs the other files sitting next to it  │
│  (like the "_internal" folder) to run. Never move or copy just   │
│  the .exe by itself — always keep the entire extracted           │
│  RepoSaveManager-main folder in one place.                       │
└──────────────────────────────────────────────────────────────────┘
```

**Want a shortcut on your Desktop?**
Right-click **`Repo Save Manager.exe`** → **Show more options** (Windows 11)
→ **Send to** → **Desktop (create shortcut)**. The shortcut can live on your
Desktop — just don't move the original `.exe` or its folder.

> **Next time:** just double-click the `.exe` (or your Desktop shortcut) —
> no setup needed again.

<details>
<summary><b>Prefer to run it from source instead? (advanced, optional)</b></summary>

1. Open the extracted `RepoSaveManager-main` folder.
2. Install Python from **[python.org/downloads](https://www.python.org/downloads/)**
   — tick **"Add python.exe to PATH"** during install.
3. Inside the folder, hold **Shift**, right-click empty space, choose
   **"Open PowerShell window here"**.
4. Run:
   ```powershell
   pip install -r requirements.txt
   python launch.py
   ```

</details>

[↑ back to top](#-table-of-contents)

---

<a id="install--linux"></a>
## ▸ 04. Install — Linux

1. Find the downloaded **`RepoSaveManager-main.zip`**.
2. Extract it: right-click → **Extract Here**, or run:
   ```bash
   unzip RepoSaveManager-main.zip
   ```
3. Open a terminal inside the extracted **`RepoSaveManager-main`** folder.
4. Run the installer:
   ```bash
   bash install.sh
   ```
5. Open **"Repo Save Manager"** from your app menu / desktop.

No `install.sh`, or it didn't work on your distro? Run it directly instead:
```bash
python3 -m pip install -r requirements.txt
python3 launch.py
```

> **Next time:** just open a terminal in that folder and run
> `python3 launch.py`.

[↑ back to top](#-table-of-contents)

---

<a id="first-launch"></a>
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