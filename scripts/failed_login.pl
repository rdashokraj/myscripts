#!/usr/bin/perl -w
# Description           :  Upon execution, this script will list all the Failed Login attempts on a Linux Server
# Mode of Execution     :  As 'root' user from shell prompt
# Developed by          :  Ashok Raj
# Version               :  1.2
# Last updated on	:  5th june 2011
# --------------------------------------------------------------------------------------------------------------

$osnam=`uname -s`;
chomp($osnam);
$cnt=0;

if($osnam eq 'Linux')
{
chdir "/var/log" or die "$!";
@arylog = `cat ./secure*|grep 'Failed password'`;
print "\n";
print "REPORT ON FAILED LOGIN ATTEMPTS\n\n";
print "DATE/TIME          USERNAME\t  HOSTNAME/IPADDRESS\n";
print "-----------------------------------------------------\n";
foreach(@arylog)
 {
 if($_ =~ m/(\w+\s+\d+\s\d\d:\d\d:\d\d)\s\S+\ssshd\[\d+\]:\s+Failed\s.*?\sfor.*?\s(\w+)\sfrom\s+(\S+)/)
            {
              printf "%-16s   %-16s%-14s\n",$1,$2,$3;
              $cnt++;
            }
}
}
print "\nTotal Number of Failed Attempts: $cnt \n\n";


