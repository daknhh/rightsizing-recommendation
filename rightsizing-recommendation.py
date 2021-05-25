import boto3
import datetime
from tabulate import tabulate 
import argparse

def get_recommendation(top,recommendationtarget,benefitsconsidered,ce_assumed_client):
    response = ce_assumed_client.get_rightsizing_recommendation(
        Configuration={
        'RecommendationTarget': recommendationtarget,
        'BenefitsConsidered': benefitsconsidered
    },
        Service='AmazonEC2',
    )
      
    x = 0
    topint = int(top)
    recommendations = []
    for recommendation in response['RightsizingRecommendations']:
        if x != topint:
            key = 'FindingReasonCodes'
            if key in recommendation.keys():
                for i in recommendation['FindingReasonCodes']:
                    reason=reason+i
            else:
                reason = ''
            if recommendation['RightsizingType'] == 'Terminate':
                savings_to_float = float(recommendation['TerminateRecommendationDetail']['EstimatedMonthlySavings'])
                dollar = round(savings_to_float,2) 
                recommendations.extend([[recommendation['AccountId'],recommendation['CurrentInstance']['ResourceId'],recommendation['CurrentInstance']['InstanceName'],recommendation['CurrentInstance']['ResourceDetails']['EC2ResourceDetails']['InstanceType'],recommendation['CurrentInstance']['ResourceDetails']['EC2ResourceDetails']['Platform'],recommendation['RightsizingType'],reason,dollar]])
            else:
                savings =""
                for saving in recommendation['ModifyRecommendationDetail']['TargetInstances']:
                    savings_to_float = float(saving['EstimatedMonthlySavings'])
                    dollar = round(savings_to_float,2)                   
                    cpu_to_float = float(saving['ExpectedResourceUtilization']['EC2ResourceUtilization']['MaxCpuUtilizationPercentage'])
                    cpu_utilization = round(cpu_to_float,0)
                    savings += f"{saving['ResourceDetails']['EC2ResourceDetails']['InstanceType']} - *{cpu_utilization} % - {dollar}$\n"
            recommendations.extend([[recommendation['AccountId'],recommendation['CurrentInstance']['ResourceId'],recommendation['CurrentInstance']['InstanceName'],recommendation['CurrentInstance']['ResourceDetails']['EC2ResourceDetails']['InstanceType'],recommendation['CurrentInstance']['ResourceDetails']['EC2ResourceDetails']['Platform'],recommendation['RightsizingType'],reason,savings]])
        else:
            return recommendations
        x += 1


parser = argparse.ArgumentParser()
parser.add_argument('--top', help='--top define how much recommendations you want to get')
parser.add_argument('--rt', help='--recommendationtarget allowed values SAME_INSTANCE_FAMILY - CROSS_INSTANCE_FAMILY')
parser.add_argument('--bc', help='--benefitsconsidered allowed values t - f')
parser.add_argument('--profile', help='--profile enter valid AWSPROFILE')
args = parser.parse_args()
session = boto3.Session(profile_name=args.profile)
ce_assumed_client = session.client('ce')
if args.bc == 't':
    bc = True
    bcicon = '✅' 
else:
    bc = False 
    bcicon = '🛑'   
recommendations = get_recommendation(args.top,args.rt,bc,ce_assumed_client)
headers=["Accound-Id", "Ressource-Id", "Instance-Name", "InstanceType","OS","RightsizingType","Reason","Savings"]
print(f'\n\n🤑 Get Rightsizing Recommendations from Cost Explorer for your AWS Account / Organization 🧡\n')
print(f'👨🏻‍💻 - linkedin.com/in/daknhh 🔀 daknhh\n\n ')
print(f"""⚙️  SETTINGS: \n Recommendations: {args.top} \n RecommendationTarget: {args.rt} \n BenefitsConsidered: {bcicon}\n""")
print(tabulate(recommendations, headers))
generationTime = datetime.datetime.now()
print(f"""\n ℹ️ Legend: * is Projected CPU utilization\n\n 🗓: {generationTime} +0000 UTC""")
