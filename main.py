from clash import *

class Main(ClashHandler):
  paths = list(module_sites)

  def __init__(self, type: KeyType = None) -> None:
    super().__init__()
    self.dirs = dir_list
    self.sub_links = {}
    self.type: KeyType = None
    self.type = type
    self.submodule_path = self.paths[0]

  def add_suffix(self, line: str) -> str:
    # 提取备注
    # 去掉 ss:// 前缀
    ss_content = line[5:]
    # 进行 Base64 解码，添加必要的填充
    base64_str = ss_content.split('@')[0]
    padding = len(base64_str) % 4
    if padding != 0:
      base64_str += '=' * (4 - padding)

    try:
      # 进行 Base64 解码
      decoded_bytes = base64.b64decode(base64_str)
      decoded_string = decoded_bytes.decode('utf-8')

      # 提取加密方式和密码
      server, port_with_remark = ss_content.split('@')[1].split(':', 1)
      method, password = decoded_string.split(':')
      port, remark = port_with_remark.split('#')
      remark = urllib.parse.unquote(remark).strip()
      if not any(x in remark for x in ('|', '剩余流量')):
        return ""
      remark = remark.replace('剩余流量', f'{self.submodule_path}')
      cleaned_remark = re.sub(r' \|.*', f'_{self.submodule_path}', remark)
      return f'ss://{base64.b64encode(f"{method}:{password}".encode()).decode()}@{server}:{port}#{urllib.parse.quote(cleaned_remark)}'
    except Exception as e:
      print(e.args)
      return line

  def parse_origin(self, text: str) -> str:
    decoded_bytes = base64.b64decode(text)
    decoded_string = decoded_bytes.decode('utf-8')
    nodes = []
    for line in decoded_string.split('\n'):
      if not line.strip(): continue
      node = self.add_suffix(line)
      if not node: continue
      nodes.append(node)
    return "\n".join(nodes)

  def get_item_link(self, key: str, url: str):
    try:
      url = self.replace_url(url)
      print(f'request {self.submodule_path} {url}')
      with requests.get(url, headers=headers, timeout=10) as res:
        print("request base64", res.status_code)
        if res.status_code < 300:
          os.makedirs(key, exist_ok=True)
          with open(self.join_path(f"{key}/{self.submodule_path}.{key}"), mode="w+", encoding="utf-8") as f:
            f.write(self.parse_origin(res.text))
      self.get_clash_nodes(url)
    except:
      self.get_item_link(key, url)

  def request_links(self):
    items = self.sub_links.items()

    if self.type:
      self.get_item_link(self.type, self.sub_links[self.type])
      return
    for key, url in items:
      self.get_item_link(key, url)

  def set_links(self):
    with open(f"{modules_dir}/{self.submodule_path}/README.md", mode="r", encoding="utf-8") as f:
      text = f.read()
      res = re.search(
        r".*?Clash订阅.*?(?P<clash>http.*?)\n"
        r".*?v2rayN订阅.*?(?P<v2ray>http.*?)\n"
        r".*?iOS小火箭订阅.*?(?P<ios>http.*?)\n.*?",
        text,
        re.DOTALL
      )
      self.sub_links = res.groupdict()

  def save_origin_sub_link(self):
    link_file = "sub/README.md"
    content = "\n### Origin Links\n\n"
    baijing_time = datetime.fromtimestamp(time.time(), tz=timezone(timedelta(hours=8)))
    content += f"> Updated Time: {baijing_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    for module in self.paths:
      self.submodule_path = module
      self.set_links()
      content += f"- **{module}**\n"
      for key, link in self.sub_links.items():
        link = self.replace_url(link)
        content += f"  - **{key}**: [*{link}*]({link})\n"
    os.system(rf"cat README.md > {link_file}")
    with open(link_file, "a") as f:
      f.write(content)

  def walk(self, p: str):
    self.submodule_path = p
    if self.submodule_path in self.paths:
      self.set_links()
      self.request_links()

    if p == 'all':
      for it in self.paths:
        self.submodule_path = it
        self.set_links()
        self.request_links()

    if self.type:
      self.dirs = [self.type]

    for d in self.dirs:
      paths = [self.join_path(d, it) for it in os.listdir(self.join_path(d)) if it.endswith(d)]
      paths.sort(key=lambda f: os.path.getmtime(f), reverse=True)
      # print(paths)
      sites = ""
      for p in paths:
        with open(p, mode="r", encoding="utf-8") as f:
          sites += (f.read().strip() + '\n')
      with open(self.join_path(f"{d}/index"), mode="w+", encoding="utf-8") as f:
        f.write(sites)
      encoded = base64.b64encode(sites.encode('utf-8')).decode('utf-8')
      with open(self.join_path(f"{d}/base64"), mode="w+", encoding="utf-8") as f:
        f.write(encoded)
    self.collect_clash_nodes()
    self.save_origin_sub_link()


if __name__ == '__main__':
  Main('v2ray').walk(argv[1])
  # Main().save_origin_sub_link()