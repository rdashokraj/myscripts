#!/usr/bin/perl
# Description       :   This script is used for mounting and un-mounting the NFS shares on several NFS clients.         |
#                       It takes List of NFS client servernames, NFS share, NFS share options as inputs and depends     |
#                       on User's choice, it either mounts or unmounts the Mount point specified. Incase if there is    |
#                       any problem in mounting/un-mounting, it reports the error and proceeds with next server.        |
#                       After performing the tasks in all the servers, it prints the final result on the screen.        |
# Mode of Execution :   Manual - from a centralized server which has password-less SSH access to NFS client machines.   |
# Author            :   Ashok Raj (arajamanikam@vmware.com)                                                             |
# Version           :   1.7                                                                                             |
# Last updated on   :   26th Feb 2013                                                                                   |
#-----------------------------------------------------------------------------------------------------------------------

# Declating the Variables
my $NfsServer;
our $NfsClientLists;
our $MntPoint;
my $NfsMountOptions;
my $NfsShare;
my $logFile;
my $choice;
our $user;
our $result;
my $outputDestination = LOGFILE;

# Declaring Sub-Routines
sub GetTime($);
sub Log($$$);
sub MountVolume($$$$$$);
sub UnMountVolume($$$);
sub RunSystemCmdByssh($$$);
sub ChkNfsSrvrStatus($$); 

# Clearing the screen
system $^O eq 'MSWin32' ? 'cls' : 'clear';

#Taking the NFS Client and Share details from User
printf "Enter your Name : ";
chomp($user=<STDIN>);

printf "You wish to Mount or Un-mount the NFS share ? \n";
do {
        printf "Enter 'M' for Mount or 'U' for Unmount : ";
        chomp($choice=<STDIN>);
   } until ($choice eq 'M' || $choice eq 'U');

if ( $choice eq 'M' ) {
        printf "\nEnter the NFS Share name with full path like following: <NFS Servername/IP>:<NFS share path> : ";
        chomp($NfsShare=<STDIN>);

        printf "Enter the NFS client mount options with comma seperated : \n";
        printf "Example: rw,sync,soft,bg,nolock\n";
        chomp($NfsMountOptions=<STDIN>);

        printf "Enter the Filename that contains the list of NFS Client ServerNames : ";
        chomp($NfsClientLists=<STDIN>);

        printf "Enter the Mount point : ";
        chomp($MntPoint=<STDIN>);

        if( $NfsShare =~ m/^(\S+):\/\w+.*$/ ) { $NfsServer = "$1"; }
}
else {
        printf "Enter the Filename that contains the list of NFS Client ServerNames : ";
        chomp($NfsClientLists=<STDIN>);

        printf "Enter the Mount point : ";
        chomp($MntPoint=<STDIN>);
}

# Creating a temporary file to track all the changes
if ( ! -d "/var/log/nfs" ) {
        system("mkdir /var/log/nfs");
}
$logFile = "/var/log/nfs/".GetTime(1)."\_"."$user"."\.log";
print "Logging NFS mount details to $logFile\n";

# Open the log file
open(LOGFILE,">$logFile") || die (print "Cannot create logfile $logFile \n");

# Starting the loop
open(IN, "$NfsClientLists") or die "Cannot open the NFS client list file ($!)";

