# Project Structure

```text
RepoSaveManager/
├── .github/
│   └── workflows/
│       └── release.yml
├── assets/
│   ├── fonts/
│   ├── icons/
│   │   └── app.svg
│   └── images/
│       └── reposavemanager.png
├── backups/
├── config/
│   └── settings.json
├── data/
│   └── backup_database.json
├── logs/
│   └── application.log
├── docs/
│   └── project-structure.md
├── src/
│   ├── __main__.py
│   ├── main.py
│   ├── managers/
│   │   ├── backup_manager.py
│   │   ├── monitor_manager.py
│   │   ├── restore_manager.py
│   │   ├── save_manager.py
│   │   └── settings_manager.py
│   ├── models/
│   │   └── save_model.py
│   ├── services/
│   │   ├── file_service.py
│   │   ├── hash_service.py
│   │   └── logger_service.py
│   ├── ui/
│   │   ├── activity_log.py
│   │   ├── dashboard.py
│   │   ├── dialogs.py
│   │   ├── logo.py
│   │   ├── main_window.py
│   │   ├── settings_window.py
│   │   ├── setup_wizard.py
│   │   └── theme.py
│   └── utils/
│       ├── constants.py
│       └── helpers.py
├── RepoSaveManager.desktop
├── RepoSaveManager.spec
├── dev-launch.sh
├── install-dev.sh
├── install.sh
├── launch.py
├── README.md
├── refresh-install.sh
├── requirements.txt
└── uninstall.sh
```
