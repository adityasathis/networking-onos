# Copyright (c) 2017 SK Telecom Ltd
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import collections
from neutron_lib.callbacks import events
from neutron_lib.callbacks import registry
from neutron_lib.callbacks import resources

from networking_onos.extensions import constant as onos_const


ONOSResource = collections.namedtuple('ONOSResource', ('singular', 'plural'))
_OPERATION_MAPPING = {
    events.PRECOMMIT_CREATE: onos_const.ONOS_CREATE,
    events.PRECOMMIT_UPDATE: onos_const.ONOS_UPDATE,
    events.PRECOMMIT_DELETE: onos_const.ONOS_DELETE,
    events.AFTER_CREATE: onos_const.ONOS_CREATE,
    events.AFTER_UPDATE: onos_const.ONOS_UPDATE,
    events.AFTER_DELETE: onos_const.ONOS_DELETE,
}

_RESOURCE_MAPPING = {
    resources.SECURITY_GROUP: ONOSResource(onos_const.ONOS_SG,
                                           onos_const.ONOS_SGS),
    resources.SECURITY_GROUP_RULE: ONOSResource(onos_const.ONOS_SG_RULE,
                                                onos_const.ONOS_SG_RULES),
}


class OnosSecurityGroupHandler(object):

    def __init__(self, precommit, postcommit):
        assert postcommit is not None
        self._precommit = precommit
        self._postcommit = postcommit
        self._subscribe()

    def _subscribe(self):
        if self._precommit is not None:
            for event in (events.PRECOMMIT_CREATE, events.PRECOMMIT_DELETE):
                registry.subscribe(self.sg_callback_precommit,
                                   resources.SECURITY_GROUP, event)
                registry.subscribe(self.sg_callback_precommit,
                                   resources.SECURITY_GROUP_RULE, event)

            registry.subscribe(self.sg_callback_precommit,
                               resources.SECURITY_GROUP,
                               events.PRECOMMIT_UPDATE)

        for event in (events.AFTER_CREATE, events.AFTER_DELETE):
            registry.subscribe(self.sg_callback_postcommit,
                               resources.SECURITY_GROUP, event)
            registry.subscribe(self.sg_callback_postcommit,
                               resources.SECURITY_GROUP_RULE, event)

        registry.subscribe(self.sg_callback_postcommit,
                           resources.SECURITY_GROUP, events.AFTER_UPDATE)

    def _sg_callback(self, callback, resource, event, trigger, **kwargs):
        if 'payload' in kwargs:
            # TODO(boden): remove shim once all callbacks use payloads
            print("ASATHISH >>> START >>> ASATHISH")
            print(resource)
            print(event)
            context = kwargs['payload'].context
            print(context)
            print("ASATHISH >>> END >>> ASATHISH")
            res = kwargs['payload'].latest_state
            res_id = kwargs['payload'].resource_id
            copy_kwargs = kwargs
        else:
            print("ASATHISH >>> START >>> ASATHISH")
            print(resource)
            print(event)
            print(kwargs['context'])
            print("ASATHISH >>> END >>> ASATHISH")
            context = kwargs['context']
            res = kwargs.get(resource)
            res_id = kwargs.get("%s_id" % resource)
            copy_kwargs = kwargs.copy()
            copy_kwargs.pop('context')

        if res_id is None:
                res_id = res.get('id')

        ops = _OPERATION_MAPPING[event]
        res_type = _RESOURCE_MAPPING[resource]
        res_dict = res

        callback(context, ops, res_type, res_id, res_dict, **copy_kwargs)

    def sg_callback_precommit(self, resource, event, trigger, **kwargs):
        self._sg_callback(self._precommit, resource, event, trigger, **kwargs)

    def sg_callback_postcommit(self, resource, event, trigger, **kwargs):
        self._sg_callback(self._postcommit, resource, event, trigger, **kwargs)
