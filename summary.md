Summary of Issue
During a Failover Test for VM Prod-SCCM to Azure (Prod-SCCM-testingrecovery), Zerto reported the task as successful (Success=True), but the recovered Azure VM failed to boot.
Upon investigation, Zerto selected Prod-SCCM_2 (a data disk on NVMe) as the Azure OS disk instead of Prod-SCCM (the actual Windows boot disk on SCSI). When the customer attempted a manual OS disk swap in the Azure portal, Azure rejected it due to a generation/metadata mismatch.
Root Cause & Mechanism
The source VM has 9 disks across 4 controllers (2 SCSI, 2 NVMe):
Prod-SCCM.vmdk at SCSI 0:0 ← the real Windows/OS disk
Prod-SCCM_2.vmdk at NVMe 0:0 ← just a data disk
Why this fails:
Deterministic Selection Logic: When building the Azure VM, Zerto sorts disk controllers and prioritizes NVMe over SCSI. Because both disks reside at slot 0:0 on their respective controllers, the NVMe data disk takes precedence and is designated as the OS disk, demoting the actual boot disk to LUN 3.
Missing Azure Gen2 Boot Metadata: Zerto only stamps Azure Generation 2 / bootable metadata onto the disk it selects as the OS disk. Because the real OS disk is provisioned as an ordinary data disk without this metadata, Azure blocks a direct manual swap.
Known Gap: This behavior is tracked under ZER-108644 (P2, referenced by //TODO: fix NVME disks selection - ZER-108644 in the code).
Evidence Summary
Metric / Check
	
Finding
	
Source / Reference


Real OS Disk
	
Prod-SCCM.vmdk (SCSI 0:0)
	
vCenter: BootDiskBusType: scsi


Zerto OS Disk Selection
	
Prod-SCCM_2.vhd (NVMe 0:0)
	
ZVM Logs: #OsDisk = ...Prod-SCCM_2.vhd


Real OS Disk Assignment
	
Demoted to Data Disk
	
Azure VM JSON: LUN 3 = Prod-SCCM


Azure Gen2 Tagging
	
Tagged on wrong disk only
	
Prod-SCCM_2 has hyperVGeneration: V2; Prod-SCCM has none


Defect Tracking
	
Open Epic / TODO in source
	
ZER-108644