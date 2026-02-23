#!/usr/bin/perl
use strict;
use warnings;
use POSIX ":sys_wait_h";
use File::Path qw(make_path);
use File::Basename qw(dirname);
use File::Spec;
use Cwd 'abs_path';
use Time::Piece;

my $container   = "reminder_mongo";
my $max_backups = 5;

# Resolve script directory safely
my $script_dir = dirname(abs_path(__FILE__));
my $backup_dir = File::Spec->catdir($script_dir, "..", "backups");

# keycloak backups
my $keycloak_container = "reminder_keycloak";
my $kc_backup_dir = File::Spec->catdir($script_dir, "..", "keycloak_backups");

my $command = shift @ARGV || "start";

if ($command eq "start") {
    start_app();
}
elsif ($command eq "stop") {
    safe_shutdown();
}
elsif ($command eq "restore") {
    my $file = shift @ARGV;
    restore_backup($file);
}
else {
    print_usage();
}

# -------------------------------------------------
# Utility: check if container is running
# -------------------------------------------------
sub container_running {
    my $status = `docker inspect -f '{{.State.Running}}' $container 2>/dev/null`;
    chomp $status;
    return $status eq "true";
}

# -------------------------------------------------
# Start Application (Detached Mode)
# -------------------------------------------------
sub start_app {

    make_path($backup_dir) unless -d $backup_dir;

    print "Building containers...\n";
    system("docker compose build") == 0
        or die "Failed to build containers\n";

    print "Starting containers in detached mode...\n";
    system("docker compose up -d") == 0
        or die "Failed to start containers\n";

    print "Application started.\n";
}

# -------------------------------------------------
# Backup
# -------------------------------------------------
sub create_backup {

    unless (container_running()) {
        print "Mongo container not running. Skipping backup.\n";
        return 0;
    }

    make_path($backup_dir) unless -d $backup_dir;

    my $timestamp = localtime->strftime('%Y%m%d_%H%M%S');
    my $backup_file = File::Spec->catfile(
        $backup_dir,
        "mongo_$timestamp.archive.gz"
    );

    print "Creating backup: $backup_file\n";

    my $cmd = "docker exec $container mongodump --archive --gzip > $backup_file";
    my $result = system($cmd);

    if ($result == 0 && -s $backup_file) {
        print "Backup successful.\n";
        rotate_backups();
        return 1;
    }
    else {
        print "Backup failed or file empty!\n";
        unlink $backup_file if -f $backup_file;
        return 0;
    }
}

# -------------------------------------------------
# Rotate Backups
# -------------------------------------------------
sub rotate_backups {

    opendir(my $dh, $backup_dir) or return;
    my @files = sort grep { /\.archive\.gz$/ } readdir($dh);
    closedir($dh);

    while (@files > $max_backups) {
        my $oldest = shift @files;
        unlink File::Spec->catfile($backup_dir, $oldest);
        print "Deleted old backup: $oldest\n";
    }
}

# -------------------------------------------------
# Keycloak Backup (Realm Export)
# -------------------------------------------------
sub create_keycloak_backup {

    make_path($kc_backup_dir) unless -d $kc_backup_dir;

    my $timestamp = localtime->strftime('%Y%m%d_%H%M%S');
    my $backup_file = File::Spec->catfile(
        $kc_backup_dir,
        "keycloak_$timestamp.json"
    );

    print "Creating Keycloak realm export: $backup_file\n";

    my $tmp_file = "/tmp/keycloak_export.json";

    # Export all realms
    my $export_cmd = "docker exec $keycloak_container ".
                     "/opt/keycloak/bin/kc.sh export ".
                     "--file $tmp_file ".
                     "--users realm_file";

    if (system($export_cmd) != 0) {
        print "Keycloak export failed!\n";
        return 0;
    }

    # Copy export out of container
    my $copy_cmd = "docker cp $keycloak_container:$tmp_file $backup_file";
    if (system($copy_cmd) != 0) {
        print "Failed to copy Keycloak export!\n";
        return 0;
    }

    # Cleanup temp file
    system("docker exec $keycloak_container rm -f $tmp_file");

    if (-s $backup_file) {
        print "Keycloak backup successful.\n";
        rotate_keycloak_backups();
        return 1;
    } else {
        print "Keycloak backup file empty!\n";
        unlink $backup_file if -f $backup_file;
        return 0;
    }
}

