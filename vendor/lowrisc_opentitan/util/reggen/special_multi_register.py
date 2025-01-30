# Copyright lowRISC contributors.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, List

from reggen import register
from .field import Field
from .lib import check_keys, check_str, check_name, check_list, check_str_dict
from .params import ReggenParams
from .reg_base import RegBase
from .register import Register
from .multi_register import MultiRegister

REQUIRED_FIELDS = {
    'name': ['s', "base name of the registers"],
    'separation': [
        's', "number of instances to generate."
        " This field can be integer or string matching"
        " from param_list."
    ],
    'multiregisters': [
        'l',
        "list of register definition groups and "
        "offset control groups"
    ]
}
OPTIONAL_FIELDS = register.OPTIONAL_FIELDS.copy()
OPTIONAL_FIELDS.update({
    'regwen_multi': [
        'pb', "If true, regwen term increments"
        " along with current multireg count."
    ],
    'compact': [
        'pb', "If true, allow multireg compacting."
        "If false, do not compact."
    ]
})


class SpecialMultiRegister(RegBase):
    def __init__(self,
                 offset: int,
                 addrsep: int,
                 reg_width: int,
                 params: ReggenParams,
                 raw: object):
        super().__init__(offset)

        rd = check_keys(raw, 'specialmultireg',
                        list(REQUIRED_FIELDS.keys()),
                        list(OPTIONAL_FIELDS.keys()))
        
        self.name = check_name(rd['name'],
                                'name field of specialmultireg')

        addr_separation = int(check_str(rd['separation'],
                              'addr_separation field of specialmultireg {}'
                              .format(self.name)))

        mregs = check_list(rd['multiregisters'],
                            'multiregisters field of specialmultireg {}'
                            .format(self.name))
        
        self._offset   = offset
        self.mregs = []

        for idx, raw_entry in enumerate(mregs):
            entry = check_str_dict(raw_entry, "spmultireg entry {}".format(idx))

            entry_body = entry.get('multireg')

            mr = MultiRegister(self._offset,
                           addr_separation, reg_width, params, entry_body)
            self.mregs.append(mr)

            self._offset   = self._offset + addrsep
