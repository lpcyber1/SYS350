#Python Menu Script for interacting with vCenter by Liam Paul
#Imports
from pyVim.connect import SmartConnect
from pyVmomi import vim, vmodl
import ssl
import socket
import json
import getpass

def connect_vcenter():
    global content
    #Imports json file with connection information
    with open('/home/liam/SYS350/vcenter-conf.json', 'r') as file:
        data = json.load(file)
    s = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    s.verify_mode = ssl.CERT_NONE

    #Sets values for vcenter server and user to connect with
    vcenter_host = data['vcenterhost']
    vcenter_user = data['vcenteradmin']

    #Requests input for password of user connecting
    passw = getpass.getpass()

    #Just reiterates what values are being used
    print("Enter password for", vcenter_user)
    print("Connecting as:", vcenter_user, "to", vcenter_host)

    #Initiates connection
    si=SmartConnect(host=vcenter_host, user=vcenter_user, pwd=passw, sslContext=s)
    aboutInfo=si.content.about
    print(aboutInfo.fullName)
    content = si.content
    return content

def get_vm(vm):
    summary = vm.summary
    vm_name = summary.config.name
    state = summary.runtime.powerState
    cpus = summary.config.numCpu
    memory = summary.config.memorySizeMB / 1024 
    ip = summary.guest.ipAddress if summary.guest.ipAddress else "N/A"

    return {
        "VM Name": vm_name,
        "State": state,
        "Number of CPUs": cpus,
        "Memory": memory,
        "IP Address": ip
    }

#Function to search VM information
def Search_VMs(content):
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM or hit enter to return all VMs: ")
    vms = container.view

    if vm_name:  # If a VM name is provided
        found = False
        for vm in vms:
            if vm_name == vm.name:  # Checks for an exact match
                vm_info = get_vm(vm)
                print("Printing info on", vm.name)
                print(json.dumps(vm_info, indent=4))
                found = True
                break  # Stop after finding the first match
        if not found:
            print("No VM found with the name:", vm_name)
    else:
        print("Listing all VMs:")
        for vm in vms:
            vm_info = get_vm(vm)
            print(json.dumps(vm_info, indent = 4))
            print("-------------------------------")

#Function to show current connection information
def Current_Connection():
    
    #Gets source IP
    source_ip = socket.gethostbyname(socket.gethostname())
    
    #Imports json file with connection information
    with open('/home/liam/SYS350/vcenter-conf.json', 'r') as file:
        data = json.load(file)
    
    vcenter_server = data['vcenterhost']
    current_user = data['vcenteradmin']

    #Prints connection info
    print('---------------------------------------')
    print("Source IP is:", source_ip)
    print("Domain/User is:", current_user)
    print("vCenter Server is:", vcenter_server)
    print('---------------------------------------')
#Menu function
def Menu(): 
    print ("1. Connect to vCenter")
    print ("2. Search VMs")
    print ("3. Show Current Connection Information")
    print ("4. Quit")

#While loop to show menu
while True:
    Menu()
    choice = input("Enter an option(1-4): ")

    if choice == '1':
        print("Connecting to vCenter...")
        print('---------------------------------------')
        connect_vcenter()

    elif choice == '2':
        print("Search VMs has been selected")
        print('---------------------------------------')
        Search_VMs(content)
    
    elif choice == '3':
        print("Showing current connection information")
        Current_Connection()
    
    elif choice == '4':
        print("Quitting...")
        break
    else:
        print("Invalid choice, try again")