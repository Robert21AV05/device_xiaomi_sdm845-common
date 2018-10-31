# Copyright (C) 2009 The Android Open Source Project
# Copyright (c) 2011, The Linux Foundation. All rights reserved.
# Copyright (C) 2017-2018 The LineageOS Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import common
import re

def FullOTA_Assertions(info):
  AddModemAssertion(info, info.input_zip)
  AddVendorAssertion(info, info.input_zip)
  return

def IncrementalOTA_Assertions(info):
  AddModemAssertion(info, info.target_zip)
  AddVendorAssertion(info, info.input_zip)
  return

def AddModemAssertion(info, input_zip):
  android_info = info.input_zip.read("OTA/android-info.txt")
  m = re.search(r'require\s+version-modem\s*=\s*(.+)', android_info)
  if m:
    timestamp, firmware_version = m.group(1).rstrip().split(',')[:2]
    if ((len(timestamp) and '*' not in timestamp) and \
        (len(firmware_version) and '*' not in firmware_version)):
      cmd = 'assert(xiaomi.verify_modem("{}") == "1" || abort("ERROR: This package requires firmware from MIUI {} developer build or newer. Please upgrade firmware and retry!"););'
      info.script.AppendExtra(cmd.format(timestamp, firmware_version))
  return

def AddVendorAssertion(info, input_zip):
  info.script.AppendExtra('ifelse(is_mounted("/vendor"), unmount("/vendor"));')
  info.script.AppendExtra('mount("ext4", "EMMC", "/dev/block/bootdevice/by-name/vendor", "/vendor");');
  android_info = info.input_zip.read("OTA/android-info.txt")
  m = re.search(r'require\s+version-modem\s*=\s*(.+)', android_info)
  if m:
    firmware_version, build_date_utc, vndk_version = m.group(1).rstrip().split(',')[1:]
    # less_than_int doesn't seem to check for equality - so bump the date by 1
    build_date_utc = int(build_date_utc) + 1
    check_vndk='file_getprop("/vendor/default.prop","ro.vndk.version") == "{}"'
    check_builddate='less_than_int(file_getprop("/vendor/build.prop", "ro.vendor.build.date.utc"), "{}")'
    abort_error='abort("ERROR: This package requires vendor from MIUI {} developer build or newer. Please upgrade your vendor and retry!");'
    info.script.AppendExtra('assert(' + check_vndk.format(vndk_version) + ' && ' + check_builddate.format(build_date_utc) + ' || ' + abort_error.format(firmware_version) + ');');
  return
