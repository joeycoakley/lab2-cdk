#!/usr/bin/env python3

from aws_cdk import core
from cdk.cdk_stack import MasterNetworkStack

network_master = core.Environment(account='256060500942', region="us-east-1")

app = core.App()
master_network = MasterNetworkStack(app, "MasterNetworkStack", env=network_master)
# fw1 = FirewallInstance(app, "Firewall1", master_network.subnets, env=network_master)

app.synth()