if($choice eq 'M') {
    while (<IN>) {
        chomp($_);
        my $item = $_;
        if(MountVolume($item,$NfsServer,$NfsShare,$MntPoint,$NfsMountOptions,LOGFILE) == '0') {
		my @fstab = `ssh $item -C cat /etc/fstab`;
                my $qtMntPoint=quotemeta($MntPoint);
		my $currentTime = &GetTime(2);
		push(@fstab, "\n#NFS entry added by $user on $currentTime\n$NfsShare\t$MntPoint\tnfs\t$NfsMountOptions\t0\ 0\n") unless grep /^( *[^\t\s#][^\t]*\t)$qtMntPoint/, @fstab;
		system("cat /dev/null > /opt/fstabtmp");
		open (OUT, '>/opt/fstabtmp')  or die "Cannot open the /etc/fstab file ($!) for writing";
		print OUT @fstab;
		close (OUT) or die "$!";
		system("scp /opt/fstabtmp $item:/etc/fstab");
	}
    }
}
else {
        while (<IN>) {
        chomp($_);
        my $item = $_;
        if (UnMountVolume($item,$MntPoint,LOGFILE) == '0') {
		my @fstab = `ssh $item -C cat /etc/fstab`;
                my $qtMntPoint=quotemeta($MntPoint);
		grep s/^( *[^\t\s#][^\t]*\t)$qtMntPoint/# $1$MntPoint/, @fstab;
                open (OUT, '>/opt/fstabtmp')  or die "$!";
                print OUT @fstab;
                close (OUT) or die "$!";
		Log("Updating /etc/fstab on $item ",0,$outputDestination);
		system("scp /opt/fstabtmp $item:/etc/fstab");
        }
        else {
                next;
        }
    }
}

close("LOGFILE");

printf "\n\nTask completed for all the Servers in the given list\n";
system("sleep 2");
printf "\nLet me display the summary of task completion for you.....Clearing the screen. \n\n";
system("sleep 3");
system $^O eq 'MSWin32' ? 'cls' : 'clear';
open(RES, "$logFile") or die "Couldn't open the Log file $logFile : $! ";
while(<RES>) {
	 if($_ =~ m/Successfully\smounted\s\S+\sto\s\S+\son\s(\S+)/) {
		my $success = "$1";
		push(@result, "$success");
	 }
	 if($_ =~ m/Successfully\sUnmounted\s\S+\sFile-system\son\s(\S+)/) {
		my $success = "$1";
		push(@result, "$success");
	 }
}
if($choice eq 'M') {
	printf "\nLIST OF NFS CLIENTS SUCCESSFULLY MOUNTED\n";
	printf "----------------------------------------\n";
	my $finresult = join ("\n", @result);
	my $finressize = length($finresult);
	if ($finressize > "1") { print "$finresult\n"; }
	else { print "No Servers\n\n"; }
}
elsif($choice eq 'U') {
	printf "LIST OF SERVERS WHERE THE MOUNT-POINT $MntPoint SUCCESSFULLY UN-MOUNTED\n";
	printf "-----------------------------------------------------------------------------\n";
	my $finresult = join ("\n", @result);
	my $finressize = length($finresult);
	if ($finressize > "1") { print "$finresult\n"; }
	else { print "No Servers\n\n"; }
}

printf "\nLIST OF FAILED SERVERS \n";
open (FAIL, ">result.txt") or die "$!";
print FAIL join("\n", @result);
print FAIL "\n";
close(FAIL);	
my @lastopt = `diff -r $NfsClientLists result.txt`;
foreach my $i(@lastopt) {
	if($i =~ m/^<\s(\S+)$/) { print "$1\n"; }		
}
print "\n";
exit 0;

#---------------------------------------SUBROUTINES SECTION--------------------------------------

sub Log($$$)
{
    my $text = $_[0];
    my $exitStatus = $_[1];
    my $outputDestination = $_[2];
    my $time = GetTime(0);
    if ($exitStatus == 1)
    {
        my $time = GetTime(0);
        print "[$time] - $text\n";
                print "[$time] - Exiting the Program !\n\n";
        exit;
    }
    print $outputDestination "[$time] - $text\n";
    print "[$time] - $text\n";
}

sub GetTime($)
{
    my ($Second, $Minute, $Hour, $Day, $Month, $Year) = (localtime)[0,1,2,3,4,5];
    $Year = $Year+1900;
    $Month = $Month+1;
    my $Time = "$Month-$Day-$Year $Hour:$Minute:$Second";
    if ($_[0] == 1)
    {
        $Time = "$Month-$Day-$Year\_$Hour\_$Minute";
        return $Time;
    }
    if ($_[0] == 2)
    {
        $Time = "$Month/$Day/$Year";
        return $Time;
    }
    return $Time;
}

sub MountVolume($$$$$$)
{
        my $host = $_[0];
        my $nfsServer = $_[1];
        my $nfsShare = $_[2];
        my $mntPoint = $_[3];
        my $nfsMountOptions = $_[4];
        Log("Attempting to see the NFS share $nfsShare from $host",0,LOGFILE);
        if (ChkNfsSrvrStatus($host,$nfsServer) == 0) {
                Log("The NFS Server $nfsServer is responding. Proceeding further....",0,LOGFILE);
                my @mount = `ssh $host -C /bin/mount`;
        	if ( grep(/$mntPoint/, @mount) )
                {
                        Log("$mntPoint is already mounted on this system",0,$outputDestination);
			return 0;
                }
                else {
                   if (RunSystemCmdByssh("$host","ls $mntPoint",$outputDestination) != 0) { 
		 	&RunSystemCmdByssh("$host","mkdir $mntPoint",$outputDestination);
		   }
                   if (RunSystemCmdByssh("$host","/bin/mount -t nfs -o $nfsMountOptions $nfsShare $mntPoint",$outputDestination) != 0)
                   {
                      Log("Could not mount $nfsShare on $host:$mntPoint. Please check manually",0,$outputDestination);
		      return 1;
                   }
                   else {
                      Log("Successfully mounted $nfsShare to $mntPoint on $host",0,$outputDestination);
		      return 0;
                   }
             }
        }
        else
        {
                Log("$nfsShare volume is not visible.",0,LOGFILE);
                Log("Please check manually on the server $host",0,LOGFILE);
		return 1;
        }
}

sub UnMountVolume($$$)
{
        my $host = $_[0];
        my $mntPoint = $_[1];
        my $outputDestination = $_[2];
        my @mount = `ssh $host -C /bin/mount`;
        Log("Attempting to Unmount $mntPoint file system on $host ",0,$outputDestination);
        if ( grep(/$mntPoint/, @mount) )
        {
                if (RunSystemCmdByssh("$host","/bin/umount $mntPoint",$outputDestination) != 0)
                {
                        Log("Could not Unmount $mntPoint file-system on $host ",0,$outputDestination);
                        Log("Please check manually",1,$outputDestination);
			return 1;
                }
                else
                { 
                        Log("Successfully Unmounted $mntPoint File-system on $host ",0,$outputDestination);
			return 0;
                }
        }
        else
        {
                Log("$mntPoint is not mounted on $host, so didn't have to do anything",0,$outputDestination);
		return 1;	
        }
}


sub RunSystemCmdByssh($$$)
{
    my $host = $_[0];
    my $command = $_[1];
    my $outputDestination = $_[2];
    my $exitStatus;
    my $commandOutput;
    Log("Executing command : ssh $host -C $command",0,$outputDestination);
    $commandOutput= `ssh $host -C $command`;
    chomp($commandOutput);
    $exitStatus = $?;
    Log("Output of command is : ",0,$outputDestination);
    Log("$commandOutput",0,$outputDestination);
    return($exitStatus);
}


sub ChkNfsSrvrStatus($$)
{
  my $host = $_[0];
  my $nfsServer = $_[1]; 
  my $exitStatus;
  my $nfStat=`ssh $host "rpcinfo -u $nfsServer nfs"`;
  $exitStatus = $?;
  return($exitStatus);
}

