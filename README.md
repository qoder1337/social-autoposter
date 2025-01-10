# Social Autoposter

> 2DO: threads und facebook Integration

## Social Media Updates

- tröpfenweises Posten der aktuellsten Beiträge auf Zufallsbasis (Quellen: RSS-Feed oder XML Sitemap)
- vollautomatischer Ablauf im Docker Container auf einem Server möglich
- aktuell: Posting auf X (Twitter) und Bluesky via API
- in Planung: Facebook und Threads Integration


## flask Architektur als Backend

- Separate SQLite-db Tabellen für jeden Account und jede Seite, um Duplikate zu vermeiden.
- striktes Achten auf flask best Practices bei der Architektur
- Integration eines detaillierten Loggers, für reibungslosen Serverbetrieb

### Requirements
- X API Key / Account
- bsky API Key / Account
