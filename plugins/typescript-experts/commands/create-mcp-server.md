---
description: Scaffold a new FastMCP server project with customizable configuration
argument-hint: "[project-name]"
---

# Create MCP Server

Scaffold a new FastMCP Model Context Protocol server with interactive configuration.

## Usage

```bash
/create-mcp-server [project-name]
```

## Arguments

- `[project-name]`: Optional - Directory name for the new project (will prompt if not provided)

## Execution Instructions for Claude Code

When this command is run:

1. **Gather project information** through interactive questions
2. **Create project structure** with proper files and configuration
3. **Install dependencies** via npm
4. **Provide next steps** for development

## Interactive Session Flow

### 1. Project Setup

```
Welcome to the FastMCP Server Generator!

Let's create a new MCP server. I'll ask a few questions to set things up.

Project name [default: mcp-server]:
```

```
Server name (displayed to clients):
Example: "File Manager", "Database Tools", "API Gateway"

Server name:
```

```
Server version [default: 1.0.0]:
```

```
Brief description of your server:
Example: "Provides file system operations for document management"

Description:
```

### 2. Transport Configuration

```
Which transport type will you primarily use?

1. stdio (Recommended) - For Claude Desktop and CLI tools
2. HTTP Streaming - For web deployments and APIs
3. Both - Support multiple transport types

Select (1-3):
```

If HTTP selected:
```
Default port for HTTP server [default: 8080]:
```

```
Enable stateless mode for serverless deployments? (yes/no) [default: no]:
```

### 3. Feature Selection

```
Which features would you like to include?

1. Tools only (most common)
2. Tools + Resources
3. Tools + Resources + Prompts
4. Full setup (all features + examples)

Select (1-4):
```

### 4. Authentication

```
Do you need authentication?

1. No authentication (development/internal use)
2. API key authentication
3. OAuth 2.0 (Google, custom provider)
4. Custom authentication (I'll implement later)

Select (1-4):
```

### 5. Additional Options

```
Additional configuration:

Enable health check endpoint? (yes/no) [default: yes]:

Add example tools/resources? (yes/no) [default: yes]:

Initialize git repository? (yes/no) [default: yes]:
```

## Generated Project Structure

```
<project-name>/
├── src/
│   ├── server.ts           # Main server entry point
│   ├── tools/              # Tool definitions
│   │   └── index.ts
│   ├── resources/          # Resource definitions (if selected)
│   │   └── index.ts
│   └── prompts/            # Prompt definitions (if selected)
│       └── index.ts
├── package.json
├── tsconfig.json
├── .env.example
├── .gitignore
└── README.md
```

## Example Generated Files

### src/server.ts (stdio transport)

```typescript
import { FastMCP } from "fastmcp";
import { registerTools } from "./tools";

const server = new FastMCP({
  name: "{{server-name}}",
  version: "{{version}}",
  instructions: "{{description}}",
});

registerTools(server);

server.start({
  transportType: "stdio",
});
```

### src/server.ts (HTTP transport)

```typescript
import { FastMCP } from "fastmcp";
import { registerTools } from "./tools";

const server = new FastMCP({
  name: "{{server-name}}",
  version: "{{version}}",
  instructions: "{{description}}",
  health: {
    enabled: true,
    path: "/healthz",
    message: "healthy",
  },
});

registerTools(server);

server.start({
  transportType: "httpStream",
  httpStream: {
    port: {{port}},
  },
});
```

### src/tools/index.ts

```typescript
import { FastMCP } from "fastmcp";
import { z } from "zod";

export function registerTools(server: FastMCP) {
  // Example tool - remove or modify as needed
  server.addTool({
    name: "hello",
    description: "A simple hello world tool",
    parameters: z.object({
      name: z.string().describe("Name to greet"),
    }),
    execute: async (args) => {
      return `Hello, ${args.name}!`;
    },
  });
}
```

### package.json

```json
{
  "name": "{{project-name}}",
  "version": "{{version}}",
  "description": "{{description}}",
  "type": "module",
  "scripts": {
    "dev": "npx fastmcp dev src/server.ts",
    "dev:http": "npx fastmcp dev src/server.ts --transport http-stream --port {{port}}",
    "build": "tsc",
    "start": "node dist/server.js"
  },
  "dependencies": {
    "fastmcp": "latest",
    "zod": "^3.23.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Post-Creation Steps

After generating the project:

1. **Install dependencies**:
   ```bash
   cd {{project-name}} && npm install
   ```

2. **Start development**:
   ```bash
   npm run dev
   ```

3. **Test with MCP Inspector**:
   ```bash
   npx @anthropic/mcp-inspector npx fastmcp dev src/server.ts
   ```

4. **Add to Claude Desktop** (if using stdio):
   Add to `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "{{server-name}}": {
         "command": "npx",
         "args": ["fastmcp", "dev", "/path/to/{{project-name}}/src/server.ts"]
       }
     }
   }
   ```

## Implementation Notes

1. **File creation**: Use the Write tool to create all files
2. **Directory creation**: Ensure all directories exist before writing files
3. **Template substitution**: Replace all `{{placeholder}}` values with user inputs
4. **npm install**: Run `npm install` after creating files
5. **Git init**: If selected, run `git init` and create initial commit
6. **Summary**: Show created files and next steps
