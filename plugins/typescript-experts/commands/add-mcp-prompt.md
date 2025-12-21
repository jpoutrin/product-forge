---
description: Add a new prompt template to an existing FastMCP server
argument-hint: "[prompt-name]"
---

# Add MCP Prompt

Add a new prompt template to an existing FastMCP server for reusable LLM interactions.

## Usage

```bash
/add-mcp-prompt [prompt-name]
```

## Arguments

- `[prompt-name]`: Optional - Name for the prompt (will prompt if not provided)

## Execution Instructions for Claude Code

When this command is run:

1. **Locate the FastMCP server** in the current project
2. **Gather prompt requirements** through interactive questions
3. **Generate prompt code** based on configuration
4. **Add prompt to server** by modifying existing files

## Interactive Session Flow

### 1. Locate Server

```
Looking for FastMCP server...

Found: src/server.ts

Is this the correct server file? (yes/no):
```

### 2. Prompt Basics

```
Let's add a new prompt to your MCP server.

Prompt name (lowercase, use hyphens):
Example: "git-commit", "code-review", "summarize-document"

Prompt name:
```

```
Prompt description (shown to clients):
Example: "Generate a Git commit message from changes"

Description:
```

### 3. Prompt Arguments

```
Does this prompt require arguments?

1. No arguments
2. Single required argument
3. Multiple arguments (some optional)

Select (1-3):
```

If arguments needed:
```
Let's define the arguments.

Argument 1:
  Name:
  Description:
  Required? (yes/no):

Add another argument? (yes/no):
```

### 4. Argument Completion

For each argument:
```
How should "{argName}" support auto-completion?

1. No completion
2. Enum - Fixed list of options
3. Dynamic completion - Custom logic

Select (1-3):
```

If enum:
```
Enter enum values (comma-separated):
Example: "typescript,javascript,python,go"

Values:
```

If dynamic:
```
What kind of dynamic completion?

1. Search/filter from list
2. API lookup
3. File system suggestions
4. Custom (I'll implement)

Select (1-4):
```

### 5. Prompt Template

```
How would you like to define the prompt template?

1. Simple text template with argument interpolation
2. Multi-part structured prompt
3. I'll write the template manually

Select (1-3):
```

If simple template:
```
Write your prompt template. Use {argumentName} for argument placeholders.

Example:
"Review the following code and provide feedback on:
- Code quality
- Potential bugs
- Performance issues

Code to review:
{code}"

Your template:
```

### 6. Prompt Options

```
Additional options:

Should the prompt return multiple messages? (yes/no) [default: no]:

Include system message? (yes/no) [default: no]:
```

## Generated Code Examples

### Simple Prompt (No Arguments)

```typescript
server.addPrompt({
  name: "{{name}}",
  description: "{{description}}",
  load: async () => {
    return "Your prompt text here";
  },
});
```

### Prompt with Single Argument

```typescript
server.addPrompt({
  name: "{{name}}",
  description: "{{description}}",
  arguments: [
    {
      name: "{{argName}}",
      description: "{{argDescription}}",
      required: true,
    },
  ],
  load: async (args) => {
    return "{{promptTemplate}}".replace("{{{argName}}}", args.{{argName}});
  },
});
```

### Prompt with Multiple Arguments

```typescript
server.addPrompt({
  name: "{{name}}",
  description: "{{description}}",
  arguments: [
    {{#each arguments}}
    {
      name: "{{name}}",
      description: "{{description}}",
      required: {{required}},
    },
    {{/each}}
  ],
  load: async (args) => {
    const { {{argumentNames}} } = args;

    return "{{promptTemplate}}";
  },
});
```

### Prompt with Enum Completion

```typescript
server.addPrompt({
  name: "{{name}}",
  description: "{{description}}",
  arguments: [
    {
      name: "{{argName}}",
      description: "{{argDescription}}",
      required: true,
      enum: [{{#each enumValues}}"{{this}}"{{#unless @last}}, {{/unless}}{{/each}}],
    },
  ],
  load: async (args) => {
    return "Process the following in " + args.{{argName}} + " format:\n\n{content}";
  },
});
```

### Prompt with Dynamic Completion

