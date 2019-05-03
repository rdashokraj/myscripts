#!/usr/bin/python
import commands, platform, os, socket, re
import subprocess as sub

#################GetNetworkdetials#############
def gethip(overs):
        ipadd,etval=[],[]
        i=0
        ifcfg=sub.Popen(["ifconfig","-a"], stdout=sub.PIPE).communicate()[0]

        for lines in ifcfg.splitlines():
           if "inet " in lines:
                if "7." in overs:
                        ipadd.append(lines.split()[1])
                        etval.append(oline.split(":")[0])
                else:
                        x=lines.split(":")[1]
                        ipadd.append(x.split()[0])
                        etval.append(oline.split()[0])
           elif "bond" in lines.lower():
                        i=i+1
           oline=lines
        if i>0:
        #print "Any Network bonding configured ?: Yes"
           nbonding="Yes"
        else:
        #print "Any Network bonding configured ?: No"
           nbonding="No"
        return etval,ipadd,nbonding
##################PrimaryNICDetials############
def primaryint():
        netstat=os.popen("netstat -rn").readlines()

        pet=netstat[2].split()[-1]

        for val in netstat:
           if "UG" in val:
                gway=val.split()[1]
           if pet in val and "10." in val.split()[0]:
                nmask=val.split()[2]
        return pet,gway,nmask
##################AddressingMode##############
def getamode(pet):
        ifcfg=("ifcfg-%s") %pet
        os.chdir("/etc/sysconfig/network-scripts/")
        f=open(ifcfg, 'r')
        try:
           for lines in f.readlines():
              if "BOOTPROTO=" in lines:
                addm=lines.rstrip().split("=")[1]
        finally:
           f.close()
        return addm
##################List of open ports###########
def getopenport():
        portv=[]
        nmapv=os.popen("nmap localhost").readlines()
        for val in nmapv:
           if "/tcp" in val:
                portv.append(val.split("/")[0])
        if len(portv) == 0:
                outport = bcolors.CRITICAL +"Check if nmap package is installed"+ bcolors.ENDC
        else:
                outport = portv
        return outport

##################CPU Utilzation###############
def getcpuutilization(hostname):
        mpstat=sub.Popen(["mpstat","1","2"], stdout=sub.PIPE).communicate()[0]

        for line in mpstat.splitlines():
           if "Average" in line:
                a=map(float,line.split()[2:])

        cpu_u=a[0]+a[2]+a[3]+a[4]+a[5]
        #print cpu_u

        if cpu_u > 80:
           cpustatus= bcolors.CRITICAL + "Critical utilization is more is 80%" + bcolors.ENDC

        elif cpu_u > 75 and cpu_u < 80:
           cpustatus= bcolors.WARNING + "High utilization is more is 75%" + bcolors.ENDC

        else:
           cpustatus= bcolors.OKGREEN + "Normal utilization minimal" + bcolors.ENDC
        return cpustatus
############Memory Utilization###################
def getmemstat(Total_M, Actual_M):
   Phy_Mem_sl=70
   Phy_Mem_hl=85
   Total_Mem_llimit = (Total_M * Phy_Mem_sl) /100
   Total_Mem_hlimit = (Total_M * Phy_Mem_hl) /100

   if Actual_M > Total_Mem_hlimit:
      memstatus = bcolors.CRITICAL + "Critical-utilization is more than 85%" + bcolors.ENDC
   elif Actual_M > Total_Mem_llimit and Actual_M < Total_Mem_hlimit:
      memstatus = bcolors.WARNING + "High-utilization is more than 70%" + bcolors.ENDC
   else:
      memstatus = bcolors.OKGREEN + "Normal-utilization minimal" + bcolors.ENDC
   return memstatus
############Swap Utiliztation###################
def getswapstat(Total_S, Sawp_Avail):
   Swap_Util_Diff= Total_S - Sawp_Avail
   Swap_Mem_sl=50
   Swap_Mem_hl=70
   Total_Swap_llimit = (Total_S * Swap_Mem_sl) /100
   Total_Swap_hlimit = (Total_S * Swap_Mem_hl) /100

   if Swap_Util_Diff > Total_Swap_hlimit:
      swapstatus = bcolors.CRITICAL + "Critical-utilization is more than 70%" + bcolors.ENDC
   elif Swap_Util_Diff > Total_Swap_llimit and Swap_Util_Diff < Total_Swap_hlimit:
      swapstatus = bcolors.WARNING + "High-utilization is more than 50%" + bcolors.ENDC
   else:
      swapstatus = bcolors.OKGREEN + "Normal-utilization minimal" + bcolors.ENDC

   return swapstatus
