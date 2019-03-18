#!/usr/bin/env python3

from __future__ import print_function
import json
import sys
import os
import argparse
import getpass
import boto3

# t2.medium	2	4.0	24	$0.0464	$33.87
# t2.large	2	8.0	36	$0.0928	$67.74

INSTANCE_TYPES = {"perf": "m4.large", "small": "t2.medium", "medium": "t2.large", "large": "m3.xlarge"}

# Ubuntu 16.04 LTS
#AMI_LINUX_IMAGE = "ami-a4dc46db"
# Ubuntu 18.04 LTS
AMI_LINUX_IMAGE = "ami-012fd5eb46f56731f"
CREATE_INSTANCE = "create"
CREATE_KEY = "create_key"
UPDATE_INSTANCE = "update"
ELASTIC_IP = "elastic"
RUNNING_INSTANCES = "running"
START_INSTANCE = "start"
STOP_INSTANCE = "stop"
DESTROY_INSTANCE = "destroy"
EBS_VOLUME_SIZE = 10

VNC_LOGIN = "vnc_login"
LOGIN = "login"
GET = "get"
PUSH = "push"
SETUP = "setup"
RESET = "reset"
CHECK_CONFIG = "check_config"
RUN_SCRIPT = "run_script"

SETUP_SCRIPT = SETUP + ".sh"
# TODO make this more configurable!
SETUP_BUNDLE = "zs-1.0.0.tar.ubuntu.xz"

PEM = ".pem"
SSH_SECRET_KEY = "key_name"
EC2_NAME = "name"
SERVER_HOSTNAME = "hostname"
AMI_ID = "ami_id"
ELASTIC_ALLOC_ID = "elastic_alloc_id"
ELASTIC_ASSOC_ID = "elastic_assoc_id"
INSTANCE_ID = "instance_id"
INSTANCE_USER = "username"
SECURITY_GROUP = "security_group"
MONITOR = "monitor"
UNMONITOR = "unmonitor"

CMDs = [CREATE_INSTANCE, RUNNING_INSTANCES, UPDATE_INSTANCE, ELASTIC_IP,
        START_INSTANCE, STOP_INSTANCE, DESTROY_INSTANCE, CREATE_KEY,
        VNC_LOGIN, LOGIN, GET, PUSH, SETUP, RESET, RUN_SCRIPT, MONITOR]

def util_strip_quotes(s):
    return s.replace("\"", "").rstrip()

def get_required_field(data, field):
    if data.get(field):
        return data[field]
    sys.exit("Usage: '%s' missing in json config!" % field)

def ssh_connect(verbose, user, secret_key_file, hostname, args=None, env_vars=""):
    add_verbose = " "
    if verbose:
        add_verbose = " -v "

    if args is None:
        cmd = "ssh{add_verbose}-i {secret_key} -o StrictHostKeyChecking=no {user}@{hostname}".format(
                        add_verbose=add_verbose, secret_key=secret_key_file,
                        user=user, hostname=hostname)
    else:
        # script_args ==> "./some_script args"
        if env_vars != "":
            env = env_vars + " "
        cmd = "ssh{add_verbose}-i {secret_key} -o StrictHostKeyChecking=no {user}@{hostname} '{env}/bin/bash -s' < {script_args}".format(
                       add_verbose=add_verbose, secret_key=secret_key_file,
                       user=user, hostname=hostname, env=env, script_args=args)
    print("[DEBUG]: " + cmd)
    os.system(cmd)
    return

def ssh_connect_vnc(verbose, user, secret_key_file, hostname, args=None):
    add_verbose = " "
    if verbose:
        add_verbose = " -v "

    if args is None:
        cmd = "ssh{add_verbose}-i {secret_key} -o StrictHostKeyChecking=no -L 5901:localhost:5901 -N -f {user}@{hostname}".format(
                        add_verbose=add_verbose, secret_key=secret_key_file,
                        user=user, hostname=hostname)
    else:
        cmd = "ssh{add_verbose}-i {secret_key} -o StrictHostKeyChecking=no -L {port}:localhost:{port} -N -f {user}@{hostname}".format(
                        add_verbose=add_verbose, secret_key=secret_key_file,
                        user=user, hostname=hostname, port=args)

    print("[DEBUG]: " + cmd)
    os.system(cmd)
    return

def secure_copy_to_server(verbose, user, secret_key_file, hostname, file):
    add_verbose = " "
    if verbose:
        add_verbose = " -v "
    cmd = "scp{add_verbose}-i {secret_key} {src} {user}@{hostname}:/home/{user}/{dst}".format(
                   add_verbose=add_verbose, secret_key=secret_key_file,
                   user=user, hostname=hostname, src=file, dst=file)
    print("[DEBUG]: " + cmd)
    os.system(cmd)
    return

