from aws_cdk import (
    aws_ec2 as ec2,
    core
)


class FirewallInstance(core.Construct):
    def __init__(self, scope: core.Construct, id: str, *, subnets: aws_ec2.SubnetSelection, prefix=None):
        super().__init__(scope, id)
        interface_names = ('mgmt', 'untrust', 'trust')
        self.__interfaces = []

        

        for name in interface_names:
            self.interfaces.append(ec2.CfnNetworkInterface(self, name, source_dest_check=False))

    # def get_interfaces():
    #     pass

    

