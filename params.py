from typing import Optional, Literal
import os
import re
from sys import argv
import time
import requests
import base64
import urllib.parse
from datetime import datetime, timezone, timedelta

clash_meta_user_agent = "ClashForWindows/0.19.12"
KeyType = Optional[Literal['ios', 'v2ray', 'clash']]

module_sites = set([])
sub_dir = "sub"
modules_dir = "submodules"

for it in os.listdir(modules_dir):
  it_dir = os.path.join(modules_dir, it)

  if not os.path.isdir(it_dir): continue
  if not os.path.exists(os.path.join(it_dir, '.git')): continue

  module_sites.add(it)

dir_list = os.listdir(sub_dir)

headers = {
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}

clash_headers = {
  "user-agent": clash_meta_user_agent
}