def secure_copy_to_server(verbose, user, secret_key_file, hostname, src_file, dst_file):
    add_verbose = " "
    if verbose:
        add_verbose = " -v "
    cmd = "scp{add_verbose}-i {secret_key} {src} {user}@{hostname}:/home/{user}/{dst}".format(
                   add_verbose=add_verbose, secret_key=secret_key_file,
                   user=user, hostname=hostname, src=src_file, dst=dst_file)
    print("[DEBUG]: " + cmd)
    os.system(cmd)
    return


def secure_copy_from_server(verbose, user, secret_key_file, hostname, rel_path_to_file, local_file):
    add_verbose = " "
    if verbose:
        add_verbose = " -v "
    # cut last part of file (e.g., /path/to/trusted_cert.pem
    path_to_file = rel_path_to_file
    if rel_path_to_file[0] in ['.', '/']:
        path_to_file = '/' + rel_path_to_file
    cmd = "scp{add_verbose}-i {secret_key} -o StrictHostKeyChecking=no {user}@{hostname}:/home/{user}/{src} {dst}".format(
        add_verbose=add_verbose, secret_key=secret_key_file, user=user, hostname=hostname,
        src=path_to_file, dst=local_file)
    os.system(cmd)
    return

def create_new_ec2_key(key_id):
    ec2 = boto3.resource('ec2')
    key_pair = ec2.create_key_pair(DryRun=False, KeyName=key_id)
    return key_pair

def list_running_instances():
    print("List running instances")
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        data = {}
        if instance.tags is not None:
            data = instance.tags[0]
        if data.get('Key') == 'Name':
            hostname = data.get('Value')
        print("EC2 instance: %s (%s : %s) =>\n\tInfo = %s : %s : %s " %
              (hostname, instance.image_id, instance.instance_type, instance.id,
               instance.public_dns_name, instance.public_ip_address))
    return

def get_running_instance(instance_id):
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        if instance.id == instance_id:
            return (instance.public_dns_name, instance.public_ip_address)
    return (None, None)

def terminate_instance(instance_id):
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[instance_id]).stop()
    ec2.instances.filter(InstanceIds=[instance_id]).terminate()
    return True

def create_ec2_instance(ami_image, instance_type, keypair, sec_group_id, ec2_name, volume_size, is_dedicated=False, verbose_=False):
    if verbose_:
        print("AMI IMAGE: ", ami_image)
        print("INSTANCE: ", instance_type)
        print("KEYPAIR: ", keypair)
    ec2 = boto3.resource('ec2')
    # check is_dedicated
    instance = ec2.create_instances(DryRun=False, SecurityGroups=[sec_group_id],
                         ImageId=ami_image, InstanceType=instance_type, KeyName=keypair,
                         BlockDeviceMappings=[{"DeviceName": "/dev/sda1", "Ebs" :
                             { "VolumeSize" : volume_size, "VolumeType": "gp2",
                               "DeleteOnTermination": True }}],
                         MinCount=1, MaxCount=1)
    # check the result
    if len(instance) == 1:
        new_instance = instance[0]
        # retrieve the instance id
        ec2.create_tags(DryRun=False, Resources=[new_instance.id],
                                      Tags=[{'Key': 'Name', 'Value': ec2_name}])
        return {AMI_ID: ami_image, SERVER_HOSTNAME: new_instance.public_dns_name,
                INSTANCE_ID: new_instance.id}
    return None

# see https://boto3.readthedocs.io/en/latest/reference/services/ec2.html#instance
def startup_instance(instance_id):
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[instance_id]).start()
    return

def shutdown_instance(instance_id):
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[instance_id]).stop()
    return

def monitor_instance(instance_id):
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[instance_id]).monitor()
    return

def unmonitor_instance(instance_id):
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[instance_id]).unmonitor()
    return

# {
#     'AllocationId': 'eipalloc-64d5890a',
#     'Domain': 'vpc',
#     'PublicIp': '203.0.113.0',
#     'ResponseMetadata': {
#         '...': '...',
#     },
# }
def attach_elastic_ip(instance_id, test_mode=False):
    client = boto3.client('ec2')
    # get a new elastic IP
    response = client.allocate_address(DryRun=test_mode, Domain="vpc")
    print("allocate_address response:", response)
    # attach to the existing instance
    if response:
        alloc_id = response["AllocationId"]
        response2 = client.associate_address(DryRun=test_mode, InstanceId=instance_id,
                                          AllocationId=alloc_id, AllowReassociation=True)
        print("associate_address response:", response2)
        return alloc_id, response2["AssociationId"], response["PublicIp"]
    return None

def attach_existing_elastic_ip(instance_id, alloc_elastic_id, test_mode=False):
    client = boto3.client('ec2')
    # get a new elastic IP
    response = client.associate_address(DryRun=test_mode, InstanceId=instance_id,
                                        AllocationId=alloc_elastic_id, AllowReassociation=True)
    print("associate_address response:", response)
    return response["AssociationId"]

