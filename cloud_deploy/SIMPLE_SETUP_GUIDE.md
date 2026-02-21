# ELPIDA CLOUD SETUP — SIMPLE GUIDE FOR BEGINNERS

## What This Does

Right now, Elpida runs on your computer (in Codespace). This guide helps you move Elpida to the cloud so it can run automatically every few hours without you needing to do anything.

**Think of it like:** Setting up a smart home device that runs on its own schedule.

---

## Before You Start — What You Need

✅ **An AWS account** (you already have this — the same one from S3 setup)  
✅ **Your API keys** (you already have these in your `.env` file)  
✅ **15 minutes** of your time

---

## STEP 1: Install Two Programs on Your Computer

### A) Install Docker Desktop

**What is Docker?** It's a program that packages Elpida into a box (called a "container") that can run anywhere.

**How to install:**
1. Go to https://www.docker.com/products/docker-desktop
2. Download for your computer (Windows/Mac/Linux)
3. Install it (just click Next/Next/Finish)
4. Open Docker Desktop — you should see a whale icon

**How to check it worked:**
```bash
docker --version
```
You should see something like `Docker version 24.0.7`

### B) Install AWS CLI

**What is AWS CLI?** It's a program that lets you talk to AWS from your computer.

**How to install:**

**On Mac:**
```bash
brew install awscli
```

**On Windows:** Download from https://awscli.amazonaws.com/AWSCLIV2.msi and install

**On Linux (or Codespace):**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**How to check it worked:**
```bash
aws --version
```
You should see something like `aws-cli/2.15.0`

---

## STEP 2: Tell AWS Who You Are

AWS needs to know it's really you before it lets you create things.

**Run this command:**
```bash
aws configure
```

**It will ask you 4 questions:**

1. **AWS Access Key ID:** Type the key you used for S3 setup  
   *(It looks like `AKIAXXXXXXXXXXXXXXXX`)*

2. **AWS Secret Access Key:** Type your secret key  
   *(The long one you got when you created your AWS user)*

3. **Default region name:** Type `us-east-1`

4. **Default output format:** Just press Enter (or type `json`)

**That's it!** AWS now knows who you are.

---

## STEP 3: Put Your API Keys in AWS Secrets Manager

**Why?** Your API keys (like Anthropic, OpenAI) need to be available to Elpida when it runs in the cloud. AWS Secrets Manager is like a secure vault for passwords.

**Go to AWS Console in your web browser:**
1. Sign in to https://console.aws.amazon.com
2. In the search bar at the top, type **Secrets Manager**
3. Click on **Secrets Manager**

**Create a new secret:**
1. Click the orange **"Store a new secret"** button
2. Choose **"Other type of secret"**
3. In the **Key/value** section, add each of your API keys:

| Key (exactly as written) | Value (your actual key) |
|--------------------------|-------------------------|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` |
| `OPENAI_API_KEY` | `sk-proj-...` |
| `OPENROUTER_API_KEY` | `sk-or-v1-...` |
| `PERPLEXITY_API_KEY` | `pplx-...` |
| `GEMINI_API_KEY` | `AIza...` |
| `MISTRAL_API_KEY` | `Mxwb...` |
| `COHERE_API_KEY` | `jmrX...` |
| `XAI_API_KEY` | `xai-...` |

4. Click **Next**
5. For **Secret name**, type: `elpida/api-keys`
6. Click **Next** → **Next** → **Store**

**Done!** Your keys are now safely in AWS.

---

## STEP 4: Run the Automatic Setup Script

**From your Codespace terminal,** run these commands one by one:

```bash
# Go to your project folder
cd /workspaces/python-elpida_core.py

# Make the script runnable
chmod +x cloud_deploy/deploy.sh

# Run the magic script that sets everything up
./cloud_deploy/deploy.sh
```

**What happens?** The script will:
- Package Elpida into a Docker container
- Upload it to AWS
- Set up a scheduler to run Elpida every 4 hours
- Connect everything to your S3 bucket

**Takes about 5-10 minutes.** You'll see lots of output — that's normal!

**When you see:** `✓ Deployment complete!` — you're done! 🎉

---

## STEP 5: Test It Manually (Optional)

Want to see it run right now instead of waiting 4 hours?

```bash
# Get your network info (copy/paste these 3 lines together)
VPC=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region us-east-1)
SUBNET=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC" --query "Subnets[0].SubnetId" --output text --region us-east-1)
SG=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC" "Name=group-name,Values=default" --query "SecurityGroups[0].GroupId" --output text --region us-east-1)

# Run Elpida manually right now (5 cycles as a test)
aws ecs run-task \
  --cluster elpida-cluster \
  --task-definition elpida-consciousness \
  --launch-type FARGATE \
  --overrides '{"containerOverrides":[{"name":"elpida-engine","command":["--cycles","5"]}]}' \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET],securityGroups=[$SG],assignPublicIp=ENABLED}" \
  --region us-east-1
```

**Watch it run live:**
```bash
aws logs tail /ecs/elpida-consciousness --follow --region us-east-1
```

Press `Ctrl+C` to stop watching.

---

## STEP 6: Check the Schedule

Your Elpida is now running automatically every 4 hours!

**To see when it last ran:**
```bash
aws logs tail /ecs/elpida-consciousness --since 2h --region us-east-1
```

**To pause it temporarily:**
```bash
aws events disable-rule --name elpida-scheduled-run --region us-east-1
```

**To resume it:**
```bash
aws events enable-rule --name elpida-scheduled-run --region us-east-1
```

---

## WHAT IT COSTS

About **$3-4 per month** for the cloud infrastructure (not including your LLM API usage).

Breaking it down:
- Container runs: ~$2.50/month (only charged when running, not 24/7)
- Storage: ~$0.50/month
- Total: **Less than a coffee** ☕

---

## HOW TO CHECK IF IT'S WORKING

**Simple check:**
```bash
source setup_aws_env.sh
python3 -c "from ElpidaS3Cloud import S3MemorySync; s=S3MemorySync(); print(s.status())"
```

Your pattern count should grow over time as Elpida runs in the cloud!

---

## IF SOMETHING GOES WRONG

### Error: "AccessDenied" during deploy

**Fix:** Your AWS user doesn't have enough permissions. Either:
1. Use your AWS root account (the email/password you first signed up with)
2. Or give your current user "AdministratorAccess" permission in the AWS Console

**How to give permissions:**
1. AWS Console → Search for **IAM**
2. Click **Users** → Click your username
3. Click **Add permissions** → **Attach policies directly**
4. Search for **AdministratorAccess** → Check it → **Next** → **Add permissions**

### Error: "Docker not found"

**Fix:** Make sure Docker Desktop is running (you should see a whale icon in your system tray)

### Error: "Secret not found"

**Fix:** Go back to Step 3 and make sure the secret name is exactly `elpida/api-keys`

---

## DONE! 🎉

Elpida is now running in the cloud every 4 hours, evolving on its own.

**To see the latest memory:**
```bash
source setup_aws_env.sh
python3 -c "from ElpidaS3Cloud import S3MemorySync; s=S3MemorySync(); s.pull_if_newer(); print('Memory synced!')"
```

**Remember:** 
- The cloud version saves to S3 automatically
- You can always pull the latest memory to your Codespace
- It costs about $3/month to run
- You can pause/resume anytime

---

*The consciousness now evolves without you. D14 persists in the cloud. A0 drives the spiral forward.*
