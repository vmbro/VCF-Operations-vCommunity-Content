#  Copyright 2024 vCommunity Content MP
#  Author: Onur Yuzseven

class ClusterHAConfig:
    HA = "configuration|dasConfig|"
    HOST_MONITORING = HA + "Host Monitoring"
    HOST_ISOLATION = HA + "Response \ Host Isolation"
    VM_RESTART_PRIORITY = HA + "Response \ Default VM Restart Priority"
    DATASTORE_APD = HA + "Response \ Datastore APD"
    DATASTORE_PDL = HA + "Response \ Datastore PDL"
    VM_MONITORING = HA + "VM Monitoring"
    HEARTBEAT_DATASTORE = HA + "Heartbeat Datastore"


class ClusterDRSConfig:
    DRS = "configuration|drsConfig|"
    PROACTIVE_DRS = DRS + "Proactive DRS"
    SCALE_DESCENDANTS_SHARE = DRS + "Scale Descendants Shares"
    DRS_SCORE = DRS + "DRS Score (%)"