##################KErnel Paging################
def getpagestat():
        mafault='10'
        pstat=os.popen('sar -B').readlines()[-2].split()[-1]
        #print pstat
        if pstat > mafault:
           kpagestat= bcolors.CRITICAL + "Critical - System reported with faults" + bcolors.ENDC
        else:
           kpagestat= bcolors.OKGREEN + "Normal" + bcolors.ENDC
        return kpagestat
##################Network Errors###############
def getnetwrkstat():
        mival='0000'
        peth=os.popen("netstat -rn").readlines()[2].split()[-1]
        #print peth

        nvalue=os.popen('netstat -i').readlines()[2].split()[3:9]
        nerr=nvalue[0]+nvalue[1]+nvalue[4]+nvalue[5]

        #print nerr,
        if nerr == mival:
           networkstat = bcolors.OKGREEN +"No error" + bcolors.ENDC
        else:
           networkstat = bcolors.CRITICAL + "Error reported" + bcolors.ENDC

        return networkstat
##################Context switching############
def getconetextswitichingstat():
        macsw='6000'
        cswstat=os.popen('sar -w').readlines()[-2].split()[-1]
#	print cswstat , macsw
        if float(cswstat) > int(macsw) :
           cs_stat=bcolors.CRITICAL +  "Critical - Context S/w is more than %s" %macsw + bcolors.ENDC
        else:
           cs_stat=bcolors.OKGREEN + "Normal" + bcolors.ENDC
        return cs_stat
##################Tcp Coonection###############
def gettcpconn():
        tval=[]
        cmd=("lsof -i @%s:1-65535 -R") %hostname
        tcpv=os.popen(cmd).readlines()
        for val in tcpv:
           if "TCP" in val.upper():
                  tval.append(val)
        if len(tval) == 0:
           tcpconn = bcolors.CRITICAL + "Check if lsof package is installed" + bcolors.ENDC
        else:
           tcpconn=len(tval)
        return tcpconn
##################Read Only FS#################
def getrostat():
        mout=os.popen("cat /proc/mounts").readlines()
        roval=[]
        for val in mout:
           if "ro," in val:
                roval.append(val)

        if len(roval) > 0:
           rostat="Yes"
        else:
           rostat="No"
        return rostat
##################Direct Root Acess############
def getdrootacess():
        sshprlogin,sshprotocal="-","-"
        os.chdir("/etc/ssh")
        f=open("sshd_config",'r')
        try:
           for line in f.readlines():
                if "#PermitRootLogin" in line.split(' ')[0]:
                   #sshprlogin=line.split(' ')
                   sshprlogin="No"
                elif "PermitRootLogin" == line.rstrip().split(' ')[0]:
                   sshprlogin="Yes"
                else:
                   sshprlogin="No"


                if "#Protocol" in line:
                   sshprotocal="-"
                elif "Protocol" in line:
                   sshprotocal=line.rstrip().split(' ')[1]
                #else:
                #   sshprotocal="-"
        finally:
           f.close()
        return sshprlogin,sshprotocal
##################Firewall status##############
def getfirewallstat(overs):
        if "7." in overs:
           iptab = sub.Popen(["systemctl","status","firewalld"], stdout=sub.PIPE).communicate()[0]
           checkip = re.findall(r'inactive',iptab.lower(),re.MULTILINE)
           #print checkip
           if not checkip:
                sfirewall="Enabled"
           else:
                sfirewall="disabled"

        else:
           iptab = sub.Popen(["chkconfig","--list","iptables"], stdout=sub.PIPE).communicate()[0]
           if iptab.find("on") >= 0:
                sfirewall="Enabled"
           else:
                sfirewall="disabled"
        return sfirewall

##################Selinux Stat#################
def getselinuxstat():
        if os.path.exists("/etc/selinux/config"):
           os.chdir("/etc/selinux/")
           f=open("config", 'r')
           try:
                for line in f.readlines():
                   if "SELINUX=" in line.split(" ")[0]:
                       slstat=line.rstrip().split("=")[1]
           finally:
                f.close()
        else:
           slstat="/etc/selinux/config file is not Found"
        return slstat
##################UID details##################
def getuiddetials():
        if os.path.exists("/etc/passwd"):
           os.chdir("/etc")
           f=open("passwd", 'r')
           try:
                for line in f.readlines():
                   if line.split(":")[2] is '0':
                          if line.split(":")[0] is 'root':
                                udetilas="root"
                          else:
                                udetilas=line.split(":")[0]
           finally:
                f.close()
        return udetilas
