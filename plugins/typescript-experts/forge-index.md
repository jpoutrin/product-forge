# TypeScript Experts Plugin

TypeScript development specialists for MCP server building with FastMCP and modern TypeScript patterns.

## Agents

### fastmcp-ts-expert
**TypeScript FastMCP specialist for building MCP servers**

Expert in FastMCP TypeScript framework for building Model Context Protocol servers. Specializes in tools, resources, prompts, authentication, session management, and transport configuration.

**When to use**: Building MCP servers with TypeScript, creating custom tools for Claude Code, implementing resource providers, adding prompts, configuring authentication, setting up transports

## Skills

### fastmcp
**TypeScript MCP server development with FastMCP**

Build MCP servers using the FastMCP TypeScript framework. Use when creating tools, resources, prompts, implementing authentication, session management, or configuring transports for Model Context Protocol servers.

**When to use**: User creates MCP servers, implements MCP tools/resources/prompts, or works with FastMCP framework

**Covers**:
- Tool creation with Zod, ArkType, or Valibot schemas
- Resources and resource templates
- Prompts with auto-completion
- Authentication (API key, role-based, OAuth)
- Session management and events
- Transport configuration (stdio, HTTP streaming, SSE)
- Progress reporting and streaming output
- Health checks and logging

### zod
**TypeScript-first schema validation with Zod**

Apply Zod patterns when writing schema validation, data parsing, or type-safe validation in TypeScript. Use for API input validation, form validation, configuration parsing, and runtime type checking.

**When to use**: User needs schema validation, data parsing, form validation, or runtime type checking in TypeScript

**Covers**:
- Schema definition and type inference
- Parsing methods (parse, safeParse, async variants)
- Primitive types and coercion
- String, number, and date validations
- Object schemas (partial, pick, omit, extend)
- Arrays, tuples, unions, and enums
- Optional, nullable, and default values
- Transforms and refinements
- Error handling and formatting
- Common patterns (API validation, env vars, forms)

## Commands

### /create-mcp-server
Scaffold a new FastMCP server project with customizable configuration. Interactive wizard for transport, features, and authentication setup.

### /add-mcp-tool
Add a new tool to an existing FastMCP server. Guides through parameters, return types, logging, progress, streaming, and authorization.

### /add-mcp-resource
Add a new resource or resource template to an existing FastMCP server. Supports static resources and dynamic templates with auto-completion.

### /add-mcp-prompt
Add a new prompt template to an existing FastMCP server. Configure arguments, enum options, and dynamic completion.

### /setup-mcp-auth
Configure authentication for an existing FastMCP server. Supports API key, role-based, OAuth 2.0, and JWT validation
