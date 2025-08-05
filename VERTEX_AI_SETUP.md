# PAAgent Vertex AI Setup Guide

This guide will help you migrate your PAAgent from OpenAI to Google Vertex AI with Claude Sonnet 4.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Vertex AI API** enabled
3. **Access to Claude models** in Vertex AI Model Garden
4. **Google Cloud SDK** installed and configured

## Step 1: Enable Vertex AI API

```bash
# Set your project ID
gcloud config set project YOUR-PROJECT-ID

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

## Step 2: Request Claude Model Access

1. Go to [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
2. Search for "Claude Sonnet 4"
3. Click "Enable" on the Claude Sonnet 4 model card
4. Wait for approval (may take 24-48 hours)

## Step 3: Configure Authentication

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Set your project ID
gcloud config set project YOUR-PROJECT-ID
```

## Step 4: Install Dependencies

```bash
# Install the updated requirements
pip install -r requirements.txt
```

## Step 5: Configure Environment Variables

Create a `.env` file with your configuration:

```bash
# Vertex AI Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id-here
VERTEX_AI_REGION=us-east5

# Google API Configuration (for Calendar, Gmail, Drive)
# Make sure you have the client_secret_*.json file in this directory

# Supabase Configuration (optional)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

## Step 6: Test the Setup

Run the setup script to test your configuration:

```bash
python setup_vertex_ai.py
```

This will:
- Verify your project ID and region
- Test the connection to Vertex AI
- Confirm Claude Sonnet 4 is accessible

## Step 7: Run Your PAAgent

Once setup is complete, you can run your PAAgent:

```bash
python api_server.py
```

## Model Configuration

Your PAAgent is now configured to use:

- **Primary Model**: `claude-sonnet-4@20250514` (Claude Sonnet 4)
- **Fast Model**: `claude-3-5-haiku@20241022` (Claude 3.5 Haiku for summaries)

## Key Changes Made

1. **Replaced OpenAI with Vertex AI**:
   - Updated `api_server.py` to use `AnthropicVertex`
   - Updated `calendar_assistant.py` to use Vertex AI
   - Changed model names to Vertex AI format

2. **Updated Requirements**:
   - Removed `openai` package
   - Added `google-cloud-aiplatform` and `anthropic[vertex]`

3. **Environment Variables**:
   - `GOOGLE_CLOUD_PROJECT_ID`: Your Google Cloud Project ID
   - `VERTEX_AI_REGION`: Region for Vertex AI (default: us-east5)

## Troubleshooting

### Common Issues

1. **"Model not found" errors**:
   - Ensure you have access to Claude models in Model Garden
   - Verify you're using the correct region (us-east5 recommended)

2. **Authentication errors**:
   - Run `gcloud auth application-default login`
   - Check your project ID is correct

3. **Quota issues**:
   - Check your Vertex AI quotas in Google Cloud Console
   - Request quota increases if needed

4. **Billing issues**:
   - Ensure billing is enabled for your project
   - Check your billing account has sufficient funds

### Regional Availability

Claude Sonnet 4 is available in these regions:
- `us-east5` (recommended)
- `europe-west1`
- `asia-east1`
- Global endpoint

## Cost Optimization

- **Prompt Caching**: Automatically enabled for repeated requests
- **Model Selection**: Uses Claude 3.5 Haiku for summaries (faster/cheaper)
- **Token Limits**: Configured for optimal cost/performance balance

## Next Steps

1. Test your API endpoints
2. Monitor usage in Google Cloud Console
3. Adjust model parameters as needed
4. Set up monitoring and alerts

## Support

If you encounter issues:
1. Check the Google Cloud Console for error details
2. Verify your Vertex AI quotas
3. Ensure all environment variables are set correctly
4. Test with the setup script first

Your PAAgent is now running on Google Vertex AI with Claude Sonnet 4! 🎉 