##################IP6 status###################
def getip6status():
        i=0
        if os.path.exists("/etc/sysconfig/network"):
           os.chdir("/etc/sysconfig/")
           f=open("network",'r')
           try:
                for line in f.readlines():
                   if "NETWORKING_IPV6" in line.split("=")[0]:
                      i=1
                   elif "#NETWORKING_IPV6" in line.split("=")[0]:
                      i=0
           finally:
                f.close()
           if i>0:
              return "No"
           else:
              return "Yes"
        else:
           return "/etc/sysconfig/network is not Found"
##################Load status##################
def getloadstat():
        cld=list(os.getloadavg())
        cload=["%.2f"%item for item in cld]
        nocores = int(commands.getoutput("cat /proc/cpuinfo | grep 'processor' | wc -l"))

        if cld[0] > nocores-2 and cld[0] < nocores+2:
                Lstatus=bcolors.OKGREEN + "Optimal Load" + bcolors.ENDC
        elif cld[0] < nocores+4 and cld[0] > nocores+2:
                Lstatus=bcolors.WARNING + "Slightly Overloaded" + bcolors.ENDC
        elif cld[0] > nocores+4:
                Lstatus=bcolors.WARNING + "System is Overloaded" + bcolors.ENDC
        else:
                Lstatus=bcolors.OKGREEN + "System is under utilized" + bcolors.ENDC
	#print cld[0]
	#print nocores
        return cload,Lstatus

##################Main#########################
if __name__ == '__main__':
   class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    CRITICAL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

   os.system('clear')
   if os.path.exists('/etc/redhat-release'):
        the_release = commands.getoutput('cat /etc/redhat-release')
   if os.path.exists('/etc/oracle-release'):
        the_release = commands.getoutput('cat /etc/oracle-release')

   hostname=socket.gethostname()

###########Menmory Infor############
   Mem_t = commands.getoutput('cat /proc/meminfo|egrep MemTotal|awk \'{print $2}\'')
   Mem_To = float (Mem_t)/1024/1024
   Mem_Av =  commands.getoutput('free -m | grep Mem| awk -F " " \'{print $4}\'')
   Mem_Available = float(Mem_Av)/1024
   if "7." in the_release:
        Mem_a = commands.getoutput('free -m | grep Mem| awk -F " " \'{print $3}\'')
        Mem_Act = float(Mem_a)/1024
   else:
        Mem_a = commands.getoutput('free -m| grep "buffers/cache" | awk \'{print $3}\'')
        Mem_Act = float(Mem_a)/1024
   Swap_T = commands.getoutput('cat /proc/meminfo|egrep SwapTotal | awk  \'{print $2}\'')
   Swap_Total = float(Swap_T)/1024/1024
   Swap_A =  commands.getoutput('cat /proc/meminfo|egrep SwapFree | awk  \'{print $2}\'')
   Swap_Available = float(Swap_A)/1024/1024
###########Network Info#############
   EthVal,IPVal,NBond=gethip(the_release)
   PriE,Gway,Nmask=primaryint()
   AdressingM=getamode(PriE)
   OpenP=getopenport()

##########System status#############
   ALoad,CLoadStat=getloadstat()
   UCpuStat=getcpuutilization(hostname)
   MemStat=getmemstat(Mem_To,Mem_Act)
   SwapStat=getswapstat(Swap_Total,Swap_Available)
   KPagingStat=getpagestat()
   NetworkE=getnetwrkstat()
   CWStat=getconetextswitichingstat()
   procount=len(os.popen('ps -A --no-headers').readlines())
   TCPConn=gettcpconn()
   ROStat=getrostat()

########Security Info################
   PRLogin,SProtocol=getdrootacess()
   FirewallStat=getfirewallstat(the_release)
   SeLStat=getselinuxstat()
   UIDZ=getuiddetials()
   IP6stat=getip6status()

