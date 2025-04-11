from params import *

class ClashHandler:
  clash_dir = f"{sub_dir}/clash"
  free_sub = f"{clash_dir}/free"
  clash_tpl = 'templates/clash.yaml'

  @staticmethod
  def join_path(*paths) -> str:
    return os.path.join(sub_dir, *paths)

  @staticmethod
  def parse_remarks(node: str) -> str:
    match = re.search(r'name:\s*([^,}]+)', node)
    return match.group(1).strip() if match else ''
  
  @staticmethod
  def parse_node_line(line: str) -> str:
    return f"  {line.strip()}\n"

  @staticmethod
  def replace_url(url: str) -> str:
    return re.sub(r'https?:/', 'https://', url) if re.match(r'https:/[^/]', url) else url

  @classmethod
  def filter_clash_nodes(cls, filepath: str) -> tuple:
    with open(filepath, 'r', encoding='utf-8') as f:
      lines = f.readlines()
    i = -1
    nodes = []
    remarks = []
    while i < len(lines):
      i += 1
      line = lines[i]
      if line.strip() != 'proxies:': continue
      while i < len(lines):
        i += 1
        node_line = lines[i]
        if node_line.strip().startswith('-'):
          nodes.append(cls.parse_node_line(node_line))
          remarks.append(cls.parse_remarks(nodes[-1]))
        else:
          break
      break
    return (nodes, remarks)

  @classmethod
  def add_nodes_to_clash(cls, nodes: list, remarks: list, filepath: str):
    with open(cls.clash_tpl, 'r', encoding='utf-8') as f:
      lines = f.readlines()
    a = next((i for i, x in enumerate(lines) if 'node_remakes:' in x), None)
    b = next((i for i, x in enumerate(lines) if 'proxies: null' in x), None)
    if a is None or b is None:
      return
    part1 = lines[:a]
    node_remakes = [f"node_remakes: &r1 {{ proxies: [{', '.join(remarks)}] }}\n"] 
    part2 = lines[a+1:b]
    proxies = ["proxies:\n"]
    part3 = lines[b+1:]
    with open(filepath, 'w+', encoding='utf-8') as f:
      f.writelines(part1 + node_remakes + part2 + proxies + nodes + part3)

  @classmethod
  def collect_clash_nodes(cls):
    clash_paths = [f"{cls.clash_dir}/{it}" for it in os.listdir(cls.clash_dir) if it.endswith('yaml')]
    clash_paths.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    # print(clash_paths)
    clash_nodes = []
    clash_remarks = []
    for p in clash_paths:
      nodes, remarks = cls.filter_clash_nodes(p)
      clash_nodes.extend(nodes)
      clash_remarks.extend(remarks)
    cls.add_nodes_to_clash(clash_nodes, clash_remarks, cls.free_sub)

  def __init__(self):
    self.submodule_path = ""

  def get_clash_nodes(self, url: str):
    try:
      with requests.get(url, headers=clash_headers, timeout=10) as res:
        print("request clash:", res.status_code)
        # res.raise_for_status()
        if res.status_code >= 300: return
        os.makedirs("clash", exist_ok=True)
        self.add_nodes_to_clash(*self.replace_clash_nodes(res.text), f"{self.clash_dir}/{self.submodule_path}.yaml")
    except Exception as e:
      print(e.args)
      self.get_clash_nodes(url)

  def replace_clash_nodes(self, text: str) -> tuple:
    lines = text.split('\n')
    nodes = []
    remarks = []
    for i in range(len(lines)):
      line = lines[i].rstrip()
      match_reg = re.match(r'.*?\-\s+\{\s+name:\s*(.+?),.*?password.*?\}.*', line)
      if not match_reg: continue 
      name = match_reg.group(1)
      if '剩余流量' in name:
        nodes.append(self.parse_node_line(re.sub('剩余流量', '流量_' + self.submodule_path, line)))
        remarks.append(self.parse_remarks(nodes[-1]))
      elif '|' in name:
        replaced_name = "'{}_{}'".format(re.sub(r'[\s\']', '', name.split('|')[0]), self.submodule_path) 
        # print(replaced_name)
        nodes.append(self.parse_node_line(re.sub(r'(name:\s*).+?,', r'\1' + replaced_name + ',', line)))
        remarks.append(self.parse_remarks(nodes[-1]))
    return (nodes, remarks)
