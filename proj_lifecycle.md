
# Appointment Reminder API

This project runs a Dockerized FastAPI + MongoDB backend for managing appointment reminder contacts.

The application lifecycle (start, stop, backup, restore) is managed through a custom Perl script: `run_app.pl`.

This ensures:

* Automatic timestamped backups on shutdown
* Rotating backups (keeps last 5)
* Restore capability from latest or specific backup
* Backups stored safely on the host filesystem
* Protection from accidental `docker compose down -v` data loss

---

# 📦 Project Structure

```
apt_reminder_proj/
│
├── run_app.pl
├── docker-compose.yml
├── backups/                # Timestamped MongoDB backups (host filesystem)
└── ...
```

Backups are stored in:

```
backups/
  mongo_YYYYMMDD_HHMMSS.archive.gz
```

---

# 🚀 Starting the Application

Build and start the application:

```bash
./run_app.pl start
```

This will:

1. Build Docker images
2. Start containers in the foreground
3. Wait until you stop the app

To stop the app safely:

Press:

```
Ctrl + C
```

The script will:

1. Create a timestamped Mongo backup
2. Rotate old backups (keep last 5)
3. Run `docker compose down`

---

# 🛑 Stopping the Application Manually

You can also stop safely with:

```bash
./run_app.pl stop
```

This will:

* Create a backup
* Shut down containers

---

# 💾 Backup Behavior

Backups are:

* Timestamped
* Compressed (`.archive.gz`)
* Stored in the `backups/` folder
* Rotated automatically (keeps latest 5)

Example backup filename:

```
backups/mongo_20260222_184530.archive.gz
```

Even if you run:

```bash
docker compose down -v
```

Backups are safe because they live on your host filesystem, not inside Docker volumes.

---

# 🔄 Restoring Data

## Restore Latest Backup

```bash
./run_app.pl restore
```

This will:

1. Start Mongo if not running
2. Drop existing database contents
3. Restore from the most recent backup

---

## Restore From Specific Backup

```bash
./run_app.pl restore backups/mongo_20260222_184530.archive.gz
```

The script will:

* Start containers
* Drop the database
* Restore from the specified archive

---

# ⚠️ Important Notes

### 1. Backups Occur Only When Using the Script

If you manually run:

```bash
docker compose down
```

No backup will occur.

Always use:

```
./run_app.pl stop
```

or stop via Ctrl+C when started with `run_app.pl start`.

---

### 2. Backup Rotation

By default, only the most recent 5 backups are kept.

You can adjust this in `run_app.pl`:

```perl
my $max_backups = 5;
```

---

### 3. Restores Use `--drop`

Restores use:

```
mongorestore --drop
```

This completely replaces existing data.

---

# 🧠 Recommended Safe Workflow

Before risky changes:

```
./run_app.pl stop
```

After changes:

```
./run_app.pl start
```

If something breaks:

```
./run_app.pl restore
```

---

# 🔧 Manual Backup (Optional)

If you ever want to manually create a backup without stopping:

```bash
docker exec reminder_mongo mongodump --archive --gzip > backups/manual_backup.archive.gz
```

---

# 🏆 Summary

This project now includes:

* Persistent Mongo volume
* Automatic timestamped backups
* Backup rotation
* Safe shutdown procedure
* One-command restore
* Immunity from accidental `docker compose down -v` data loss
