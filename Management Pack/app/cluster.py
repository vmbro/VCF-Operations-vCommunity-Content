#  Copyright 2024 vCommunity Content MP
#  Author: Onur Yuzseven

import logging
from typing import Any
from typing import List
from aria.ops.object import Object
from aria.ops.result import CollectResult
from aria.ops.suite_api_client import SuiteApiClient
from constants.main import VCENTER_ADAPTER_KIND
from constants.clusterConfig import ClusterHAConfig
from constants.clusterConfig import ClusterDRSConfig
from pyVmomi import vim

NULL_STATUS = "null"

logger = logging.getLogger(__name__)


def add_ha_properties(cluster_obj, cluster):
    
    if cluster.configuration.dasConfig.enabled == False:
        cluster_obj.with_property(ClusterHAConfig.HOST_MONITORING, NULL_STATUS)
        cluster_obj.with_property(ClusterHAConfig.HOST_ISOLATION, NULL_STATUS)
        cluster_obj.with_property(ClusterHAConfig.VM_RESTART_PRIORITY, NULL_STATUS)
        cluster_obj.with_property(ClusterHAConfig.DATASTORE_APD, NULL_STATUS)
        cluster_obj.with_property(ClusterHAConfig.DATASTORE_PDL, NULL_STATUS)
        cluster_obj.with_property(ClusterHAConfig.VM_MONITORING, NULL_STATUS)
        cluster_obj.with_property(ClusterHAConfig.HEARTBEAT_DATASTORE, NULL_STATUS)
    else:
        if cluster.configuration.dasConfig.hostMonitoring == 'disabled':
            cluster_obj.with_property(ClusterHAConfig.HOST_MONITORING, "false")
            cluster_obj.with_property(ClusterHAConfig.HOST_ISOLATION, NULL_STATUS)
            cluster_obj.with_property(ClusterHAConfig.VM_RESTART_PRIORITY, NULL_STATUS)
            cluster_obj.with_property(ClusterHAConfig.DATASTORE_APD, NULL_STATUS)
            cluster_obj.with_property(ClusterHAConfig.DATASTORE_PDL, NULL_STATUS)
        else:
            cluster_obj.with_property(ClusterHAConfig.HOST_MONITORING, "true")
            cluster_obj.with_property(ClusterHAConfig.HOST_ISOLATION, str(cluster.configuration.dasConfig.defaultVmSettings.isolationResponse))
            cluster_obj.with_property(ClusterHAConfig.VM_RESTART_PRIORITY, str(cluster.configuration.dasConfig.defaultVmSettings.restartPriority))
            cluster_obj.with_property(ClusterHAConfig.DATASTORE_APD, str(cluster.configuration.dasConfig.defaultVmSettings.vmComponentProtectionSettings.vmStorageProtectionForAPD))
            cluster_obj.with_property(ClusterHAConfig.DATASTORE_PDL, str(cluster.configuration.dasConfig.defaultVmSettings.vmComponentProtectionSettings.vmStorageProtectionForPDL))
        cluster_obj.with_property(ClusterHAConfig.VM_MONITORING, str(cluster.configuration.dasConfig.vmMonitoring))         
        cluster_obj.with_property(ClusterHAConfig.HEARTBEAT_DATASTORE, str(cluster.configuration.dasConfig.hBDatastoreCandidatePolicy))


def add_drs_properties(cluster_obj, drs_config, drs_score):
    if drs_config.configuration.drsConfig.enabled == False:
        cluster_obj.with_property(ClusterDRSConfig.PROACTIVE_DRS, NULL_STATUS)
        cluster_obj.with_property(ClusterDRSConfig.SCALE_DESCENDANTS_SHARE, NULL_STATUS)
        cluster_obj.with_metric(ClusterDRSConfig.DRS_SCORE, 0)
    else:
        cluster_obj.with_property(ClusterDRSConfig.PROACTIVE_DRS, str(drs_config.configurationEx.proactiveDrsConfig.enabled))
        cluster_obj.with_property(ClusterDRSConfig.SCALE_DESCENDANTS_SHARE, str(drs_config.configuration.drsConfig.scaleDescendantsShares))
        cluster_obj.with_metric(ClusterDRSConfig.DRS_SCORE, int(drs_score))


def add_cluster_metrics(
    suite_api_client: SuiteApiClient,
    adapter_instance_id: str,
    result: CollectResult,
    content: Any,
) -> None:
    container = content.rootFolder
    view_type = [vim.ClusterComputeResource]
    recursive = True
    container_view = content.viewManager.CreateContainerView(
        container, view_type, recursive
    )

    # Retrieve object types from the Aria Operations
    clusters: List[Object] = suite_api_client.query_for_resources(
        {
            "adapterKind": [VCENTER_ADAPTER_KIND],
            "resourceKind": ["ClusterComputeResource"],
            "adapterInstanceId": [adapter_instance_id],
        }
    )

    # Match the Aria Operations objects with the related identifier
    clusters_by_uuid: dict[str, Object] = {
        cluster.get_identifier_value("VMEntityObjectID"): cluster for cluster in clusters
    }

    # Push your metrics below
    children = container_view.view
    for cluster in children:
        cluster_obj = clusters_by_uuid.get(cluster._moId)
        if cluster_obj:
            #add_ha_properties(cluster_obj, cluster.configuration.dasConfig)
            add_ha_properties(cluster_obj, cluster)
            #add_drs_properties(cluster_obj, cluster.configurationEx, cluster.summary.drsScore)
            add_drs_properties(cluster_obj, cluster, cluster.summary.drsScore)
            result.add_object(cluster_obj)
        else:
            logger.warning(
                f"Could not find Cluster '{cluster.name}' with MoID: {cluster._moId}."
            )