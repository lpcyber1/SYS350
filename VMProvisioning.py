#Python Menu Script for interacting with vCenter by Liam Paul
#Imports
from pyVim.connect import SmartConnect
from pyVmomi import vim
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
    global summary # sets summary as a global variable to be used throughout script
    summary = vm.summary # summary of VM
    vm_name = summary.config.name # VM name
    state = summary.runtime.powerState # VM power state (on/off)
    cpus = summary.config.numCpu # VM cpu count
    memory = summary.config.memorySizeMB / 1024 # VM memory count 
    ip = summary.guest.ipAddress if summary.guest.ipAddress else "N/A" #VM IP address

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
    global vm_name
    vm_name = input("Enter the name of the VM or hit enter to return all VMs: ") # Asks for VM Name
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
            print(json.dumps(vm_info, indent = 4)) # Prints info on VM 
            print("-------------------------------")

#Function to show current connection information
def Current_Connection():
    
    #Gets source IP
    source_ip = socket.gethostbyname(socket.gethostname())
    
    #Imports json file with connection information
    with open('/home/liam/SYS350/vcenter-conf.json', 'r') as file:
        data = json.load(file)
    
    vcenter_server = data['vcenterhost'] # Pulls vcenter server name from config file
    current_user = data['vcenteradmin'] # Pulls vcenter username from config file

    #Prints connection info
    print('---------------------------------------')
    print("Source IP is:", source_ip)
    print("Domain/User is:", current_user)
    print("vCenter Server is:", vcenter_server)
    print('---------------------------------------')

def Power_On():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ") # Asks for VM Name
    vms = container.view

    if vm_name:  # If a VM name is provided
        found = False
        for vm in vms:
            if vm_name == vm.name:  # Checks for an exact match
                vm_info = get_vm(vm)
                if summary.runtime.powerState == "poweredOn": # Checks if VM is already powered on
                    print(vm_name, "is already powered on")
                    break
                elif summary.runtime.powerState == "poweredOff":
                    print(vm_name, "is being powered on...") 
                    task = [vm.PowerOn()] #Powers on the VM
                found = True
                break  # Stop after finding the first match
        if not found:
            print("No VM found with the name:", vm_name)
    
    


def Power_Off():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ") # Asks for VM Name
    vms = container.view

    if vm_name:  # If a VM name is provided
        found = False
        for vm in vms:
            if vm_name == vm.name:  # Checks for an exact match
                vm_info = get_vm(vm)
                if summary.runtime.powerState == "poweredOff": # Checks if VM is already off
                    print(vm_name, "is already powered off")
                    break
                elif summary.runtime.powerState == "poweredOn":
                    print(vm_name, "is being powered off...")  
                    task = [vm.PowerOff()] # Powers VM off
                found = True
                break  # Stop after finding the first match
        if not found:
            print("No VM found with the name:", vm_name)

def Create_Snapshot():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ") # Asks for VM Name
    vms = container.view

    if vm_name:  # If a VM name is provided
        found = False
        for vm in vms:
            if vm_name == vm.name:  # Checks for an exact match
                vm_info = get_vm(vm)
                snapshot_name = input("Enter a name for the snapshot: ") # Name of snapshot 
                snapshot_description = input("Enter snapshot description: ") # Description for snapshot
                snapshot_memory = bool(input("Snapshot memory (True/False): ")) 
                #Task for creating the snapshot with the settings entered
                vm.CreateSnapshot_Task(
                name=snapshot_name, 
                description=snapshot_description, 
                memory=snapshot_memory,  # If True, snapshot the VM's memory
                quiesce=False  # If True, pause I/O and freeze file system for consistent state
                )
                found = True
                break  # Stop after finding the first match
        if not found:
            print("No VM found with the name:", vm_name)


def Tweak_Performance():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ") # Asks for VM Name
    vms = container.view

    if vm_name:  # If a VM name is provided
        found = False
        for vm in vms:
            if vm_name == vm.name:  # Checks for an exact match
                vm_info = get_vm(vm)
                config_spec = vim.vm.ConfigSpec()
                new_memory = int(input("Enter new memory amount in gb: "))
                new_memory_mb = (new_memory * 1024)
                new_cpu = int(input("Enter new amount of CPUs: "))
                config_spec.memoryMB = new_memory_mb
                config_spec.numCPUs = new_cpu
                print("Changing Memory and CPU count for", vm_name)
                task = vm.ReconfigVM_Task(config_spec)
                found = True
                break  # Stop after finding the first match
        if not found:
            print("No VM found with the name:", vm_name)

def Restart_VM():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ") # Asks for VM Name
    vms = container.view
    if vm_name:  # If a VM name is provided
        found = False
        for vm in vms:
            if vm_name == vm.name:  # Checks for an exact match
                vm_info = get_vm(vm)
                if summary.runtime.powerState == "poweredOff":
                    print(vm_name, "is powered off...")
                    power_input = input("Would you like to power it on? (y/n): ")
                    if power_input == 'y' or power_input == 'Y':
                        task = [vm.PowerOn()]
                    else:
                        print("Returning to menu...")
                        break
                elif summary.runtime.powerState == "poweredOn":
                    print(vm_name, "is being restarted...")
                    try:
                        vm.RebootGuest()
                    except:
                        vm.ResetVM_Task()
                found = True
                break  # Stop after finding the first match
        if not found:
            print("No VM found with the name:", vm_name)

def Delete_VM():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ") # Asks for VM Name
    vms = container.view

    if vm_name:  # If a VM name is provided
        found = False
        for vm in vms:
            if vm_name == vm.name:  # Checks for an exact match
                vm_info = get_vm(vm)
                confirm = input("Are you sure you want to delete this vm? (y/n): ")
                if confirm == 'y' or confirm == 'Y':
                    print("Deleting:", vm_name)
                    task = vm.Destroy_Task()
                else:
                    print("Returning to menu...")
                    break
                found = True
                break  # Stop after finding the first match
        if not found:
            print("No VM found with the name:", vm_name)


#Menu function
def Menu(): 
    print ("1. Connect to vCenter")
    print ("2. Search VMs")
    print ("3. Show Current Connection Information")
    print ("4. Power on a VM")
    print ("5. Power off a VM")
    print ("6. Create a snapshot of a VM")
    print ("7. Tweak the CPUs or Memory of a VM")
    print ("8. Restart a VM")
    print ("9. Delete a VM")
    print ("10. Quit")

#While loop to show menu
while True:
    Menu()
    choice = input("Enter an option(1-10): ")

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
        print('---------------------------------------')
        Current_Connection()

    elif choice == '4':
        print("Powering a VM on has been selected")
        print('---------------------------------------')
        Power_On()
   
    elif choice == '5':
        print("Powering a VM off has been selected")
        print('---------------------------------------')
        Power_Off()

    elif choice == '6':
        print("Creating a snapshot has been selected")
        print('---------------------------------------')
        Create_Snapshot()
    
    elif choice == '7':
        print("Tweaking a VM's performance has been selected")
        print('---------------------------------------')
        Tweak_Performance()

    elif choice == '8':
        print("Restarting a VM")
        print('---------------------------------------')
        Restart_VM()

    elif choice == '9':
        print("Deleting a VM")
        print('---------------------------------------')
        Delete_VM()
    
    elif choice == '10':
        print("Quitting...")
        print('---------------------------------------')
        break
    else:
        print("Invalid choice, try again") # Error handling to make sure if anything other than the specified options are entered it doesn't break