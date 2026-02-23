#!/usr/bin/perl
use strict;
use warnings;
use POSIX ":sys_wait_h";
use File::Path qw(make_path);
use File::Basename;
use Time::Piece;

my $container   = "reminder_mongo";
my $backup_dir  = "backups";
my $max_backups = 5;  # number of backups to keep

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

# ----------------------------
# Start Application
# ----------------------------
sub start_app {
    make_path($backup_dir) unless -d $backup_dir;

    print "Building containers...\n";
    system("docker compose build") == 0
        or die "Failed to build containers\n";

    print "Starting containers...\n";

    my $pid = fork();
    die "Fork failed\n" unless defined $pid;

    if ($pid == 0) {
        exec("docker compose up");
        exit(0);
    }

    $SIG{INT} = sub {
        print "\nCaught Ctrl+C\n";
        backup_and_shutdown($pid);
    };

    $SIG{TERM} = sub {
        backup_and_shutdown($pid);
    };

    waitpid($pid, 0);
}

# ----------------------------
# Backup Function
# ----------------------------
sub create_backup {
    my $timestamp = localtime->strftime('%Y%m%d_%H%M%S');
    my $backup_file = "$backup_dir/mongo_$timestamp.archive.gz";

    print "Creating backup: $backup_file\n";

    my $cmd = "docker exec $container mongodump --archive --gzip > $backup_file";
    if (system($cmd) == 0) {
        print "Backup successful.\n";
        rotate_backups();
    } else {
        print "Backup failed!\n";
    }
}

# ----------------------------
# Rotate Backups
# ----------------------------
sub rotate_backups {
    opendir(my $dh, $backup_dir) or return;
    my @files = sort grep { /\.archive\.gz$/ } readdir($dh);
    closedir($dh);

    while (@files > $max_backups) {
        my $oldest = shift @files;
        unlink "$backup_dir/$oldest";
        print "Deleted old backup: $oldest\n";
    }
}

# ----------------------------
# Safe Shutdown
# ----------------------------
sub backup_and_shutdown {
    my ($compose_pid) = @_;

    create_backup();

    print "Stopping containers...\n";
    system("docker compose down");

    kill 'TERM', $compose_pid if $compose_pid;
    exit(0);
}

sub safe_shutdown {
    create_backup();
    system("docker compose down");
}

# ----------------------------
# Restore Function
# ----------------------------
sub restore_backup {
    my ($file) = @_;

    unless ($file) {
        opendir(my $dh, $backup_dir) or die "No backups found.\n";
        my @files = sort grep { /\.archive\.gz$/ } readdir($dh);
        closedir($dh);

        die "No backups available.\n" unless @files;
        $file = "$backup_dir/" . $files[-1];
        print "Restoring latest backup: $file\n";
    }

    unless (-f $file) {
        die "Backup file not found: $file\n";
    }

    print "Restoring database from $file...\n";

    system("docker compose up -d");
    sleep 3;  # give mongo time to start

    my $cmd = "docker exec -i $container mongorestore --archive --gzip --drop < $file";
    if (system($cmd) == 0) {
        print "Restore successful.\n";
    } else {
        print "Restore failed!\n";
    }
}

# ----------------------------
# Usage
# ----------------------------
sub print_usage {
    print <<EOF;
Usage:
  ./run_app.pl start          # build + run
  ./run_app.pl stop           # backup + stop
  ./run_app.pl restore        # restore latest backup
  ./run_app.pl restore <file> # restore specific backup
EOF
}