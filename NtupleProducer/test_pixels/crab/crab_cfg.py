# crab submit -c crab_cfg.py General.requestName=<name> Data.inputDataset=<dataset> [Data.totalUnits=N]
from CRABClient.UserUtilities import config
config = config()
config.General.requestName = "l1pix_test"
config.General.workArea = "crab_l1pix"
config.General.transferOutputs = True
config.JobType.pluginName = "Analysis"
config.JobType.psetName = "step1_crab_cfg.py"
config.JobType.scriptExe = "run_crab.sh"
config.JobType.inputFiles = ["step2_crab_cfg.py"]
config.JobType.outputFiles = ["inputs.root", "perfNano.root"]
config.JobType.numCores = 4
config.JobType.maxMemoryMB = 8000
config.JobType.maxJobRuntimeMin = 600
config.JobType.allowUndistributedCMSSW = True
config.Data.inputDataset = ""
config.Data.splitting = "FileBased"
config.Data.unitsPerJob = 1
config.Data.outLFNDirBase = "/store/user/anovak/l1pixels"
config.Data.publication = False
config.Site.storageSite = "T2_US_MIT"
