from jinja2 import Environment, Template, FileSystemLoader

dna_connector = '192.168.1.1'
wlc_list = ['10.1.1.1', '10.1.1.2']
ap_subnet_list = ['10.2.2.0 0.0.0.255', '10.2.3.0 0.0.0.255']
dns_server = '8.8.8.8'
ntp_server = '1.1.1.1'
templateLoader = FileSystemLoader(searchpath="./templates")
templateEnv = Environment(loader=templateLoader)
TEMPLATE_FILE = "dna_spaces_connector_acl_template.jinja2"
template = templateEnv.get_template(TEMPLATE_FILE)
acl = template.render(dna_connector=dna_connector,
                      wlc_list=wlc_list,
                      ap_subnet_list=ap_subnet_list,
                      dns_server=dns_server,
                      ntp_server=ntp_server,
                      )
print(acl)
