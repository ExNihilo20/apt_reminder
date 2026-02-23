# Appointment Reminder API

This project runs a Dockerized FastAPI + MongoDB backend for managing appointment reminder contacts.

The application lifecycle (start, stop, backup, restore) is managed through a custom Perl script: `run_app.pl`.

This ensures:

* Automatic timestamped backups on shutdown
* Rotating backups (keeps last 5)
* Restore capability from latest or specific backup
* Backups stored safely on the host filesystem (outside project directory)
* Protection from accidental `docker compose down -v` data loss

---

# 📦 Project Structure

```
apt_reminder_proj/
│
├── backups/                # Timestamped MongoDB backups (host filesystem)
│
└── apt_reminder/
    ├── run_app.pl
    ├── docker-compose.yml
    └── ...
```

Backups are stored in:

```
../backups/
  mongo_YYYYMMDD_HHMMSS.archive.gz
```

(Resolved relative to `run_app.pl`, independent of current working directory.)

---

# 🚀 Starting the Application

Build and start the application:

```bash
./run_app.pl start
```

This will:

1. Build Docker images
2. Start containers in **detached mode**
3. Return control to your terminal

To view logs:

```bash
docker compose logs -f
```

---

# 🛑 Stopping the Application

Stop safely with:

```bash
./run_app.pl stop
```

This will:

1. Create a timestamped Mongo backup (if Mongo is running)
2. Rotate old backups (keep last 5)
3. Run `docker compose down`

If Mongo is not running, backup is skipped safely.

---

# 💾 Backup Behavior

Backups are:

* Timestamped
* Compressed (`.archive.gz`)
* Stored in `../backups/` (outside project folder)
* Rotated automatically (keeps latest 5)
* Verified to ensure non-empty archive

Example backup filename:

```
../backups/mongo_20260222_184530.archive.gz
```

Even if you run:

```bash
docker compose down -v
```

Backups remain safe because they live outside Docker volumes and outside the project directory.

---

# 🔄 Restoring Data

## Restore Latest Backup

```bash
./run_app.pl restore
```

This will:

1. Start containers (if needed)
2. Wait for Mongo to be ready
3. Drop existing database contents
4. Restore from the most recent backup

---

## Restore From Specific Backup

```bash
./run_app.pl restore ../backups/mongo_20260222_184530.archive.gz
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
docker exec reminder_mongo mongodump --archive --gzip > ../backups/manual_backup.archive.gz
```

---
