# Graph Report - .  (2026-05-23)

## Corpus Check
- 24 files · ~123,955 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 131 nodes · 190 edges · 15 communities (11 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_FUSE Virtual Filesystem|FUSE Virtual Filesystem]]
- [[_COMMUNITY_Media Processing Pipeline|Media Processing Pipeline]]
- [[_COMMUNITY_Application Core & Scheduling|Application Core & Scheduling]]
- [[_COMMUNITY_Database Operations|Database Operations]]
- [[_COMMUNITY_Metadata & API Integration|Metadata & API Integration]]
- [[_COMMUNITY_Application Functions|Application Functions]]
- [[_COMMUNITY_Docker & CICD|Docker & CI/CD]]
- [[_COMMUNITY_STRM File Generation|STRM File Generation]]
- [[_COMMUNITY_Enums & Configuration|Enums & Configuration]]
- [[_COMMUNITY_Graphify Integration|Graphify Integration]]
- [[_COMMUNITY_Linux Setup Script|Linux Setup Script]]
- [[_COMMUNITY_macOS Setup Script|macOS Setup Script]]
- [[_COMMUNITY_Download Type Enums|Download Type Enums]]
- [[_COMMUNITY_Version Info|Version Info]]

## God Nodes (most connected - your core abstractions)
1. `VirtualFileSystem` - 10 edges
2. `TorBoxMediaCenterFuse` - 10 edges
3. `getAllUserDownloads()` - 6 edges
4. `searchMetadata()` - 6 edges
5. `getDatabase()` - 6 edges
6. `getDatabaseLock()` - 6 edges
7. `clearDatabase()` - 6 edges
8. `insertData()` - 6 edges
9. `getAllData()` - 6 edges
10. `requestWrapper()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Blocking Scheduler (STRM)` --implements--> `STRM Mount Method`  [INFERRED]
  main.py → README.md
- `Background Scheduler (FUSE)` --implements--> `FUSE Mount Method`  [INFERRED]
  main.py → README.md
- `APScheduler Dependency` --enables--> `APScheduler Job Scheduler`  [INFERRED]
  requirements.txt → main.py
- `TorBox Header Image` --represents--> `TorBox Media Center`  [EXTRACTED]
  assets/header.png → README.md
- `Metadata Scanning Configuration` --enables--> `TorBox Metadata Search API`  [INFERRED]
  library/app.py → README.md

## Hyperedges (group relationships)
- **Media Server Compatibility Pattern** — readme_mount_method_strm, readme_jellyfin, readme_emby [EXTRACTED 1.00]
- **Scheduler Mount Method Selection Pattern** — main_scheduler, main_blocking_scheduler, main_background_scheduler [EXTRACTED 1.00]
- **File Processing Pipeline** — torbox_api_pagination, torbox_file_processor, torbox_metadata_search, torbox_parallel_processing [EXTRACTED 0.90]
- **CI/CD Pipeline** — workflow_docker_build, workflow_docker_hub, workflow_ghcr [EXTRACTED 1.00]

## Communities (15 total, 4 thin omitted)

### Community 0 - "FUSE Virtual Filesystem"
Cohesion: 0.16
Nodes (5): FuseStat, runFuse(), TorBoxMediaCenterFuse, VirtualFileSystem, Fuse

### Community 1 - "Media Processing Pipeline"
Cohesion: 0.18
Nodes (15): insertData(), Inserts data into the database with thread safety., cleanTitle(), cleanYear(), constructSeriesTitle(), Removes invalid characters from the title., Cleans the year listing which can be a string (2023-2024) or an int (2023)., Constructs a proper title for a series based on the season and episode.      :pa (+7 more)

### Community 2 - "Application Core & Scheduling"
Cohesion: 0.13
Nodes (17): Mount Refresh Time Enum, TorBox Header Image, Application Entry Point, Background Scheduler (FUSE), Blocking Scheduler (STRM), Mount Refresh Job, APScheduler Job Scheduler, Emby Media Server (+9 more)

### Community 3 - "Database Operations"
Cohesion: 0.22
Nodes (12): clearDatabase(), closeAllDatabases(), closeDatabase(), getAllData(), getDatabase(), getDatabaseLock(), Returns the TinyDB database instance with thread-safe storage.     Uses a connec, Closes all database connections. (+4 more)

### Community 4 - "Metadata & API Integration"
Cohesion: 0.17
Nodes (13): Metadata Scanning Configuration, Raw Mode Configuration, TorBox Metadata Search API, HTTPX Dependency, Parse Torrent Title Dependency, API Pagination Handler, Download Link Generator, File Processing Pipeline (+5 more)

### Community 5 - "Application Functions"
Cohesion: 0.27
Nodes (9): bootUp(), getAllUserDownloadsFresh(), getLatestVersion(), getMountMethod(), getMountRefreshTime(), initializeFolders(), unmountFuse(), getUserDownloads() (+1 more)

### Community 6 - "Docker & CI/CD"
Cohesion: 0.22
Nodes (10): Environment Configuration, Docker Compose Service Configuration, Volume Mount Configuration, Docker Deployment, Environment Variables Configuration, TorBox API Key Configuration, Docker Build Workflow, Docker Hub Registry (+2 more)

### Community 7 - "STRM File Generation"
Cohesion: 0.36
Nodes (7): getAllUserDownloads(), generateFolderPath(), generateStremFile(), Deletes all strm files and any subfolders in the mount path for cleaning up., Takes in a user download and returns the folder path for the download., runStrm(), unmountStrm()

### Community 8 - "Enums & Configuration"
Cohesion: 0.38
Nodes (5): Enum, DownloadType, IDType, MountRefreshTimes, MountMethods

### Community 9 - "Graphify Integration"
Cohesion: 0.50
Nodes (4): Community Structure, God Nodes, Graphify Integration, Knowledge Graph

## Knowledge Gaps
- **22 isolated node(s):** `setup-linux.sh script`, `setup-macos.sh script`, `Jellyfin Media Server`, `Emby Media Server`, `Plex Media Server` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `getAllUserDownloads()` connect `STRM File Generation` to `FUSE Virtual Filesystem`, `Database Operations`, `Application Functions`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `TorBox Media Center` connect `Application Core & Scheduling` to `Metadata & API Integration`, `Docker & CI/CD`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **What connects `Process a single file and return the processed data`, `Returns the TinyDB database instance with thread-safe storage.     Uses a connec`, `Returns the lock for the specified database.` to the rest of the system?**
  _43 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Application Core & Scheduling` be split into smaller, more focused modules?**
  _Cohesion score 0.1323529411764706 - nodes in this community are weakly interconnected._