def print_config(conf):
    print(json.dumps(conf, indent=4, sort_keys=False))
    return

def write_config(conf, filename):
    output_str = json.dumps(conf, indent=4, sort_keys=False)
    f = open(filename, 'w')
    f.write(output_str)
    f.close()
    return

def write_key(key_data, key_file):
    f = open(key_file, 'w')
    f.write(key_data)
    f.close()
    return

def aws_execute(input_config, json_config, cmd, options, verbose):
    args = options.get("args")
    # these are for creating/updating/listing/destroying EC2 instances
    if cmd == CREATE_INSTANCE:
        print("Creating an instance:", args) # small, medium or large
        if args is None:
            sys.exit("[!] Missing the instance type: %s" % list(INSTANCE_TYPES.keys()))

        instance_id = json_config.get(INSTANCE_ID)
        if instance_id is not None and instance_id != "":
            (public_dns_name, public_ip_address) = get_running_instance(instance_id)
            if public_dns_name is not None:
                print("Instance '%s' already running. "
                      "Must terminate existing one first: %s"
                      % (instance_id, public_dns_name))
                return 1

        is_dedicated = options.get("dedicated")
        ec2_name = get_required_field(json_config, EC2_NAME)
        keypair_id = get_required_field(json_config, SSH_SECRET_KEY)
        sec_group_id = get_required_field(json_config, SECURITY_GROUP)
        instance_type = INSTANCE_TYPES.get(args)
        ami_image = AMI_LINUX_IMAGE
        volume_size = options.get("volume_size")
        instance_output = create_ec2_instance(ami_image, instance_type, keypair_id,
                                              sec_group_id, ec2_name, volume_size, is_dedicated=is_dedicated)
        if instance_output is not None:
            new_json_config = dict(json_config)
            new_json_config.update(instance_output)
            write_config(new_json_config, input_config)
            print("Successfully created new instance for '%s'" % ec2_name)
        else:
            print("Failed to create EC2 instance.")
            return -1
        return 0
    elif cmd == CREATE_KEY:
        key_id = args
        if key_id:
            key_pair = create_new_ec2_key(key_id)
            priv_key_bits = key_pair.key_material
            priv_key_file = str(key_pair.key_name) + ".pem"
            print("Key Fingerprint: ", key_pair.key_fingerprint)
            write_key(priv_key_bits, priv_key_file)
        else:
            sys.exit("[!] Missing the key_id. Please try again with '-a' argument")
        return 0
    elif cmd == RUNNING_INSTANCES:
        list_running_instances()
        return 0
    elif cmd == UPDATE_INSTANCE:
        instance_id = get_required_field(json_config, INSTANCE_ID)
        (dns_name, ip_addr) = get_running_instance(instance_id)
        if dns_name:
            json_config.update({SERVER_HOSTNAME: dns_name})
        write_config(json_config, input_config)
        return 0
    elif cmd == START_INSTANCE:
        instance_id = get_required_field(json_config, INSTANCE_ID)
        startup_instance(instance_id)
    elif cmd == STOP_INSTANCE:
        instance_id = get_required_field(json_config, INSTANCE_ID)
        shutdown_instance(instance_id)
    elif cmd == DESTROY_INSTANCE:
        hostname = get_required_field(json_config, SERVER_HOSTNAME)
        instance_id = get_required_field(json_config, INSTANCE_ID)
        if terminate_instance(instance_id):
            new_json_config = dict(json_config)
            new_json_config[INSTANCE_ID] = ""
            new_json_config[SERVER_HOSTNAME] = ""
            new_json_config[AMI_ID] = ""
            if new_json_config.get(ELASTIC_ASSOC_ID):
                new_json_config[ELASTIC_ASSOC_ID] = ""
            write_config(new_json_config, input_config)
            print("Terminating the instance: ", hostname)
        return 0
    elif cmd == ELASTIC_IP:
        instance_id = get_required_field(json_config, INSTANCE_ID)
        elastic_alloc_id = json_config.get(ELASTIC_ALLOC_ID)
        if elastic_alloc_id is not None and elastic_alloc_id != "":
            assoc_id = attach_existing_elastic_ip(instance_id, elastic_alloc_id)
            json_config.update({ELASTIC_ASSOC_ID: assoc_id})
        else:
            alloc_elastic_id, assoc_id, public_ip = attach_elastic_ip(instance_id)
            print("Public IP:", public_ip)
            json_config.update({ELASTIC_ALLOC_ID: elastic_alloc_id,
                                ELASTIC_ASSOC_ID: assoc_id,
                                SERVER_HOSTNAME: public_ip})
        print("Elastic Alloc ID:", elastic_alloc_id)
        print("Elastic Assoc ID:", assoc_id)
        # TODO: add route 53 entry for "name" => "public_ip"
        write_config(json_config, input_config)
    elif cmd == MONITOR:
        instance_id = get_required_field(json_config, INSTANCE_ID)
        monitor_instance(instance_id)
    elif cmd == UNMONITOR:
        instance_id = get_required_field(json_config, INSTANCE_ID)
        unmonitor_instance(instance_id)

    else:
        pass

    # all the non-create/running/destroy instance commands
    secret_key_id = get_required_field(json_config, SSH_SECRET_KEY)
    secret_key = secret_key_id + PEM # TODO: assert that this file really exists!!
    user = get_required_field(json_config, INSTANCE_USER)
    hostname = get_required_field(json_config, SERVER_HOSTNAME)
    if cmd == LOGIN:
        # log "login to 'hostname'"
        ssh_connect(verbose, user, secret_key, hostname)
        # sys.exit("login to server: %s" % str(args))
    elif cmd == VNC_LOGIN:
        # adds: -L 5901:localhost:5901 -N -f
        port = int(args) 
        ssh_connect_vnc(verbose, user, secret_key, hostname, port)
    elif cmd == PUSH:
        inputs = args.split("->") # TODO: add example for users
        # pushing file to home dir in server
        if len(inputs) == 2:
            src_file, dst_file = inputs
            src_file = src_file.replace(" ", "")
            dst_file = dst_file.replace(" ", "")
            secure_copy_to_server(verbose, user, secret_key, hostname, src_file, dst_file)
        elif len(inputs) == 1:
            file = inputs
            secure_copy_to_server(verbose, user, secret_key, hostname, file)
        else:
            sys.exit("[!] Invalid inputs: " + args)
    elif cmd == GET:
        inputs1 = args.split("->")
        inputs2 = args.split(" ")
        if len(inputs1) == 2:
            dest_file, local_path_dir = inputs1
            dest_file = dest_file.replace(" ", "")
            local_file = local_path_dir.replace(" ", "")
        elif len(inputs2) == 2:
            dest_file, local_file = inputs2
        else:
            sys.exit("[!] Invalid inputs: " + args)
        # log "downloading
        secure_copy_from_server(verbose, user, secret_key, hostname, dest_file, local_file)
    elif cmd == SETUP:
        # TODO: assert this SETUP_BUNDLE and SETUP_SCRIPT exist!!
        secure_copy_to_server(verbose, user, secret_key, hostname, SETUP_BUNDLE)
        script_arg = "{setup_script}".format(setup_script=SETUP_SCRIPT)
        ssh_connect(verbose, user, secret_key, hostname, script_arg)
    elif cmd == RESET:
        script_arg = cmd + ".sh"
        ssh_connect(verbose, user, secret_key, hostname, script_arg)
    elif cmd == RUN_SCRIPT:
        script_arg = args
        env = options.get("env")
        ssh_connect(verbose, user, secret_key, hostname, script_arg, env_vars=env)
    return 0