###########################Print Statement#######################################

   print bcolors.HEADER + ("SYSYEM INFORMATION") + bcolors.ENDC + (9 * "\t"),
   print bcolors.HEADER + ("SYSTEM HEALTH STATUS") + bcolors.ENDC
   print ("------------------------") + (8 * "\t"),
   print ("------------------------")
   #print commands.getoutput('/usr/sbin/dmidecode| grep -A 2 "System Information"')

   print "Hostname\t\t\t\t" + ":  %-43s" %commands.getoutput('hostname'),
   print " Load Average Status \t\t:  " + CLoadStat

   print "Kernel Version\t\t\t\t" + ":  %-43s" %commands.getoutput('uname -r'),
   print " Load on the system \t\t:  %s" %ALoad

   print "Date\t\t\t\t\t" + ":  %-43s" %commands.getoutput('date'),
   print " CPU utilization \t\t:  " + UCpuStat

   print "Uptime\t\t\t\t\t" + ":  %-43s" %(commands.getoutput('uptime | awk -F "up " \'{print $2}\' | awk -F "," \'{print$1}\' ')),
   print " Memory Utilization \t\t:  "+MemStat

   print "OS Release\t\t\t\t" + ":  %-43s" %the_release,
   print " Swap Utilization \t\t:  "+SwapStat

   print "Manufacturer\t\t\t\t" + ":  %-43s" %commands.getoutput('dmidecode -s system-manufacturer'),
   print " Kernel Paging Status \t\t:  " + KPagingStat

   print "Model\t\t\t\t\t" + ":  %-43s" %commands.getoutput('dmidecode -s system-product-name'),
   print " Network errors \t\t\t:  " + NetworkE

##############CPU STATUS##############################
   print ("------------------------") + (8 * "\t"),
   print "Context Switching Status \t:  " + CWStat

   print bcolors.HEADER + ("CPU Information") + bcolors.ENDC + (10*"\t"),
   print "No. of Processes forked \t:  %s" %procount

   print ("------------------------") + (8*"\t"),
   print "Tot No. of TCP connects \t:  %s" %TCPConn

   print "CPU\t\t\t\t\t" + ":  %-43s" %commands.getoutput('cat /proc/cpuinfo | grep "model name"| uniq| awk -F ": " \'{print $2}\' | awk -F " " \'{print $1" "$2" "$3" "$4}\''),
   print " Any FS in Read-Only Mode? \t:  " + ROStat

   print ("CPU Architecture\t\t\t:  " + platform.architecture()[0])
   print ("No of CPU's\t\t\t\t:  " + commands.getoutput('cat /proc/cpuinfo | grep processor| wc -l'))
   print ("CPU MHz\t\t\t\t\t:  " + commands.getoutput('cat /proc/cpuinfo | grep "model name"| uniq| awk -F ": " \'{print $2}\'| awk -F "@ " \'{print $2}\' '))

##############Memory Status###########################
   print ("------------------------") + (8 * "\t"),
   print ("------------------------")
   print bcolors.HEADER + ("MEMORY INFORMATION") + bcolors.ENDC + (9 * "\t"),
   print bcolors.HEADER + ("SYSTEM SECURITY STATUS") + bcolors.ENDC
   print ("------------------------") + (8 * "\t"),
   print ("------------------------")

   print ('Total Physical Memory(GB)\t\t')+":  %-43.2f" %Mem_To,
   print " Direct Root SSH access blocked ?:  "+PRLogin

   print ('Free Memory Available\t\t\t' +":  %-43.2f" %Mem_Available),
#   print " SSH using Protocol Version '2' ?:  "+SProtocol#
   print " Selinux \t\t\t:  " +SeLStat

   print ("Hugepagessize\t\t\t\t") + ":  %-43s" %commands.getoutput('cat /proc/meminfo|egrep Hugepagesize|awk \'{print $2}\''),
   print " Firewall \t\t\t:  " +FirewallStat

   print ('Total Swap Memory(GB)\t\t\t')+ ":  %-43.2f" %Swap_Total,
   print " Is IPv6 Disabled ? \t\t:  " +IP6stat
#   print " Selinux \t\t\t:  " +SeLStat

   print ('Available Swap Memory(GB)\t\t') + ":  %-43.2f" %Swap_Available,
   if "root" == UIDZ:
        print " Non-root user has UID set to 0 ?:  No"
   else:
        print " Non-root user has UID set to 0 ?:  Yes"



################NetwrokInfo#################

   print ("------------------------") + (8 * "\t")
#   print "Is IPv6 Disabled ? \t\t:  " +IP6stat

   print bcolors.HEADER + ("NETWORK INFORMATION") + bcolors.ENDC
   print ("------------------------")
   print "Primary Network Interface\t\t:  " +PriE
   print "Gateway Server IP\t\t\t:  " +Gway
   print "Subnet mask "+PriE+ "\t\t\t:  "+Nmask
   print "IP Addressing Mode\t\t\t:  "+AdressingM
   print "List of Opened ports\t\t\t:  %s" %OpenP
   print "Network bonding configured ?\t\t:  "+NBond
   i=0
   for val in EthVal:
#        print "%s\t\t\t\t\t:  %s" %(val,IPVal[i])
        print "%s \t\t: %s " %(val.rjust(29),IPVal[i])
        i=i+1