```typescript
server.addPrompt({
  name: "{{name}}",
  description: "{{description}}",
  arguments: [
    {
      name: "{{argName}}",
      description: "{{argDescription}}",
      required: true,
      complete: async (value) => {
        // Search/filter logic
        const options = await getAvailableOptions();
        const filtered = options.filter(opt =>
          opt.toLowerCase().includes(value.toLowerCase())
        );
        return { values: filtered };
      },
    },
  ],
  load: async (args) => {
    const data = await loadData(args.{{argName}});
    return "Analyze the following data:\n\n" + JSON.stringify(data, null, 2);
  },
});
```

### Git Commit Message Prompt

```typescript
server.addPrompt({
  name: "git-commit",
  description: "Generate a Git commit message from changes",
  arguments: [
    {
      name: "changes",
      description: "Git diff or description of changes",
      required: true,
    },
    {
      name: "type",
      description: "Commit type",
      required: false,
      enum: ["feat", "fix", "docs", "style", "refactor", "test", "chore"],
    },
  ],
  load: async (args) => {
    const typeHint = args.type
      ? "Use commit type: " + args.type
      : "Choose appropriate commit type (feat, fix, docs, etc.)";

    return "Generate a concise Git commit message following conventional commits format.\n\n" +
      typeHint + "\n\n" +
      "Changes:\n" + args.changes + "\n\n" +
      "Format: <type>(<optional scope>): <description>\n\n" +
      "Keep the description under 72 characters.";
  },
});
```

### Code Review Prompt

```typescript
server.addPrompt({
  name: "code-review",
  description: "Review code for quality, bugs, and improvements",
  arguments: [
    {
      name: "code",
      description: "Code to review",
      required: true,
    },
    {
      name: "language",
      description: "Programming language",
      required: false,
      enum: ["typescript", "javascript", "python", "go", "rust"],
    },
    {
      name: "focus",
      description: "Focus area for review",
      required: false,
      enum: ["security", "performance", "readability", "all"],
    },
  ],
  load: async (args) => {
    const lang = args.language || "the detected language";
    const focus = args.focus || "all aspects";

    return "Review the following " + lang + " code, focusing on " + focus + ".\n\n" +
      "Provide feedback on:\n" +
      "1. Code quality and best practices\n" +
      "2. Potential bugs or edge cases\n" +
      "3. Performance considerations\n" +
      "4. Security issues (if applicable)\n" +
      "5. Suggestions for improvement\n\n" +
      "Code:\n```\n" + args.code + "\n```\n\n" +
      "Format your response with clear sections and specific line references where applicable.";
  },
});
```

### Document Summary Prompt

```typescript
server.addPrompt({
  name: "summarize",
  description: "Summarize a document or text",
  arguments: [
    {
      name: "content",
      description: "Content to summarize",
      required: true,
    },
    {
      name: "length",
      description: "Summary length",
      required: false,
      enum: ["brief", "detailed", "bullet-points"],
    },
    {
      name: "audience",
      description: "Target audience",
      required: false,
    },
  ],
  load: async (args) => {
    const style = {
      brief: "Provide a 2-3 sentence summary",
      detailed: "Provide a comprehensive summary with key points",
      "bullet-points": "Summarize as a bulleted list of key points",
    }[args.length || "brief"];

    const audienceNote = args.audience
      ? "Write for: " + args.audience
      : "";

    return style + ". " + audienceNote + "\n\n" +
      "Content to summarize:\n" + args.content;
  },
});
```

### Multi-Message Prompt

```typescript
server.addPrompt({
  name: "{{name}}",
  description: "{{description}}",
  arguments: [
    {
      name: "context",
      description: "Context for the conversation",
      required: true,
    },
  ],
  load: async (args) => {
    // Return array of messages for multi-turn context
    return [
      {
        role: "user",
        content: {
          type: "text",
          text: "Context: " + args.context,
        },
      },
      {
        role: "assistant",
        content: {
          type: "text",
          text: "I understand the context. How can I help?",
        },
      },
      {
        role: "user",
        content: {
          type: "text",
          text: "Now proceed with the main task...",
        },
      },
    ];
  },
});
```

## File Placement

```
Where should the prompt code be added?

1. Inline in server.ts
2. New file in prompts/ directory
3. Existing prompts file

Select (1-3):
```

## Implementation Notes

1. **Find existing server**: Locate FastMCP server files
2. **Check for prompts directory**: Create if needed
3. **Generate code**: Create prompt with selected options
4. **Add imports**: Ensure necessary imports exist
5. **Insert code**: Add prompt at appropriate location
6. **Summary**: Show generated prompt and usage example
