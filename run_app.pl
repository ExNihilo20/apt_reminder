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
# Safe Shutdown
# -------------------------------------------------
sub safe_shutdown {
    create_backup();
    print "Stopping containers...\n";
    system("docker compose down");
}

# -------------------------------------------------
# Restore
# -------------------------------------------------
sub restore_backup {
    my ($file) = @_;

    unless ($file) {
        opendir(my $dh, $backup_dir) or die "No backups found.\n";
        my @files = sort grep { /\.archive\.gz$/ } readdir($dh);
        closedir($dh);

        die "No backups available.\n" unless @files;
        $file = File::Spec->catfile($backup_dir, $files[-1]);
        print "Restoring latest backup: $file\n";
    }

    unless (-f $file) {
        die "Backup file not found: $file\n";
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

    print "Restoring database from $file...\n";

    my $cmd = "docker exec -i $container mongorestore --archive --gzip --drop < $file";
    if (system($cmd) == 0) {
        print "Restore successful.\n";
    }
    else {
        die "Restore failed!\n";
    }
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