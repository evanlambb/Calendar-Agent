# LangSmith Setup Guide

LangSmith provides powerful tracing and observability for your calendar agent, allowing you to debug conversations, monitor performance, and analyze tool usage.

## Step 1: Get Your LangSmith API Key

1. Go to [https://smith.langchain.com](https://smith.langchain.com)
2. Sign up or sign in with your account
3. Click on your profile in the top right corner
4. Go to **Settings** → **API Keys**
5. Click **Create API Key**
6. Copy the generated API key (you won't be able to see it again!)

## Step 2: Create Environment Variables

Create a `.env` file in your project root with the following content:

```bash
# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=calendar-agent

# Google AI Configuration  
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Set to false to disable tracing temporarily
# LANGCHAIN_TRACING_V2=false
```

**Important:** Replace `your_langsmith_api_key_here` with your actual LangSmith API key from Step 1.

## Step 3: Verify Setup

Run your calendar agent:

```bash
python agent.py
```

If everything is configured correctly, you should see your traces appearing in the LangSmith dashboard at [https://smith.langchain.com](https://smith.langchain.com).

## Step 4: View Your Traces

1. Go to [https://smith.langchain.com](https://smith.langchain.com)
2. Navigate to the **Projects** section
3. Click on your **calendar-agent** project
4. You'll see all your agent conversations, tool calls, and performance metrics

## What You'll See in LangSmith

### 🔍 **Detailed Traces**
- Every conversation with your agent
- All tool calls (get_events, create_event, delete_event)
- Token usage and latency for each LLM call
- Input/output for every step

### 📊 **Performance Analytics**
- Response times
- Token consumption
- Error rates
- Most used tools

### 🐛 **Debugging Features**
- Step-by-step execution flow
- Tool call parameters and results
- Error messages and stack traces
- Feedback and annotation tools

## Troubleshooting

### Traces Not Appearing?

1. **Check your API key**: Make sure it's correctly set in `.env`
2. **Verify environment loading**: The agent loads `.env` on startup
3. **Check project name**: Make sure `LANGCHAIN_PROJECT=calendar-agent` matches your project
4. **Network issues**: Try `LANGCHAIN_ENDPOINT=https://api.smith.langchain.com`

### Temporarily Disable Tracing

Set `LANGCHAIN_TRACING_V2=false` in your `.env` file to turn off tracing without removing LangSmith entirely.

## Advanced Configuration

### Custom Project Names
You can create separate projects for different environments:

```bash
# Development
LANGCHAIN_PROJECT=calendar-agent-dev

# Production  
LANGCHAIN_PROJECT=calendar-agent-prod
```

### Environment-Specific Tracing
```bash
# Only trace in development
LANGCHAIN_TRACING_V2=true

# For production, you might want to sample traces
LANGCHAIN_TRACING_V2=false
```

## Security Note

- Never commit your `.env` file to version control
- Your `.env` file is already ignored by git in this project
- Keep your LangSmith API key secure and don't share it

---

**🎉 That's it!** Your calendar agent now has full observability with LangSmith. Every conversation, tool call, and decision will be tracked and available for analysis. 