CMD_WITHOUT_CONFIG = [RUNNING_INSTANCES, CREATE_KEY]
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AWS EC2 provisioner wrapper")  # TODO: add some color!
    parser.add_argument('--config', help="json config with AWS details for the EC2 instance", required=False)
    parser.add_argument('-c', '--cmd', help="command options: %s" % str(CMDs), required=True)
    parser.add_argument('-a', '--args', help="arguments for the specific command in quotes", default=None, required=False)
    parser.add_argument('-v', '--verbose', help="increase ssh/scp verbosity", action="store_true")
    parser.add_argument('--env', help="add environment variables", default="", required=False)
    parser.add_argument('--dedicated', help="create instance on dedicated hardware (only for performance tests)", action="store_true")
    parser.add_argument('--volume-size', help="optionally specify the size of the EBS volume (in GB)", default=EBS_VOLUME_SIZE, required=False)
    cli_args = parser.parse_args()
    json_config = ""

    if cli_args.config is not None:
        try:
            with open(cli_args.config) as config_content:
                json_config = json.load(config_content)
        except:
            sys.exit("Could not load the json file: %s" % cli_args.config)

    if cli_args.config is None and cli_args.cmd not in CMD_WITHOUT_CONFIG:
        sys.exit("Config is required for the '%s' command" % cli_args.cmd)

    if cli_args.cmd not in CMDs:
        sys.stdout.write("Unrecognized command: %s\n" % cli_args.cmd)
        sys.exit("Available commands: %s" % str(CMDs))

    options = {"args": cli_args.args, "dedicated": cli_args.dedicated, "env": cli_args.env, "volume_size": int(cli_args.volume_size)}
    rc = aws_execute(cli_args.config, json_config, cli_args.cmd, options, cli_args.verbose)
    sys.exit(rc)