# -------------------------------------------------
# Rotate Keycloak Backups
# -------------------------------------------------
sub rotate_keycloak_backups {

    opendir(my $dh, $kc_backup_dir) or return;
    my @files = sort grep { /\.json$/ } readdir($dh);
    closedir($dh);

    while (@files > $max_backups) {
        my $oldest = shift @files;
        unlink File::Spec->catfile($kc_backup_dir, $oldest);
        print "Deleted old Keycloak backup: $oldest\n";
    }
}

# -------------------------------------------------
# Restore Keycloak Realm
# -------------------------------------------------
sub restore_keycloak_backup {

    my ($kc_file) = @_;

    unless ($kc_file) {
        opendir(my $dh, $kc_backup_dir) or die "No Keycloak backups found.\n";
        my @files = sort grep { /\.json$/ } readdir($dh);
        closedir($dh);

        die "No Keycloak backups available.\n" unless @files;
        $kc_file = File::Spec->catfile($kc_backup_dir, $files[-1]);
        print "Restoring latest Keycloak backup: $kc_file\n";
    }

    unless (-f $kc_file) {
        die "Keycloak backup file not found: $kc_file\n";
    }

    print "Stopping containers before Keycloak restore...\n";
    system("docker compose down");

    # Wipe Postgres data directory (this resets Keycloak DB)
    my $pg_data_dir = File::Spec->catdir($script_dir, "..", "keycloak_db");
    print "Clearing Postgres data directory: $pg_data_dir\n";
    system("rm -rf $pg_data_dir/*");

    print "Restarting containers for Keycloak import...\n";
    system("docker compose up -d");

    print "Waiting for Keycloak to be ready...\n";
    sleep 10;  # simple wait; can improve later

    # Copy JSON into container
    my $tmp_path = "/tmp/keycloak_import.json";
    system("docker cp $kc_file $keycloak_container:$tmp_path");

    print "Importing Keycloak realm...\n";

    my $import_cmd = "docker exec $keycloak_container ".
                     "/opt/keycloak/bin/kc.sh import ".
                     "--file $tmp_path";

    if (system($import_cmd) == 0) {
        print "Keycloak restore successful.\n";
        system("docker exec $keycloak_container rm -f $tmp_path");
    } else {
        die "Keycloak restore failed!\n";
    }
}

# -------------------------------------------------
# Safe Shutdown
# -------------------------------------------------
sub safe_shutdown {

    create_backup();           # Mongo
    create_keycloak_backup();  # Keycloak

    print "Stopping containers...\n";
    system("docker compose down");
}

# -------------------------------------------------
# Restore
# -------------------------------------------------
sub restore_backup {

    my ($mongo_file) = @_;

    # --------------------------
    # Restore Mongo
    # --------------------------
    unless ($mongo_file) {
        opendir(my $dh, $backup_dir) or die "No Mongo backups found.\n";
        my @files = sort grep { /\.archive\.gz$/ } readdir($dh);
        closedir($dh);

        die "No Mongo backups available.\n" unless @files;
        $mongo_file = File::Spec->catfile($backup_dir, $files[-1]);
        print "Restoring latest Mongo backup: $mongo_file\n";
    }

    unless (-f $mongo_file) {
        die "Mongo backup file not found: $mongo_file\n";
    }

    print "Starting containers for restore...\n";
    system("docker compose up -d");

    print "Waiting for Mongo to be ready...\n";
    my $retries = 10;
    while ($retries--) {
        last if container_running();
        sleep 1;
    }

    unless (container_running()) {
        die "Mongo container failed to start.\n";
    }

    print "Restoring Mongo database...\n";

    my $cmd = "docker exec -i $container mongorestore --archive --gzip --drop < $mongo_file";
    die "Mongo restore failed!\n" unless system($cmd) == 0;

    print "Mongo restore successful.\n";

    # --------------------------
    # Restore Keycloak
    # --------------------------
    restore_keycloak_backup();
}

# -------------------------------------------------
# Usage
# -------------------------------------------------
sub print_usage {
    print <<EOF;
Usage:
  ./run_app.pl start          # build + run (detached)
  ./run_app.pl stop           # backup + stop
  ./run_app.pl restore        # restore latest backup
  ./run_app.pl restore <file> # restore specific backup
EOF
}