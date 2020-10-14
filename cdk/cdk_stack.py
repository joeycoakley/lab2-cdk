from aws_cdk import (
    aws_ec2 as ec2,
    core
)


class MasterNetworkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        security_vpc = ec2.Vpc(
            self, "SecurityVPC",
            cidr="10.0.0.0/16",
            nat_gateways=0,
            max_azs=2,
            subnet_configuration=[ec2.SubnetConfiguration(
                cidr_mask=24,
                name="untrust",
                subnet_type=ec2.SubnetType.PUBLIC
            ), ec2.SubnetConfiguration(
                cidr_mask=24,
                name="trust",
                subnet_type=ec2.SubnetType.ISOLATED
            ), ec2.SubnetConfiguration(
                cidr_mask=28,
                name="transit",
                subnet_type=ec2.SubnetType.ISOLATED
            ), ec2.SubnetConfiguration(
                cidr_mask=28,
                name='fw_mgmt',
                subnet_type=ec2.SubnetType.ISOLATED
            )
            ]
        )

        #Expose subnets for child stacks
        # self.subnets = {
        #     'fw_mgmt': security_vpc.select_subnets(subnet_group_name="fw_mgmt"),
        #     'untrust': security_vpc.select_subnets(subnet_group_name='untrust'),
        #     'trust': security_vpc.select_subnets(subnet_group_name='trust')
        # }

        security_vpc.add_gateway_endpoint(
            "S3GW",
            service=ec2.GatewayVpcEndpointAwsService.S3  
        )

        management_vpc = ec2.Vpc(
            self, "ManagmentVPC",
            cidr="10.255.0.0/16",
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name="Management",
                    subnet_type=ec2.SubnetType.PUBLIC
                )
            ]
        )

        management_host = ec2.Instance(
            self, "ManagementHost",
            instance_type=ec2.InstanceType("t2.micro"),
            vpc=management_vpc,
            machine_image=ec2.MachineImage.latest_windows(ec2.WindowsVersion("WINDOWS_SERVER_2019_ENGLISH_FULL_BASE")),
            key_name='joeycoak-alz-network-us-east-1',
        )

        # rdp = ec2.Port(
        #     protocol=ec2.Protocol("TCP"),
        #     string_representation="RDP",
        #     to_port=3389,
        #     from_port=3389
        # )

        management_host.connections.allow_from_any_ipv4(ec2.Port.tcp(3389), "Allow RDP Inbound")

        interface_endpoint_services = ("ec2", "ssm", "secretsmanager")

        for endpoint_service in interface_endpoint_services:
            security_vpc.add_interface_endpoint(
                "{}-Endpoint".format(endpoint_service),
                service = ec2.InterfaceVpcEndpointService("com.amazonaws.{region}.{endpoint_service}".format(region=self.region, endpoint_service=endpoint_service)),
                subnets=ec2.SubnetSelection(subnet_group_name="fw_mgmt")
            )

        ec2.CfnTransitGateway(self, "MyCdkTgw", default_route_table_propagation="disable", default_route_table_association="disable")

