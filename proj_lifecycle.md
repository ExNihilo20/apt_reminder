
# Appointment Reminder API

This project runs a Dockerized FastAPI + MongoDB backend with a production-mode Keycloak (Postgres-backed) identity provider.

The application lifecycle (start, stop, backup, restore) is managed through a custom Perl script: `run_app.pl`.

This ensures:

- Automatic Mongo backups on shutdown  
- Automatic Keycloak realm exports on shutdown  
- Rotating backups (keeps last 5)  
- Full restore capability (Mongo + Keycloak)  
- Postgres bind-mounted persistence  
- Protection from accidental `docker compose down -v`  
- Full disaster recovery validation  

---

## NOTE:
Run this to give yourself ownership of the keycloak db if applicable:
```bash
sudo chown -R $USER:$USER ../keycloak_db
```
`You only need to run this command once.` Doing this allows the database folder and contents to be deleted for a safe re-creation in the event a restore is required. 

# 📦 Project Structure

```

apt_reminder_proj/
│
├── backups/               # Mongo backups (host filesystem)
├── keycloak_backups/      # Keycloak realm exports
├── keycloak_db/           # Postgres data (bind mount persistence)
│
└── apt_reminder/
├── run_app.pl
├── docker-compose.yml
└── ...

````

---

# 🔐 Data Architecture

| Component | Persistence Type       | Survives `down -v` | Backup Strategy |
|-----------|------------------------|--------------------|-----------------|
| Mongo     | Named Docker volume    | ❌                 | `mongodump`     |
| Keycloak  | Postgres bind mount    | ✅                 | Realm export    |
| Postgres  | Host directory         | ✅                 | Realm export    |

Containers are fully disposable.

---

# 🚀 Starting the Application

```bash
./run_app.pl start
````

This will:

1. Build Docker images
2. Start containers in detached mode
3. Return control to terminal

View logs:

```bash
docker compose logs -f
```

---

# 🛑 Stopping the Application

```bash
./run_app.pl stop
```

This will:

1. Create Mongo backup
2. Export all Keycloak realms to JSON
3. Rotate backups (keep last 5)
4. Stop containers

Backups are skipped safely if containers are not running.

---

# 💾 Backup Locations

## Mongo

```
../backups/
  mongo_YYYYMMDD_HHMMSS.archive.gz
```

## Keycloak

```
../keycloak_backups/
  keycloak_YYYYMMDD_HHMMSS.json
```

Both are stored outside Docker volumes and outside the application directory.

---

# 🔄 Restoring Data

## Restore Latest Backups

```bash
./run_app.pl restore
```

This will:

1. Restore Mongo from latest archive
2. Reset Postgres data directory
3. Restart containers
4. Import latest Keycloak realm export

Full system state is restored automatically.

---

## Restore Specific Mongo Backup

```bash
./run_app.pl restore ../backups/mongo_20260222_184530.archive.gz
```

Keycloak restore still uses the latest realm export unless customized.

---

# 🧪 Disaster Recovery Validation

The stack has been tested against:

* `docker compose down`
* `docker compose down -v`
* Container removal
* Container recreation
* Postgres data wipe
* Full Mongo wipe

All state is recoverable via:

```bash
./run_app.pl restore
```

---

# ⚠️ Important Notes

## 1. Use the Script for Lifecycle Management

Manual `docker compose down` does not create backups.

Always use:

```bash
./run_app.pl stop
```

---

## 2. Backup Rotation

Only the most recent 5 backups are retained.

Adjust in `run_app.pl`:

```perl
my $max_backups = 5;
```

---

## 3. Mongo Restores Use `--drop`

Mongo restore uses:

```
mongorestore --drop
```

All existing collections are replaced.

---

## 4. Keycloak Restore Resets Postgres

During restore:

* Postgres data directory is cleared
* Containers restart
* Realm JSON is imported

This ensures clean state restoration.

---

## 🧾 Keycloak Backup Scope

Keycloak backups use realm export (kc.sh export) and include:

- Realms
- Clients
- Roles
- Users
- User credentials (realm-managed)
- Mappers and protocol settings

They do not include:
- Internal Infinispan cache state
- Runtime cluster state

Realm exports are portable and version-safe across container rebuilds.

## 🔁 Restore Specific Keycloak Backup (Optional)

By default, ./run_app.pl restore restores:

- Latest Mongo backup
- Latest Keycloak realm export

To manually import a specific Keycloak backup:
```bash
docker cp ../keycloak_backups/keycloak_YYYYMMDD_HHMMSS.json reminder_keycloak:/tmp/import.json

docker exec reminder_keycloak \
  /opt/keycloak/bin/kc.sh import --file /tmp/import.json
```

# 🧠 Recommended Workflow

Before risky changes:

```bash
./run_app.pl stop
```

After changes:

```bash
./run_app.pl start
```

If something breaks:

```bash
./run_app.pl restore
```


