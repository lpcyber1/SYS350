# Script written by Liam Paul for cloning a VM using the HyperV Powershell Module

#Writes out names of Base VMs to clone
$Available = Get-VM | Where-Object {$_.Name -match "Base"}

Write-Host $Available

#Prompt for name of VM to clone
$SourceVM = Read-Host "Enter the name of the VM you would like to clone"

#Error handling
if ($null -eq $SourceVM) {
    Write-Host "VM '$SourceVM' not found, exiting..."
    exit
}

#Prompt for new VM name
$NewName = Read-Host "Enter the name of the new VM"

#Gets the parent disk of the VM that was entered to be cloned
$ParentPath = "C:\ProgramData\Microsoft\Windows\Virtual Hard Disks\$SourceVM.vhdx"

#Assigns the path and name of the new VM hard disk
$NewDiskPath = "C:\ProgramData\Microsoft\Windows\Virtual Hard Disks\$NewName.vhdx"

#Creates new differencing disk and gives it 5 seconds to be created before creating the new VM
$NewDisk = New-VHD -ParentPath $ParentPath -Path $NewDiskPath -Differencing
Write-Host "Creating new differencing disk..."
Start-Sleep -Seconds 5

#Creates the Linked Clone using the differencing disk 
New-VM -Name $NewName -MemoryStartupBytes 2GB -VHDPath $NewDisk -Generation 2 