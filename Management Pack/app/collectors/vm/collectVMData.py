#  Copyright 2024 vCommunity Content MP
#  Author: Onur Yuzseven

import logging
from typing import Any
from typing import List
from aria.ops.object import Object
from aria.ops.result import CollectResult
from aria.ops.suite_api_client import SuiteApiClient
from constants.main import VCENTER_ADAPTER_KIND
from pyVmomi import vim
from metrics.vm.vm_snapshot_metrics import collect_vm_metrics
from properties.vm.vmConfig import collect_vm_config_properties
from properties.vm.vm_Age import collect_vm_Age_metrics
from properties.vm.vm_extra_config import collect_vm_config_properties

logger = logging.getLogger(__name__)

def collect_vm_data(
    suite_api_client: SuiteApiClient,
    adapter_instance_id: str,
    result: CollectResult,
    content: Any,
) -> None:
    container = content.rootFolder
    view_type = [vim.VirtualMachine]
    recursive = True
    container_view = content.viewManager.CreateContainerView(
        container, view_type, recursive
    )

    # Retrieve object types from the Aria Operations
    vms: List[Object] = suite_api_client.query_for_resources(
        {
            "adapterKind": [VCENTER_ADAPTER_KIND],
            "resourceKind": ["VirtualMachine"],
            "adapterInstanceId": [adapter_instance_id],
        }
    )

    # Match the Aria Operations objects with the related identifier
    vms_by_uuid: dict[str, Object] = {
        vm.get_identifier_value("VMEntityObjectID"): vm for vm in vms
    }

    # Push your metrics below
    children = container_view.view
    for vm in children:
        logger.warning(f"{vm.name}")
        vm_obj = vms_by_uuid.get(vm._moId)
        if vm_obj:
            collect_vm_metrics(vm_obj, vm)
            collect_vm_config_properties(vm_obj, vm)
            collect_vm_Age_metrics(vm_obj, vm)
            collect_vm_config_properties(vm_obj, vm)
            result.add_object(vm_obj)
        else:
            logger.warning(
                f"Could not find vm '{vm.name}' with MoID: {vm._moId}."
            )